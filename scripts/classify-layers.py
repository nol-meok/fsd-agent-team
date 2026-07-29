#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FSD 레이어 판정 — 파일명이 아니라 코드 의미로 분류한다.

왜 이 도구가 있는가
  2026-07-27 client-brics-works(963파일) 마이그레이션에서 파일명 기반 분류의
  실측 정확도가 **73%** 였다. `*Content.tsx` `*Card.tsx` `*Header.tsx` 같은 중립적
  이름을 쓰면서 실제로는 변경 API를 호출하는 컴포넌트가 많았다. 557개 중 148개가
  이름과 내용이 불일치했고, 최종적으로 171개 컴포넌트의 레이어가 이름 기반 배정과
  달랐다 (widgets→features 72 · features→widgets 96 · →shared 3).

판정 기준
  features  유즈케이스를 소유한다
            - 변경 API 호출 (직접 또는 자기 훅/lib 경유)
            - 폼 상태 소유 (useForm / zodResolver / handleSubmit)
            - 공유·URL 상태 쓰기
  widgets   표시·조합만 한다
            - 조회 훅이나 props 로 받아 렌더
            - 로컬 표현 상태(아코디언·모달 열림·입력 초안)만
            - 실제 동작은 부모 콜백이나 자식 feature 에 위임
  shared    같은 레이어의 2개 이상 슬라이스가 사용한다
            (FSD 는 같은 레이어 교차 import 를 금지한다)

이 도구가 하는 일
  1) tsconfig.json 의 paths 로 import 를 실제 해석해 의존 그래프를 만든다
  2) 변경/조회 신호를 뽑아 features-확실 / widgets-확실 / 애매 로 나눈다
  3) 간접 변경은 "변경이 어디서 오는가" 로 갈라준다
     자기 훅·lib 경유 → features / 자식 컴포넌트만 → widgets(조합)
  4) 같은 레이어 교차 사용 파일을 찾아준다 (shared 로 내릴 후보)
  5) **애매 목록을 내놓는다. 이건 사람이 읽고 판정해야 한다** — 도구가 추측하지 않는다

사용법
  python3 scripts/classify-layers.py <프로젝트경로> [옵션]

    --src DIR         분석 대상 디렉토리 (반복 가능, 기본: src app lib 중 존재하는 것)
    --generated DIR   자동 생성 API 디렉토리. 있으면 동사를 전수 추출해 읽기 동사를 뺀 나머지를
                      모두 변경으로 본다 (예: __generated__)
    --read-verbs CSV  읽기 동사 화이트리스트 (기본: Get,Find,Count,Is,List,Fetch,Read,Search)
    --slices FILE     경로→슬라이스 매핑 JSON. 있으면 교차 슬라이스 검사를 수행한다
                      형식: {"원본경로": "슬라이스명"}
    --json FILE       결과를 JSON 으로 저장

주의 (실제로 틀렸던 것들)
  * 생성 API 는 훅(use…)뿐 아니라 **명령형 호출**(`dealControllerUpdateX(...)`)로도 쓰인다.
    둘 다 잡아야 한다.
  * mutator 를 직접 부르는 코드(`await fetcher({...})`)도 변경이다.
  * 동사 경계는 `\\bGet\\b` 로 잡히지 않는다 — `GetAddFoo` 처럼 대문자가 이어진다.
  * 순환 의존이 있으면 재귀+메모가 부분 결과를 캐시한다. 고정점 반복을 써야 한다.
  * 읽기용 `fetch(` 를 변경으로 오판하지 않도록 mutator 이름만 본다.
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

EXTS = (".ts", ".tsx")
IMPORT = re.compile(r"""(?:from|import)\s*\(?\s*['"]([^'"]+)['"]""")

DEFAULT_READ_VERBS = ["Get", "Find", "Count", "Is", "List", "Fetch", "Read", "Search"]

# 프레임워크 중립 변경 신호
MUT_GENERIC = re.compile(
    r"(useMutation\b|useSWRMutation\b|\bmutateAsync\b|"
    r"axios\.(post|put|patch|delete)\b|"
    r"fetch\([^)]*method\s*:\s*['\"](POST|PUT|PATCH|DELETE)['\"]|"
    r"\$fetch\([^)]*method)", re.I)
FORM_OWNER = re.compile(r"(useForm\b|zodResolver|handleSubmit\b|useFieldArray\b)")
SHARED_WRITE = re.compile(
    r"(useQueryStates?\s*\(|setQueryParams|setSearchParams|"
    r"\bdispatch\s*\(|\.setState\s*\(|useStore\w*\s*\([^)]*=>[^)]*set)")
LOCAL_ONLY = re.compile(r"(useState|useReducer)")
HANDLER = re.compile(r"\bon[A-Z]\w*\s*[=:]")


def strip_jsonc(text):
    """JSONC(주석 허용 JSON)에서 주석과 트레일링 콤마를 제거한다.

    정규식으로 하면 안 된다. tsconfig 의 경로 글롭이 주석으로 오인된다:
    `"@/app/*"` 의 `/*` 부터 `"**/*.ts"` 의 `*/` 까지 한 덩어리로 지워져
    paths 블록이 사라진다 (실제로 그렇게 별칭 0개가 되어 alias import 를 전부 놓쳤다).
    문자열 안/밖을 추적하며 한 글자씩 본다.
    """
    out = []
    i, n = 0, len(text)
    in_str = in_line = in_block = False
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_line:
            if c == "\n":
                in_line = False
                out.append(c)
        elif in_block:
            if c == "*" and nxt == "/":
                in_block = False
                i += 1
        elif in_str:
            out.append(c)
            if c == "\\":
                if i + 1 < n:
                    out.append(nxt)
                    i += 1
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
                out.append(c)
            elif c == "/" and nxt == "/":
                in_line = True
                i += 1
            elif c == "/" and nxt == "*":
                in_block = True
                i += 1
            else:
                out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def load_aliases(project):
    """tsconfig.json 의 compilerOptions.paths 를 읽어 별칭 → 실제 경로로 만든다."""
    aliases = {}
    tsconfig = os.path.join(project, "tsconfig.json")
    if not os.path.isfile(tsconfig):
        return aliases
    try:
        cfg = json.loads(strip_jsonc(open(tsconfig, encoding="utf-8").read()))
    except ValueError:
        return aliases
    co = cfg.get("compilerOptions", {})
    base = co.get("baseUrl", ".")
    for pat, targets in (co.get("paths") or {}).items():
        if not targets:
            continue
        t = targets[0]
        if "node_modules" in t:
            continue
        aliases[pat.replace("*", "")] = os.path.normpath(
            os.path.join(base, t.replace("*", ""))).lstrip("./") or ""
    return aliases


def make_resolver(project, aliases):
    def resolve(spec, frm):
        target = None
        if spec.startswith("."):
            target = os.path.normpath(os.path.join(os.path.dirname(frm), spec))
        else:
            for a in sorted(aliases, key=len, reverse=True):
                if spec.startswith(a):
                    target = os.path.normpath(aliases[a] + spec[len(a):])
                    break
        if target is None:
            return None
        cands = [target + e for e in EXTS] + \
                [os.path.join(target, "index" + e) for e in EXTS]
        for c in cands:
            if os.path.isfile(os.path.join(project, c)):
                return c
        return None
    return resolve


def extract_generated_verbs(project, generated):
    """생성 API 이름에서 동사를 전수 추출한다. 추측 목록보다 정확하다."""
    verbs = set()
    root = os.path.join(project, generated)
    pat = re.compile(r"\b[a-zA-Z0-9]+Controller([A-Z][A-Za-z0-9]*)\b")
    for dp, _dn, fns in os.walk(root):
        for fn in fns:
            if not fn.endswith(EXTS):
                continue
            try:
                s = open(os.path.join(dp, fn), encoding="utf-8").read()
            except OSError:
                continue
            for v in pat.findall(s):
                m = re.match(r"[A-Z][a-z]+", v)
                if m:
                    verbs.add(m.group(0))
    return verbs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--src", action="append", default=[])
    ap.add_argument("--generated")
    ap.add_argument("--read-verbs")
    ap.add_argument("--slices")
    ap.add_argument("--json")
    a = ap.parse_args()

    project = os.path.abspath(a.project)
    srcs = a.src or [d for d in ("src", "app", "lib") if os.path.isdir(os.path.join(project, d))]
    if not srcs:
        sys.exit("분석할 디렉토리가 없습니다. --src 로 지정하세요.")

    read_verbs = [v.strip() for v in a.read_verbs.split(",")] if a.read_verbs else DEFAULT_READ_VERBS
    # 경계 주의: \b 는 GetAddFoo 에서 매칭되지 않는다. 다음 대문자/끝을 직접 본다.
    read_re = re.compile(r"^(%s)(?=[A-Z0-9]|$)" % "|".join(read_verbs))

    gen_verbs = extract_generated_verbs(project, a.generated) if a.generated else set()
    if gen_verbs:
        mut_verbs = sorted(v for v in gen_verbs if not read_re.match(v))
        print("생성 API 동사 %d종 추출 — 읽기 %d / 변경 %d"
              % (len(gen_verbs), len(gen_verbs) - len(mut_verbs), len(mut_verbs)))

    # 생성 API 호출: 훅 형태와 명령형 형태 둘 다
    gen_hook = re.compile(r"\buse([A-Za-z0-9]+?)Controller([A-Z][A-Za-z0-9]*)")
    gen_fn = re.compile(r"\b([a-z][A-Za-z0-9]*?)Controller([A-Z][A-Za-z0-9]*)\s*\(")
    # mutator 직접 호출. 단 fetcher 는 조회에도 쓰이므로 method 를 봐야 한다.
    # (PostViewerDialog 는 GET 전용인데 변경으로 오판했었다)
    raw_mutator_call = re.compile(
        r"\bfetcher\s*(?:<[^>]*>)?\s*\(\s*\{(.{0,400}?)\}", re.S)
    mut_method = re.compile(r"method\s*:\s*['\"](POST|PUT|PATCH|DELETE)['\"]", re.I)
    any_method = re.compile(r"method\s*:", re.I)

    aliases = load_aliases(project)
    resolve = make_resolver(project, aliases)

    files = []
    for d in srcs:
        for dp, dn, fns in os.walk(os.path.join(project, d)):
            dn[:] = [x for x in dn if x != "node_modules"]
            for fn in fns:
                if fn.endswith(EXTS):
                    files.append(os.path.relpath(os.path.join(dp, fn), project))
    files.sort()

    src_of, deps, facts = {}, defaultdict(set), {}
    for f in files:
        try:
            s = src_of[f] = open(os.path.join(project, f), encoding="utf-8").read()
        except OSError:
            continue
        mut = set()
        qry = set()
        for dom, verb in gen_hook.findall(s):
            (qry if read_re.match(verb) else mut).add(dom + verb)
        for dom, verb in gen_fn.findall(s):
            if dom.startswith("use"):
                continue
            (qry if read_re.match(verb) else mut).add(dom + verb)
        facts[f] = {
            "mutApi": sorted(mut), "queryApi": sorted(qry),
            "mutGeneric": bool(MUT_GENERIC.search(s)),
            "rawMutator": any(mut_method.search(m) for m in raw_mutator_call.findall(s)),
            # method 를 못 읽은 fetcher 호출이 있으면 사람이 확인해야 한다
            "rawFetcherUnknown": any(not any_method.search(m)
                                     for m in raw_mutator_call.findall(s)),
            "form": bool(FORM_OWNER.search(s)),
            "sharedWrite": bool(SHARED_WRITE.search(s)),
            "handler": bool(HANDLER.search(s)),
            "local": bool(LOCAL_ONLY.search(s)),
        }
        for spec in IMPORT.findall(s):
            t = resolve(spec, f)
            if t and t != f:
                deps[f].add(t)

    direct = {f for f, v in facts.items()
              if v["mutApi"] or v["mutGeneric"] or v["rawMutator"]}

    # 순환 의존이 있으므로 고정점 반복으로 전파한다 (재귀+메모는 부분 결과를 캐시해 틀린다)
    via_hook = dict.fromkeys(facts, False)
    via_comp = dict.fromkeys(facts, False)
    changed = True
    while changed:
        changed = False
        for f in facts:
            for d in deps[f]:
                if d not in facts:
                    continue
                if not (d in direct or via_hook[d] or via_comp[d]):
                    continue
                key = via_comp if d.endswith(".tsx") else via_hook
                if not key[f]:
                    key[f] = True
                    changed = True

    result = {}
    for f, v in facts.items():
        if f in direct or v["form"] or v["sharedWrite"]:
            bucket, why = "features", "변경 API/폼 소유/공유상태 쓰기 (직접 증거)"
        elif via_hook[f]:
            bucket, why = "features", "자기 훅·lib 을 통해 변경 API 호출"
        elif via_comp[f]:
            bucket, why = "ambiguous", "자식 컴포넌트만 변경 — 조합일 수 있다. 읽고 판정"
        elif v["rawFetcherUnknown"]:
            bucket, why = "ambiguous", "mutator 직접 호출인데 method 를 못 읽었다. 읽고 판정"
        elif not v["handler"] and not v["local"]:
            bucket, why = "widgets", "조회·props 표시 전용 (핸들러·로컬상태 없음)"
        else:
            bucket, why = "ambiguous", "핸들러·로컬상태만 — 부모 위임인지 확인 필요. 읽고 판정"
        result[f] = {"bucket": bucket, "why": why, "facts": v}

    # ---- 같은 레이어 교차 사용 검사
    cross = {}
    if a.slices:
        slices = json.load(open(a.slices, encoding="utf-8"))
        importers = defaultdict(set)
        for f in facts:
            for d in deps[f]:
                importers[d].add(f)
        for f in facts:
            users = {slices[u] for u in importers.get(f, ())
                     if u in slices and slices.get(u) != slices.get(f)}
            if len(users) >= 2:
                cross[f] = sorted(users)

    n = len(result)
    counts = defaultdict(int)
    for v in result.values():
        counts[v["bucket"]] += 1
    print("\n분석 %d개 파일 (별칭 %d개 해석)" % (n, len(aliases)))
    for k in ("features", "widgets", "ambiguous"):
        print("  %-10s %4d개 (%4.1f%%)" % (k, counts[k], 100.0 * counts[k] / max(n, 1)))
    print("\n  ★ ambiguous %d개는 도구가 판정하지 않는다. 읽고 정해야 한다." % counts["ambiguous"])
    if cross:
        print("\n같은 레이어 교차 사용 %d개 → shared 로 내릴 후보" % len(cross))
        for f, users in sorted(cross.items(), key=lambda x: -len(x[1]))[:15]:
            print("  %-56s %d개 슬라이스" % (os.path.basename(f), len(users)))

    if a.json:
        json.dump({"buckets": result, "crossSlice": cross},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("\n→ %s 저장" % a.json)


if __name__ == "__main__":
    main()
