---
name: plan
description: 요구사항을 분석하고 HTML 작업계획서를 작성합니다.
argument-hint: "작업 설명 (예: 음식점 리뷰 작성 기능)"
---

# 작업계획서 작성

사용자 요청: $ARGUMENTS

## 1단계: 프로젝트 분석

1. 대상 프로젝트(`__PROJECT_PATH__`) 구조 탐색 (Glob/Grep/Read)
2. 프로젝트의 CLAUDE.md, 레이어별 CLAUDE.md 확인
3. 관련 기존 코드 탐색 — 이미 있는 슬라이스를 재사용할지 판단
4. `package.json` 으로 스택 확인 (Next.js / React / React Native 등)

## 2단계: 플랫폼 타겟 확인

- Next.js/React = 웹 또는 반응형, React Native/Flutter = 앱
- **이전 계획서에서 이미 결정했으면 그대로 쓰고 재질문하지 않는다.**
- 미확정이면 `decisions` 에 `platform` 카드 추가:
  - `모바일 앱 전용` — 터치 퍼스트, 바텀 내비, 44px 최소 터치 영역, SafeArea
  - `웹 전용` — 데스크톱 중심, 호버 인터랙션, 사이드바/탑바 내비
  - `반응형` — 모바일 퍼스트 → 640 → 768 → 1024 브레이크포인트

## 3단계: 기존 디자인 시스템 탐색

먼저 프로젝트에서 디자인 토큰을 추출해본다:

- `shared/config/globals.scss` — CSS 변수
- `tailwind.config.*` — 커스텀 테마
- 기존 `*.module.scss` — 컴포넌트 스타일 패턴

**판단:**
- 색상 5개+ / 폰트 / 토큰이 갖춰짐 → **있음.** `design.source: 'existing'` 으로 기록하고 4단계 건너뛴다.
- CSS 변수 2~3개 수준 → **없음.** 4단계 실행.

## 4단계: 디자인 시스템 생성 (기존에 없을 때만)

`tools/ui-ux-pro-max` 로 생성한다. **UI/UX 는 축약 대상이 아니다.**

> **이 도구의 존재 이유가 "값을 지어내지 않는 것"이다.**
> duration/easing, 아이콘 라이브러리, 간격·타입 수치를 기억이나 감으로 채우면
> 도구를 쓰는 의미가 없다. 아래 9개를 **전부 호출한다.**
> 결과가 0건이면 조용히 기본값으로 넘어가지 말고, DB 매칭 실패를 **명시**하고
> 다른 키워드로 재시도한다.

```bash
cd tools/ui-ux-pro-max
```

### 4-1. 종합 디자인 시스템
```bash
python3 search.py "<프로젝트 키워드>" --design-system --json
```
→ 색상·폰트·스타일·패턴·효과·안티패턴 종합. 나머지 단계의 기준선.

### 4-2. 색상 팔레트 후보 (결정 카드용)
```bash
python3 search.py "<키워드>" --domain color --json -n 3
```
→ `decisions.color-palette` 의 선택지. `options[].colors` 에 hex 를 넣어 칩으로 보이게 한다.

### 4-3. 폰트 페어링 후보 (결정 카드용)
```bash
python3 search.py "<키워드>" --domain typography --json -n 3
python3 search.py "<확정 폰트명>" --domain google-fonts --json -n 2   # googleFontsUrl 확인
```
→ `decisions.typography` 의 선택지 + `design.googleFontsUrl`.
→ **한글 서비스면 latin 전용 폰트만 고르지 않는다.** 한글 폴백을 페어링에 함께 적는다.

### 4-4. UI 스타일 방향 (결정 카드용) — **가장 중요**
```bash
python3 search.py "<키워드>" --domain style --json -n 3
```
이 행에서 반드시 뽑아 `design` 에 옮긴다:

| CSV 컬럼 | PLAN 필드 | 왜 |
|----------|-----------|-----|
| `Implementation Checklist` | **`design.checklist`** | 48px gaps / 32px+ type 같은 **구체 수치**가 여기 있다. 이게 없으면 구현이 밋밋해진다 |
| `Design System Variables` | `design.tokens` | `--block-gap: 48px` 등 |
| `Effects & Animation` | `design.style.effects` | |
| `Keywords` | `design.style.keywords` | |
| `Accessibility` | `design.uxRules` 에 추가 | `◐ Ensure WCAG` 등 |
| (안티패턴) | `design.style.antiPatterns` | |

### 4-5. 레이아웃 & 페이지 패턴
```bash
python3 search.py "<키워드>" --domain landing --json -n 2
```
→ 섹션 순서, CTA 배치, 컬러 전략 → `design.pattern` / `design.layout`.

### 4-6. UX 가이드라인
```bash
python3 search.py "<기능 키워드> navigation responsive" --domain ux --json -n 5
python3 search.py "accessibility contrast keyboard" --domain ux --json -n 3
python3 search.py "empty state loading feedback" --domain ux --json -n 3
```
→ Do/Don't + Severity → `design.uxRules`. `Critical`/`High` 는 반드시 계획서에 싣는다.

### 4-7. 모션 프리셋
```bash
python3 search.py "<인터랙션> hover" --domain gsap --json -n 3
python3 search.py "scroll reveal stagger" --domain gsap --json -n 2
```
→ `Duration`/`Easing`/`GSAP Snippet`/`Framework Notes` 를 **그대로** `design.motion` 에.
→ `Framework Notes` 의 주의사항(유료 플러그인 라이선스, React 바인딩 방식 등)도 함께 옮긴다.
→ **duration/easing 을 임의로 바꾸지 않는다.**

### 4-8. 스택 가이드라인
```bash
python3 search.py "<키워드>" --stack <nextjs|react|vue|...> --json -n 5
```
→ 라우팅/데이터/성능 Do/Don't → `design.stackGuides`.

### 4-9. 아이콘
```bash
python3 search.py "<기능 키워드>" --domain icons --json -n 3
```
→ `Library` + `Import Code` 를 그대로 `design.icons` 에.
→ **DB 가 추천한 라이브러리를 쓴다.** 기억으로 다른 라이브러리를 적지 않는다
   (설치까지 하면 되돌리기 번거롭다).

### 필요 시 추가
- `--domain chart` — 차트/데이터 시각화가 있을 때
- `--domain product` — 제품 UI 패턴(대시보드, 설정 등)
- `--domain react` / `--domain web` — 성능·구조 보강

## 5단계: 사용자 결정 vs 자동 적용 분리

### [A] 결정 카드로 물어볼 것 → `decisions`

| id | 내용 | 출처 |
|----|------|------|
| `platform` | 플랫폼 타겟 | 2단계 |
| `color-palette` | 색상 후보 3개 (`options[].colors` 로 칩 표시) | 4-2 |
| `typography` | 폰트 페어링 후보 3개 | 4-3 |
| `ui-style` | 스타일 방향 3개 | 4-4 |
| `icon-library` | 아이콘 라이브러리 후보 2~3개 | 4-9 |
| 그 외 | 상태관리 방식, UI 방식 등 기능 고유 결정 | 1단계 분석 |

#### 승계 규칙 — 언제 다시 묻는가

이전 계획서에 확정값이 있으면 기본은 승계지만, **아래에 하나라도 해당하면 다시 묻는다.**

| 상황 | 동작 |
|------|------|
| 같은 도메인 + 확정값이 이미 코드(`globals.scss`)에 반영됨 | **승계.** 카드 없음 |
| **도메인/카테고리가 바뀜** (예: 레스토랑 → 날씨) | **다시 묻기** |
| **확정값이 아직 코드에 반영되지 않음** | **다시 묻기.** 확정 이력만으로 잠그지 않는다 |
| 사용자가 명시 요청 ("디자인 다시", "팔레트 바꿔") | **다시 묻기** |

다시 물을 때는 **기존 확정값을 옵션에 함께 넣는다** (`label` 에 "기존 유지" 표기).
앱 전체 톤 일관성을 택할 수도 있어야 한다. 승계했을 때는 `design.notes` 에
"어느 계획서에서 승계했는지"를 남긴다.

> 도메인이 바뀌었는데 팔레트를 강제 승계하면 날씨 페이지에 식욕 레드가 박힌다.
> 실제로 그렇게 만든 적이 있다.

#### 아이콘 카드 만들 때

`icons.csv` 는 수록 범위가 넓지 않다 (라이브러리 종류가 적고, 도메인 글리프는
빠져 있을 수 있음). 그래서:

- 4-9 결과가 있으면 **그것을 "DB 추천" 으로 표시하고 추천 배지를 준다**
- DB 에 없는 라이브러리를 후보에 넣을 때는 **`desc` 에 "DB 미수록" 을 명시한다**
- 기능에 필요한 글리프(예: 날씨 아이콘)를 따로 검색해서 **0건이면 그 사실을 적는다.**
  글리프 커버리지가 선택 기준이 되므로 사용자가 알아야 한다

### [B] 질문 없이 자동 적용 → `design` 에 기록, `/code` 에서 Coder가 따름

| 필드 | 출처 |
|------|------|
| **`checklist`** | 4-4 Implementation Checklist — **구현 수치의 근거. 빠뜨리면 안 된다** |
| `tokens` | 4-4 Design System Variables |
| `uxRules` | 4-6 (+ 4-4 Accessibility) |
| `motion` | 4-7 (duration/easing/snippet/notes 원문 그대로) |
| `stackGuides` | 4-8 |
| `pattern` / `layout` | 4-5 |
| `icons` | `icon-library` 결정 확정 후 그 라이브러리의 `Import Code` |

기술적 베스트 프랙티스는 물어볼 대상이 아니다. 다만 **기록은 빠뜨리지 않는다** —
계획서에 없으면 `/code` 가 알 수 없고, 결과는 밋밋한 UI 가 된다.

### 디자인 원칙 (항상)
- UI 는 트렌디하게. 올드한 디자인 금지
- AI스러운 디자인 금지 — 보라+파랑 그라디언트 남발, 스파클 아이콘, 뻔한 생성물 느낌
- 다크/라이트는 자유. 추천 컬러는 트렌디한 UI 위에 입힌다

## 6단계: 계획서 작성

`docs/plan-template.md` 의 md 템플릿과 PLAN 스키마를 따른다.

```bash
# 1) md 작성
#    plans/feature/YYYYMMDD-제목.md
#    (섹션 제목은 템플릿 그대로 유지 — 렌더러가 제목으로 시각화를 붙인다)

# 2) PLAN JSON 작성 → 빌더로 html 생성
#    JSON 은 계획서 옆에 둔다. /tmp 에 두면 나중에 재빌드가 불가능하다.
python3 scripts/build-plan-html.py plans/feature/YYYYMMDD-제목.md \
  --data plans/feature/YYYYMMDD-제목.plan.json
```

**HTML 을 직접 작성하거나 템플릿을 문자열 치환하지 않는다.** 반드시 빌더를 쓴다.
이유와 스키마는 `docs/plan-template.md` 참고.

**`beforeAfter` 는 넣지 않는다.** 이 필드가 있으면 렌더러가 `## 3. FSD 레이어 배치` 를
migrate 용 2컬럼 비교 뷰로 바꾼다. 기능 계획서는 플로우 바 + 레이어별 파일트리가 맞다.
`type` 이 `feature`/`bugfix` 인데 `beforeAfter` 가 있으면 빌더가 빌드를 거부한다.
기존 구조를 크게 옮기는 작업이면 `/migrate-fsd` 를 쓴다.

### 계획서 필수 포함
- FSD 레이어별 파일 배치 (`layers`) — 레이어 색상은 `docs/plan-template.md` 팔레트 고정
- 작업 순서 타임라인 (`steps`)
- Import 의존성 (`deps`, md 에는 코드 펜스로)
- 사용자 결정 항목 (`decisions`)
- 디자인 시스템 (`design`) — 기존 추출 또는 4단계 생성
  - **`design.checklist` 는 필수** (4-4 결과). 여기 없는 수치는 구현에 반영되지 않는다
  - `design.motion` 의 duration/easing 은 4-7 원문값
  - `design.icons` 는 4-9 가 추천한 라이브러리
- FSD 검증 체크리스트

### 자기 점검 (계획서 확정 전)

4단계를 실행했다면 아래가 모두 채워져 있어야 한다. 비어 있으면 해당 쿼리를 다시 돌린다.

- [ ] `design.checklist` — 구체 수치가 담긴 항목이 3개 이상
- [ ] `design.motion` — 각 항목에 duration + easing 이 DB 값으로 들어있음
- [ ] `design.icons.library` — `icon-library` 결정과 일치 (기억으로 적지 않았음)
- [ ] 디자인 결정 카드(`color-palette`/`typography`/`ui-style`/`icon-library`)가
      승계 규칙에 맞게 있거나 없는지 — 도메인이 바뀌었으면 **있어야 한다**
- [ ] `design.uxRules` — `Critical`/`High` 항목이 포함됨
- [ ] `design.stackGuides` — 프로젝트 스택에 맞는 항목
- [ ] `design.pattern` — 섹션 순서/CTA 전략

## 7단계: 승인 요청

1. 빌더 검증 `✓` 가 **전부** 나왔는지 확인한다. 하나라도 `✗` 면 고칠 때까지 사용자에게 보여주지 않는다.
2. `open plans/feature/YYYYMMDD-제목.html`
3. 안내: "브라우저에서 계획서를 확인하고, 결정 사항을 선택한 뒤 [프롬프트로 복사] 버튼을 눌러 채팅에 붙여넣어 주세요."
4. 사용자가 결정사항을 붙여넣으면:
   - md 의 "사용자 결정 사항" 확정
   - PLAN JSON 의 각 결정에 `decided` 채우고 `--force` 로 재빌드
   - `/code` 로 코딩 디스패치
