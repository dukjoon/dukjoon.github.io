---
title: '[Trend] 2026-10-20: Claude Code, Supabase 기반 독립 스킬 디렉터리 격리와 모듈형 런타임'
pubDatetime: '2026-10-20T00:00:00Z'
description: 2026-10-20 수집된 alexey-orlov/AO-Personal-OS, Ninni-71/Artcraft, janbkrejci/HAIFA 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- claude-md
- supabase
- stripe
- openai
draft: false
---

2026-10-20 수집된 오픈소스 저장소들에서는 Claude Code, Supabase, Stripe, OpenAI SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트 | `alexey-orlov/AO-Personal-OS`, `janbkrejci/HAIFA`, `koda-ai-studio/agent-bom` | 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 브라우저 확장·모노레포 워크스페이스 및 공유 상수 아키텍처 | `Ninni-71/Artcraft`, `omii2691/Claude`, `achimdehnert/platform` | 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인, 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. 모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트

### 2.1 Claude Code 기반 `skills/message-writing` 모듈 분리와 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`alexey-orlov/AO-Personal-OS`)

- **출처**: [`alexey-orlov/AO-Personal-OS`](https://github.com/alexey-orlov/AO-Personal-OS) · **핵심 스택**: `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `automations/call-pipeline/CLAUDE.md` 발췌본을 기반으로 확인되는 `alexey-orlov/AO-Personal-OS` 저장소는 Claude Code, Supabase, Stripe 스택 위에서 Claude Code 기반 `skills/message-writing` 모듈 분리와 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`skills/message-writing`)를 분리해 구성하며 문서 내 주요 섹션(`AO-Personal-OS — agent working notes`, `Message-writing skill preference`, `call-pipeline — agent notes`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `alexey-orlov/AO-Personal-OS`(TO-BE)에서는 `CLAUDE.md`, `automations/call-pipeline/CLAUDE.md`, `skills/message-writing` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.2 Python 기반 `pytest` 워크플로우 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`janbkrejci/HAIFA`)

- **출처**: [`janbkrejci/HAIFA`](https://github.com/janbkrejci/HAIFA) · **핵심 스택**: `Python`, `Claude Code`, `OpenAI SDK`, `Gemini SDK`, `uv`, `Playwright` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `aifactory/src/aifactory/web/app.py` 발췌본을 기반으로 확인되는 `janbkrejci/HAIFA` 저장소는 Python, Claude Code, OpenAI SDK 스택 위에서 Python 기반 `pytest` 워크플로우 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`tests/backlog/test_backlog_cli.py`, `api/health`, `api/runs`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`pytest`, `pytest args`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `janbkrejci/HAIFA`(TO-BE)에서는 `CLAUDE.md`, `aifactory/src/aifactory/web/app.py`, `pytest` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 Python 기반 `_query` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`koda-ai-studio/agent-bom`)

- **출처**: [`koda-ai-studio/agent-bom`](https://github.com/koda-ai-studio/agent-bom) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `Docker`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `deploy/snowflake/streamlit_app.py` 발췌본을 기반으로 확인되는 `koda-ai-studio/agent-bom` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `_query` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 핵심 심볼(`_query`, `load_jobs`, `load_fleet`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Claude-specific addendum`, `Memory`, `Too`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `koda-ai-studio/agent-bom`(TO-BE)에서는 `CLAUDE.md`, `deploy/snowflake/streamlit_app.py`, `_query` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 브라우저 확장·모노레포 워크스페이스 및 공유 상수 아키텍처

### 3.1 TypeScript 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`Ninni-71/Artcraft`)

- **출처**: [`Ninni-71/Artcraft`](https://github.com/Ninni-71/Artcraft) · **핵심 스택**: `TypeScript`, `Rust`, `Claude Code`, `Stripe`, `SQLite`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `crates/CLAUDE.md` 발췌본을 기반으로 확인되는 `Ninni-71/Artcraft` 저장소는 TypeScript, Rust, Claude Code 스택 위에서 TypeScript 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Project Structure`, `Rust Workspace`, `Code Style`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `Ninni-71/Artcraft`(TO-BE)에서는 `CLAUDE.md`, `crates/CLAUDE.md` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

### 3.2 Claude Code 기반 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`omii2691/Claude`)

- **출처**: [`omii2691/Claude`](https://github.com/omii2691/Claude) · **핵심 스택**: `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `docs/i18n/ar/CLAUDE.md` 발췌본을 기반으로 확인되는 `omii2691/Claude` 저장소는 Claude Code, OpenAI SDK, Anthropic SDK 스택 위에서 Claude Code 기반 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Worktree isolation — Claude Code specifics`, `CLAUDE.md (العربية)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `omii2691/Claude`(TO-BE)에서는 `CLAUDE.md`, `docs/i18n/ar/CLAUDE.md` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

### 3.3 Python 기반 `_apps_py` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`achimdehnert/platform`)

- **출처**: [`achimdehnert/platform`](https://github.com/achimdehnert/platform) · **핵심 스택**: `Python`, `Claude Code`, `Anthropic SDK`, `Django` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `scripts/gen_django_app.py` 발췌본을 기반으로 확인되는 `achimdehnert/platform` 저장소는 Python, Claude Code, Anthropic SDK 스택 위에서 Python 기반 `_apps_py` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`tests/test_`)를 분리해 구성하며 핵심 심볼(`_apps_py`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Platform — Repo Context`, `️ Dieses Repo ist ÖFFENTLICH`, `── Templates ───────────────────────────────────────────────`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `achimdehnert/platform`(TO-BE)에서는 `CLAUDE.md`, `scripts/gen_django_app.py`, `_apps_py` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `alexey-orlov/AO-Personal-OS`의 `CLAUDE.md` 구성처럼 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `Ninni-71/Artcraft`의 `CLAUDE.md` 구성처럼 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `janbkrejci/HAIFA`의 `CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-10-20 수집 시점의 공개 저장소 `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
