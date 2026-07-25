---
name: refactor
description: 대상 프로젝트의 코드 품질을 분석하고 FSD 규칙 내에서 개선을 제안합니다.
argument-hint: "리팩토링 대상 (예: widgets/home-hero)"
---

# 리팩토링 분석

대상: $ARGUMENTS

## 절차

### 1단계: 코드 분석
- 대상 프로젝트(`__PROJECT_PATH__`)에서 지정된 대상 코드 읽기
- 대상이 지정되지 않으면 src/ 전체 스캔
- docs/agents/refactor.md 프로필 참조

### 2단계: 문제 탐지 (5가지 카테고리)

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

#### 코드 스타일
- function 키워드 사용 (화살표 함수 아닌 경우)
- any 타입 사용
- 네이밍 규칙 위반 (Boolean 접두사, 핸들러 네이밍 등)

### 3단계: HTML 리포트 생성 (다크모드)
- 각 문제에 대해:
  - 심각도: critical / warning / info
  - 파일 경로 + 줄 수
  - 문제 설명
  - Before/After 코드 예시로 개선 방안 제시
- 상단에 요약 카운트
- `open` 명령으로 브라우저에서 열기

### 4단계: 사용자 승인 후 실행
- 사용자가 승인한 항목만 수정
- 한 번에 하나의 변경만 적용
- 변경 후 `npm run build` 빌드 확인
- 변경 후 `npm run lint:fsd` FSD 검사
- 기능이 깨지지 않았는지 확인
