---
title: '[Trend] 2026-07-16: FastAPI, Python 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-07-16T00:00:00Z'
description: 2026-07-16 수집된 CopilotKit/CopilotKit, wandb/weave, jackin-project/jackin 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- fastapi
- python
- mcp
- claude-md
draft: false
---

2026-07-16 수집된 오픈소스 저장소들에서는 FastAPI, Python, MCP, Claude Code 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `CopilotKit/CopilotKit`, `wandb/weave`, `jackin-project/jackin`, `sleep2agi/agent-network` | MCP 도구 스키마 분리 및 런타임 세션 격리, 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 브라우저 확장·모노레포 워크스페이스 및 공유 상수 아키텍처 | `jperner11/NutrigoalApp`, `duapraveen/agentlens-web` | 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 FastAPI 기반 `health` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`CopilotKit/CopilotKit`)

- **출처**: [`CopilotKit/CopilotKit`](https://github.com/CopilotKit/CopilotKit) · **핵심 스택**: `FastAPI`, `Python`, `MCP`, `Claude Code`, `Supabase`, `Pydantic` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `examples/canvas/gemini/agent/main.py` 발췌본을 기반으로 확인되는 `CopilotKit/CopilotKit` 저장소는 FastAPI, Python, MCP 스택 위에서 FastAPI 기반 `health` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 핵심 심볼(`health`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`General Guidelines for working with Nx`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `CopilotKit/CopilotKit`(TO-BE)에서는 `CLAUDE.md`, `examples/canvas/gemini/agent/main.py`, `health` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 FastAPI 기반 `health` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`wandb/weave`)

- **출처**: [`wandb/weave`](https://github.com/wandb/weave) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `LangGraph`, `CrewAI`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `examples/remote_scorer/remote_scorer_app.py` 발췌본을 기반으로 확인되는 `wandb/weave` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `health` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 핵심 심볼(`health`, `score`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make sense`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `wandb/weave`(TO-BE)에서는 `CLAUDE.md`, `examples/remote_scorer/remote_scorer_app.py`, `make sense` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.3 Claude Code 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`jackin-project/jackin`)

- **출처**: [`jackin-project/jackin`](https://github.com/jackin-project/jackin) · **핵심 스택**: `Claude Code`, `Docker`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.github/CLAUDE.md`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `jackin-project/jackin` 저장소는 Claude Code, Docker, OpenAI SDK 스택 위에서 Claude Code 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`.github/ rules — agent reference`, `Hard rules (always-on)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `jackin-project/jackin`(TO-BE)에서는 `.github/CLAUDE.md`, `CLAUDE.md` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.4 TypeScript 기반 `bun run src` 워크플로우 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`sleep2agi/agent-network`)

- **출처**: [`sleep2agi/agent-network`](https://github.com/sleep2agi/agent-network) · **핵심 스택**: `TypeScript`, `MCP`, `Claude Code`, `SQLite`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `server/CLAUDE.md` 발췌본을 기반으로 확인되는 `sleep2agi/agent-network` 저장소는 TypeScript, MCP, Claude Code 스택 위에서 TypeScript 기반 `bun run src` 워크플로우 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/agent-reply-to-dashboard.md`, `src/index.ts`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`bun run src`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `sleep2agi/agent-network`(TO-BE)에서는 `CLAUDE.md`, `server/CLAUDE.md`, `bun run src` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 브라우저 확장·모노레포 워크스페이스 및 공유 상수 아키텍처

### 3.1 Next.js 기반 `npm run dev:web` 워크플로우 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`jperner11/NutrigoalApp`)

- **출처**: [`jperner11/NutrigoalApp`](https://github.com/jperner11/NutrigoalApp) · **핵심 스택**: `Next.js`, `React`, `TypeScript`, `Claude Code`, `Supabase`, `Stripe` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `packages/shared/CLAUDE.md` 발췌본을 기반으로 확인되는 `jperner11/NutrigoalApp` 저장소는 Next.js, React, TypeScript 스택 위에서 Next.js 기반 `npm run dev:web` 워크플로우 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`apps/web`, `apps/mobile`, `packages/shared`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run dev:web`, `npm run build:web`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `jperner11/NutrigoalApp`(TO-BE)에서는 `CLAUDE.md`, `packages/shared/CLAUDE.md`, `npm run dev:web` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

### 3.2 FastAPI 기반 `create_app` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`duapraveen/agentlens-web`)

- **출처**: [`duapraveen/agentlens-web`](https://github.com/duapraveen/agentlens-web) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `uv`, `pytest` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `agentlens/api/main.py` 발췌본을 기반으로 확인되는 `duapraveen/agentlens-web` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `create_app` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`api/health`)를 분리해 구성하며 핵심 심볼(`create_app`, `health`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`uv sync`, `uv run`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `duapraveen/agentlens-web`(TO-BE)에서는 `CLAUDE.md`, `agentlens/api/main.py`, `uv sync` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `CopilotKit/CopilotKit`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `wandb/weave`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `jackin-project/jackin`의 `.github/CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-16 수집 시점의 공개 저장소 `CLAUDE.md`, `.github/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
