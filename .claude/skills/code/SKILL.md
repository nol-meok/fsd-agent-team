---
name: code
description: 승인된 계획에 따라 대상 프로젝트에서 FSD 규칙을 준수하여 코드를 작성합니다.
argument-hint: "작업 내용 또는 승인 메시지"
---

# 코딩 실행

작업 내용: $ARGUMENTS

## 절차

### 1단계: 계획 확인
1. 대화 내 승인된 계획서 내용 확인
2. 대상 프로젝트(`__PROJECT_PATH__`)의 CLAUDE.md 규칙 확인

### 2단계: Coder 디스패치
- docs/agents/coder.md 프로필 참조
- FSD 작업 순서에 따라 Task 도구로 디스패치
- 작업 디렉토리: `__PROJECT_PATH__`

### 3단계: 검증
- 빌드 확인 (`npm run build`)
- 포맷 적용 (`npm run format`)
- FSD 린트 (`npm run lint:fsd`)

### 4단계: 보고
- 변경 파일 목록 + 주요 변경 사항 요약
- `/review-fsd`로 검수 가능하다고 안내
