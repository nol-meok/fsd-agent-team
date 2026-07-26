---
name: review-fsd
description: 대상 프로젝트의 FSD 구조, 의존성, 코드 컨벤션을 검수하여 HTML 리포트를 생성합니다.
argument-hint: "(인자 없음)"
---

# FSD 검수

## 1단계: 자동 린트 먼저 실행

기계가 잡을 수 있는 위반은 에이전트가 읽기 전에 걸러낸다.

```bash
# 대상 프로젝트에 lint:fsd 가 설정된 경우
cd __PROJECT_PATH__ && npm run lint:fsd

# 설정되어 있지 않으면 이 워크스페이스의 린터를 직접 실행
npx tsx scripts/lint-fsd.ts __PROJECT_PATH__/src
```

린터가 잡는 항목 (아래 2단계 8가지와 동일 — 중복 검사하지 않는다):
단방향 의존성, 교차 슬라이스 import, 슬라이스 내부 직접 import, index.ts 누락,
entities 내 UI, app 레이어 비-라우팅 파일, function 키워드,
`any` / `console.log` / `@ts-ignore` / 인라인 스타일 / `!important`.

대상 프로젝트에 아직 없으면 설치를 안내한다:

```bash
cp scripts/lint-fsd.ts __PROJECT_PATH__/scripts/
# package.json → "lint:fsd": "npx tsx scripts/lint-fsd.ts"
```

## 2단계: 린터 검사 항목 (참고)

#### 구조
1. **app 레이어** — page/layout 등 라우팅 파일만 (스타일·컴포넌트 금지)
2. **index.ts 존재** — widgets/features/entities 각 슬라이스에 public API
3. **entities에 UI 없음** — `ui/` 폴더나 `*.tsx` 없음

#### import 의존성
4. **단방향** — app → widgets → features → entities → shared 방향만
5. **동일 레이어 교차** — feature A → feature B 금지
6. **슬라이스 내부 직접 import** — `@/entities/review/model/types` 금지 (index.ts 통해서만)

#### 코드 컨벤션
7. **function 키워드** — page.tsx/layout.tsx default export 외 금지
8. **금지 항목** — `any`, `console.log`, `@ts-ignore`, `@ts-nocheck`, 인라인 스타일

## 3단계: Reviewer 디스패치 — 판단이 필요한 항목만

- docs/agents/reviewer.md 프로필 참조
- 대상 프로젝트(`__PROJECT_PATH__`)에서 **읽기 전용**으로 실행
- 린터가 이미 잡은 1~8번은 건너뛰고, 아래 배치 적절성에 집중한다:

- API 호출이 shared 에 있지 않은지
- 비즈니스 로직이 widgets 에 있지 않은지
- 인터랙션 로직(onClick 핸들러 내 fetch 등)이 entities 에 있지 않은지
- 스타일 파일이 app 이나 entities 에 있지 않은지
- 1곳에서만 쓰는 유틸이 shared 에 있지 않은지
- 슬라이스 이름이 역할을 드러내는지 (features 는 동작, entities 는 대상)

## 4단계: HTML 리포트 생성

- `reports/review/YYYYMMDD-HHMM.html` 생성 (다크모드)
  - 검수 결과는 승인 대상이 아니므로 `plans/` 에 두지 않는다 (`plans/` 는 계획서 전용)
  - 색상은 `docs/plan-template.html` 의 CSS 변수 팔레트를 따른다
- 상단 요약: 검사 파일 수, 통과 수, 위반 수 (린터 결과 + Reviewer 판단 합산)
- 위반 항목: 파일 경로 + 줄 번호 + 위반 유형 + 구체적 수정 방법
- 위반이 없으면 "FSD 검수 통과 ✅" 표시
- `open` 명령으로 브라우저에서 열기

## 5단계: 후속 조치 안내

검수는 수정하지 않는다. 위반이 있으면 다음을 안내한다:

| 위반 성격 | 후속 |
|-----------|------|
| 명확한 규칙 위반 (import 방향, index.ts 누락 등) | `/code` 로 수정 |
| 구조 개선이 필요한 경우 (레이어 재배치, 파일 분리) | `/refactor` 로 분석 후 승인 |
| 레이어 대규모 재편 | `/migrate-fsd` |
