# 작업계획서 템플릿

파일명: `plans/유형/YYYYMMDD-제목.md`

## md + html 동시 생성 (필수)

작업계획서를 만들 때는 **같은 이름의 .html도 함께 생성**한다.
- `plans/유형/YYYYMMDD-제목.md` + `.html`
- HTML은 `docs/plan-template.html` 복사 후 두 블록만 채움:
  - [A] `PLAN` 객체: title, decisions[]
  - [B] `plan-md`: md 본문 그대로 붙여넣기
- md 수정 시 html도 같은 턴에 갱신 (둘 중 하나만 수정 금지)

---

## 템플릿

```markdown
# [제목]

## 1. 개요
- 작업 유형: feature / bugfix / refactor
- 요청 사항: (사용자 요청 요약)
- 사용자 결정 사항:
  - 결정 항목 1: **선택값** (옵션 나열)
  - 결정 항목 2: **선택값**

## 2. 현재 상태 분석
- 관련 기존 코드 (파일 경로)
- 프로젝트 구조 현황

## 3. FSD 레이어 배치

| 파일 경로 | 레이어 | 작업 유형 | 설명 |
|-----------|--------|----------|------|
| src/entities/review/model/types.ts | entities | CREATE | Review 타입 정의 |
| ... | ... | ... | ... |

## 4. 작업 순서
1. shared (해당 시)
2. entities
3. features
4. widgets
5. app

## 5. FSD 검증 체크리스트
- [ ] 단방향 의존성 준수
- [ ] 같은 레이어 교차 import 없음
- [ ] app에 로직/스타일 없음
- [ ] entities에 UI 없음
- [ ] 각 슬라이스 index.ts 존재
- [ ] 화살표 함수 사용

## 6. 작업 배분

| 담당 | 작업 내용 | 의존성 |
|------|----------|--------|
| Coder | entities 생성 | 없음 |
| Coder | features 생성 | entities 완료 후 |
| Coder | widgets 생성 | features 완료 후 |
| Coder | app 페이지 생성 | widgets 완료 후 |
| Reviewer | FSD 검수 | 전체 완료 후 |
```
