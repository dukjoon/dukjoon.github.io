---
title: '[Trend] 2026-03-25: Python, Claude Code 기반 DDD 기반 API·워커 분리와 모듈형 런타임'
pubDatetime: '2026-03-25T00:00:00Z'
description: 2026-03-25 수집된 devarakondasrikanth/litellm, Turbo31150/jarvis-linux, scaleapi/scale-agentex 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- claude-md
- supabase
- stripe
draft: false
---

2026-03-25 수집된 오픈소스 저장소들에서는 Python, Claude Code, Supabase, Stripe 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진 | `devarakondasrikanth/litellm`, `Turbo31150/jarvis-linux`, `armaanpriyadarshan/arc`, `73ai/openbotkit` | DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 |
| 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리 | `scaleapi/scale-agentex`, `ElijahTowers/QuartaPotestas` | FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조 |

---

## 2. 에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진

### 2.1 Python 기반 `interactive_chat` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`devarakondasrikanth/litellm`)

- **출처**: [`devarakondasrikanth/litellm`](https://github.com/devarakondasrikanth/litellm) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `Stripe`, `LangGraph`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `cookbook/anthropic_agent_sdk/main.py` 발췌본을 기반으로 확인되는 `devarakondasrikanth/litellm` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `interactive_chat` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`tests/test_litellm`, `tests/path/to/test_file.py`)를 분리해 구성하며 핵심 심볼(`interactive_chat`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make install-dev`, `make install-proxy-dev`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `devarakondasrikanth/litellm`(TO-BE)에서는 `CLAUDE.md`, `cookbook/anthropic_agent_sdk/main.py`, `make install-dev` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.2 Python 기반 `setup_logging` 중심의 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`Turbo31150/jarvis-linux`)

- **출처**: [`Turbo31150/jarvis-linux`](https://github.com/Turbo31150/jarvis-linux) · **핵심 스택**: `Python`, `Claude Code`, `Redis`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `archive/src_corrupt/tache21_systray/main.py`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `Turbo31150/jarvis-linux` 저장소는 Python, Claude Code, Redis 스택 위에서 Python 기반 `setup_logging` 중심의 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 핵심 심볼(`setup_logging`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Ajoute le répertoire parent au path`, `JARVIS MASTER DOCTRINE — DISTRIBUTED PARALLEL ENGINE`, `ARCHITECTURE`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `Turbo31150/jarvis-linux`(TO-BE)에서는 `archive/src_corrupt/tache21_systray/main.py`, `CLAUDE.md`, `setup_logging` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 Python 기반 `run_agent` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`armaanpriyadarshan/arc`)

- **출처**: [`armaanpriyadarshan/arc`](https://github.com/armaanpriyadarshan/arc) · **핵심 스택**: `Python`, `Claude Code`, `LangGraph` · **적용 판단**: `Trial`
- **기술 개요**: `ARC-AGI-3-Agents/main.py`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `armaanpriyadarshan/arc` 저장소는 Python, Claude Code, LangGraph 스택 위에서 Python 기반 `run_agent` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 핵심 심볼(`run_agent`, `cle`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`ruff: noqa: E402`, `Hide standard ports in URL`, `Key types (from arc-agi / arcengine)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `armaanpriyadarshan/arc`(TO-BE)에서는 `ARC-AGI-3-Agents/main.py`, `CLAUDE.md`, `run_agent` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.4 Claude Code 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`73ai/openbotkit`)

- **출처**: [`73ai/openbotkit`](https://github.com/73ai/openbotkit) · **핵심 스택**: `Claude Code`, `SQLite`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `assistant/CLAUDE.md` 발췌본을 기반으로 확인되는 `73ai/openbotkit` 저장소는 Claude Code, SQLite, OpenAI SDK 스택 위에서 Claude Code 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Project Guidelines`, `Coding Guidelines`, `Destructive Actions`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `73ai/openbotkit`(TO-BE)에서는 `CLAUDE.md`, `assistant/CLAUDE.md` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

## 3. 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리

### 3.1 FastAPI 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`scaleapi/scale-agentex`)

- **출처**: [`scaleapi/scale-agentex`](https://github.com/scaleapi/scale-agentex) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Docker`, `LangGraph`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `agentex/src/api/app.py` 발췌본을 기반으로 확인되는 `scaleapi/scale-agentex` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Repository Overview`, `Development Environment Setup`, `Prerequisites`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `scaleapi/scale-agentex`(TO-BE)에서는 `CLAUDE.md`, `agentex/src/api/app.py` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.2 FastAPI 기반 `frontend/package.json` 모듈 분리와 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`ElijahTowers/QuartaPotestas`)

- **출처**: [`ElijahTowers/QuartaPotestas`](https://github.com/ElijahTowers/QuartaPotestas) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Pydantic`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/app/main.py` 발췌본을 기반으로 확인되는 `ElijahTowers/QuartaPotestas` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `frontend/package.json` 모듈 분리와 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`frontend/package.json`)를 분리해 구성하며 문서 내 주요 섹션(`QuartaPotestas — Project Brief`, `This machine`, `PM2 services`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `ElijahTowers/QuartaPotestas`(TO-BE)에서는 `CLAUDE.md`, `backend/app/main.py`, `frontend/package.json` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `devarakondasrikanth/litellm`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `Turbo31150/jarvis-linux`의 `archive/src_corrupt/tache21_systray/main.py` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `scaleapi/scale-agentex`의 `CLAUDE.md` 구성처럼 FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-03-25 수집 시점의 공개 저장소 `CLAUDE.md`, `archive/src_corrupt/tache21_systray/main.py`, `ARC-AGI-3-Agents/main.py` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
