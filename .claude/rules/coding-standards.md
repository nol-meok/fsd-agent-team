# 코딩 규칙

## 함수 스타일
- 모든 함수는 화살표 함수(`=>`) 사용. `function` 키워드 금지 (page.tsx, layout.tsx default export 제외)

## 네이밍
- 컴포넌트 파일: PascalCase (`LoginForm.tsx`)
- 슬라이스 폴더: kebab-case (`write-review/`)
- 훅/유틸: camelCase (`useAuth.ts`, `formatDate.ts`)
- Props 타입: `XxxProps`
- Boolean: `isXxx`, `hasXxx`, `canXxx`, `shouldXxx`
- 상수: `UPPER_SNAKE_CASE`
- 이벤트 핸들러: 내부 `handleXxx`, props `onXxx`

## import 순서
1. React/Next.js 내장
2. 외부 라이브러리
3. @/shared
4. @/entities
5. @/features
6. @/widgets
7. 상대 경로
8. 스타일

## TypeScript
- `any` 금지 → `unknown` + 타입 가드
- `as` 최소화
- `enum` 금지 → `as const` 객체
- 객체: `interface` / 유니온·유틸리티: `type`

## 스타일
- Tailwind: 레이아웃, 간격, 반응형
- SCSS module: 컴포넌트 고유 스타일
- 인라인 스타일 금지

## 조건부 렌더링
- early return 우선
- 삼항 네스팅 금지 (1단계만)
- 복잡한 조건은 변수로 추출

## 에러 처리
- entities api: throw만
- features/widgets: try/catch로 처리
- catch는 `unknown` 타입 + 타입 가드

## 접근성
- img에 alt 필수
- 텍스트 없는 버튼에 aria-label
- `<div onClick>` 금지 → `<button>` 사용

## 금지 사항
- console.log 커밋
- @ts-ignore, @ts-nocheck
- !important
- 하드코딩 API URL
- index.tsx를 컴포넌트로 사용 (re-export만)

## 한국어 소통
- 모든 대화, 계획서, 리포트는 한국어로 작성
