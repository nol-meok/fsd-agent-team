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

## 레이어 판정 기준 (파일 내부 코드로 판단한다)

파일명으로 정하지 않는다. `Button`/`Form`/`Table` 같은 이름은 실제 역할과 자주 어긋난다
(브릭스 실측: 이름 기반 정확도 **73%**, 171개 오분류).

**질문은 하나다 — 이 컴포넌트가 유즈케이스를 소유하는가, 남에게 위임하는가.**

| 판정 | 코드에서 확인할 것 |
|------|-------------------|
| **features** | 변경 API 호출(직접 또는 자기 훅·lib 경유) · `useForm` 폼 소유 또는 자기 슬라이스 폼의 필드 · 공유·URL 상태 쓰기(`setQueryParams` 등) · 다운로드/업로드 실행이 목적 |
| **widgets** | 조회 훅·props 로 받아 렌더 · 로컬 표현 상태(아코디언·모달 열림·입력 초안)만 · 핸들러가 부모 콜백만 호출 |
| **entities** | 도메인 타입 · API 함수 · 서버 상태 훅. **UI 없음** |
| **shared** | 같은 레이어 **2개 이상 슬라이스**가 사용 · 범용 UI/유틸 |

같은 이름 슬라이스가 `widgets/X` + `features/X` 로 갈리는 것은 정상이다
(widget 이 feature 를 조합한다). 레이어가 다르므로 충돌이 아니다.

### 슬라이스 도메인 그룹

슬라이스가 20개를 넘으면 도메인 그룹 폴더로 묶는다.

```
features/admin/functions/     features/deal/inspection-comprehensive/
features/admin/role-detail/   features/deal/preview-sales/
```

**그룹 폴더는 `index.ts` 를 갖지 않는다.** public API 는 항상 슬라이스에만 둔다.
그룹에 `index.ts` 를 만들면 "슬라이스 안의 슬라이스" 가 되어 FSD 위반이다.

| | |
|---|---|
| ✅ | `features/admin/functions/index.ts` |
| ❌ | `features/admin/index.ts` |

그룹 이름과 같은 이름의 슬라이스가 있으면 그룹으로 만들지 않는다.

### 같은 레이어 교차 import 는 금지 — 공유되면 내린다

`features/A` 가 `features/B` 를 import 하면 위반이다. 2개 이상 슬라이스가 쓰는 파일은
`shared`(또는 `entities`)로 내린다. 판정 도구: `scripts/classify-layers.py`

---

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
