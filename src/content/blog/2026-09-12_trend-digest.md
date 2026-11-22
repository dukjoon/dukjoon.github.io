---
title: '[Trend] 2026-09-12: MCP, Claude Code 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-09-12T00:00:00Z'
description: 2026-09-12 수집된 BuilderIO/agent-native, daniel-ospina/tortoise, woahwhattheheck/commons 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- mcp
- claude-md
- supabase
- stripe
draft: false
---

2026-09-12 수집된 오픈소스 저장소들에서는 MCP, Claude Code, Supabase, Stripe 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `BuilderIO/agent-native`, `woahwhattheheck/commons`, `internetarchive/openlibrary`, `octaviojuli/commerce-agents` | MCP 도구 스키마 분리 및 런타임 세션 격리, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `daniel-ospina/tortoise`, `seethroughlab/clapback` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, Ray 기반 분산 오케스트레이션 및 학습·추론 엔진 계층화 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 MCP 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`BuilderIO/agent-native`)

- **출처**: [`BuilderIO/agent-native`](https://github.com/BuilderIO/agent-native) · **핵심 스택**: `MCP`, `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `packages/core/src/templates/default/CLAUDE.md` 발췌본을 기반으로 확인되는 `BuilderIO/agent-native` 저장소는 MCP, Claude Code, Supabase 스택 위에서 MCP 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Agent-Native Framework`, `Skills`, `{{APP_NAME}} — Agent Guide`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `BuilderIO/agent-native`(TO-BE)에서는 `CLAUDE.md`, `packages/core/src/templates/default/CLAUDE.md` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 Python 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`woahwhattheheck/commons`)

- **출처**: [`woahwhattheheck/commons`](https://github.com/woahwhattheheck/commons) · **핵심 스택**: `Python`, `Claude Code`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `evidence/archive_misdescribed/ZERO_RAM_PROOF_RUN_BY_CLAUDE.m` 발췌본을 기반으로 확인되는 `woahwhattheheck/commons` 저장소는 Python, Claude Code, Stripe 스택 위에서 Python 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Owner publication terms — Commons and Slack, every peer and `, `~0 RAM PROOF — RUN BY CLAUDE, NOT THE OWNER (2026-07-18)`, `1. The ~0 RAM meter (the owner's own instrument, re-run by t`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `woahwhattheheck/commons`(TO-BE)에서는 `CLAUDE.md`, `evidence/archive_misdescribed/ZERO_RAM_PROOF_RUN_BY_CLAUDE.m` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 FastAPI 기반 `docs/ai/README.md` 모듈 분리와 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`internetarchive/openlibrary`)

- **출처**: [`internetarchive/openlibrary`](https://github.com/internetarchive/openlibrary) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Docker` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `docker/mockservices/main.py` 발췌본을 기반으로 확인되는 `internetarchive/openlibrary` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `docs/ai/README.md` 모듈 분리와 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/ai/README.md`, `docs/ai/i18n.md`, `docs/wiki/developers/frontend/jinja.md`)를 분리해 구성하며 문서 내 주요 섹션(`Quick Reference`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `internetarchive/openlibrary`(TO-BE)에서는 `CLAUDE.md`, `docker/mockservices/main.py`, `docs/ai/README.md` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.4 Python 기반 `core/shopping_agent` 모듈 분리와 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`octaviojuli/commerce-agents`)

- **출처**: [`octaviojuli/commerce-agents`](https://github.com/octaviojuli/commerce-agents) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `examples/entertainment/api/main.py` 발췌본을 기반으로 확인되는 `octaviojuli/commerce-agents` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 `core/shopping_agent` 모듈 분리와 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`core/shopping_agent`, `core/merchant_agent`, `api/merchant`)를 분리해 구성하며 문서 내 주요 섹션(`commerce-agents`, `Layout`, `Copyright 2026 Anthropic PBC`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `octaviojuli/commerce-agents`(TO-BE)에서는 `CLAUDE.md`, `examples/entertainment/api/main.py`, `core/shopping_agent` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 FastAPI 기반 `docker compose up` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`daniel-ospina/tortoise`)

- **출처**: [`daniel-ospina/tortoise`](https://github.com/daniel-ospina/tortoise) · **핵심 스택**: `FastAPI`, `React`, `Python`, `MCP`, `Claude Code`, `Supabase` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `apps/graph-viz/server/main.py` 발췌본을 기반으로 확인되는 `daniel-ospina/tortoise` 저장소는 FastAPI, React, Python 스택 위에서 FastAPI 기반 `docker compose up` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`apps/graph-viz`, `server/main.py`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`docker compose up`, `make the`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `daniel-ospina/tortoise`(TO-BE)에서는 `CLAUDE.md`, `apps/graph-viz/server/main.py`, `docker compose up` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 FastAPI 기반 `lifespan` 중심의 분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리 (`seethroughlab/clapback`)

- **출처**: [`seethroughlab/clapback`](https://github.com/seethroughlab/clapback) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `PostgreSQL`, `SQLAlchemy`, `PyTorch` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `packages/server/app/main.py` 발췌본을 기반으로 확인되는 `seethroughlab/clapback` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `lifespan` 중심의 분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`packages/embed`, `packages/embed/src/clapback_embed/__init__.py`)를 분리해 구성하며 핵심 심볼(`lifespan`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Clapback`, `Architecture`, `Startup`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 언어모델의 강화학습(RL)이나 고속 추론 서버에서 롤아웃 생성, 보상 계산, 가중치 동기화를 단일 스크립트로 묶으면 GPU 유휴 시간과 체크포인트 병목이 심각해집니다. 반면 `seethroughlab/clapback`(TO-BE)에서는 `CLAUDE.md`, `packages/server/app/main.py`, `lifespan` 등 명시적 아티팩트를 기준으로 오케스트레이션 코어, 추론 엔진(SGLang/vLLM), 학습 백엔드(Megatron), 분산 체크포인트 서비스를 계층별로 분리하고 게이트웨이 어댑터로 실험 프로토콜을 표준화합니다. 다만 다중 노드 클러스터와 GPU 메모리 토폴로지에 민감하므로 단위 컴포넌트 모킹 테스트와 실제 분산 환경의 가중치 변환 회귀 테스트를 이원화해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `BuilderIO/agent-native`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `daniel-ospina/tortoise`의 `CLAUDE.md` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `woahwhattheheck/commons`의 `CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-09-12 수집 시점의 공개 저장소 `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
