---
title: "[Trend] 2026-05-08: 컨텍스트 엔지니어링, MCP REPL 평가와 스펙 기반 복원력"
pubDatetime: 2026-05-08T00:00:00Z
description: "100줄 이하 CLAUDE.md와 brief-fetch 훅, Metabase MCP REPL 테스트, Zed Rust 오류 전파 규율, 스펙 주도 개발 및 B2G·퀀트 파이프라인 사례를 분석합니다."
category: trend
tags:
  - trend
  - ai-agent
  - claude-md
  - mcp
  - fastapi
draft: false
---

2026년 5월 8일 수집 데이터에서는 "프롬프트 문구 다듬기보다 컨텍스트 윈도우 큐레이션이 중요하다"는 원칙 아래 `CLAUDE.md`를 100줄 이내로 압축하고 MCP 훅과 REPL 평가 도구로 실행 정확도를 끌어올리는 패턴이 두드러집니다. 도메인 백엔드 측에서는 스펙 기반 점진 개발(SDD), 기동 시 중단 작업 자동 복구, 그리고 목업 대시보드의 실데이터 전환 부채 추적 사례가 확인되었습니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 컨텍스트 엔지니어링과 언어·런타임 특화 에이전트 워크플로우 | `wagnerra23/oimpresso.com`, `metabase/metabase`, `Superoldman96/zed` | 100줄 이하 `CLAUDE.md`+`brief-fetch` 훅과 GUI 비대화형 제약 명시, `clojure-eval` MCP REPL 평가, Rust `unwrap()`/`let _ =` 금지를 적용함 |
| 스펙 기반 점진적 개발과 도메인 파이프라인 복원력 | `rledesma912/automated_narrative`, `psilhon/TradingAgents-CN`, `tjsasakifln/SmartLic` | `SPECIFY->PLAN->TASKS->IMPLEMENT` 승인 게이트와 기동 시 작업 복구, OpenSpec 부채 추적, B2G 다중 소스 중복 제거 및 LLM 중재기를 구현함 |

---

## 2. 컨텍스트 엔지니어링과 언어·런타임 특화 에이전트 워크플로우

### 2.1 100줄 프라이머, `@memory` 임포트와 데스크톱 GUI 실행 제약 (`wagnerra23/oimpresso.com`)

- **출처**: [`wagnerra23/oimpresso.com`](https://github.com/wagnerra23/oimpresso.com) · **핵심 스택**: `TypeScript`, `React`, `MCP (brief-fetch)`, `ADR`, `CLAUDE.md` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`를 100줄 이하 프라이머로 유지하면서 `@memory/why-oimpresso.md` 같은 재귀적 임포트를 두고, `SessionStart` 훅으로 `mcp__oimpresso__brief-fetch`를 호출해 핵심 컨텍스트를 적재하며 `.tsx` 수정 전 인접 `.charter.md`를 읽도록 강제합니다. 특히 에이전트가 데스크톱 GUI 환경에서 동작해 표준 입력(`stdin`)이 없으므로 암호 입력이 필요한 SSH, `git rebase -i`, `gh auth login`은 실패하고 인증된 `gh` CLI만 동작한다는 실행 제약을 명시했습니다. 함께 포함된 `HOW_TO_ASK_CLAUDE.md`는 ADR과 정확한 `file:line`을 큐레이션하는 컨텍스트 엔지니어링 원칙을 정리합니다.

**실무 적용 해설**: 장황한 `CLAUDE.md`는 모델의 주의를 분산시키고, GUI 기반 에이전트 런타임에서 `git rebase -i` 같은 대화형 명령을 실행하면 프로세스가 무한 대기(Hang) 상태에 빠집니다. 기존(AS-IS)의 정적 대형 문서 대신 100줄 상한 프라이머 + `SessionStart` MCP 브리프 주입 + `stdin` 불가 명령 명시적 배제(TO-BE)를 적용하면 에이전트 세션 초기화 속도와 명령 성공률을 크게 개선할 수 있습니다. 다만 `brief-fetch` MCP 서버 의존성이 추가되므로 해당 서버 장애 시 최소한의 로컬 폴백 컨텍스트 경로를 함께 확보해야 합니다.

---

### 2.2 언어별 스킬 분리와 MCP REPL 기반 Clojure 평가 (`metabase/metabase`)

- **출처**: [`metabase/metabase`](https://github.com/metabase/metabase) · **핵심 스택**: `Clojure`, `ClojureScript`, `clojure-mcp`, `React 18`, `TypeScript`, `Mantine v8`, `Rspack` · **적용 판단**: `Trial`
- **기술 개요**: 대규모 분석 플랫폼 Metabase의 `CLAUDE.md`는 Clojure와 TypeScript 작업 규범을 `.claude/skills/` 하위 스킬(`clojure-eval`, `clojure-write`, `clojure-review`, `typescript-write`, `typescript-review`)로 분리합니다. 특히 Clojure 코드 검증과 테스트 실행 시 셸 명령 대신 `clojure-eval` MCP 도구나 `clj-nrepl-eval`을 우선 사용하도록 규정하며, `frontend/CLAUDE.md`에서는 Emotion `styled-components`를 폐기하고 `metabase/ui`(Mantine v8) 및 CSS Modules, Rspack 빌드로 마이그레이션하는 프론트엔드 표준을 명시합니다.

**실무 적용 해설**: Clojure처럼 JVM 기동 비용이 큰 언어에서 에이전트가 매 테스트마다 셸로 새 프로세스를 띄우면 단일 피드백 루프에 수십 초에서 수 분이 낭비됩니다. 기존(AS-IS)의 콜드 스타트 셸 테스트를 상주 nREPL에 연결된 `clojure-eval` MCP 평가 루프(TO-BE)로 대체하면 컴파일·단위 테스트 피드백을 즉각적으로 받을 수 있습니다. 또한 프론트엔드 하위 `CLAUDE.md`에서 레거시 스타일링(`styled-components`) 제안을 명시적으로 금지해 디자인 시스템 전환 중 역행 코드가 섞이는 것을 막습니다. 단, 상태가 유지되는 REPL 특성상 네임스페이스 오염을 피하기 위해 주기적인 클린 리로드 규율이 필요합니다.

---

### 2.3 `unwrap()`·무음 에러 폐기를 금지하는 Rust 규약 (`Superoldman96/zed`)

- **출처**: [`Superoldman96/zed`](https://github.com/Superoldman96/zed) · **핵심 스택**: `Rust`, `Python`, `Typer`, `PyTZ` · **적용 판단**: `Assess`
- **기술 개요**: Zed 에디터 포크 저장소의 `CLAUDE.md`는 성급한 최적화보다 코드 정확성과 명료성을 우선시하며, 패닉을 유발하는 `unwrap()`이나 실패 가능한 연산의 결과를 조용히 버리는 `let _ =` 사용을 전면 금지합니다. 대신 호출부로 전파하는 `?`, 가시성을 남기는 `.log_err()`, 또는 명시적 `match`/`if let` 분기를 강제하고, 코드 요약용 주석("what") 대신 비직관적인 이유("why")만 주석으로 남기며 과도한 소형 파일 분할을 지양하도록 지시합니다.

**실무 적용 해설**: LLM 코딩 에이전트는 Rust 코드를 작성할 때 컴파일러의 타입·소유권 요구를 빠르게 통과하려고 `unwrap()`이나 `let _ =`로 오류 처리를 생략하는 습관이 있어 프로덕션 패닉의 원인이 됩니다. `CLAUDE.md`에 패닉 유발 API 및 무음 에러 폐기 금지 규칙과 "why" 중심 주석 원칙을 못 박으면(TO-BE) 에이전트가 생성하는 시스템 코드의 런타임 안정성이 눈에 띄게 높아집니다. 물론 모든 오류 경로를 `?`나 `match`로 풀어내야 하므로 함수 시그니처와 에러 타입 변환 코드가 다소 길어지는 트레이드오프가 따릅니다.

---

## 3. 스펙 기반 점진적 개발과 도메인 파이프라인 복원력

### 3.1 4단계 승인 게이트 SDD와 기동 시 미완료 작업 복구 (`rledesma912/automated_narrative`)

- **출처**: [`rledesma912/automated_narrative`](https://github.com/rledesma912/automated_narrative) · **핵심 스택**: `Python`, `FastAPI`, `SQLite`, `Express`, `Ruff`, `Pytest` · **적용 판단**: `Trial`
- **기술 개요**: 서사 생성 플랫폼 백엔드(`src/main.py`)는 `SPECIFY -> PLAN -> TASKS -> IMPLEMENT` 4단계 스펙 주도 개발(SDD)과 단계별 사용자 승인 게이트를 `CLAUDE.md`로 강제하며, 초기 반복 속도를 높이기 위해 DB 마이그레이션 스크립트 없이 `init_db()`로 `data/stories.db`를 재생성합니다. 동시에 `FastAPI` `lifespan` 기동 시 `SQLStoryRepository().recover_processing_stories()`를 실행해 서버 재시작 중 중단된 `processing` 상태 작업을 자동 복구합니다.

**실무 적용 해설**: 비동기 생성 작업을 처리하는 FastAPI 서버가 배포나 장애로 재시작되면 진행 중이던 레코드가 영원히 `processing` 상태에 고립되는 좀비 작업 문제가 발생합니다. 초기 프로토타입 단계에서 마이그레이션 오버헤드는 덜어내되 `lifespan` 기동 훅에 상태 복구(`recover_processing_stories()`)를 심어두고 SDD 승인 게이트로 점진적 슬라이스를 검증하는 구성(TO-BE)은 개발 민첩성과 상태 일관성을 균형 있게 챙긴 선택입니다. 단, 스키마 변경 시 DB를 재생성하는 방식은 실제 사용자 데이터가 쌓이기 전 프리알파 단계까지만 유효하며 이후에는 Alembic 등 정식 마이그레이션으로 전환해야 합니다.

---

### 3.2 OpenSpec 기반 목업 패널 실데이터 전환과 기술 부채 추적 (`psilhon/TradingAgents-CN`)

- **출처**: [`psilhon/TradingAgents-CN`](https://github.com/psilhon/TradingAgents-CN) · **핵심 스택**: `Python`, `FastAPI`, `SSE`, `Vue 3`, `LangGraph` · **적용 판단**: `Assess`
- **기술 개요**: `hsliuping/TradingAgents-CN`의 다운스트림 포크(`v1.2.1`)로, FastAPI + SSE 백엔드와 Vue 3 + LangGraph 다중 에이전트 주식 분석 시스템을 구현합니다. `CLAUDE.md`는 누적 33건의 OpenSpec 아카이브를 통해 대시보드 시뮬레이션 계좌의 9개 목업(Mock) 패널을 TWRR·Sharpe·낙폭·Beta/VaR·가중 PE/PB 등 실데이터 파이프라인으로 전환한 이력을 기록하고, 아직 남은 캐시 계층·역방향 임포트·에이전트 상태 관련 후속 부채를 `docs/code-review-2026-05-05.md`에 명시적으로 추적합니다.

**실무 적용 해설**: AI 에이전트가 대시보드 UI를 빠르게 만들 때 백엔드 집계 로직 대신 하드코딩된 목업 데이터를 연결한 채 작업을 마치는 경우가 많습니다. OpenSpec 변경 이력으로 어떤 목업 패널이 실제 지표 계산과 연결되었는지 추적하고, 미해결 아키텍처 부채(역방향 임포트, 캐시 누락)를 리뷰 문서와 `CLAUDE.md`에 투명하게 남긴 방식(TO-BE)은 점진적 프로덕션 전환에 유용한 관리 패턴입니다. 다만 다중 벤치마크나 몬테카를로 VaR 같은 고급 정량 지표가 후속 과제로 남아 있어 금융 분석 정확도 검증이 별도로 요구됩니다.

---

### 3.3 B2G 조달 다중 소스 중복 제거와 4요소 타당성 스코어링 (`tjsasakifln/SmartLic`)

- **출처**: [`tjsasakifln/SmartLic`](https://github.com/tjsasakifln/SmartLic) · **핵심 스택**: `Synkra AIOS`, `GPT-4.1-nano`, `Supabase`, `Stripe`, `Gemini` · **적용 판단**: `Assess`
- **기술 개요**: 프레임워크 계층(`.claude/CLAUDE.md`)의 Synkra AIOS 역할 페르소나(`@dev`, `@qa`, `@architect`)·스토리 기반 개발(`docs/stories/`)과 제품 계층(`CLAUDE.md`)의 도메인 규칙을 결합한 B2G 공공조달 인텔리전스 SaaS입니다. 핵심 파이프라인은 PNCP·PCP v2·ComprasGov v3 공고를 중복 제거해 통합한 뒤, 키워드 매칭에서 누락되는 건을 `GPT-4.1-nano` LLM 중재기(Arbiter)로 분류하고 4요소 타당성 점수(`modalidade` 30%, `timeline` 25%, `valor` 25% 등)를 산출합니다.

**실무 적용 해설**: 여러 공공 조달 포털의 데이터를 수집할 때 단순 키워드 필터만 쓰면 동의어·약어로 표기된 핵심 입찰 공고를 놓치고, 반대로 모든 공고에 대형 LLM을 돌리면 비용이 감당되지 않습니다. 기존(AS-IS)의 단일 키워드 검색을 다중 소스 정규화·중복 제거 + 경량 모델(`GPT-4.1-nano`) 기반 0건 매칭 보완 중재기 + 가중치 스코어링(TO-BE)으로 설계하면 리콜(Recall)과 API 단가를 동시에 잡을 수 있습니다. 다만 모호한 입찰 공고 문구에서 경량 중재기 모델의 오분류 가능성과 지연 시간을 모니터링해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `CLAUDE.md`가 비대화되었다면 100줄 이내 프라이머와 `@memory`·MCP 브리프 로딩으로 분리하고, 에이전트가 GUI/비대화형 환경에서 실행될 때 금지할 `stdin` 의존 명령을 명시합니다.
  - JVM·대형 빌드 생태계(Clojure 등)에서 셸 기반 반복 테스트 대신 MCP REPL 평가 도구를 연결해 피드백 주기를 단축할 수 있는지 검토합니다.
  - 비동기 작업 큐나 상태 머신을 운영하는 백엔드의 `lifespan` 기동 훅에 비정상 종료로 멈춘 `processing` 레코드 복구 루틴이 포함되어 있는지 확인합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-05-08 수집 시점의 공개 저장소 `CLAUDE.md`, 프레임워크 규칙, 엔트리포인트 발췌본에 근거하며, LLM 중재기 분류 정확도 및 실거래 지표 산출 검증은 별도 평가가 필요합니다.
