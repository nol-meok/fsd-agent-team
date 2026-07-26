---
name: code
description: 승인된 계획에 따라 대상 프로젝트에서 FSD 규칙을 준수하여 코드를 작성합니다.
argument-hint: "작업 내용 또는 승인 메시지"
---

# 코딩 실행

작업 내용: $ARGUMENTS

## 1단계: 계획 확인

1. 승인된 계획서(`plans/**/*.md`)에서 어떤 파일을 어느 레이어에 생성/수정하는지 확인
2. **승인되지 않은 계획이면 여기서 멈추고 `/plan` 을 먼저 안내한다**
3. 대상 프로젝트(`__PROJECT_PATH__`)의 CLAUDE.md 로 코드 컨벤션 확인
4. 작업할 레이어의 CLAUDE.md 가 있으면 해당 규칙도 확인

## 2단계: 디자인 시스템 적용

계획서 `PLAN.design` 의 `source` 에 따라 갈린다:

| source | 처리 |
|--------|------|
| `existing` | 기존 CSS 변수/Tailwind 유틸리티를 그대로 사용. **건드리지 않는다** |
| `generated` / `new` | 확정된 색상·폰트·토큰을 `shared/config/globals.scss` 에 CSS 변수로 작성 |

- Google Fonts 가 있으면 `app/layout.tsx` 에 `next/font` 설정
- 이미 디자인 변수가 있으면 덮어쓰지 않는다 (중복 방지)

## 3단계: PLAN.design 자동 적용 항목

계획서에 기록된 아래 항목은 **사용자에게 다시 묻지 않고** 코드에 반영한다.
`Critical` / `High` severity 는 반드시 준수한다.

| 필드 | 반영 방법 |
|------|-----------|
| **`checklist`** | **구체 수치를 그대로 코드에 넣는다.** `48px+ gaps` → `gap: 3rem`, `32px+ type` → `font-size: clamp(2rem, …)`. 눈대중으로 줄이지 않는다 |
| `tokens` | `globals.scss` CSS 변수로 작성 (`--block-gap: 48px` 등) |
| `uxRules` | 각 규칙의 Do/Don't 를 코드에 적용 (예: Content Jumping → 이미지에 `aspect-ratio`, Loading Indicators → 스켈레톤 컴포넌트 + `loading.tsx`) |
| `motion` | `duration`/`easing` 을 **계획서 값 그대로** CSS transition/animation 에. 임의로 바꾸지 않는다. `notes` 의 주의사항(라이선스 등) 확인 |
| `stackGuides` | Next.js: App Router, `next/image`, `error.tsx`, `'use client'` 최소화 / React: `memo`·`useCallback` |
| `pattern` / `layout` | 섹션 순서, CTA 배치 전략 |
| `icons` | **계획서에 적힌 라이브러리를 쓴다.** 다른 걸로 바꾸려면 사용자에게 먼저 확인한다 (설치가 따라온다). 이모지를 아이콘 대용으로 쓰지 않는다 |

`prefers-reduced-motion` 대응은 모션이 있으면 항상 넣는다.

> **`checklist` 와 `motion` 은 "적당히" 반영하면 실패한다.**
> 과거에 gap 을 48px 대신 12px, 제목을 32px 대신 17px 로 만들어 계획한 디자인 강도에
> 한참 못 미친 사례가 있다. 수치는 계획서 값을 기준으로 하고, 줄일 이유가 있으면
> 보고에 근거를 적는다.

## 4단계: Coder 디스패치

- `.claude/rules/dispatch-protocol.md` 의 디스패치 방식을 따른다
- `docs/agents/coder.md` 프로필을 프롬프트로 사용
- 작업 디렉토리: `__PROJECT_PATH__`
- FSD 순서: `shared → entities → features → widgets → app`
- 같은 레이어의 서로 독립적인 슬라이스는 병렬 디스패치 가능

### FSD 구조 (Coder 프롬프트에 포함)

| 레이어 | 넣는 것 | 넣지 않는 것 |
|--------|---------|--------------|
| `app` | page.tsx, layout.tsx (URL → widget 연결) | 로직, 스타일, 컴포넌트 |
| `widgets` | 페이지 섹션, 독립 UI 블록, 스타일 | 비즈니스 로직 |
| `features` | 사용자 동작, 비즈니스 로직, `model/` + `api/` + `ui/` | — |
| `entities` | 데이터 타입(`model/types.ts`) + API(`api/`) | UI 일체 |
| `shared` | 범용 코드 (다른 프로젝트에서도 동작) | 도메인 지식 |

각 슬라이스에 `index.ts` public API 필수.

### 플랫폼별 UI 규칙

계획서의 `platform` 결정에 따른다:

- **모바일 앱 전용** — 터치 영역 최소 44px, 바텀 내비, SafeArea padding, 스와이프 제스처
- **웹 전용** — 호버 인터랙션, 사이드바/탑바 내비, min-width 1024px 기준
- **반응형** — 모바일 퍼스트 → `640px` → `768px` → `1024px`. 터치 + 호버 겸용

### 디자인 원칙

- UI 는 항상 트렌디하게. 올드한 디자인 금지
- AI스러운 디자인 금지 — 보라+파랑 그라디언트 남발, 스파클 아이콘, 뻔한 생성물 느낌
- 다크/라이트는 자유

> 코드 스타일(화살표 함수, import 순서, 네이밍, `any`/`enum` 금지 등)은
> `.claude/rules/coding-standards.md` 에 있고 항상 자동 로드된다. 여기서 반복하지 않는다.

## 5단계: 검증

순서대로 실행한다. **`package.json` 에 스크립트가 없으면 건너뛰지 말고 대체 명령을 쓴다.**

```bash
cd __PROJECT_PATH__

npm run build           # 없으면: npx tsc --noEmit
npm run lint            # 있는 경우
npm run format          # 없으면: npx prettier --write <변경한 파일>
npm run lint:fsd        # 없으면: npx tsx scripts/lint-fsd.ts src
```

- 에러가 나면 **수정 후 재검증**한다. 실패 상태로 완료 보고하지 않는다
- 3회 시도해도 같은 에러가 반복되면 진행을 멈추고 원인과 함께 사용자에게 보고한다
- `lint:fsd` 가 없으면 이 워크스페이스의 `scripts/lint-fsd.ts` 를 대상 프로젝트에
  복사하도록 안내한다

### 디자인 대조 (빌드 통과만으로는 부족하다)

빌드·린트는 디자인이 계획대로 됐는지 알려주지 않는다. 아래를 직접 대조한다:

- [ ] `design.checklist` 항목을 하나씩 짚어 **실제 CSS 값과 비교** — 수치가 계획보다 작지 않은지
- [ ] `design.motion` 의 각 항목이 코드에 존재하는지 (hover / reveal / stagger 등 **개수까지** 확인)
- [ ] `uxRules` 의 `Critical`/`High` 가 전부 구현됐는지 — 특히 로딩·빈 상태·aria 레이블
- [ ] `design.icons.library` 를 실제로 썼는지
- [ ] 계획서에 있는데 구현하지 않은 항목이 있으면 **보고에 명시** (조용히 빼지 않는다)

## 6단계: 보고

- 생성/수정/삭제한 파일 목록
- 주요 변경 사항 요약
- 검증 결과 (빌드/린트/FSD 린트 각각의 실제 결과 — 통과했다고만 쓰지 않는다)
- **디자인 대조 결과** — checklist·motion·uxRules 중 반영한 것과 빠뜨린 것
- 계획서와 달라진 점과 그 근거
- **커밋하지 않는다.** 커밋은 사용자가 결정한다
- 다음 단계로 `/review-fsd` (FSD 검수) 또는 `/test` (테스트 작성) 안내
