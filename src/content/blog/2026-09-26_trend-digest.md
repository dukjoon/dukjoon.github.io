---
title: '[Trend] 2026-09-26: Claude Code, Supabase 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-09-26T00:00:00Z'
description: 2026-09-26 수집된 groeneai/ClickHouse, huh0303-cmyk/-WP-QWEN-autobot, andi1180/peak-shaving 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- claude-md
- supabase
- stripe
- pydantic
draft: false
---

2026-09-26 수집된 오픈소스 저장소들에서는 Claude Code, Supabase, Stripe, Pydantic 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `groeneai/ClickHouse`, `andi1180/peak-shaving` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 |
| 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리 | `huh0303-cmyk/-WP-QWEN-autobot`, `Freegle/Iznik`, `futuregene/future-os`, `Khoality-dev/KurisuAssistant` | FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일, Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 Claude Code 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`groeneai/ClickHouse`)

- **출처**: [`groeneai/ClickHouse`](https://github.com/groeneai/ClickHouse) · **핵심 스택**: `Claude Code`, `Supabase`, `Stripe`, `Pydantic`, `LangGraph`, `CrewAI` · **적용 판단**: `Trial`
- **기술 개요**: `.claude/CLAUDE.md`, `ci/CLAUDE.md` 발췌본을 기반으로 확인되는 `groeneai/ClickHouse` 저장소는 Claude Code, Supabase, Stripe 스택 위에서 Claude Code 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Working with CI (praktika) from an agent`, `Reading a run's results`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `groeneai/ClickHouse`(TO-BE)에서는 `.claude/CLAUDE.md`, `ci/CLAUDE.md` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 Claude Code 기반 `apps/web` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`andi1180/peak-shaving`)

- **출처**: [`andi1180/peak-shaving`](https://github.com/andi1180/peak-shaving) · **핵심 스택**: `Claude Code`, `Supabase`, `Stripe` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `apps/web/CLAUDE.md` 발췌본을 기반으로 확인되는 `andi1180/peak-shaving` 저장소는 Claude Code, Supabase, Stripe 스택 위에서 Claude Code 기반 `apps/web` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`apps/web`, `apps/web/CLAUDE.md`, `apps/web/Pflichtenheft_Website_Coolin.md`)를 분리해 구성하며 문서 내 주요 섹션(`CLAUDE.md — Peak Shaving Kalkulator`, `CLAUDE.md — coolin.at Website`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `andi1180/peak-shaving`(TO-BE)에서는 `CLAUDE.md`, `apps/web/CLAUDE.md`, `apps/web` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

## 3. 비동기 API 서버·백그라운드 워커 및 도메인 모듈 분리

### 3.1 Python 기반 `docs/LONDON_PROJECT_BLUEPRINT.md` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`huh0303-cmyk/-WP-QWEN-autobot`)

- **출처**: [`huh0303-cmyk/-WP-QWEN-autobot`](https://github.com/huh0303-cmyk/-WP-QWEN-autobot) · **핵심 스택**: `Python`, `Claude Code`, `OpenAI SDK`, `Gemini SDK`, `Flask` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `control_center/app.py` 발췌본을 기반으로 확인되는 `huh0303-cmyk/-WP-QWEN-autobot` 저장소는 Python, Claude Code, OpenAI SDK 스택 위에서 Python 기반 `docs/LONDON_PROJECT_BLUEPRINT.md` 모듈 분리와 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/LONDON_PROJECT_BLUEPRINT.md`, `docs/LONDON_PROJECT_CONTENT_PIPELINES.md`, `docs/LONDON_PROJECT_ACTIVITY_LEDGER.md`)를 분리해 구성하며 문서 내 주요 섹션(`Claude Work Assistant — 런던프로젝트 (London Project)`, `Command hierarchy`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `huh0303-cmyk/-WP-QWEN-autobot`(TO-BE)에서는 `CLAUDE.md`, `control_center/app.py`, `docs/LONDON_PROJECT_BLUEPRINT.md` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

### 3.2 Claude Code 기반 `make coverage` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`Freegle/Iznik`)

- **출처**: [`Freegle/Iznik`](https://github.com/Freegle/Iznik) · **핵심 스택**: `Claude Code`, `Stripe`, `Docker`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `iznik-batch/CLAUDE.md` 발췌본을 기반으로 확인되는 `Freegle/Iznik` 저장소는 Claude Code, Stripe, Docker 스택 위에서 Claude Code 기반 `make coverage` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/developers/reference/coding-standards.md`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make coverage`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `Freegle/Iznik`(TO-BE)에서는 `CLAUDE.md`, `iznik-batch/CLAUDE.md`, `make coverage` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.3 React 기반 `docs/README.md` 모듈 분리와 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화 (`futuregene/future-os`)

- **출처**: [`futuregene/future-os`](https://github.com/futuregene/future-os) · **핵심 스택**: `React`, `TypeScript`, `Rust`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `desktop/CLAUDE.md` 발췌본을 기반으로 확인되는 `futuregene/future-os` 저장소는 React, TypeScript, Rust 스택 위에서 React 기반 `docs/README.md` 모듈 분리와 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/README.md`, `docs/guide/directory-layout.md`, `docs/internals/desktop`)를 분리해 구성하며 문서 내 주요 섹션(`Workspace layout`, `Desktop Development Guide (desktop/)`, `Document Map (read relevant sections on demand — don't pull `)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 모바일이나 데스크톱 클라이언트에서 UI 화면 코드 안에 각 AI 벤더 호출과 문서 파싱, 다국어 번역 리소스를 직접 결합하면 앱 빌드 시간과 유지보수 복잡도가 크게 증가합니다. 반면 `futuregene/future-os`(TO-BE)에서는 `CLAUDE.md`, `desktop/CLAUDE.md`, `docs/README.md` 등 명시적 아티팩트를 기준으로 UI·AI SDK 추상화·문서 파서·검색 모듈을 다중 모듈 아키텍처로 격리하고 터미널 기반 번역·검증 도구나 시뮬레이터 테스트 규칙을 병행하여 클라이언트 품질을 관리합니다. 다만 네이티브 모듈과 내장 웹/TUI 도구 간 빌드 파이프라인이 나뉘므로 릴리스 아티팩트 패키징과 CI 러너의 리소스 제약을 고려한 테스트 설계가 요구됩니다.

---

### 3.4 FastAPI 기반 `backend/CLAUDE.md` 모듈 분리와 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`Khoality-dev/KurisuAssistant`)

- **출처**: [`Khoality-dev/KurisuAssistant`](https://github.com/Khoality-dev/KurisuAssistant) · **핵심 스택**: `FastAPI`, `React`, `TypeScript`, `Python`, `Claude Code`, `Docker` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/CLAUDE.md` 발췌본을 기반으로 확인되는 `Khoality-dev/KurisuAssistant` 저장소는 FastAPI, React, TypeScript 스택 위에서 FastAPI 기반 `backend/CLAUDE.md` 모듈 분리와 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`backend/CLAUDE.md`, `apps/desktop`, `apps/desktop/CLAUDE.md`)를 분리해 구성하며 문서 내 주요 섹션(`Documentation Index`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `Khoality-dev/KurisuAssistant`(TO-BE)에서는 `CLAUDE.md`, `backend/CLAUDE.md`, `backend/CLAUDE.md` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `groeneai/ClickHouse`의 `.claude/CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `huh0303-cmyk/-WP-QWEN-autobot`의 `CLAUDE.md` 구성처럼 FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `andi1180/peak-shaving`의 `CLAUDE.md` 구성처럼 DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-09-26 수집 시점의 공개 저장소 `.claude/CLAUDE.md`, `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
