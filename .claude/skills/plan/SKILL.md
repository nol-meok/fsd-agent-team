---
name: plan
description: 요구사항을 분석하고 HTML 작업계획서를 작성합니다.
argument-hint: "작업 설명 (예: 음식점 리뷰 작성 기능)"
---

# 작업계획서 작성

사용자 요청: $ARGUMENTS

## 절차

### 1단계: 분석
1. 대상 프로젝트(`__PROJECT_PATH__`) 구조 탐색 (src/ 하위, Glob/Grep/Read 활용)
2. 프로젝트의 CLAUDE.md와 레이어별 CLAUDE.md 읽기
3. 관련 기존 코드 탐색

### 2단계: 계획서 작성
1. `plans/feature/YYYYMMDD-제목.md` 작성 (docs/plan-template.md 참고)
2. `plans/feature/YYYYMMDD-제목.html` 작성 (docs/plan-template.html 참고하여 PLAN 데이터 + md 본문 채움)
   - 기존 예시 참고: plans/feature/20260726-review.html
3. md + html 동시 생성 필수. 한쪽만 만들지 않는다.

### 3단계: 사용자 승인 요청
1. HTML 파일 경로를 제시하고 `open` 명령으로 브라우저 열기
2. "브라우저에서 계획서를 확인하고, 결정 사항을 선택한 뒤 [프롬프트로 복사] 버튼을 눌러 채팅에 붙여넣어 주세요." 안내
3. 사용자가 결정사항을 붙여넣으면 → md 확정 + html decisions에 decided 채움 → 코딩 디스패치

## 계획서 필수 포함
- FSD 레이어별 파일 배치 계획 (PLAN.layers)
- 작업 순서 타임라인 (PLAN.steps)
- Import 의존성 (PLAN.deps)
- 사용자 결정이 필요한 항목 (PLAN.decisions)
- FSD 검증 체크리스트
