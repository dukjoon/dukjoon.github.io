---
title: '[Trend] 2026-03-27: Python, Claude Code 기반 DDD 기반 API·워커 분리와 모듈형 런타임'
pubDatetime: '2026-03-27T00:00:00Z'
description: 2026-03-27 수집된 thiago-carbonera/litellm, davila7/claude-code-templates, rysweet/amplihack 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- claude-md
- supabase
- stripe
draft: false
---

2026-03-27 수집된 오픈소스 저장소들에서는 Python, Claude Code, Supabase, Stripe 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진 | `thiago-carbonera/litellm`, `davila7/claude-code-templates`, `rysweet/amplihack`, `darrenoakey/arbiter` | DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 브라우저 확장·모노레포 워크스페이스 및 공유 상수 아키텍처 | `waaseyaa/framework`, `bernardopg/doctoralia-scrapper` | 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. 에이전틱 RAG 파이프라인 및 도메인 주도 워크플로우 엔진

### 2.1 Python 기반 `interactive_chat` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`thiago-carbonera/litellm`)

- **출처**: [`thiago-carbonera/litellm`](https://github.com/thiago-carbonera/litellm) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `Stripe`, `LangGraph`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `cookbook/anthropic_agent_sdk/main.py` 발췌본을 기반으로 확인되는 `thiago-carbonera/litellm` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `interactive_chat` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`tests/test_litellm`, `tests/path/to/test_file.py`)를 분리해 구성하며 핵심 심볼(`interactive_chat`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make install-dev`, `make install-proxy-dev`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `thiago-carbonera/litellm`(TO-BE)에서는 `CLAUDE.md`, `cookbook/anthropic_agent_sdk/main.py`, `make install-dev` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.2 Python 기반 `npm test` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`davila7/claude-code-templates`)

- **출처**: [`davila7/claude-code-templates`](https://github.com/davila7/claude-code-templates) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `Stripe`, `LangGraph`, `CrewAI` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `cli-tool/components/skills/ai-research/loki-mode/CLAUDE.md` 발췌본을 기반으로 확인되는 `davila7/claude-code-templates` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `npm test` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/generate_components_json.py`, `docs/components.json`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`npm test`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `davila7/claude-code-templates`(TO-BE)에서는 `CLAUDE.md`, `cli-tool/components/skills/ai-research/loki-mode/CLAUDE.md`, `npm test` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.3 Python 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`rysweet/amplihack`)

- **출처**: [`rysweet/amplihack`](https://github.com/rysweet/amplihack) · **핵심 스택**: `Python`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.github/scripts/pr_triage_main.py`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `rysweet/amplihack` 저장소는 Python, Claude Code, OpenAI SDK 스택 위에서 Python 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Add scripts directory to path for imports`, `Get PR number from environment`, `Create validator`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `rysweet/amplihack`(TO-BE)에서는 `.github/scripts/pr_triage_main.py`, `CLAUDE.md` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.4 FastAPI 기반 `respond` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`darrenoakey/arbiter`)

- **출처**: [`darrenoakey/arbiter`](https://github.com/darrenoakey/arbiter) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `SQLite`, `Pydantic` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/arbiter/worker_main.py` 발췌본을 기반으로 확인되는 `darrenoakey/arbiter` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `respond` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/arbiter/server.py`, `src/arbiter/scheduler.py`, `src/arbiter/memory.py`)를 분리해 구성하며 핵심 심볼(`respond`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Arbiter — Development Guide`, `Architecture`, `Thread-safe stdout writing`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `darrenoakey/arbiter`(TO-BE)에서는 `CLAUDE.md`, `src/arbiter/worker_main.py`, `respond` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 브라우저 확장·모노레포 워크스페이스 및 공유 상수 아키텍처

### 3.1 Claude Code 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`waaseyaa/framework`)

- **출처**: [`waaseyaa/framework`](https://github.com/waaseyaa/framework) · **핵심 스택**: `Claude Code`, `Stripe`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `skeleton/CLAUDE.md` 발췌본을 기반으로 확인되는 `waaseyaa/framework` 저장소는 Claude Code, Stripe, OpenAI SDK 스택 위에서 Claude Code 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Waaseyaa`, `Project Structure`, `Architecture`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `waaseyaa/framework`(TO-BE)에서는 `CLAUDE.md`, `skeleton/CLAUDE.md` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

### 3.2 FastAPI 기반 `make venv` 워크플로우 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`bernardopg/doctoralia-scrapper`)

- **출처**: [`bernardopg/doctoralia-scrapper`](https://github.com/bernardopg/doctoralia-scrapper) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Redis`, `Flask`, `pytest` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `main.py` 발췌본을 기반으로 확인되는 `bernardopg/doctoralia-scrapper` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `make venv` 워크플로우 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. `CLAUDE.md` 등에 명시된 실행·검증 명령(`make venv`, `make install`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `bernardopg/doctoralia-scrapper`(TO-BE)에서는 `CLAUDE.md`, `main.py`, `make venv` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `thiago-carbonera/litellm`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `davila7/claude-code-templates`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `rysweet/amplihack`의 `.github/scripts/pr_triage_main.py` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-03-27 수집 시점의 공개 저장소 `CLAUDE.md`, `.github/scripts/pr_triage_main.py` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
