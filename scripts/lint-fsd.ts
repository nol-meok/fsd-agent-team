#!/usr/bin/env npx tsx
/**
 * FSD 구조 자동 검사
 *
 * 대상 프로젝트에 복사해서 쓴다:
 *   cp scripts/lint-fsd.ts [프로젝트]/scripts/
 *   # package.json
 *   "lint:fsd": "npx tsx scripts/lint-fsd.ts"
 *
 * 사용법:
 *   npx tsx scripts/lint-fsd.ts [src경로]     # 기본: ./src
 *   npx tsx scripts/lint-fsd.ts --json        # 기계 판독용 출력
 *
 * 종료 코드: 위반(error)이 하나라도 있으면 1, 없으면 0 (warning 은 0).
 *
 * 의존성 없음 (node + tsx 만 필요). 정규식 기반이므로 AST 수준의 정밀도는 없다.
 * 판단이 필요한 항목(파일 배치 적절성 등)은 /review-fsd 가 담당한다.
 */

import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

// ---------------------------------------------------------------- 설정

/** 상위 → 하위만 import 가능. 인덱스가 클수록 상위 레이어. */
const LAYER_ORDER = ['shared', 'entities', 'features', 'widgets', 'app'] as const;
type Layer = (typeof LAYER_ORDER)[number];

/** 슬라이스 개념이 있는 레이어 — 교차 import 와 index.ts 를 검사한다. */
const SLICED_LAYERS: Layer[] = ['entities', 'features', 'widgets'];

/** app 레이어에 허용되는 파일 (Next.js App Router 규약) */
const APP_ALLOWED = /^(page|layout|template|loading|error|global-error|not-found|route|default|sitemap|robots|manifest|opengraph-image|icon|apple-icon|favicon)\.(tsx?|jsx?)$/;

const SEVERITY = { error: 'error', warn: 'warn' } as const;
type Severity = keyof typeof SEVERITY;

interface Finding {
  severity: Severity;
  rule: string;
  file: string;
  line: number;
  message: string;
  fix: string;
}

// ---------------------------------------------------------------- 유틸

const findings: Finding[] = [];

const report = (
  severity: Severity, rule: string, file: string, line: number, message: string, fix: string,
) => { findings.push({ severity, rule, file, line, message, fix }); };

const walk = (dir: string, out: string[] = []): string[] => {
  for (const entry of readdirSync(dir)) {
    if (entry === 'node_modules' || entry.startsWith('.')) continue;
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, out);
    else if (/\.(ts|tsx|js|jsx)$/.test(entry) && !/\.d\.ts$/.test(entry)) out.push(full);
  }
  return out;
};

/** 주석과 문자열 리터럴을 공백으로 치환한다. 코드가 아닌 곳의 오탐을 막는다. */
const stripNonCode = (source: string): string => {
  let out = '';
  let mode: 'code' | 'line' | 'block' | 'single' | 'double' | 'tpl' = 'code';
  for (let i = 0; i < source.length; i += 1) {
    const ch = source[i];
    const next = source[i + 1];
    const keep = ch === '\n' ? '\n' : ' ';
    if (mode === 'code') {
      if (ch === '/' && next === '/') { mode = 'line'; out += '  '; i += 1; continue; }
      if (ch === '/' && next === '*') { mode = 'block'; out += '  '; i += 1; continue; }
      if (ch === "'") { mode = 'single'; out += ch; continue; }
      if (ch === '"') { mode = 'double'; out += ch; continue; }
      if (ch === '`') { mode = 'tpl'; out += ch; continue; }
      out += ch;
      continue;
    }
    if (mode === 'line') { if (ch === '\n') { mode = 'code'; out += '\n'; } else out += ' '; continue; }
    if (mode === 'block') {
      if (ch === '*' && next === '/') { mode = 'code'; out += '  '; i += 1; } else out += keep;
      continue;
    }
    // 문자열 안 — import 경로는 살려야 하므로 내용을 유지한다
    if (ch === '\\') { out += source.slice(i, i + 2); i += 1; continue; }
    if ((mode === 'single' && ch === "'") || (mode === 'double' && ch === '"') || (mode === 'tpl' && ch === '`')) {
      mode = 'code';
    }
    out += ch;
  }
  return out;
};

const lineOf = (source: string, index: number): number =>
  source.slice(0, index).split('\n').length;

// ---------------------------------------------------------------- 경로 해석

const SRC_ROOT_ARG = process.argv.find((a) => !a.startsWith('-') && !/node|tsx|lint-fsd/.test(a));
const SRC = SRC_ROOT_ARG ?? 'src';
const JSON_OUT = process.argv.includes('--json');

interface Location { layer: Layer | null; slice: string | null; }

/** src 기준 상대 경로에서 레이어와 슬라이스를 뽑는다. */
const locate = (relPath: string): Location => {
  const parts = relPath.split(sep);
  const layer = LAYER_ORDER.find((l) => l === parts[0]) ?? null;
  if (!layer) return { layer: null, slice: null };
  // app 은 라우트 구조이므로 슬라이스 개념이 없다
  const slice = SLICED_LAYERS.includes(layer) ? (parts[1] ?? null) : null;
  return { layer, slice };
};

/** import 구문에서 경로를 모두 수집한다 (정적 + 재수출 + 동적). */
const collectImports = (code: string): { spec: string; index: number }[] => {
  const results: { spec: string; index: number }[] = [];
  const patterns = [
    /\bimport\s+[^;'"]*?\bfrom\s*['"]([^'"]+)['"]/g, // import x from '...'
    /\bimport\s*['"]([^'"]+)['"]/g,                  // import '...'
    /\bexport\s+[^;'"]*?\bfrom\s*['"]([^'"]+)['"]/g, // export { x } from '...'
    /\bimport\s*\(\s*['"]([^'"]+)['"]\s*\)/g,        // import('...')
  ];
  for (const re of patterns) {
    let m: RegExpExecArray | null;
    while ((m = re.exec(code)) !== null) results.push({ spec: m[1], index: m.index });
  }
  return results;
};

/**
 * import 스펙을 src 기준 상대 경로로 정규화한다.
 * 외부 패키지면 null.
 */
const resolveSpec = (spec: string, fromRel: string): string | null => {
  // 별칭: @/... 또는 ~/...
  const alias = spec.match(/^[@~]\/(.+)$/);
  if (alias) return alias[1].split('/').join(sep);
  // 절대 레이어 경로: 'entities/review' 처럼 baseUrl=src 인 경우
  if (LAYER_ORDER.some((l) => spec === l || spec.startsWith(`${l}/`))) {
    return spec.split('/').join(sep);
  }
  // 상대 경로
  if (spec.startsWith('.')) {
    const fromDir = fromRel.split(sep).slice(0, -1);
    const segments = spec.split('/');
    const stack = [...fromDir];
    for (const seg of segments) {
      if (seg === '.' || seg === '') continue;
      if (seg === '..') stack.pop();
      else stack.push(seg);
    }
    return stack.join(sep);
  }
  return null; // 외부 패키지
};

// ---------------------------------------------------------------- 검사 실행

if (!existsSync(SRC)) {
  console.error(`❌ 경로가 없습니다: ${SRC}`);
  console.error(`   사용법: npx tsx scripts/lint-fsd.ts [src경로]`);
  process.exit(1);
}

const files = walk(SRC);

// --- 1. 슬라이스별 index.ts 존재 확인
for (const layer of SLICED_LAYERS) {
  const layerDir = join(SRC, layer);
  if (!existsSync(layerDir)) continue;
  for (const slice of readdirSync(layerDir)) {
    const sliceDir = join(layerDir, slice);
    if (!statSync(sliceDir).isDirectory()) continue;
    const hasIndex = ['index.ts', 'index.tsx'].some((f) => existsSync(join(sliceDir, f)));
    if (!hasIndex) {
      report('error', 'slice-public-api', `${layer}/${slice}`, 0,
        'public API 파일이 없습니다',
        `${layer}/${slice}/index.ts 를 만들어 외부에 노출할 것만 re-export 하세요`);
    }
  }
}

// --- 2. 파일 단위 검사
for (const file of files) {
  const rel = relative(SRC, file);
  const display = rel.split(sep).join('/');
  const { layer, slice } = locate(rel);
  const raw = readFileSync(file, 'utf8');
  const code = stripNonCode(raw);
  const basename = rel.split(sep).pop() ?? '';

  // 2-1. entities 에 UI 없음
  if (layer === 'entities') {
    const isComponent = /\.tsx$/.test(basename);
    const inUiSegment = rel.split(sep).includes('ui');
    if (isComponent || inUiSegment) {
      report('error', 'entities-no-ui', display, 1,
        isComponent ? '.tsx 컴포넌트가 entities 에 있습니다' : 'ui/ 세그먼트가 entities 에 있습니다',
        'UI 는 features(인터랙션) 또는 widgets(화면 조합) 으로 옮기세요. entities 는 타입 + API 만');
    }
  }

  // 2-2. app 레이어는 라우팅 파일만
  if (layer === 'app' && !APP_ALLOWED.test(basename)) {
    report('error', 'app-routing-only', display, 1,
      `app 레이어에 라우팅 파일이 아닌 ${basename} 이 있습니다`,
      '화면 구현은 widgets/ 로 옮기고, app 에서는 widget 을 배치만 하세요');
  }

  // 2-3. function 키워드 (page/layout 등 default export 는 예외)
  const isRouteFile = layer === 'app' && APP_ALLOWED.test(basename);
  let fnMatch: RegExpExecArray | null;
  const fnRe = /\bfunction\s+[A-Za-z_$]/g;
  while ((fnMatch = fnRe.exec(code)) !== null) {
    const at = fnMatch.index;
    const isDefaultExport = /\bexport\s+default\s+(async\s+)?$/.test(code.slice(Math.max(0, at - 30), at));
    if (isRouteFile && isDefaultExport) continue;
    report('warn', 'arrow-function', display, lineOf(code, at),
      'function 키워드를 사용했습니다',
      '화살표 함수로 바꾸세요 (page.tsx / layout.tsx 의 default export 만 예외)');
  }

  // 2-4. 금지 패턴
  const banned: [RegExp, string, string, Severity][] = [
    [/(:\s*any\b|<any>|\bas\s+any\b|\bany\[\])/g, 'no-any',
      'unknown + 타입 가드로 바꾸거나 구체 타입을 선언하세요', 'error'],
    [/\bconsole\.log\s*\(/g, 'no-console',
      '커밋 전에 제거하세요 (의도적 로깅은 별도 로거 사용)', 'error'],
    [/@ts-(ignore|nocheck)\b/g, 'no-ts-suppress',
      '타입 에러를 실제로 해결하세요', 'error'],
    [/\bstyle=\{\{/g, 'no-inline-style',
      'Tailwind 유틸리티 또는 *.module.scss 로 옮기세요', 'error'],
    [/!important/g, 'no-important',
      '선택자 구체성을 조정하세요', 'warn'],
  ];
  // @ts-ignore 등은 주석 안에 있으므로 raw 를 본다
  for (const [re, rule, fix, severity] of banned) {
    const target = rule === 'no-ts-suppress' ? raw : code;
    let m: RegExpExecArray | null;
    re.lastIndex = 0;
    while ((m = re.exec(target)) !== null) {
      report(severity, rule, display, lineOf(target, m.index), `${m[0].trim()} 사용`, fix);
    }
  }

  // 2-5. import 의존성
  if (!layer) continue;
  const fromRank = LAYER_ORDER.indexOf(layer);

  for (const { spec, index } of collectImports(code)) {
    const resolved = resolveSpec(spec, rel);
    if (!resolved) continue; // 외부 패키지

    const target = locate(resolved);
    if (!target.layer) continue;
    const toRank = LAYER_ORDER.indexOf(target.layer);
    const line = lineOf(code, index);

    // 역방향 의존
    if (toRank > fromRank) {
      report('error', 'layer-direction', display, line,
        `${layer} → ${target.layer} 역방향 import (${spec})`,
        `의존 방향은 ${LAYER_ORDER.slice().reverse().join(' → ')} 만 허용됩니다. ` +
        `공통 코드는 하위 레이어로 내리세요`);
      continue;
    }

    // 같은 레이어 교차 슬라이스 (app/shared 는 제외)
    if (toRank === fromRank && SLICED_LAYERS.includes(layer)) {
      if (slice && target.slice && slice !== target.slice) {
        report('error', 'cross-slice', display, line,
          `같은 레이어의 다른 슬라이스를 import 했습니다 (${layer}/${slice} → ${layer}/${target.slice})`,
          '공통 부분을 하위 레이어로 추출하거나, 상위 레이어에서 두 슬라이스를 조합하세요');
        continue;
      }
    }

    // 슬라이스 내부 경로 직접 접근 (다른 슬라이스일 때만)
    if (SLICED_LAYERS.includes(target.layer) && target.slice) {
      const targetParts = resolved.split(sep);
      const reachesInside = targetParts.length > 2 && targetParts[2] !== 'index';
      const sameSlice = layer === target.layer && slice === target.slice;
      if (reachesInside && !sameSlice) {
        report('error', 'no-deep-import', display, line,
          `슬라이스 내부 경로를 직접 import 했습니다 (${spec})`,
          `@/${target.layer}/${target.slice} 처럼 index.ts public API 를 통해 가져오세요`);
      }
    }
  }
}

// ---------------------------------------------------------------- 출력

const errors = findings.filter((f) => f.severity === 'error');
const warns = findings.filter((f) => f.severity === 'warn');

if (JSON_OUT) {
  console.log(JSON.stringify({
    scanned: files.length,
    errors: errors.length,
    warnings: warns.length,
    findings,
  }, null, 2));
  process.exit(errors.length > 0 ? 1 : 0);
}

const RULE_LABEL: Record<string, string> = {
  'slice-public-api': 'index.ts public API 누락',
  'entities-no-ui': 'entities 에 UI 존재',
  'app-routing-only': 'app 레이어에 비-라우팅 파일',
  'layer-direction': '단방향 의존성 위반',
  'cross-slice': '같은 레이어 교차 import',
  'no-deep-import': '슬라이스 내부 직접 import',
  'arrow-function': 'function 키워드 사용',
  'no-any': 'any 타입 사용',
  'no-console': 'console.log 사용',
  'no-ts-suppress': '@ts-ignore / @ts-nocheck',
  'no-inline-style': '인라인 스타일',
  'no-important': '!important',
};

console.log(`\n🔍 FSD 구조 검사 — ${SRC} (${files.length}개 파일)\n`);

if (findings.length === 0) {
  console.log('✅ FSD 검수 통과 — 위반 없음\n');
  process.exit(0);
}

const byRule = new Map<string, Finding[]>();
for (const f of findings) {
  if (!byRule.has(f.rule)) byRule.set(f.rule, []);
  byRule.get(f.rule)!.push(f);
}

for (const [rule, items] of byRule) {
  const isError = items[0].severity === 'error';
  console.log(`${isError ? '❌' : '⚠️ '} ${RULE_LABEL[rule] ?? rule} (${items.length}건)`);
  for (const f of items) {
    console.log(`   ${f.file}${f.line ? `:${f.line}` : ''} — ${f.message}`);
  }
  console.log(`   → ${items[0].fix}\n`);
}

console.log(`📊 요약: 검사 ${files.length}개 · 위반 ${errors.length}건 · 경고 ${warns.length}건\n`);
process.exit(errors.length > 0 ? 1 : 0);
