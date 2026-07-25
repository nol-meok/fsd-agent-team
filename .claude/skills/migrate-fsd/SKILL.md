---
name: migrate-fsd
description: 기존 프로젝트를 FSD 아키텍처로 변환하는 단계별 계획을 수립합니다.
argument-hint: "(인자 없음 또는 추가 지시)"
---

# FSD 마이그레이션

추가 지시: $ARGUMENTS

## 절차

### 1단계: 현재 구조 깊이 분석

대상 프로젝트(`/Users/minchangsung/nol-meok/nol-meok`)의 src/ 전체를 탐색하여 다음을 수행한다:

#### 1-1. 파일 전수 조사
- src/ 하위 모든 파일 목록 확인
- 각 파일의 줄 수 측정 (wc -l)
- 각 파일의 import문 분석

#### 1-2. 문제점 탐지 (issue 목록 생성)

각 파일에 대해 아래 7가지 카테고리를 검사하고 발견된 issue마다 심각도(critical/warning/info)를 매긴다:

| 카테고리 | 검사 내용 | 심각도 기준 |
|---------|----------|------------|
| **거대 파일** | 150줄 초과 컴포넌트 | 300줄+ critical, 150줄+ warning |
| **깊은 중첩** | 3단계 이상 폴더 중첩 (components/common/ui/Button/) | 4단계+ critical, 3단계 warning |
| **로직/UI 혼재** | 컴포넌트에서 fetch/API 직접 호출, 상태관리 + 렌더링 혼재 | API 호출 있으면 critical |
| **중복 코드** | 유사한 함수/컴포넌트가 여러 곳에 존재 | 동일 로직 2곳+ warning |
| **타입 분산** | types/가 별도 폴더, 또는 타입이 여러 파일에 흩어짐 | 별도 폴더면 warning |
| **플랫 구조** | components/에 10개+ 파일이 역할 구분 없이 나열 | 15개+ critical, 10개+ warning |
| **순환 의존** | A→B→A 형태의 순환 import | 발견 시 critical |

#### 1-3. 파일 역할 분류
각 파일을 FSD 레이어로 분류:
- 데이터 타입 정의 → entities
- API 호출 함수 → entities
- 서버 상태 훅 (React Query 등) → entities
- 비즈니스 로직/인터랙션 훅 → features
- 인터랙션 UI (폼, 검색바) → features
- 페이지 섹션/조합 컴포넌트 → widgets
- 범용 UI (Button, Modal) → shared
- 범용 유틸 (formatDate) → shared
- 라우팅 파일 → app

### 2단계: HTML 마이그레이션 계획서 생성

`plans/migrate/YYYYMMDD-제목.md` + `.html` 쌍으로 작성한다.

#### HTML에 포함할 시각화 섹션:

**A. 현재 상태 분석 (issues)**
PLAN 데이터에 `issues` 배열을 추가:
```js
issues: [
  {
    severity: 'critical',  // critical | warning | info
    category: '거대 파일',
    file: 'src/components/ProductPage.tsx',
    lines: 420,
    desc: '420줄. 데이터 fetching + 비즈니스 로직 + UI 렌더링이 한 파일에 혼재',
    suggestion: 'entities/product (타입+API) + features/product-detail (로직) + widgets/product-page (UI 조합)으로 분리',
  },
  ...
]
```

시각화:
- severity별 색상 (critical=빨강, warning=노랑, info=파랑)
- 카테고리별 아이콘
- 파일 경로 + 줄 수 + 문제 설명
- 개선 방안 (어떻게 분리할지)
- 상단에 요약 카운트 (critical N개, warning N개, info N개)

**B. Before → After 비교**
PLAN 데이터에 `beforeAfter` 객체를 추가:
```js
beforeAfter: {
  before: [
    'src/components/Header.tsx',
    'src/components/ProductCard.tsx',
    // ... 현재 구조 파일 목록
  ],
  after: [
    // FSD 구조 파일 목록 (layers 데이터에서 자동 생성)
  ],
}
```

시각화:
- 좌우 2컬럼 레이아웃 (Before | After)
- Before: 현재 폴더 트리 (문제 파일에 빨간 점)
- After: FSD 폴더 트리 (레이어 색상)
- 화살표로 이동 경로 표시 (가능하면)

**C. FSD 레이어 배치 (기존과 동일)**
- 플로우 바 + 레이어별 파일트리 + MOVE/CREATE/MODIFY 태그

**D. 타임라인 (기존과 동일)**
- Phase별 작업 순서

**E. 결정 콘솔 (기존과 동일)**

### 3단계: 사용자 승인 후 Phase별 실행
- 한 Phase씩 실행, 매번 빌드 확인
- import 경로 일괄 변경
- 각 슬라이스에 index.ts 생성
- 문제점으로 발견된 거대 파일은 분리 작업 포함
