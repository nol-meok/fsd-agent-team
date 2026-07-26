# 작업계획서 템플릿

계획서는 항상 **`.md` + `.html` 한 쌍**으로 만든다.

| 파일 | 역할 |
|------|------|
| `plans/유형/YYYYMMDD-제목.md` | 계획서 본문 (사람이 읽고 git diff 로 추적) |
| `plans/유형/YYYYMMDD-제목.html` | 결정 콘솔 + 시각화 (브라우저에서 승인) |

`유형` 은 `feature` 또는 `migrate`.

---

## HTML 은 반드시 빌더로 생성한다

`docs/plan-template.html` 을 복사해서 문자열 치환하지 **않는다.**

```bash
# 1) PLAN 데이터를 JSON 파일로 작성
#    (또는 stdin 으로 파이프)
python3 scripts/build-plan-html.py plans/feature/20260727-제목.md --data /tmp/plan.json

# 기존 html 점검 (수정 없음)
python3 scripts/build-plan-html.py plans/feature/20260727-제목.html --verify-only

# 이미 있는 html 갱신
python3 scripts/build-plan-html.py plans/feature/20260727-제목.md --data /tmp/plan.json --force
```

빌더는 쓰기 전에 검증하고, 검증에 실패하면 **파일을 남기지 않는다.**
`✓` 가 전부 나오기 전에는 `open` 으로 사용자에게 보여주지 않는다.

### 왜 빌더인가

2026-07-26에 템플릿을 `tpl.index('<script id="plan-data">')` 로 직접 치환했다가,
상단 사용법 주석 안의 동일 문구가 먼저 매칭됐다. 주석 종료 `-->` 가 함께 삭제되어
PLAN 정의가 주석에 갇히고, 렌더러가 `PLAN.title` 에서 ReferenceError 로 죽어
화면이 완전히 비었다. 더 나쁜 건 검증도 같은 정규식을 써서 "정상" 이라고 보고한 것이다.

빌더는 이걸 구조적으로 막는다:

- 프로세 텍스트에 나타날 수 없는 센티넬 라인만 치환하고, **정확히 1개**인지 확인한다.
- 검증은 **HTML 주석을 먼저 제거한 뒤** 필수 요소가 주석 밖에 있는지 본다.
- 주석 짝(`<!--` / `-->`) 개수 균형을 본다 — 위 사고를 직접 잡는 검사다.
- PLAN 을 순수 JSON 으로 주입해 실제 파싱을 확인한다.
- `decided` 값이 `options` 안에 실제로 있는지 확인한다 (확정 뷰가 조용히 깨지는 것 방지).

---

## md 본문 템플릿

HTML 렌더러는 아래 h2 제목을 키워드로 찾아 해당 섹션을 시각 컴포넌트로 교체한다.
**제목 문구를 유지해야 시각화가 붙는다.** (못 찾으면 본문 끝에 덧붙는다)

| md 섹션 제목 | 교체되는 시각화 | PLAN 필드 |
|--------------|-----------------|-----------|
| `## 2.5 디자인 시스템` | 색상/폰트/규칙 카드 | `design` |
| `## 3. FSD 레이어 배치` | 플로우 바 + 파일트리 | `layers` |
| `## 4. 작업 순서` | 타임라인 | `steps` |
| `## 문제 분석` (migrate) | severity 카드 | `issues` |
| `## 구조 비교` (migrate) | Before/After 2컬럼 | `beforeAfter` |

```markdown
# [제목]

## 1. 개요
- 작업 유형: feature / bugfix / refactor / migrate
- 요청 사항: (사용자 요청 요약)
- 사용자 결정 사항:
  - 결정 항목 1: **선택값** (옵션 나열)

## 2. 현재 상태 분석
- 관련 기존 코드 (파일 경로)
- 프로젝트 구조 현황

## 2.5 디자인 시스템
(PLAN.design 이 이 섹션을 대체한다. 요약 한두 줄만 적어두면 된다)

## 3. FSD 레이어 배치
(PLAN.layers 가 이 섹션을 대체한다. md 에는 표로 적어 git diff 로 읽히게 유지)

| 파일 경로 | 레이어 | 작업 | 설명 |
|-----------|--------|------|------|
| src/entities/review/model/types.ts | entities | CREATE | Review 타입 |

## 4. 작업 순서
(PLAN.steps 가 이 섹션을 대체한다)

## 5. Import 의존성
(코드 펜스로 의존 방향 표기)

## 6. FSD 검증 체크리스트
- [ ] 단방향 의존성 준수
- [ ] 같은 레이어 교차 import 없음
- [ ] app 에 로직/스타일 없음
- [ ] entities 에 UI 없음
- [ ] 각 슬라이스 index.ts 존재
- [ ] 화살표 함수 사용

## 7. 작업 배분

| 담당 | 작업 내용 | 의존성 |
|------|----------|--------|
| Coder | entities 생성 | 없음 |
| Reviewer | FSD 검수 | 전체 완료 후 |
```

---

## PLAN 데이터 스키마

빌더에 넘기는 JSON. `title` / `type` / `scope` / `summary` / `decisions` 는 필수,
나머지는 있으면 렌더링되고 없으면 해당 섹션이 생략된다. (`mdFile` 은 빌더가 자동 계산)

```json
{
  "title": "음식점 리뷰 작성 기능",
  "type": "feature",
  "scope": "entities → features → widgets → app",
  "summary": "한 줄 요약 — 무엇을 왜 하는지",

  "layers": [
    {
      "name": "entities", "label": "Entities", "order": 1,
      "color": "#d4a72c", "bg": "#40351f", "desc": "데이터 타입 + API",
      "files": [
        { "path": "src/entities/review/model/types.ts", "type": "CREATE", "desc": "Review 타입" }
      ]
    }
  ],

  "steps": [
    {
      "step": 1, "layer": "entities", "title": "데이터 기반 구축",
      "tasks": ["Review 타입 정의", "index.ts public API"],
      "done": "npm run build 통과"
    }
  ],

  "deps": [{ "from": "widgets/review-feed", "to": "entities/review" }],

  "design": {
    "source": "generated",
    "generator": "ui-ux-pro-max",
    "category": "Food Delivery / On-Demand",
    "colors": [{ "name": "primary", "value": "#EA580C", "desc": "주요" }],
    "typography": { "heading": { "family": "Playfair Display", "weight": "700" } },
    "sampleText": "폰트 미리보기에 쓸 문장 (생략 시 기본 팬그램)",
    "checklist": [
      "Block layout with 48px+ gaps",
      "Large typography 32px+",
      "4-6 vibrant colors max"
    ],
    "tokens": [{ "name": "--block-gap", "value": "48px" }],
    "style": { "name": "Vibrant & Block-based", "keywords": "…", "effects": "…", "antiPatterns": "…" },
    "pattern": { "name": "App Store Style Landing", "sections": "Hero > Features > CTA" },
    "uxRules": [{ "category": "Layout", "issue": "Content Jumping", "do": "…", "dont": "…", "severity": "High" }],
    "motion": [{ "category": "Hover", "trigger": "hover", "duration": "200ms", "easing": "ease-out", "desc": "translateY(-2px)" }],
    "stackGuides": [{ "category": "Images", "guideline": "next/image 사용", "do": "…", "severity": "High" }],
    "icons": { "library": "Lucide", "import": "import { Star } from 'lucide-react'" },
    "googleFontsUrl": "https://fonts.googleapis.com/css2?…",
    "notes": "생성 근거 메모"
  },

  "issues": [
    {
      "severity": "critical", "category": "거대 파일",
      "file": "src/components/ProductPage.tsx", "lines": 420,
      "desc": "데이터 fetching + 로직 + UI 혼재",
      "suggestion": "entities/product + features/product-detail + widgets/product-page 로 분리"
    }
  ],

  "beforeAfter": {
    "before": [{ "path": "src/components/ProductPage.tsx", "issue": true, "movesTo": "widgets/product-page" }],
    "after": ["src/widgets/product-page/ui/ProductPage.tsx"]
  },

  "decisions": [
    {
      "id": "state-management",
      "title": "상태 관리 방식",
      "desc": "이 기능의 상태를 어떻게 관리할지 결정합니다.",
      "type": "single",
      "required": true,
      "options": [
        { "label": "React Query", "desc": "서버 상태 캐싱 (entities/model/)", "recommended": true },
        { "label": "Zustand", "desc": "클라이언트 전역 상태 (features/model/)" }
      ]
    }
  ]
}
```

> PLAN JSON 은 **순수 JSON**이어야 한다. 주석·따옴표 없는 키·trailing comma 는 빌더가 거부한다.

### 필드 규칙

- `type`: `feature` | `bugfix` | `refactor` | `migrate`
- `deps`: 렌더러가 시각화하지 않는다. 화면에 보이는 쪽은 md 의 "5. Import 의존성" 코드 펜스이고,
  이 필드는 기계 판독용 기록이다. 둘 중 하나만 채우지 말고 내용을 일치시킨다
- `design.checklist`: `ui-ux-pro-max` 의 `--domain style` 결과에 있는
  **Implementation Checklist** 를 그대로 옮긴다 (`48px+ gaps`, `32px+ type` 같은 구체 수치).
  HTML 에 체크리스트로 렌더링되고, `/code` 가 항목별로 확인한다.
  **이걸 비우면 구현이 계획한 디자인 강도에 못 미친다** — 실제로 그렇게 실패한 적이 있다
- `design.motion[].notes`: `--domain gsap` 의 `Framework Notes` (유료 플러그인 라이선스,
  React 바인딩 방식 등). duration/easing 은 DB 값을 그대로 쓴다
- `layers[].files[].type`: `CREATE` | `MODIFY` | `DELETE` | `MOVE`
- `issues[].severity`: `critical` | `warning` | `info`
- `decisions[].type`: `single` (택1) | `multi` (복수)
- `decisions[].options[].colors`: 색상 팔레트 결정 카드에서 칩 미리보기로 표시
- `decisions[].options[].custom: true`: 직접 입력 필드 노출
- `decisions[].id` 와 `options[].label` 은 중복 불가

### 레이어 색상 팔레트 (고정)

계획서마다 색이 달라지지 않도록 아래 값을 그대로 쓴다.

| 레이어 | color | bg |
|--------|-------|-----|
| shared | `#8b949e` | `#21262d` |
| entities | `#d4a72c` | `#40351f` |
| features | `#56d364` | `#1f402d` |
| widgets | `#a371f7` | `#2d1f40` |
| app | `#58a6ff` | `#1f2d40` |
| 검증 | `#3fb950` | `#1a3028` |

---

## 승인 라이프사이클

1. **승인 전** — `decisions[]` 에 `options` 만 채운다. 하단 결정 콘솔이 활성화된다.
2. 사용자가 브라우저에서 선택 → **[프롬프트로 복사]** → 채팅에 붙여넣는다.
3. **확정 후** — 각 결정에 `decided` 를 채워 **다시 빌드**한다 (`--force`).
   결정 카드가 잠기고, 액션바·메모·미리보기가 숨겨져 읽기용 문서로 전환된다.
   - 택1 → 문자열 (`"decided": "React Query"`)
   - 복수 → 배열 (`"decided": ["이미지 첨부", "좋아요"]`)
4. md 를 수정하면 html 도 **같은 턴에** 재빌드한다. 둘 중 하나만 고치지 않는다.
