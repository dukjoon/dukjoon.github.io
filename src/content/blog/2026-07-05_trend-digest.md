---
title: '[Trend] 2026-07-05: TypeScript, Claude Code 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-07-05T00:00:00Z'
description: 2026-07-05 수집된 elizaOS/eliza, LukeMathWalker/openfirma, Growthub-ai/growthub-local 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- typescript
- claude-md
- supabase
- stripe
draft: false
---

2026-07-05 수집된 오픈소스 저장소들에서는 TypeScript, Claude Code, Supabase, Stripe 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `elizaOS/eliza`, `LukeMathWalker/openfirma`, `Growthub-ai/growthub-local`, `mertoege/invest-pi` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, MCP 도구 스키마 분리 및 런타임 세션 격리, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리 | `hitechpanda-dangnamhai/sicp`, `mmiura-2351/mc-server-dashboard-v2` | FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 TypeScript 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`elizaOS/eliza`)

- **출처**: [`elizaOS/eliza`](https://github.com/elizaOS/eliza) · **핵심 스택**: `TypeScript`, `Claude Code`, `Supabase`, `Stripe`, `LangGraph`, `CrewAI` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `packages/agent/CLAUDE.md` 발췌본을 기반으로 확인되는 `elizaOS/eliza` 저장소는 TypeScript, Claude Code, Supabase 스택 위에서 TypeScript 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`elizaOS — repository guide for agents`, `Naming`, `Toolchain`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `elizaOS/eliza`(TO-BE)에서는 `CLAUDE.md`, `packages/agent/CLAUDE.md` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 Python 기반 `cargo test` 워크플로우 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`LukeMathWalker/openfirma`)

- **출처**: [`LukeMathWalker/openfirma`](https://github.com/LukeMathWalker/openfirma) · **핵심 스택**: `Python`, `Rust`, `Claude Code`, `Supabase`, `Stripe`, `PostgreSQL` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `examples/agents/agents_sdk_py/agent/main.py` 발췌본을 기반으로 확인되는 `LukeMathWalker/openfirma` 저장소는 Python, Rust, Claude Code 스택 위에서 Python 기반 `cargo test` 워크플로우 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. `CLAUDE.md` 등에 명시된 실행·검증 명령(`cargo test`, `cargo build`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `LukeMathWalker/openfirma`(TO-BE)에서는 `CLAUDE.md`, `examples/agents/agents_sdk_py/agent/main.py`, `cargo test` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.3 MCP 기반 `docs/GOVERNED_WORKSPACE_TOPOLOGY_V1.md` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`Growthub-ai/growthub-local`)

- **출처**: [`Growthub-ai/growthub-local`](https://github.com/Growthub-ai/growthub-local) · **핵심 스택**: `MCP`, `Claude Code`, `Cursor Rules`, `Supabase`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `Growthub-ai/growthub-local` 저장소는 MCP, Claude Code, Cursor Rules 스택 위에서 MCP 기반 `docs/GOVERNED_WORKSPACE_TOPOLOGY_V1.md` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/GOVERNED_WORKSPACE_TOPOLOGY_V1.md`, `scripts/runtime-control.sh`, `skills/README.md`)를 분리해 구성하며 문서 내 주요 섹션(`.cursorrules — pointer to AGENTS.md`, `CLAUDE.md — pointer to AGENTS.md`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `Growthub-ai/growthub-local`(TO-BE)에서는 `.cursorrules`, `CLAUDE.md`, `docs/GOVERNED_WORKSPACE_TOPOLOGY_V1.md` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.4 FastAPI 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`mertoege/invest-pi`)

- **출처**: [`mertoege/invest-pi`](https://github.com/mertoege/invest-pi) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `WebSocket` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `terminal/main.py` 발췌본을 기반으로 확인되는 `mertoege/invest-pi` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`CLAUDE.md — Invest-Pi`, `Mission — EIN Ziel: den Markt schlagen`, `Arbeitsweise — volle Autonomie (von Mert ausdruecklich ertei`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `mertoege/invest-pi`(TO-BE)에서는 `CLAUDE.md`, `terminal/main.py` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리

### 3.1 Python 기반 `docs/ICP_WORKFLOW_V2.md` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`hitechpanda-dangnamhai/sicp`)

- **출처**: [`hitechpanda-dangnamhai/sicp`](https://github.com/hitechpanda-dangnamhai/sicp) · **핵심 스택**: `Python`, `Claude Code`, `Redis`, `Flask`, `WebSocket` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `apps/ai/src/main.py` 발췌본을 기반으로 확인되는 `hitechpanda-dangnamhai/sicp` 저장소는 Python, Claude Code, Redis 스택 위에서 Python 기반 `docs/ICP_WORKFLOW_V2.md` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/ICP_WORKFLOW_V2.md`, `docs/ICP_PLAYBOOK_V2.md`, `docs/slices/S`)를 분리해 구성하며 문서 내 주요 섹션(`ICP — Luật cho Claude Code (đọc trước MỌI task)`, `1. Định hướng`, `2. Nghi thức MỞ TASK (bắt buộc, trước dòng code đầu tiên)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `hitechpanda-dangnamhai/sicp`(TO-BE)에서는 `CLAUDE.md`, `apps/ai/src/main.py`, `docs/ICP_WORKFLOW_V2.md` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.2 FastAPI 기반 `docs/REQUIREMENTS.md` 모듈 분리와 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`mmiura-2351/mc-server-dashboard-v2`)

- **출처**: [`mmiura-2351/mc-server-dashboard-v2`](https://github.com/mmiura-2351/mc-server-dashboard-v2) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `api/src/mc_server_dashboard_api/app.py` 발췌본을 기반으로 확인되는 `mmiura-2351/mc-server-dashboard-v2` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `docs/REQUIREMENTS.md` 모듈 분리와 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/REQUIREMENTS.md`)를 분리해 구성하며 문서 내 주요 섹션(`1. Think Before Coding`, `2. Simplicity First`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `mmiura-2351/mc-server-dashboard-v2`(TO-BE)에서는 `CLAUDE.md`, `api/src/mc_server_dashboard_api/app.py`, `docs/REQUIREMENTS.md` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `elizaOS/eliza`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `LukeMathWalker/openfirma`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `Growthub-ai/growthub-local`의 `.cursorrules` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-05 수집 시점의 공개 저장소 `CLAUDE.md`, `.cursorrules` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
