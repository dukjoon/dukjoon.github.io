---
title: '[Trend] 2026-07-20: Python, Claude Code 기반 DDD 기반 API·워커 분리와 모듈형 런타임'
pubDatetime: '2026-07-20T00:00:00Z'
description: 2026-07-20 수집된 apache/airflow, bsvalues/terrafusion_os_1.0, architectcgz/my-agents 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- claude-md
- langgraph
- openai
draft: false
---

2026-07-20 수집된 오픈소스 저장소들에서는 Python, Claude Code, LangGraph, OpenAI SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진 | `apache/airflow`, `bsvalues/terrafusion_os_1.0`, `architectcgz/my-agents`, `librefang/librefang`, `langfuse/langfuse-docs` | DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, MCP 도구 스키마 분리 및 런타임 세션 격리, 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `gesmith0606/nfl_data_engineering` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 |

---

## 2. 에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진

### 2.1 Python 기반 `scripts/tools/setup_breeze` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`apache/airflow`)

- **출처**: [`apache/airflow`](https://github.com/apache/airflow) · **핵심 스택**: `Python`, `Claude Code`, `LangGraph`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `airflow-core/src/airflow/api_fastapi/app.py` 발췌본을 기반으로 확인되는 `apache/airflow` 저장소는 Python, Claude Code, LangGraph 스택 위에서 Python 기반 `scripts/tools/setup_breeze` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/tools/setup_breeze`)를 분리해 구성하며 문서 내 주요 섹션(`AGENTS instructions`, `Naming`, `Environment Setup`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `apache/airflow`(TO-BE)에서는 `CLAUDE.md`, `airflow-core/src/airflow/api_fastapi/app.py`, `scripts/tools/setup_breeze` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.2 React 기반 `docs/security/baseline.md` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`bsvalues/terrafusion_os_1.0`)

- **출처**: [`bsvalues/terrafusion_os_1.0`](https://github.com/bsvalues/terrafusion_os_1.0) · **핵심 스택**: `React`, `Python`, `Claude Code`, `Supabase`, `LangGraph`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `QUARANTINE/top-level-dirs/applications/bcbs-gis-pro-producti` 발췌본을 기반으로 확인되는 `bsvalues/terrafusion_os_1.0` 저장소는 React, Python, Claude Code 스택 위에서 React 기반 `docs/security/baseline.md` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/security/baseline.md`)를 분리해 구성하며 문서 내 주요 섹션(`Canonical Instructions (Source of Truth)`, `Launcher Constitution (Dev OS)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `bsvalues/terrafusion_os_1.0`(TO-BE)에서는 `CLAUDE.md`, `QUARANTINE/top-level-dirs/applications/bcbs-gis-pro-producti`, `docs/security/baseline.md` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 Python 기반 `parse_args` 중심의 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`architectcgz/my-agents`)

- **출처**: [`architectcgz/my-agents`](https://github.com/architectcgz/my-agents) · **핵심 스택**: `Python`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `harness/harness_initializer/app.py` 발췌본을 기반으로 확인되는 `architectcgz/my-agents` 저장소는 Python, Claude Code, OpenAI SDK 스택 위에서 Python 기반 `parse_args` 중심의 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 핵심 심볼(`parse_args`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`全局协作规范`, `0. AGENTS 层级归属`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `architectcgz/my-agents`(TO-BE)에서는 `CLAUDE.md`, `harness/harness_initializer/app.py`, `parse_args` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.4 React 기반 `used` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`librefang/librefang`)

- **출처**: [`librefang/librefang`](https://github.com/librefang/librefang) · **핵심 스택**: `React`, `TypeScript`, `MCP`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `crates/librefang-api/dashboard/CLAUDE.md` 발췌본을 기반으로 확인되는 `librefang/librefang` 저장소는 React, TypeScript, MCP 스택 위에서 React 기반 `used` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/main.tsx`, `src/pages`, `src/lib`)를 분리해 구성하며 핵심 심볼(`used`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`LibreFang — Agent Instructions`, `️ Before any work: verify you are in a worktree, not the mai`, `Dashboard — Agent Instructions`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `librefang/librefang`(TO-BE)에서는 `CLAUDE.md`, `crates/librefang-api/dashboard/CLAUDE.md`, `used` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.5 Claude Code 기반 `pnpm dev` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`langfuse/langfuse-docs`)

- **출처**: [`langfuse/langfuse-docs`](https://github.com/langfuse/langfuse-docs) · **핵심 스택**: `Claude Code`, `Pydantic`, `LangGraph`, `CrewAI`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md` 발췌본을 기반으로 확인되는 `langfuse/langfuse-docs` 저장소는 Claude Code, Pydantic, LangGraph 스택 위에서 Claude Code 기반 `pnpm dev` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/update_cookbook_docs.sh`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`pnpm dev`, `pnpm build`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `langfuse/langfuse-docs`(TO-BE)에서는 `CLAUDE.md`, `pnpm dev` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 FastAPI 기반 `pytest tests` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`gesmith0606/nfl_data_engineering`)

- **출처**: [`gesmith0606/nfl_data_engineering`](https://github.com/gesmith0606/nfl_data_engineering) · **핵심 스택**: `FastAPI`, `Next.js`, `Python`, `Claude Code`, `Supabase`, `Stripe` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `web/api/main.py` 발췌본을 기반으로 확인되는 `gesmith0606/nfl_data_engineering` 저장소는 FastAPI, Next.js, Python 스택 위에서 FastAPI 기반 `pytest tests` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/validate_project.py`, `scripts/bronze_ingestion_simple.py`, `scripts/bronze_odds_ingestion.py`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`pytest tests`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `gesmith0606/nfl_data_engineering`(TO-BE)에서는 `CLAUDE.md`, `web/api/main.py`, `pytest tests` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `apache/airflow`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `bsvalues/terrafusion_os_1.0`의 `CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `architectcgz/my-agents`의 `CLAUDE.md` 구성처럼 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-20 수집 시점의 공개 저장소 `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
