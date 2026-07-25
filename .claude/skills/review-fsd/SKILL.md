---
name: review-fsd
description: 대상 프로젝트의 FSD 구조, 의존성, 코드 컨벤션을 검수하여 HTML 리포트를 생성합니다.
argument-hint: "(인자 없음)"
---

# FSD 검수

## 절차

### 1단계: Reviewer 디스패치
- docs/agents/reviewer.md 프로필 참조
- 대상 프로젝트(`__PROJECT_PATH__`)에서 검수 실행
- 자동 린트(`npm run lint:fsd`)도 실행 (있는 경우)

### 2단계: 검수 항목 (8가지)

#### 구조 검사
1. **app 레이어** - page.tsx, layout.tsx, CLAUDE.md 외 파일 존재 여부 (스타일, 컴포넌트 금지)
2. **index.ts 존재** - widgets, features, entities의 각 슬라이스에 public API 파일 있는지
3. **entities에 UI 없음** - entities 하위에 ui/ 폴더나 *.tsx 컴포넌트가 없는지

#### import 의존성 검사
4. **단방향 의존성** - app→widgets→features→entities→shared 방향만 허용
5. **동일 레이어 교차** - widget A → widget B, feature A → feature B 등 금지
6. **슬라이스 내부 직접 import** - `@/entities/review/model/types` 같은 내부 경로 접근 금지 (index.ts 통해서만)

#### 코드 컨벤션 검사
7. **function 키워드** - page.tsx, layout.tsx default export 외에 `export function` 사용 여부
8. **금지 항목** - `any`, `console.log`, `@ts-ignore`, `@ts-nocheck`, 인라인 스타일(`style={{}}`)

### 3단계: 파일 배치 적절성 (내용 기반 판단)
- API 호출이 shared에 있지 않은지
- 비즈니스 로직이 widgets에 있지 않은지
- 인터랙션 로직(onClick 핸들러 내 fetch 등)이 entities에 있지 않은지
- 스타일 파일이 app이나 entities에 있지 않은지
- 1곳에서만 쓰는 유틸이 shared에 있지 않은지

### 4단계: HTML 리포트 생성
- `plans/review-YYYYMMDD-HHMM.html` 생성 (다크모드)
- 상단 요약: 검사 파일 수, 통과 수, 위반 수
- 통과 항목: ✅ 목록
- 위반 항목: ❌ 파일 경로 + 위반 유형 + 구체적 수정 방법
- 위반이 없으면 "FSD 검수 통과 ✅" 표시
- `open` 명령으로 브라우저에서 열기
