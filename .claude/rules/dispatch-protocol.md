# 팀원 디스패치 프로토콜

## 전제 조건

**작업계획서(`plans/**/*.md`)가 사용자 승인을 받은 후에만 디스패치한다.**

## 디스패치 방식

팀원은 별도로 등록된 subagent 가 아니라 **프롬프트 템플릿**이다.
`docs/agents/*.md` 의 템플릿을 읽어 Task 도구 프롬프트로 사용한다.

1. 해당 팀원의 `docs/agents/<팀원>.md` 를 읽는다
2. "디스패치 프롬프트 템플릿" 의 `{중괄호}` 자리를 계획서 내용으로 채운다
3. Task 도구로 실행한다

## 프롬프트 필수 포함 사항

- 작업 디렉토리: `__PROJECT_PATH__`
- 구체적인 작업 내용 (파일 경로, 생성/수정/삭제)
- FSD 레이어 규칙 리마인드
- 커밋하지 말 것 / 한국어로 소통

## FSD 작업 순서

의존성 기반으로 순서를 지킨다:

1. `shared` (의존 없음)
2. `entities` (shared 만 의존)
3. `features` (entities + shared 의존)
4. `widgets` (features + entities + shared 의존)
5. `app` (최종 조합)

## 병렬 디스패치 가능 조건

- **같은 레이어 내 다른 슬라이스**: 병렬 가능 (서로 import 안 하므로)
- **Reviewer + Tester**: 대부분 병렬 가능
- **다른 레이어**: 의존 관계 확인 후 판단. 하위 레이어 완료 전에는 금지

## 팀원별 프로필

| 팀원 | 프로필 | 쓰기 범위 |
|------|--------|-----------|
| Planner | `docs/agents/planner.md` | 계획서만 |
| Coder | `docs/agents/coder.md` | 대상 프로젝트 코드 |
| Reviewer | `docs/agents/reviewer.md` | 없음 (읽기 전용) |
| Tester | `docs/agents/tester.md` | 테스트 파일 |
| Refactor | `docs/agents/refactor.md` | 승인된 항목만 |
| Migrator | `docs/agents/migrator.md` | 없음 (계획만) |

## 검증은 별도 패스로

작성한 에이전트가 자기 결과를 승인하지 않는다.
Coder 작업 후 Reviewer/Tester 를 **별도 디스패치**해서 검증한다.
