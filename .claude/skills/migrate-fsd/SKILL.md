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

#### 1-3. 파일 역할 분류
각 파일을 FSD 레이어로 분류:
- 데이터 타입 정의 → entities
- API 호출 함수 → entities
- 서버 상태 훅 (React Query 등) → entities
- 비즈니스 로직/인터랙션 훅 → features
- 인터랙션 UI (폼, 검색바) → features
- 페이지 섹션/조합 컴포넌트 → widgets
- 범용 UI (Button, Modal) → shared
- 범용 유틸 (formatDate) → shared
- 라우팅 파일 → app

### 2단계: HTML 마이그레이션 계획서 생성

`plans/migrate/YYYYMMDD-제목.md` + `.html` 쌍으로 작성한다.
**html 은 반드시 빌더로 생성한다** — 스키마와 이유는 `docs/plan-template.md` 참고.

```bash
python3 scripts/build-plan-html.py plans/migrate/YYYYMMDD-제목.md --data /tmp/plan.json
```

md 섹션 제목을 유지하면 렌더러가 아래 시각화를 자동으로 붙인다:

| md 섹션 | PLAN 필드 | 시각화 |
|---------|-----------|--------|
| `## 문제 분석` | `issues` | severity 카드 + 상단 요약 카운트 |
| `## 구조 비교` | `beforeAfter` | Before/After 2컬럼 (문제 파일 🔴, 이동 경로 →) |
| `## 3. FSD 레이어 배치` | `layers` | 플로우 바 + 파일트리 (MOVE/CREATE/MODIFY 태그) |
| `## 4. 작업 순서` | `steps` | Phase별 타임라인 |

마이그레이션 특유의 데이터:
- `issues[]` — 1-2 에서 찾은 문제. `severity` 는 `critical`/`warning`/`info`
- `beforeAfter.before[]` — `{ path, issue: true, movesTo: '이동 대상' }` 형태로 적으면
  문제 파일에 빨간 점과 이동 경로가 함께 표시된다
- `layers[].files[].type` 에 `MOVE` 를 쓴다 (신규 생성이 아닌 이동)
- `decisions` — Phase 분할 범위, 한 번에 갈지 점진적으로 갈지 등

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
