---
title: '[Trend] 2026-03-11: Python, Cursor Rules 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-03-11T00:00:00Z'
description: 2026-03-11 수집된 RodrigoMvs123/Aden-Hive, vrlo/litellm, dagster-io/dagster 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- cursorrules
- stripe
- langgraph
draft: false
---

2026-03-11 수집된 오픈소스 저장소들에서는 Python, Cursor Rules, Stripe, LangGraph 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `RodrigoMvs123/Aden-Hive`, `vrlo/litellm`, `tmdqja75/coding-agent-setting` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, MCP 도구 스키마 분리 및 런타임 세션 격리 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `dagster-io/dagster`, `PrairieLearn/PrairieLearn`, `Abhinandan-Khurana/background-agents` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 Python 기반 `safe_path_segment` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`RodrigoMvs123/Aden-Hive`)

- **출처**: [`RodrigoMvs123/Aden-Hive`](https://github.com/RodrigoMvs123/Aden-Hive) · **핵심 스택**: `Python`, `Cursor Rules`, `Stripe`, `LangGraph`, `CrewAI`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `core/framework/server/app.py` 발췌본을 기반으로 확인되는 `RodrigoMvs123/Aden-Hive` 저장소는 Python, Cursor Rules, Stripe 스택 위에서 Python 기반 `safe_path_segment` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`core/pyproject.toml`)를 분리해 구성하며 핵심 심볼(`safe_path_segment`, `resolve_session`)을 중심으로 실행 흐름을 정의하고 `.cursorrules` 등에 명시된 실행·검증 명령(`make lint`, `make check`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `RodrigoMvs123/Aden-Hive`(TO-BE)에서는 `.cursorrules`, `core/framework/server/app.py`, `make lint` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 Python 기반 `interactive_chat` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`vrlo/litellm`)

- **출처**: [`vrlo/litellm`](https://github.com/vrlo/litellm) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `LangGraph`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `cookbook/anthropic_agent_sdk/main.py` 발췌본을 기반으로 확인되는 `vrlo/litellm` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `interactive_chat` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`tests/test_litellm`, `tests/path/to/test_file.py`)를 분리해 구성하며 핵심 심볼(`interactive_chat`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make install-dev`, `make install-proxy-dev`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `vrlo/litellm`(TO-BE)에서는 `CLAUDE.md`, `cookbook/anthropic_agent_sdk/main.py`, `make install-dev` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.3 FastAPI 기반 `npm run dev` 워크플로우 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`tmdqja75/coding-agent-setting`)

- **출처**: [`tmdqja75/coding-agent-setting`](https://github.com/tmdqja75/coding-agent-setting) · **핵심 스택**: `FastAPI`, `Next.js`, `TypeScript`, `Python`, `MCP`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `agent/main.py` 발췌본을 기반으로 확인되는 `tmdqja75/coding-agent-setting` 저장소는 FastAPI, Next.js, TypeScript 스택 위에서 FastAPI 기반 `npm run dev` 워크플로우 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. `CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run dev`, `npm run build`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `tmdqja75/coding-agent-setting`(TO-BE)에서는 `CLAUDE.md`, `agent/main.py`, `npm run dev` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 TypeScript 기반 `filter_steps_by_quarantined` 중심의 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`dagster-io/dagster`)

- **출처**: [`dagster-io/dagster`](https://github.com/dagster-io/dagster) · **핵심 스택**: `TypeScript`, `Python`, `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `buildkite/dagster-buildkite/dagster_buildkite/pipelines/dags`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `dagster-io/dagster` 저장소는 TypeScript, Python, Claude Code 스택 위에서 TypeScript 기반 `filter_steps_by_quarantined` 중심의 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/docs/about/contributing.md`)를 분리해 구성하며 핵심 심볼(`filter_steps_by_quarantined`)을 중심으로 실행 흐름을 정의하고 `buildkite/dagster-buildkite/dagster_buildkite/pipelines/dags` 등에 명시된 실행·검증 명령(`make ruff`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `dagster-io/dagster`(TO-BE)에서는 `buildkite/dagster-buildkite/dagster_buildkite/pipelines/dags`, `CLAUDE.md`, `make ruff` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 React 기반 `add_files` 중심의 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`PrairieLearn/PrairieLearn`)

- **출처**: [`PrairieLearn/PrairieLearn`](https://github.com/PrairieLearn/PrairieLearn) · **핵심 스택**: `React`, `TypeScript`, `Python`, `Claude Code`, `Stripe`, `PostgreSQL` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `graders/python/python_autograder/pl_main.py` 발췌본을 기반으로 확인되는 `PrairieLearn/PrairieLearn` 저장소는 React, TypeScript, Python 스택 위에서 React 기반 `add_files` 중심의 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`apps/prairielearn`, `apps/prairielearn/src/server.ts`, `apps/prairielearn/src/pages`)를 분리해 구성하며 핵심 심볼(`add_files`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`PrairieLearn`, `Tech stack`, `Applications`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `PrairieLearn/PrairieLearn`(TO-BE)에서는 `CLAUDE.md`, `graders/python/python_autograder/pl_main.py`, `add_files` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

### 3.3 FastAPI 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`Abhinandan-Khurana/background-agents`)

- **출처**: [`Abhinandan-Khurana/background-agents`](https://github.com/Abhinandan-Khurana/background-agents) · **핵심 스택**: `FastAPI`, `Next.js`, `React`, `TypeScript`, `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `packages/modal-infra/src/app.py` 발췌본을 기반으로 확인되는 `Abhinandan-Khurana/background-agents` 저장소는 FastAPI, Next.js, React 스택 위에서 FastAPI 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Architecture`, `Main Modal application`, `Image for Modal functions (not sandbox)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `Abhinandan-Khurana/background-agents`(TO-BE)에서는 `CLAUDE.md`, `packages/modal-infra/src/app.py` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `RodrigoMvs123/Aden-Hive`의 `.cursorrules` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `vrlo/litellm`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `dagster-io/dagster`의 `buildkite/dagster-buildkite/dagster_buildkite/pipelines/dags` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-03-11 수집 시점의 공개 저장소 `.cursorrules`, `CLAUDE.md`, `buildkite/dagster-buildkite/dagster_buildkite/pipelines/dags` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
