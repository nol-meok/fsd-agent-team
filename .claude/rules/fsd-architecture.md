# FSD 아키텍처 규칙

대상 프로젝트: `__PROJECT_PATH__`

## 레이어 구조 (단방향 의존성)

```
app → widgets → features → entities → shared
```

상위 → 하위만 import 가능. 역방향/동일 레이어 간 import 절대 금지.

## 각 레이어 역할

| 레이어 | 역할 | 비유 | 포함 |
|--------|------|------|------|
| app | URL → widget 연결 (라우팅 설정) | 리모컨 | page.tsx, layout.tsx만 |
| widgets | 화면 자체를 구현 | TV 프로그램 | 페이지 섹션, 독립 UI 블록, 스타일 |
| features | 사용자 동작 처리 (~하기) | 기능 버튼 | 비즈니스 로직, 상태, 인터랙션 UI |
| entities | 데이터 구조 정의 (~이다) | 데이터 사전 | 타입 + API만. UI 없음 |
| shared | 범용 코드 (다른 프로젝트에서도 동작) | 공구함 | Button, useDebounce, formatDate |

## 슬라이스 내부 구조

### widgets / features
```
slice-name/
├── ui/            # 컴포넌트 + 스타일 (*.module.scss)
├── model/         # 상태, 로직, 타입 (features만)
├── api/           # API 호출 (features만)
└── index.ts       # public API (필수)
```

### entities (UI 없음)
```
entity-name/
├── model/types.ts  # 데이터 타입 (필수)
├── api/            # CRUD API (선택)
└── index.ts        # public API (필수)
```

## 상태 관리 배치

| 상태 종류 | 레이어 | 위치 |
|-----------|--------|------|
| 서버 상태 (API 캐싱) | entities | entities/*/model/ |
| 기능 상태 (유즈케이스) | features | features/*/model/ |
| 전역 UI 상태 | shared | shared/lib/stores/ |
| 로컬 상태 | 해당 컴포넌트 | useState |
