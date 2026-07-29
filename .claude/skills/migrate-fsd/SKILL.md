---
name: migrate-fsd
description: 기존 프로젝트를 FSD 아키텍처로 변환하는 단계별 계획을 수립합니다.
argument-hint: "(인자 없음 또는 추가 지시)"
---

# FSD 마이그레이션

추가 지시: $ARGUMENTS

## 절차

### 1단계: 현재 구조 깊이 분석

대상 프로젝트(`__PROJECT_PATH__`)의 src/ 전체를 탐색하여 다음을 수행한다:

#### 1-0. 자동 생성 코드는 대상에서 빼고, 생성기가 가리키는 파일은 **고정**한다

스웨거/OpenAPI 로 생성하는 코드(`__generated__` `generated` `.gen` 등)는 **이동·수정 대상이 아니다.**
재생성되면 되돌아가므로 옮겨봐야 의미가 없다.

더 중요한 건 **생성기 설정이 가리키는 파일**이다. 이걸 옮기면 생성 코드가 깨지거나
재생성이 필요해진다 — 불간섭 원칙 위반이다.

```bash
# 1) 생성 설정에서 외부 파일을 가리키는 곳을 찾는다
cat orval.config.ts        # mutator.path / formData.path
grep -nE "mutator|formData|customInstance|httpClient" orval.config.ts

# 2) 생성 코드가 바깥을 참조하는 지점을 전수 확인한다
grep -rhoE "from '(\.\./)+[^']+'" __generated__ --include="*.ts" \
  | sed "s/from '//;s/'$//" | sed 's|^\(\.\./\)*||' | sort | uniq -c | sort -rn
```

브릭스 사례: `orval.config.ts` 가 `mutator.path: '../lib/orval-fetcher.ts'` 를 하드코딩하고
생성 코드가 `'../../../lib/orval-fetcher'` 를 **108회**, `lib/formdata` 를 **6회** import 했다.
이 2개를 옮기는 계획을 세웠다가 사용자가 잡아냈다.

**고정 파일 처리**

- 원래 위치에 그대로 둔다 (`lib/orval-fetcher.ts`)
- 계획서 `beforeAfter.before` 에는 넣되 **`moveTo` 를 생략**한다 (제자리 표시)
- `layers` 에는 넣지 않는다 (이동·생성·수정 대상이 아니므로)
- 그 파일을 가리키는 **tsconfig 별칭도 유지**한다 (`@/lib/*` 를 지우면 안 된다)
- md 에 「이동하지 않는 파일」 표로 이유와 함께 남긴다

**작업 트리가 생성 코드 때문에 dirty 하면** 3-0 의 "깨끗해야 한다" 를 만족시킬 수 없다.
stash 하지 말고 그대로 두되, **커밋에 경로를 명시**해서 섞이지 않게 한다:
`git commit -- src lib app tsconfig.json`

#### 1-1. 파일 전수 조사
- src/ 하위 모든 파일 목록 확인
- 각 파일의 줄 수 측정 (wc -l)
- 각 파일의 import문 분석

#### 1-2. 문제점 탐지 (issue 목록 생성)

각 파일에 대해 아래 7가지 카테고리를 검사하고 발견된 issue마다 심각도(critical/warning/info)를 매긴다:

| 카테고리 | 검사 내용 | 심각도 기준 |
|---------|----------|------------|
| **거대 파일** | 150줄 초과 컴포넌트 | 300줄+ critical, 150줄+ warning |
| **깊은 중첩** | 3단계 이상 폴더 중첩 (components/common/ui/Button/) | 4단계+ critical, 3단계 warning |
| **로직/UI 혼재** | 컴포넌트에서 fetch/API 직접 호출, 상태관리 + 렌더링 혼재 | API 호출 있으면 critical |
| **중복 코드** | 유사한 함수/컴포넌트가 여러 곳에 존재 | 동일 로직 2곳+ warning |
| **타입 분산** | types/가 별도 폴더, 또는 타입이 여러 파일에 흩어짐 | 별도 폴더면 warning |
| **플랫 구조** | components/에 10개+ 파일이 역할 구분 없이 나열 | 15개+ critical, 10개+ warning |
| **순환 의존** | A→B→A 형태의 순환 import | 발견 시 critical |

#### 1-3. 레이어 판정 — **파일명이 아니라 파일 내부 코드를 읽는다**

`Button`/`Form`/`Table` 같은 이름으로 레이어를 정하지 않는다.
2026-07-27 client-brics-works(963파일)에서 이름 기반 분류의 실측 정확도는 **73%** 였다.
`*Content.tsx` `*Card.tsx` `*Header.tsx` 처럼 중립적 이름을 쓰면서 실제로는 변경 API를
호출하는 컴포넌트가 많았고, 최종적으로 **171개**의 레이어가 이름 기반 배정과 달랐다
(widgets→features 72 · features→widgets 96 · →shared 3).

```bash
python3 scripts/classify-layers.py <프로젝트경로> \
  --src app --src src --src lib \
  --generated __generated__ \
  --json /tmp/layers.json
```

이 도구는 **확실한 것만 판정하고 애매한 것은 목록으로 내놓는다.** 추측하지 않는다.

**판정 기준 (코드가 무엇을 하는지)**

| 판정 | 근거 |
|------|------|
| **features** | 변경 API 호출(직접 또는 자기 훅·lib 경유) · `useForm` 폼 소유 또는 자기 슬라이스 폼의 필드 · 공유·URL 상태 쓰기 · 다운로드/업로드처럼 부수효과 실행이 컴포넌트의 목적 |
| **widgets** | 조회 훅·props 로 받아 표시·조합 · 로컬 표현 상태(아코디언·모달 열림·입력 초안)만 · 실제 동작은 부모 콜백이나 자식 feature 에 위임 |
| **entities** | 도메인 타입 · API 호출 함수 · 서버 상태 훅 (UI 없음) |
| **shared** | 같은 레이어의 **2개 이상 슬라이스**가 사용 · 범용 UI/유틸 |
| **app** | 라우팅 파일만 (`page` `layout` `route` `error` `not-found`) |

**애매 목록은 전부 읽어서 판정한다.** 도구 출력의 `ambiguous` 를 건너뛰면 안 된다.
확인할 것은 하나다 — **이 컴포넌트가 유즈케이스를 소유하는가, 아니면 남에게 위임하는가.**

- 핸들러 본문이 부모 콜백(`onChangeXxx(...)`)만 부르면 → widgets
- 핸들러 본문이 변경 API/`fetcher({method:'POST'})`/외부 변경 함수를 부르면 → features
- 간접 변경은 **변경이 어디서 오는가**로 가른다:
  자기 훅·lib 경유 → features / 자식 컴포넌트만 변경 → 조합이므로 widgets

**실제로 틀렸던 것들 (같은 실수를 반복하지 않기 위해)**

| 함정 | 사례 |
|------|------|
| 훅만 보고 **명령형 호출**을 놓침 | `await dealControllerUpdateWorkerDetails(...)` — `use` 접두사가 없다 |
| mutator 직접 호출을 놓침 | `await fetcher({ url, method: 'POST' })` |
| mutator 를 무조건 변경으로 오판 | `fetcher({ method: 'GET' })` 는 조회다. **`method` 를 봐야 한다** |
| 동사 목록을 추측 | `Apply` `Collect` `Upsert` 를 조회로 오판했다. 생성 코드 동사를 **전수 추출**해 읽기 동사만 화이트리스트로 둔다 |
| 정규식 경계 | `^(Get)\b` 는 `GetAddFoo` 에서 매칭되지 않는다 |
| 순환 의존 구간에서 재귀+메모 | 부분 결과를 캐시해 "변경 없음" 을 잘못 내놓는다. **고정점 반복**을 쓴다 |
| 이름 grep 으로 사용처 판단 | 동명 파일 2개를 혼동했다. **해석된 import** 로 봐야 한다 |
| 외부 패키지 변경 함수 | `updateResource(...)` 처럼 생성 API가 아닌 변경도 있다 |

#### 1-4. 같은 레이어 교차 import 검사 (필수)

FSD는 같은 레이어 간 import 를 금지한다. **같은 레이어의 2개 이상 슬라이스가 쓰는 파일은
`shared` 로 내린다.** 이걸 빠뜨리면 구조가 성립하지 않는다.

```bash
# 경로→슬라이스 매핑을 만든 뒤
python3 scripts/classify-layers.py <프로젝트경로> --slices /tmp/slices.json --json /tmp/layers.json
```

브릭스 사례: `EditableTableCell.tsx` 를 inspection **7개 슬라이스**가 쓰는데 그 7개가 모두
`features` 로 판정됐다. features 안에 두면 features → features 교차 import 가 되어
`lint-fsd` 가 7건 전부 위반으로 잡는다. 이런 파일이 **17개** 나왔다.

#### 1-5. 슬라이스 도메인 그룹 (슬라이스가 20개 넘으면)

`features/admin-functions/` `features/admin-role-detail/` 처럼 평평하게 나열하면
슬라이스 수십 개를 훑기 어렵다. 도메인이 같은 것은 그룹 폴더로 묶는다.

```
features/admin/functions/     ← features/admin-functions/
features/admin/role-detail/   ← features/admin-role-detail/
features/deal/inspection-*/   ← features/deal-inspection-*/
```

**그룹 폴더는 `index.ts` 를 갖지 않는다.** `features/admin/index.ts` 를 만들면 그룹이
슬라이스가 되어 "슬라이스 안의 슬라이스" 가 된다. FSD 에서 public API 는 항상 슬라이스에만 둔다.

| | 위치 |
|---|---|
| ✅ 슬라이스 public API | `features/admin/functions/index.ts` |
| ❌ 그룹 폴더 public API | `features/admin/index.ts` |

적용 조건 (하나라도 어기면 평평하게 둔다):

- 같은 도메인 접두사를 쓰는 슬라이스가 **2개 이상**
- 그룹 이름과 **똑같은 슬라이스가 없다** (있으면 슬라이스와 그룹이 충돌한다)

**그룹 이름은 명시적으로 정한다.** 기계적으로 첫 하이픈 토큰을 쓰면
`send-message` / `send-message-history` 가 `send/` 로 묶여 동사가 도메인이 되어버린다.

트레이드오프: 경로가 한 단계 깊어진다. `index.tsx` 전용 폴더 붕괴(1-6)와 함께 적용하면
깊이 증가를 상쇄할 수 있다.

#### 1-6. 과분할 병합 — **형제 묶기를 부모 흡수보다 먼저**

작은 파일이 많으면 합친다. 순서가 중요하다.

| 순서 | 규칙 | 비고 |
|------|------|------|
| A | `style.ts` 를 짝 컴포넌트 파일로 흡수 | 짝 외에 쓰는 곳이 있으면 건드리지 않는다 |
| **B2** | **형제 묶기** — 같은 폴더 + 같은 부모 하나만 쓰는 + 이름 단어 접두사를 공유하는 형제를 한 파일로 | **B 보다 먼저** |
| B | 부모가 1곳뿐이고 작은(≈40줄 이하) 컴포넌트를 부모로 흡수 | 남은 것만 |

**왜 B2 가 먼저인가.** 부모 흡수는 부모 크기에 좌우된다. 브릭스에서 `Address1`(25줄)만
`AddressSelect` 에 흡수되고 `Address2`(45) · `Address3`(75) 는 크기 조건에 걸려 남았다 —
같은 패턴 3형제 중 하나만 합쳐지는 비대칭이 생겼다. 형제 묶기는 그 우연을 없앤다.

**공통 접두사는 CamelCase 단어 경계에서만 인정한다.** 문자 단위로 자르면
`EmployeeDetailCard` + `EmploymentInsuranceCard` 가 `Employ` 로 묶인다 — 관심사가 다른데
앞글자만 같은 경우다 (실제로 그렇게 잘못 묶였다).

**공통 가드**

- 병합 결과가 **150줄을 넘기면 하지 않는다** (거대 파일을 새로 만들지 않는다)
- import 하는 곳이 **2곳 이상이면 건드리지 않는다** — 공유 컴포넌트다
  (`Common/Spacing.tsx` 는 10줄인데 34곳이 쓴다)
- **병합은 `git mv` 가 아니라 내용 편집이다.** 그 파일들은 이력 보존이 깨진다.
  테스트가 빈약하면 이게 가장 큰 위험이므로 계획서에 명시하고, 완료 후
  원본 줄수 합계와 병합 결과를 대조한다

**분리에 기술적 이유가 있는지 먼저 확인한다.** `AddressSelect` 의 3분할은 임의 분해가
아니었다 — 단계마다 다른 조회 훅을 쓰고 그 훅이 상위 값을 인자로 요구하는데 훅은 조건부
호출이 안 되므로, 래퍼가 분기하고 `RealXxx` 가 실제 훅을 부르는 **훅 가드 패턴**이었다.
한 파일로 모으는 것은 안전하지만 **한 컴포넌트로 합치려면 조건부 fetch 리팩토링**이 필요하다.

### 2단계: HTML 마이그레이션 계획서 생성

`plans/migrate/YYYYMMDD-제목.md` + `.html` 쌍으로 작성한다.
**html 은 반드시 빌더로 생성한다** — 스키마와 이유는 `docs/plan-template.md` 참고.

PLAN JSON 은 `/tmp` 가 아니라 **계획서 옆에** 둔다. `/tmp` 에 두면 세션이 끝난 뒤
html 을 다시 빌드할 방법이 사라진다 (`plans/migrate/20260726-legacy-shop.html` 이
실제로 그 상태다 — 렌더러가 바뀌어도 갱신이 불가능하다).

```bash
python3 scripts/build-plan-html.py plans/migrate/YYYYMMDD-제목.md \
  --data plans/migrate/YYYYMMDD-제목.plan.json
```

따라서 계획서는 **3개 파일 한 세트**다: `.md` (본문) · `.plan.json` (PLAN 데이터) ·
`.html` (빌더 산출물). 셋 중 하나만 고치지 않는다.

md 섹션 제목을 유지하면 렌더러가 아래 시각화를 자동으로 붙인다:

| md 섹션 | PLAN 필드 | 시각화 |
|---------|-----------|--------|
| `## 문제 분석` | `issues` | severity 카드 + 상단 요약 카운트 |
| `## 3. FSD 레이어 배치` | `beforeAfter.before` + `layers` | **2컬럼 비교 뷰** — 왼쪽 현재 구조, 오른쪽 FSD 구조. 왼쪽 파일 클릭 → 오른쪽에서 목적지 하이라이트 |
| `## 4. 작업 순서` | `steps` | Phase별 타임라인 |

**`## 구조 비교` 섹션을 따로 만들지 않는다.** `beforeAfter.before` 가 있으면 렌더러가
`## 3. FSD 레이어 배치` 를 2컬럼 비교 뷰로 바꾼다 (플로우 바는 폭 때문에 생략된다).
섹션을 둘로 나누면 같은 FSD 트리를 두 번 그리게 된다. 남아 있으면 렌더러가 걷어낸다.

마이그레이션 특유의 데이터:
- `issues[]` — 1-2 에서 찾은 문제. `severity` 는 `critical`/`warning`/`info`
- `beforeAfter.before[]` — `{ path, lines, issue: true, moveTo }` 형태.
  **마이그레이션 전 파일을 전수로 넣는다** (일부만 넣으면 현재 구조 스냅샷이 안 된다)
  - `moveTo` 는 **정확한 목적지 파일 경로**다. `'widgets'` 나 `'widgets/meal-card 로 분리'`
    같은 설명 문구를 쓰면 클릭해도 하이라이트가 안 된다 (조용히 실패)
  - 거대 파일이 여러 곳으로 쪼개지면 **배열**로 전부 나열한다 → 목적지가 동시에 하이라이트된다
  - 그대로 남는 파일은 `moveTo` 생략 — 라우팅 파일과 **1-0 의 고정 파일**이 여기 해당한다
  - **병합되어 사라지는 파일은 `merge: true`** 를 함께 넣고 `moveTo` 에 흡수 대상 파일을 적는다.
    이게 없으면 화면에서 단순 이동과 구분되지 않는다 (실제로 133개가 그렇게 묻혔다).
    렌더러가 보라색 취소선 + `병합·삭제` 배지로 그린다
  - 오른쪽 패널은 `layers` 로 그려지므로 `moveTo` 는 `layers[].files[].path` 에
    **반드시 존재해야 한다.** 빌더가 검사해서 안 맞으면 빌드를 거부한다
- `layers[].files[].type` 에 `MOVE` 를 쓴다 (신규 생성이 아닌 이동).
  `path` 는 **한 항목 = 한 파일**. 중괄호 글롭(`{a,b}.tsx`), 공백으로 이어붙인 여러 경로,
  `/` 로 끝나는 폴더 경로는 빌더가 거부한다 (트리가 안 쪼개지고 `moveTo` 매칭도 깨진다).
  폴더 단위 삭제는 md 본문에 글로 적는다
- `decisions` — Phase 분할 범위, 한 번에 갈지 점진적으로 갈지 등

**계획서 수치는 세 가지가 다르다.** 혼동하지 말고 md 에 분리해서 적는다:

| 수치 | 뜻 |
|------|-----|
| 원본 파일 수 | 마이그레이션 전 파일 (`before` 길이) |
| 이동 파일 수 | 원본 − 병합소멸 − 제자리 |
| `layers` 항목 수 | 이동 + **신규 `index.ts`** + 유지·수정(app + tsconfig) |

`layers` 수는 원본 수에서 뺄셈으로 나오지 않는다. 신규 `index.ts` 가 수십~백 개 더해지고
고정 파일은 빠지기 때문이다. 사용자가 반드시 물어본다 — md 에 먼저 풀어서 적어둔다.

### 3단계: 사용자 승인 후 Phase별 실행

마이그레이션은 되돌리기 어려운 대규모 파일 이동이다. 아래 순서를 지킨다.

#### 3-0. 시작 전 (한 번)

```bash
cd __PROJECT_PATH__
git status --short                      # 작업 트리가 깨끗해야 한다
npm run build                           # 기준선 확보 — 실패하면 먼저 고친다
npm test 2>/dev/null || echo "테스트 없음"
git switch -c fsd-migration             # 전용 브랜치
```

- 작업 트리가 더럽거나 빌드가 깨진 상태로 시작하지 않는다
- 테스트가 없으면 **회귀를 검증할 수단이 없다는 것을 사용자에게 먼저 알린다**
- 경로 별칭(`@/*`)이 `tsconfig.json` 에 없으면 먼저 추가한다 (이게 없으면 import 정리가 불가능)

#### 3-1. Phase 순서

의존성 방향의 **역순이 아니라 정순**으로 간다. 하위 레이어가 먼저 자리를 잡아야
상위 레이어가 그걸 가리킬 수 있다.

1. `shared` — 범용 UI/유틸 이동
2. `entities` — 타입 + API 이동, 흩어진 `types/` 통합
3. `features` — 비즈니스 로직/인터랙션 UI 이동, 거대 파일 분리
4. `widgets` — 페이지 섹션 조합
5. `app` — 라우팅만 남기고 나머지 비우기

#### 3-2. 각 Phase 내부 절차

```
파일 이동(git mv) → 슬라이스 index.ts 생성 → import 경로 수정 → 빌드 → 커밋 제안
```

- **`git mv` 를 쓴다.** 복사 후 삭제하면 이력이 끊긴다
- 이동한 슬라이스마다 `index.ts` 를 **즉시** 만든다. 나중에 몰아서 하지 않는다
- import 경로는 이동한 파일을 **참조하는 쪽 전부**를 찾아 고친다:
  `grep -rn "이전/경로" src/`
- Phase 끝마다 `npm run build` + `npm run lint:fsd` (없으면 `npx tsx scripts/lint-fsd.ts src`)
- 빌드가 깨진 상태로 다음 Phase 로 넘어가지 않는다
- Phase 완료 시 커밋을 제안한다 (사용자가 결정). Phase 단위 커밋이면 되돌리기가 쉽다

#### 3-3. 순환 의존 해소

`critical` 로 표시된 순환 의존은 파일 이동만으로 풀리지 않는다.
해당 Phase 에서 먼저 처리한다:

- 공통으로 쓰는 부분을 **하위 레이어로 추출** (대개 entities 타입 또는 shared 유틸)
- 한쪽 방향을 역전시킬 수 없으면, 상위 레이어에서 두 슬라이스를 조합하는 형태로 바꾼다

#### 3-4. 거대 파일 분리

`issues` 에서 찾은 150줄+ 파일은 이동과 **동시에** 분리한다.
이동만 하고 나중에 분리하면 FSD 구조에 거대 파일이 그대로 남는다.

- 데이터 fetching → `entities/*/api`
- 상태·유효성 검사 → `features/*/model`
- 렌더링 → `features/*/ui` 또는 `widgets/*/ui`

#### 3-5. 완료 보고

- Phase별 이동 파일 수 / 생성한 index.ts / 수정한 import 수
- 각 Phase 의 빌드·린트 결과 (실제 출력 기준)
- 남은 위반과 그 이유
- `/review-fsd` 로 최종 검수 안내
