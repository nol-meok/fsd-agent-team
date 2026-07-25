# 팀원 디스패치 프로토콜

## 전제 조건
**작업계획서(plans/*.md)가 사용자 승인을 받은 후에만 디스패치한다.**

## 디스패치 방식
팀원에게 작업을 배분할 때 Task 도구를 사용한다.

## 프롬프트 필수 포함 사항
- 작업 디렉토리: `/Users/minchangsung/nol-meok/nol-meok`
- 구체적인 작업 내용 (파일 경로, 생성/수정/삭제)
- FSD 레이어 규칙 리마인드
- 해당 팀원의 docs/agents/*.md 프로필 참조

## FSD 작업 순서
의존성 기반으로 순서를 지킨다:
1. shared (의존 없음)
2. entities (shared만 의존)
3. features (entities + shared 의존)
4. widgets (features + entities + shared 의존)
5. app (최종 조합)

## 병렬 디스패치 가능 조건
- 같은 레이어 내 다른 슬라이스: 병렬 가능 (서로 import 안 하므로)
- Reviewer + Tester: 대부분 병렬 가능
- 다른 레이어: 의존 관계 확인 후 판단

## 팀원별 프로필
- docs/agents/planner.md
- docs/agents/coder.md
- docs/agents/reviewer.md
- docs/agents/tester.md
