---
name: plan
description: 요구사항을 분석하고 HTML 작업계획서를 작성합니다.
argument-hint: "작업 설명 (예: 음식점 리뷰 작성 기능)"
---

# 작업계획서 작성

사용자 요청: $ARGUMENTS

## 절차

### 1단계: 분석
1. 대상 프로젝트(`/Users/minchangsung/nol-meok/nol-meok`) 구조 탐색 (src/ 하위)
2. 프로젝트의 CLAUDE.md와 레이어별 CLAUDE.md 읽기
3. 관련 기존 코드 탐색 (Explore 에이전트 활용)

### 2단계: 계획서 작성
1. `plans/feature/YYYYMMDD-제목.md` 작성 (docs/plan-template.md 참고)
2. `plans/feature/YYYYMMDD-제목.html`은 **반드시 빌더로 생성**한다:
   ```bash
   python3 scripts/build-plan-html.py plans/feature/YYYYMMDD-제목.md < plan.json
   ```
   - `plan.json`: PLAN 객체를 JSON으로 작성 (스키마는 스크립트 docstring 참고). 스크래치패드에 두고 커밋하지 않는다
   - **템플릿을 직접 복사해 문자열 치환하는 것 금지.** 상단 사용법 주석에 태그 문구가 있어 오인 치환되면 문서 전체가 주석 처리되고 빈 화면이 된다 (실제 발생한 사고)
   - 빌더가 생성 후 자동 검증한다. `✓` 줄이 모두 출력되지 않으면 **브라우저를 열지 말고** 원인을 고친다
3. md + html 동시 생성 필수. 한쪽만 만들지 않는다.

### 3단계: 사용자 승인 요청
1. `open` 전에 검증이 통과했는지 확인한다. 이미 있는 html을 손으로 고쳤다면:
   ```bash
   python3 scripts/build-plan-html.py --verify-only plans/feature/YYYYMMDD-제목.html
   ```
2. HTML 파일 경로를 제시하고 `open` 명령으로 브라우저 열기
2. "브라우저에서 계획서를 확인하고, 결정 사항을 선택한 뒤 [프롬프트로 복사] 버튼을 눌러 채팅에 붙여넣어 주세요." 안내
3. 사용자가 결정사항을 붙여넣으면 → md 확정 + html decisions에 decided 채움 → 코딩 디스패치

## 계획서 필수 포함
- FSD 레이어별 파일 배치 계획
- 작업 순서 (shared → entities → features → widgets → app)
- 사용자 결정이 필요한 항목 (decisions)
- FSD 검증 체크리스트
