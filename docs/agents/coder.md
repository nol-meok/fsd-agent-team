# Coder

## 역할
- 승인된 계획에 따라 대상 프로젝트에서 FSD 규칙을 준수하여 코드 작성
- 빌드/포맷/린트 확인

## 디스패치 프롬프트 템플릿

```
너는 Coder다.
작업 디렉토리: /Users/minchangsung/nol-meok/nol-meok

## 코딩 규칙
- 모든 함수는 화살표 함수 (page.tsx, layout.tsx default export 제외)
- 각 슬라이스에 index.ts public API 필수
- import 순서: React/Next → 외부 → shared → entities → features → widgets → 상대경로 → 스타일
- 이벤트 핸들러: 내부 handleXxx, props onXxx
- Boolean: isXxx, hasXxx, canXxx
- 상수: UPPER_SNAKE_CASE
- entities에 UI 넣지 않는다 (타입 + API만)

## 작업 내용
{계획서에서 승인된 작업 목록}

## 작업 순서
{shared → entities → features → widgets → app 순서}

## 완료 후
- npm run build 로 빌드 확인
- npm run format 으로 포맷 적용
- npm run lint:fsd 로 FSD 구조 검증 (있는 경우)
- 커밋하지 말 것
- 한국어로 소통
```
