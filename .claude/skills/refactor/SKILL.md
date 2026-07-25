---
name: refactor
description: 대상 프로젝트의 코드 품질을 분석하고 FSD 규칙 내에서 개선을 제안합니다.
argument-hint: "리팩토링 대상 (예: widgets/home-hero)"
---

# 리팩토링 분석

대상: $ARGUMENTS

## 절차

### 1단계: 분석
- 대상 프로젝트(`/Users/minchangsung/nol-meok/nol-meok`)에서 코드 분석
- 중복 코드, 150줄 초과 컴포넌트, 잘못된 레이어 배치, 불필요한 의존성

### 2단계: HTML 리포트 생성
- 발견된 문제 + 심각도 + Before/After 제안
- 브라우저에서 확인

### 3단계: 사용자 승인 후 실행
- 한 번에 하나의 변경만 적용
- 매번 빌드 확인
