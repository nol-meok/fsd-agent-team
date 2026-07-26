---
name: test
description: 대상 프로젝트의 코드에 레이어별 전략에 맞는 테스트를 작성합니다.
argument-hint: "테스트 대상 (예: review 기능)"
---

# 테스트 작성

테스트 대상: $ARGUMENTS

## 절차

### 1단계: 테스트 환경 확인 (먼저)

테스트 러너가 없으면 테스트를 써도 돌지 않는다. 작성 전에 확인한다.

```bash
cd __PROJECT_PATH__
cat package.json | grep -E '"(test|vitest|jest)"'
ls vitest.config.* jest.config.* 2>/dev/null
```

| 상황 | 처리 |
|------|------|
| vitest / jest 설정 있음 | 그 러너의 관례(설정 파일, setup 파일)를 따른다 |
| 러너 없음 | **테스트를 먼저 쓰지 않는다.** 스택에 맞는 러너 설치를 제안하고 사용자 승인을 받는다 (Next.js/React → vitest + @testing-library/react + jsdom) |
| 기존 테스트 있음 | 그 파일의 구조·네이밍·모킹 방식을 그대로 따른다 |

### 2단계: 대상 코드 분석
- 대상 프로젝트(`__PROJECT_PATH__`)에서 테스트할 파일 탐색
- 각 파일이 속한 FSD 레이어 확인
- 의존성(import) 파악 — 모킹할 경계를 여기서 정한다

### 3단계: Tester 디스패치
- `.claude/rules/dispatch-protocol.md` 의 디스패치 방식을 따른다
- docs/agents/tester.md 프로필을 프롬프트로 사용
- 작업 디렉토리: `__PROJECT_PATH__`

### 4단계: 레이어별 테스트 전략

| 대상 | 테스트 유형 | 포인트 |
|------|-----------|--------|
| shared/lib/utils | 유닛 테스트 | 순수 함수 입출력, 엣지 케이스 |
| shared/lib/hooks | 훅 테스트 | renderHook, act |
| entities/model | 타입/변환 테스트 | 매퍼 함수, 타입 가드 |
| entities/api | API 모킹 테스트 | fetch mock, 에러 케이스 |
| features/model | 상태/로직 테스트 | renderHook, 유효성 검사 로직 |
| features/ui | 인터랙션 테스트 | render, fireEvent (클릭, 입력, 제출) |
| widgets/ui | 통합 테스트 | 하위 레이어 조합 렌더링 확인 |

### 5단계: 테스트 작성 규칙
- 테스트 파일 위치: 대상 파일 옆에 `__tests__/` 폴더 또는 `*.test.ts(x)`
- 화살표 함수로 작성, describe/it 구조
- 테스트명 한국어 가능
- 각 테스트는 하나의 동작만 검증
- Happy path + Edge case + Error case 포함
- 외부 의존성(API, 라우터 등)은 모킹
- 구현 세부사항이 아닌 **동작**을 검증 (내부 상태·호출 횟수보다 결과)

### 6단계: 실행 및 보고

```bash
cd __PROJECT_PATH__ && npm test
# 커버리지: npm test -- --coverage (러너가 지원하는 경우)
```

- **실제로 실행해서 통과를 확인한다.** 작성만 하고 통과했다고 보고하지 않는다
- 실패 시 원인 분석 후 수정 → 재실행
- `test.skip` / `test.only` / 빈 테스트 본문을 남기지 않는다.
  구현이 어려워 건너뛴 케이스는 리포트에 **건너뛴 이유와 함께 명시**한다
- 보고: 추가한 테스트 파일 목록, 통과/실패 수, 커버리지(가능한 경우), 미작성 케이스
