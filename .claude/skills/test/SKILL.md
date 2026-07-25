---
name: test
description: 대상 프로젝트의 코드에 레이어별 전략에 맞는 테스트를 작성합니다.
argument-hint: "테스트 대상 (예: review 기능)"
---

# 테스트 작성

테스트 대상: $ARGUMENTS

## 절차

### 1단계: 대상 코드 분석
- 대상 프로젝트(`__PROJECT_PATH__`)에서 테스트할 파일 탐색
- 각 파일이 속한 FSD 레이어 확인
- 의존성(import) 파악

### 2단계: Tester 디스패치
- docs/agents/tester.md 프로필 참조
- 작업 디렉토리: `__PROJECT_PATH__`

### 3단계: 레이어별 테스트 전략

| 대상 | 테스트 유형 | 포인트 |
|------|-----------|--------|
| shared/lib/utils | 유닛 테스트 | 순수 함수 입출력, 엣지 케이스 |
| shared/lib/hooks | 훅 테스트 | renderHook, act |
| entities/model | 타입/변환 테스트 | 매퍼 함수, 타입 가드 |
| entities/api | API 모킹 테스트 | fetch mock, 에러 케이스 |
| features/model | 상태/로직 테스트 | renderHook, 유효성 검사 로직 |
| features/ui | 인터랙션 테스트 | render, fireEvent (클릭, 입력, 제출) |
| widgets/ui | 통합 테스트 | 하위 레이어 조합 렌더링 확인 |

### 4단계: 테스트 작성 규칙
- 테스트 파일 위치: 대상 파일 옆에 `__tests__/` 폴더 또는 `*.test.ts(x)`
- 화살표 함수로 작성
- describe/it 구조
- 테스트명 한국어 가능
- 각 테스트는 하나의 동작만 검증
- Happy path + Edge case + Error case 포함
- 외부 의존성(API, 라우터 등)은 모킹
- 구현 세부사항이 아닌 동작을 검증

### 5단계: 실행 및 보고
- 테스트 실행하여 전체 통과 확인
- 실패 시 원인 분석 후 수정
- 커버리지 요약 보고 (가능한 경우)
