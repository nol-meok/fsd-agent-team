---
name: code
description: 승인된 계획에 따라 대상 프로젝트에서 FSD 규칙을 준수하여 코드를 작성합니다.
argument-hint: "작업 내용 또는 승인 메시지"
---

# 코딩 실행

작업 내용: $ARGUMENTS

## 절차

### 1단계: 계획 확인
1. 대화 내 승인된 계획서 내용 확인 (어떤 파일을 어느 레이어에 생성/수정하는지)
2. 대상 프로젝트(`__PROJECT_PATH__`)의 CLAUDE.md 읽어 코드 컨벤션 확인
3. 작업할 레이어의 CLAUDE.md가 있으면 해당 규칙도 확인

### 2단계: Coder 디스패치
- docs/agents/coder.md 프로필 참조
- FSD 작업 순서에 따라 디스패치: shared → entities → features → widgets → app
- 작업 디렉토리: `__PROJECT_PATH__`

### 3단계: 코딩 규칙 (Coder가 준수할 것)

#### FSD 구조
- app: page.tsx, layout.tsx만 (URL → widget 연결)
- widgets: 페이지 섹션, 독립 UI 블록 (화면 구현). 스타일 포함
- features: 사용자 동작, 비즈니스 로직. 상태관리(model/) + API(api/) + UI(ui/)
- entities: 데이터 타입(model/types.ts) + API(api/)만. UI 없음
- shared: 범용 코드 (다른 프로젝트에서도 동작하는 것만)
- 각 슬라이스에 index.ts public API 필수

#### 코드 스타일
- 모든 함수 화살표 함수 (page.tsx, layout.tsx default export 제외)
- import 순서: React/Next → 외부 → shared → entities → features → widgets → 상대경로 → 스타일
- 이벤트 핸들러: 내부 `handleXxx`, props `onXxx`
- Boolean: `isXxx`, `hasXxx`, `canXxx`
- 상수: `UPPER_SNAKE_CASE`
- 조건부 렌더링: early return 우선, 삼항 네스팅 금지
- `any` 금지 → `unknown` + 타입 가드
- `enum` 금지 → `as const` 객체

### 4단계: 검증
- `npm run build` — 빌드 에러 없는지 확인
- `npm run format` — Prettier 포맷 적용
- `npm run lint:fsd` — FSD 구조 자동 검사 (있는 경우)
- 에러 발생 시 수정 후 재검증

### 5단계: 보고
- 생성/수정/삭제한 파일 목록
- 주요 변경 사항 요약
- `/review-fsd`로 FSD 검수 가능하다고 안내
