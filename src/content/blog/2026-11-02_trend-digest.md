---
title: '[Trend] 2026-11-02: Python, Claude Code 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-11-02T00:00:00Z'
description: 2026-11-02 수집된 Vivaliz-site/site-shopvivaliz, frankbria/auto-author, open-metadata/OpenMetadata 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- claude-md
- supabase
- openai
draft: false
---

2026-11-02 수집된 오픈소스 저장소들에서는 Python, Claude Code, Supabase, OpenAI SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `Vivaliz-site/site-shopvivaliz`, `open-metadata/OpenMetadata`, `mo-ri-ch/reel-agent` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `frankbria/auto-author`, `luworks/today`, `openhive-network/haf` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화, 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 Python 기반 `scripts/agent_task_state.py` 모듈 분리와 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`Vivaliz-site/site-shopvivaliz`)

- **출처**: [`Vivaliz-site/site-shopvivaliz`](https://github.com/Vivaliz-site/site-shopvivaliz) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `OpenAI SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `scripts/ia_pipeline_main.py` 발췌본을 기반으로 확인되는 `Vivaliz-site/site-shopvivaliz` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `scripts/agent_task_state.py` 모듈 분리와 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/agent_task_state.py`)를 분리해 구성하며 문서 내 주요 섹션(`Checkpoint obrigatorio antes de executar`, `Checklist transacional obrigatorio: todos os agentes e todas`, `Ajustar sys.path para importações relativas funcionarem`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `Vivaliz-site/site-shopvivaliz`(TO-BE)에서는 `CLAUDE.md`, `scripts/ia_pipeline_main.py`, `scripts/agent_task_state.py` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 Python 기반 `docs/index.md` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`open-metadata/OpenMetadata`)

- **출처**: [`open-metadata/OpenMetadata`](https://github.com/open-metadata/OpenMetadata) · **핵심 스택**: `Python`, `Claude Code`, `Docker`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `ingestion/operators/docker/main.py` 발췌본을 기반으로 확인되는 `open-metadata/OpenMetadata` 저장소는 Python, Claude Code, Docker 스택 위에서 Python 기반 `docs/index.md` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/index.md`)를 분리해 구성하며 문서 내 주요 섹션(`Copyright 2025 Collate`, `Licensed under the Collate Community License, Version 1.0 (t`, `you may not use this file except in compliance with the Lice`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `open-metadata/OpenMetadata`(TO-BE)에서는 `CLAUDE.md`, `ingestion/operators/docker/main.py`, `docs/index.md` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 Python 기반 `voice_request` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`mo-ri-ch/reel-agent`)

- **출처**: [`mo-ri-ch/reel-agent`](https://github.com/mo-ri-ch/reel-agent) · **핵심 스택**: `Python`, `Claude Code`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `main.py` 발췌본을 기반으로 확인되는 `mo-ri-ch/reel-agent` 저장소는 Python, Claude Code, Gemini SDK 스택 위에서 Python 기반 `voice_request` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 핵심 심볼(`voice_request`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Gradient Daily reel agent: rules for Claude`, `Mission & goals (keep every change aimed at these)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `mo-ri-ch/reel-agent`(TO-BE)에서는 `CLAUDE.md`, `main.py`, `voice_request` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 FastAPI 기반 `docs/README.md` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`frankbria/auto-author`)

- **출처**: [`frankbria/auto-author`](https://github.com/frankbria/auto-author) · **핵심 스택**: `FastAPI`, `Next.js`, `Python`, `Claude Code`, `Stripe`, `Pydantic` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `backend/app/main.py` 발췌본을 기반으로 확인되는 `frankbria/auto-author` 저장소는 FastAPI, Next.js, Python 스택 위에서 FastAPI 기반 `docs/README.md` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/README.md`, `docs/references`, `docs/CHANGELOG.md`)를 분리해 구성하며 문서 내 주요 섹션(`Auto Author`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `frankbria/auto-author`(TO-BE)에서는 `CLAUDE.md`, `backend/app/main.py`, `docs/README.md` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 Python 기반 `samples` 중심의 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화 (`luworks/today`)

- **출처**: [`luworks/today`](https://github.com/luworks/today) · **핵심 스택**: `Python`, `Claude Code`, `OpenAI SDK`, `SwiftUI` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `tests/performance/compare_app.py` 발췌본을 기반으로 확인되는 `luworks/today` 저장소는 Python, Claude Code, OpenAI SDK 스택 위에서 Python 기반 `samples` 중심의 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/goal-and-rubric.md`)를 분리해 구성하며 핵심 심볼(`samples`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Today — iPhone planner (native app + HTML prototype)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 모바일이나 데스크톱 클라이언트에서 UI 화면 코드 안에 각 AI 벤더 호출과 문서 파싱, 다국어 번역 리소스를 직접 결합하면 앱 빌드 시간과 유지보수 복잡도가 크게 증가합니다. 반면 `luworks/today`(TO-BE)에서는 `CLAUDE.md`, `tests/performance/compare_app.py`, `samples` 등 명시적 아티팩트를 기준으로 UI·AI SDK 추상화·문서 파서·검색 모듈을 다중 모듈 아키텍처로 격리하고 터미널 기반 번역·검증 도구나 시뮬레이터 테스트 규칙을 병행하여 클라이언트 품질을 관리합니다. 다만 네이티브 모듈과 내장 웹/TUI 도구 간 빌드 파이프라인이 나뉘므로 릴리스 아티팩트 패키징과 CI 러너의 리소스 제약을 고려한 테스트 설계가 요구됩니다.

---

### 3.3 Python 기반 `scripts/ci-helpers/list-haf-caches.sh` 모듈 분리와 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`openhive-network/haf`)

- **출처**: [`openhive-network/haf`](https://github.com/openhive-network/haf) · **핵심 스택**: `Python`, `Claude Code`, `PostgreSQL`, `SQLAlchemy` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `src/hive_fork_manager/doc/examples/hive_fork_app.py` 발췌본을 기반으로 확인되는 `openhive-network/haf` 저장소는 Python, Claude Code, PostgreSQL 스택 위에서 Python 기반 `scripts/ci-helpers/list-haf-caches.sh` 모듈 분리와 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/ci-helpers/list-haf-caches.sh`, `scripts/ci-helpers/examples/quick-test-example.gitlab`)를 분리해 구성하며 문서 내 주요 섹션(`HAF (Hive Application Framework) - Claude Code Instructions`, `Quick Test Mode`, `Quick Reference`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `openhive-network/haf`(TO-BE)에서는 `CLAUDE.md`, `src/hive_fork_manager/doc/examples/hive_fork_app.py`, `scripts/ci-helpers/list-haf-caches.sh` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `Vivaliz-site/site-shopvivaliz`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `frankbria/auto-author`의 `CLAUDE.md` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `open-metadata/OpenMetadata`의 `CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-11-02 수집 시점의 공개 저장소 `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
