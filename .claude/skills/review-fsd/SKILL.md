---
name: review-fsd
description: 대상 프로젝트의 FSD 구조, 의존성, 코드 컨벤션을 검수하여 HTML 리포트를 생성합니다.
argument-hint: "(인자 없음)"
---

# FSD 검수

## 절차

### 1단계: Reviewer 디스패치
- docs/agents/reviewer.md 프로필 참조
- 대상 프로젝트(`/Users/minchangsung/nol-meok/nol-meok`)에서 검수 실행
- 자동 린트(`npm run lint:fsd`)도 실행

### 2단계: 검수 항목
1. 구조 검사 - app에 허용되지 않는 파일
2. import 의존성 - 단방향 규칙 위반, 동일 레이어 교차
3. entities에 UI 없는지 확인
4. index.ts 존재 여부
5. 코드 컨벤션 - function 키워드, any, console.log
6. 파일 배치 적절성

### 3단계: HTML 리포트 생성
- `plans/review-YYYYMMDD-HHMM.html` 생성
- 통과/위반 항목 시각화
- 위반 시 구체적 수정 방법 제시
- 브라우저에서 열기
