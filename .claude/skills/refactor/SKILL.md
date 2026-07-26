---
name: refactor
description: 대상 프로젝트의 코드 품질을 분석하고 FSD 규칙 내에서 개선을 제안합니다.
argument-hint: "리팩토링 대상 (예: widgets/home-hero)"
---

# 리팩토링 분석

대상: $ARGUMENTS

## 절차

### 1단계: 안전망 확인 (먼저)

리팩토링은 동작을 바꾸지 않아야 한다. 그걸 보장할 수단이 있는지부터 본다.

```bash
cd __PROJECT_PATH__
npm test 2>/dev/null || echo "테스트 없음"
npm run build            # 리팩토링 전 기준선(baseline) 확보
git status --short       # 작업 트리가 깨끗한지
```

| 상황 | 처리 |
|------|------|
| 테스트 있고 통과 | 진행. 각 변경 후 재실행해서 회귀를 잡는다 |
| 테스트 없음 | **구조 변경(파일 분리·레이어 이동) 전에 `/test` 로 테스트를 먼저 만들자고 제안한다.** 사용자가 거부하면 진행하되, 리포트에 "회귀 검증 수단 없음" 을 명시한다 |
| 작업 트리 더러움 | 되돌릴 수 없는 상태로 섞이므로, 커밋 또는 stash 를 먼저 안내한다 |
| 빌드 실패 | 리팩토링 전에 빌드를 먼저 고친다 (기준선 없이는 회귀 판별 불가) |

### 2단계: 코드 분석
- 대상 프로젝트(`__PROJECT_PATH__`)에서 지정된 대상 코드 읽기
- 대상이 지정되지 않으면 src/ 전체 스캔
- `.claude/rules/dispatch-protocol.md` 에 따라 docs/agents/refactor.md 프로필로 디스패치

### 3단계: 문제 탐지 (4가지 카테고리)

> 코드 스타일 위반(`function` 키워드, `any`, `console.log`, 인라인 스타일)과
> 명확한 FSD import 위반은 `npx tsx scripts/lint-fsd.ts <src>` 가 기계적으로 잡는다.
> 여기서는 **린터가 잡을 수 없는, 판단이 필요한 문제**에 집중한다.

#### 중복 코드
- 동일하거나 유사한 로직이 2곳 이상 존재하는가
- 공통 유틸이나 훅으로 추출 가능한가

#### 컴포넌트 비대화
- 150줄 초과 컴포넌트가 있는가
- 하나의 컴포넌트가 여러 역할(데이터 fetch + 로직 + UI)을 하는가

#### FSD 레이어 위반
- shared에 도메인 코드가 있는가
- entities에 UI가 있는가
- widgets에 비즈니스 로직이 있는가
- features끼리 교차 import하는가

#### 불필요한 의존성
- 사용하지 않는 import가 있는가
- 과도하게 넓은 범위를 import하는가 (전체 모듈 import)

### 4단계: HTML 리포트 생성 (다크모드)
- `reports/refactor/YYYYMMDD-HHMM.html` 생성
  - `plans/` 는 계획서 전용. 분석 리포트는 `reports/` 에 둔다
  - 색상은 `docs/plan-template.html` 의 CSS 변수 팔레트를 따른다
- 각 문제에 대해:
  - 심각도: critical / warning / info
  - 파일 경로 + 줄 수
  - 문제 설명
  - Before/After 코드 예시로 개선 방안 제시
- 상단에 요약 카운트
- `open` 명령으로 브라우저에서 열기

### 5단계: 사용자 승인 후 실행

- 사용자가 **승인한 항목만** 수정한다. 승인 없이 "겸사겸사" 고치지 않는다
- **한 번에 하나의 변경만** 적용하고, 매번 아래를 확인한다:

```bash
cd __PROJECT_PATH__
npm test                 # 안전망 (있는 경우)
npm run build            # 빌드
npm run lint:fsd         # 없으면 npx tsx scripts/lint-fsd.ts src
```

- 하나라도 실패하면 **다음 항목으로 넘어가지 않고** 그 변경을 되돌리거나 고친다
- 기능 동작이 바뀌었으면 리팩토링이 아니다. 되돌리고 사용자에게 보고한다
- 커밋하지 않는다. 변경 단위가 크면 사용자에게 커밋 시점을 제안한다
- 보고: 적용한 항목, 건너뛴 항목(과 이유), 각 단계 검증 결과
