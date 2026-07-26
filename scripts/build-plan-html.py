#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
작업계획서 HTML 빌더

docs/plan-template.html 을 단일 소스로 두고, PLAN 데이터(JSON)와 .md 본문을
센티넬 라인에 주입해서 plans/**/*.html 을 생성한다.

사용법:
  # 빌드 (PLAN JSON을 stdin으로)
  python3 scripts/build-plan-html.py plans/feature/20260727-foo.md < plan.json

  # 빌드 (PLAN JSON을 파일로)
  python3 scripts/build-plan-html.py plans/feature/20260727-foo.md --data plan.json

  # 기존 산출물 점검 (수정 없음)
  python3 scripts/build-plan-html.py plans/feature/20260727-foo.html --verify-only

왜 빌더를 쓰는가:
  템플릿을 직접 문자열 치환하면 안 된다. 2026-07-26에 `tpl.index('<script id="plan-data">')`
  로 치환했다가 상단 사용법 주석 안의 동일 문구가 먼저 매칭됐고, 주석 종료 `-->`가 함께
  삭제되어 PLAN 정의가 주석에 갇혔다. 렌더러가 ReferenceError로 죽어 화면이 완전히 비었는데,
  검증도 같은 정규식을 써서 "정상"이라고 보고했다.

  그래서 이 빌더는:
   1) 프로세 텍스트에 나타날 수 없는 센티넬(`@@PLAN_JSON@@`)만 치환한다.
   2) 센티넬이 정확히 1개인지 확인한다 (0개/2개면 에러).
   3) 검증은 HTML 주석을 먼저 제거한 뒤, 필수 요소가 주석 '밖'에 있는지 본다.
   4) PLAN을 순수 JSON으로 주입해서 json.loads()로 실제 파싱을 확인한다.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "docs" / "plan-template.html"

SENTINEL_JSON = "@@PLAN_JSON@@"
SENTINEL_MD = "@@PLAN_MD@@"

# 센티넬 라인 전체를 잡는다 (줄 시작 앵커 — 문서가 자기 태그를 설명 문구로 담고 있어도 안전)
RE_SENTINEL_JSON = re.compile(r"^[ \t]*/\*[ \t]*" + re.escape(SENTINEL_JSON) + r"[ \t]*\*/[ \t]*$", re.M)
RE_SENTINEL_MD = re.compile(r"^[ \t]*" + re.escape(SENTINEL_MD) + r"[ \t]*$", re.M)

RE_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

REQUIRED_KEYS = ("title", "type", "scope", "summary", "mdFile")
VALID_TYPES = ("feature", "bugfix", "refactor", "migrate")


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- 주입 헬퍼


def js_safe(text):
    """script 요소 안에 넣을 때 조기 종료를 막는다.

    raw text 요소(script)는 `</script` 를 만나면 즉시 끝난다. JSON 문자열
    안에서는 `<\\/` 가 유효한 이스케이프(\\/ → /)이므로 의미가 보존된다.
    """
    return text.replace("</", "<\\/")


def md_safe(text):
    """text/markdown 스크립트 블록에 넣을 md 본문을 보호한다.

    md 안에 `</script` 가 있으면 블록이 조기 종료되어 나머지 본문이
    문서에 그대로 유출된다. 흔치 않지만 발생하면 조용히 깨지므로 막는다.
    """
    if "</script" in text.lower():
        raise BuildError(
            "md 본문에 '</script' 문자열이 있습니다. HTML 주입이 조기 종료되므로 "
            "코드 펜스 안에서 표기를 바꾸거나(예: '<\\/script') 제거해주세요."
        )
    return text


def inject(template, plan_json, md_body):
    """센티넬을 정확히 1회씩 치환한다."""
    for name, pattern in (("PLAN_JSON", RE_SENTINEL_JSON), ("PLAN_MD", RE_SENTINEL_MD)):
        hits = len(pattern.findall(template))
        if hits != 1:
            raise BuildError(
                f"템플릿의 {name} 센티넬이 {hits}개입니다 (정확히 1개여야 함). "
                f"{TEMPLATE.relative_to(REPO_ROOT)} 를 확인하세요."
            )

    out = RE_SENTINEL_JSON.sub(lambda _: plan_json, template, count=1)
    out = RE_SENTINEL_MD.sub(lambda _: md_body, out, count=1)
    return out


# ---------------------------------------------------------------- 검증


def strip_comments(html):
    """HTML 주석을 제거한다. 검증은 항상 이 결과에 대해 수행한다."""
    return RE_HTML_COMMENT.sub("", html)


def structural_plan_check(raw):
    """JS 객체 리터럴을 구조만 확인한다 (파이썬에서 JS 를 온전히 파싱할 수는 없다).

    빌더가 만든 산출물은 항상 순수 JSON 이므로 이 경로를 타지 않는다.
    빌더 도입 이전에 손으로 작성된 레거시 계획서를 점검할 때만 쓴다.
    """
    if not raw.strip().startswith("const PLAN"):
        return False, "const PLAN 으로 시작하지 않음"
    if raw.count("{") != raw.count("}"):
        return False, f"중괄호 불균형 ({raw.count('{')} open / {raw.count('}')} close)"
    if raw.count("[") != raw.count("]"):
        return False, f"대괄호 불균형 ({raw.count('[')} open / {raw.count(']')} close)"
    for key in ("title", "type", "decisions"):
        if not re.search(r'["\']?\b' + key + r'\b["\']?\s*:', raw):
            return False, f"{key} 키 없음"
    return True, ""


def verify(html, source_label="산출물", strict=True):
    """생성물이 브라우저에서 실제로 렌더링될 수 있는지 확인한다.

    strict=True  — PLAN 이 순수 JSON 이어야 한다 (빌더 산출물)
    strict=False — JS 객체 리터럴도 구조 검사로 통과시킨다 (레거시 점검)

    반환: (ok: bool, checks: list[(passed, message)])
    """
    checks = []

    def check(passed, message):
        checks.append((bool(passed), message))
        return bool(passed)

    # 1) 주석 짝이 맞는가 — 안 맞으면 아래 검사 전체가 무의미해진다
    open_n, close_n = html.count("<!--"), html.count("-->")
    check(open_n == close_n, f"HTML 주석 짝 균형 ({open_n} open / {close_n} close)")

    # 2) 주석을 제거한 뒤 필수 요소가 '주석 밖'에 있는가
    bare = strip_comments(html)

    n_data = len(re.findall(r'<script\s+id="plan-data"', bare))
    check(n_data == 1, f'주석 밖에 <script id="plan-data"> 정확히 1개 ({n_data}개 발견)')

    n_md = len(re.findall(r'<script\s+id="plan-md"', bare))
    check(n_md == 1, f'주석 밖에 <script id="plan-md"> 정확히 1개 ({n_md}개 발견)')

    # 3) PLAN 정의가 주석 밖에 있는가 (사고의 직접 원인)
    check(re.search(r"^\s*const PLAN\s*=", bare, re.M) is not None,
          "주석 밖에 `const PLAN =` 정의 존재")

    # 4) 센티넬 잔여물 없음
    leftovers = [s for s in (SENTINEL_JSON, SENTINEL_MD) if s in html]
    check(not leftovers, f"센티넬 잔여물 없음 {leftovers if leftovers else ''}".strip())

    # 5) PLAN 이 실제로 파싱되는가 — 파싱 성공이 렌더링을 보장하진 않지만,
    #    실패하면 확실히 렌더링되지 않는다
    plan_obj = None
    m = re.search(r'<script\s+id="plan-data">(.*?)</script>', bare, re.S)
    if m:
        raw_block = m.group(1).strip()
        raw = re.sub(r"^const PLAN\s*=\s*", "", raw_block).rstrip().rstrip(";")
        try:
            plan_obj = json.loads(raw)
            check(True, "PLAN JSON 파싱 성공")
        except json.JSONDecodeError as exc:
            if strict:
                check(False, f"PLAN JSON 파싱 실패: {exc}")
            else:
                ok_struct, reason = structural_plan_check(raw_block)
                check(ok_struct,
                      "PLAN 구조 검사 통과 — 레거시 JS 리터럴 (빌더로 재생성 권장)"
                      if ok_struct else f"PLAN 파싱/구조 검사 실패: {reason}")
    else:
        check(False, "PLAN 블록 추출 실패")

    # 6) PLAN 필수 필드
    if isinstance(plan_obj, dict):
        missing = [k for k in REQUIRED_KEYS if not plan_obj.get(k)]
        check(not missing, f"PLAN 필수 필드 존재 {('누락: ' + ', '.join(missing)) if missing else ''}".strip())
        check(plan_obj.get("type") in VALID_TYPES,
              f"PLAN.type 유효값 ({plan_obj.get('type')!r} / 허용: {', '.join(VALID_TYPES)})")
        decisions = plan_obj.get("decisions")
        check(isinstance(decisions, list) and len(decisions) > 0,
              f"decisions 배열 비어있지 않음 ({len(decisions) if isinstance(decisions, list) else 0}건)")

    # 7) md 본문이 비어있지 않은가 (빈 본문이면 계획서 상세가 렌더링되지 않는다)
    m_md = re.search(r'<script\s+id="plan-md"[^>]*>(.*?)</script>', bare, re.S)
    body_len = len(m_md.group(1).strip()) if m_md else 0
    check(body_len > 50, f"md 본문 존재 ({body_len}자)")

    # 8) 문서가 닫혔는가
    check(bare.rstrip().endswith("</html>"), "</html> 로 종료")

    ok = all(passed for passed, _ in checks)
    return ok, checks


def print_checks(checks, label):
    print(f"\n[검증] {label}")
    for passed, message in checks:
        print(f"  {'✓' if passed else '✗'} {message}")


# ---------------------------------------------------------------- PLAN 정규화


def normalize_plan(plan, md_path):
    """PLAN 데이터를 검사하고 유도 가능한 필드를 채운다."""
    if not isinstance(plan, dict):
        raise BuildError("PLAN 데이터는 JSON 객체여야 합니다.")

    try:
        rel_md = md_path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel_md = md_path.name
    plan.setdefault("mdFile", rel_md)

    missing = [k for k in REQUIRED_KEYS if not plan.get(k)]
    if missing:
        raise BuildError(f"PLAN 필수 필드 누락: {', '.join(missing)}")

    if plan["type"] not in VALID_TYPES:
        raise BuildError(f"PLAN.type 은 {', '.join(VALID_TYPES)} 중 하나여야 합니다 (받은 값: {plan['type']!r})")

    decisions = plan.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise BuildError("PLAN.decisions 는 최소 1건 이상의 배열이어야 합니다.")

    seen = set()
    for idx, dec in enumerate(decisions):
        where = f"decisions[{idx}]"
        for key in ("id", "title", "type", "options"):
            if not dec.get(key):
                raise BuildError(f"{where}.{key} 가 필요합니다.")
        if dec["id"] in seen:
            raise BuildError(f"{where}.id 중복: {dec['id']!r}")
        seen.add(dec["id"])
        if dec["type"] not in ("single", "multi"):
            raise BuildError(f"{where}.type 은 'single' 또는 'multi' 여야 합니다.")
        if not isinstance(dec["options"], list) or not dec["options"]:
            raise BuildError(f"{where}.options 는 비어있지 않은 배열이어야 합니다.")
        labels = [o.get("label") for o in dec["options"]]
        if not all(labels):
            raise BuildError(f"{where}.options[].label 이 모두 필요합니다.")
        if len(set(labels)) != len(labels):
            raise BuildError(f"{where}.options[].label 중복: {labels}")
        # decided 는 반드시 options 안의 label 이어야 한다 (확정 뷰가 조용히 깨지는 것 방지)
        decided = dec.get("decided")
        if decided is not None:
            picked = decided if isinstance(decided, list) else [decided]
            unknown = [p for p in picked if p not in labels]
            if unknown:
                raise BuildError(f"{where}.decided 가 options 에 없는 값입니다: {unknown}")
            if dec["type"] == "single" and isinstance(decided, list) and len(decided) > 1:
                raise BuildError(f"{where}: type 'single' 인데 decided 가 복수입니다.")

    # 레이어 순서는 렌더러가 sort 하지만, 데이터에서 미리 보장해두면 진단이 쉽다
    for idx, layer in enumerate(plan.get("layers") or []):
        for key in ("name", "label", "color", "bg", "files"):
            if key not in layer:
                raise BuildError(f"layers[{idx}].{key} 가 필요합니다.")
        layer.setdefault("order", idx + 1)
        for f_idx, entry in enumerate(layer["files"]):
            if not entry.get("path"):
                raise BuildError(f"layers[{idx}].files[{f_idx}].path 가 필요합니다.")
            entry.setdefault("type", "CREATE")
            entry.setdefault("desc", "")
            if entry["type"] not in ("CREATE", "MODIFY", "DELETE", "MOVE"):
                raise BuildError(
                    f"layers[{idx}].files[{f_idx}].type 은 CREATE/MODIFY/DELETE/MOVE 중 하나여야 합니다."
                )

    for idx, issue in enumerate(plan.get("issues") or []):
        if issue.get("severity") not in ("critical", "warning", "info"):
            raise BuildError(f"issues[{idx}].severity 는 critical/warning/info 중 하나여야 합니다.")

    return plan


# ---------------------------------------------------------------- CLI


def cmd_verify(target):
    if not target.exists():
        raise BuildError(f"파일이 없습니다: {target}")
    # 레거시(손으로 작성된) 계획서도 점검할 수 있게 strict 를 끈다.
    ok, checks = verify(target.read_text(encoding="utf-8"), str(target), strict=False)
    print_checks(checks, target.name)
    if ok:
        print(f"\n✅ {target.name} — 모든 검증 통과")
    else:
        print(f"\n❌ {target.name} — 검증 실패. 브라우저에서 열지 말고 먼저 고치세요.")
    return 0 if ok else 1


def cmd_build(md_path, data_arg, out_path, force):
    if not md_path.exists():
        raise BuildError(f"md 파일이 없습니다: {md_path}")
    if not TEMPLATE.exists():
        raise BuildError(f"템플릿이 없습니다: {TEMPLATE}")

    if data_arg:
        data_path = Path(data_arg)
        if not data_path.exists():
            raise BuildError(f"PLAN 데이터 파일이 없습니다: {data_path}")
        raw = data_path.read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            raise BuildError("PLAN JSON 을 --data 파일이나 stdin 으로 넘겨주세요.")
        raw = sys.stdin.read()

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BuildError(f"PLAN JSON 파싱 실패: {exc}")

    plan = normalize_plan(plan, md_path)

    out = out_path or md_path.with_suffix(".html")
    if out.exists() and not force:
        # 계획서는 승인 이력이 담긴 문서다. 조용히 덮어쓰지 않는다.
        raise BuildError(f"이미 존재합니다: {out}\n  덮어쓰려면 --force 를 붙이세요.")

    md_body = md_safe(md_path.read_text(encoding="utf-8").strip())
    plan_json = "const PLAN = " + js_safe(json.dumps(plan, ensure_ascii=False, indent=2))

    html = inject(TEMPLATE.read_text(encoding="utf-8"), plan_json, md_body)

    # 쓰기 전에 검증한다. 깨진 산출물을 디스크에 남기지 않는다.
    ok, checks = verify(html, str(out))
    print_checks(checks, out.name)
    if not ok:
        raise BuildError("검증 실패 — 파일을 쓰지 않았습니다.")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    print(f"\n✅ 생성 완료: {out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out}")
    print(f"   PLAN: {len(plan.get('decisions', []))}개 결정 · "
          f"{sum(len(l['files']) for l in plan.get('layers') or [])}개 파일 · "
          f"{len(plan.get('steps') or [])}단계")
    print(f"   열기: open {out}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="작업계획서 HTML 빌더 (docs/plan-template.html 기반)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("target", help="빌드할 .md 경로, 또는 --verify-only 시 점검할 .html 경로")
    parser.add_argument("--data", help="PLAN JSON 파일 경로 (없으면 stdin)")
    parser.add_argument("-o", "--output", help="출력 html 경로 (기본: md와 같은 이름)")
    parser.add_argument("--force", action="store_true", help="기존 html 덮어쓰기")
    parser.add_argument("--verify-only", action="store_true", help="빌드하지 않고 기존 html만 점검")
    args = parser.parse_args()

    target = Path(args.target)
    try:
        if args.verify_only:
            return cmd_verify(target)
        return cmd_build(target, args.data, Path(args.output) if args.output else None, args.force)
    except BuildError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
