---
name: test
description: 대상 프로젝트의 코드에 레이어별 전략에 맞는 테스트를 작성합니다.
argument-hint: "테스트 대상 (예: review 기능)"
---

# 테스트 작성

테스트 대상: $ARGUMENTS

## 절차

### 1단계: Tester 디스패치
- docs/agents/tester.md 프로필 참조
- 대상 프로젝트(`/Users/minchangsung/nol-meok/nol-meok`)에서 작업

### 2단계: 레이어별 테스트 전략
- shared/lib → 유닛 테스트 (순수 함수)
- entities/model → 타입/변환 테스트
- entities/api → API 모킹 테스트
- features/model → 상태/훅 테스트
- features/ui → 인터랙션 테스트
- widgets/ui → 통합 테스트

### 3단계: 실행 및 보고
- 테스트 실행 확인
- 결과 보고
