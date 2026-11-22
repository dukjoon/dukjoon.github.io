---
title: '[Trend] 2026-07-06: Python, Claude Code 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-07-06T00:00:00Z'
description: 2026-07-06 수집된 Hecpac/Dr.-strange, dancinlab/hexa-lang, khalidbelhadj/reading-list 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- claude-md
- langgraph
- openai
draft: false
---

2026-07-06 수집된 오픈소스 저장소들에서는 Python, Claude Code, LangGraph, OpenAI SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `Hecpac/Dr.-strange`, `LMU-ISBA/ai-dev-workflow-tutorial-2026070401` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `dancinlab/hexa-lang`, `khalidbelhadj/reading-list`, `Mu-L/fury`, `sige0002/kairos` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인, 정적 타입 계약 기반 런타임 분리 및 빌드·검증 파이프라인, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 Python 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`Hecpac/Dr.-strange`)

- **출처**: [`Hecpac/Dr.-strange`](https://github.com/Hecpac/Dr.-strange) · **핵심 스택**: `Python`, `Claude Code`, `LangGraph`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `claw_v2/main.py` 발췌본을 기반으로 확인되는 `Hecpac/Dr.-strange` 저장소는 Python, Claude Code, LangGraph 스택 위에서 Python 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Your role here (read before anything else)`, `Regla de arranque (siempre activa)`, `Forward-ref only: ToolRegistry is imported lazily inside the`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `Hecpac/Dr.-strange`(TO-BE)에서는 `CLAUDE.md`, `claw_v2/main.py` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 Python 기반 `get_data` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`LMU-ISBA/ai-dev-workflow-tutorial-2026070401`)

- **출처**: [`LMU-ISBA/ai-dev-workflow-tutorial-2026070401`](https://github.com/LMU-ISBA/ai-dev-workflow-tutorial-2026070401) · **핵심 스택**: `Python`, `Claude Code`, `pytest` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `app.py` 발췌본을 기반으로 확인되는 `LMU-ISBA/ai-dev-workflow-tutorial-2026070401` 저장소는 Python, Claude Code, pytest 스택 위에서 Python 기반 `get_data` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 핵심 심볼(`get_data`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`pytest`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `LMU-ISBA/ai-dev-workflow-tutorial-2026070401`(TO-BE)에서는 `CLAUDE.md`, `app.py`, `pytest` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 Claude Code 기반 `docs/hypotheses` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`dancinlab/hexa-lang`)

- **출처**: [`dancinlab/hexa-lang`](https://github.com/dancinlab/hexa-lang) · **핵심 스택**: `Claude Code`, `Stripe`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `ATLAS/CLAUDE.md`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `dancinlab/hexa-lang` 저장소는 Claude Code, Stripe, OpenAI SDK 스택 위에서 Claude Code 기반 `docs/hypotheses` 모듈 분리와 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/hypotheses`)를 분리해 구성하며 문서 내 주요 섹션(`ATLAS — domain guide (sub-CLAUDE · formerly TECS-L, renamed `, `What is this directory`, `hexa-lang`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `dancinlab/hexa-lang`(TO-BE)에서는 `ATLAS/CLAUDE.md`, `CLAUDE.md`, `docs/hypotheses` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

### 3.2 TypeScript 기반 `make_sample` 중심의 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`khalidbelhadj/reading-list`)

- **출처**: [`khalidbelhadj/reading-list`](https://github.com/khalidbelhadj/reading-list) · **핵심 스택**: `TypeScript`, `Python`, `Claude Code`, `Supabase`, `uv`, `Bun` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `analysis/main.py` 발췌본을 기반으로 확인되는 `khalidbelhadj/reading-list` 저장소는 TypeScript, Python, Claude Code 스택 위에서 TypeScript 기반 `make_sample` 중심의 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`make_sample`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`bun run check`, `bun run typecheck`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `khalidbelhadj/reading-list`(TO-BE)에서는 `CLAUDE.md`, `analysis/main.py`, `bun run check` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

### 3.3 Python 기반 `docs/security/index.md` 모듈 분리와 컴파일 타임 타입 안전성과 고성능 시스템 런타임 설계 (`Mu-L/fury`)

- **출처**: [`Mu-L/fury`](https://github.com/Mu-L/fury) · **핵심 스택**: `Python`, `Rust`, `Claude Code`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `python/pyfory/tests/xlang_test_main.py` 발췌본을 기반으로 확인되는 `Mu-L/fury` 저장소는 Python, Rust, Claude Code 스택 위에서 Python 기반 `docs/security/index.md` 모듈 분리와 컴파일 타임 타입 안전성과 고성능 시스템 런타임 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/security/index.md`, `docs/security/threat-model.md`, `docs/security/deserialization.md`)를 분리해 구성하며 문서 내 주요 섹션(`Load Additional Guidance On Demand`, `Licensed to the Apache Software Foundation (ASF) under one`, `or more contributor license agreements. See the NOTICE file`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 고빈도 입출력이나 프로세스 체크포인팅, 동시성 처리를 동적 스크립트 단일 계층으로만 처리하면 런타임 오류와 메모리·지연 시간 병목을 조기에 통제하기 어렵습니다. 반면 `Mu-L/fury`(TO-BE)에서는 `CLAUDE.md`, `python/pyfory/tests/xlang_test_main.py`, `docs/security/index.md` 등 명시적 아티팩트를 기준으로 핵심 실행 경로와 상태 덤프·복원 또는 API 계약을 시스템 언어와 벤치마크 도구로 격리하고 재현 가능한 측정·빌드 절차를 문서에 고정하여 런타임 신뢰성을 높입니다. 다만 커널·네이티브 의존성이나 다중 언어 툴체인 유지에 따른 환경 제약이 존재하므로 컨테이너 격리와 플랫폼별 호환성 검증을 선행해야 합니다.

---

### 3.4 FastAPI 기반 `make design` 워크플로우 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`sige0002/kairos`)

- **출처**: [`sige0002/kairos`](https://github.com/sige0002/kairos) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Docker` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `libs/kairos_common/src/kairos_common/app.py` 발췌본을 기반으로 확인되는 `sige0002/kairos` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `make design` 워크플로우 기반 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/specs/ja`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`make design`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `sige0002/kairos`(TO-BE)에서는 `CLAUDE.md`, `libs/kairos_common/src/kairos_common/app.py`, `make design` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `Hecpac/Dr.-strange`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `dancinlab/hexa-lang`의 `ATLAS/CLAUDE.md` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `khalidbelhadj/reading-list`의 `CLAUDE.md` 구성처럼 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-06 수집 시점의 공개 저장소 `CLAUDE.md`, `ATLAS/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
