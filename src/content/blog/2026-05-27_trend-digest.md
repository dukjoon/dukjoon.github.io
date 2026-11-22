---
title: '[Trend] 2026-05-27: Python, Claude Code 기반 계획·실행·검증 에이전트 역할 분리와 모듈형 런타임'
pubDatetime: '2026-05-27T00:00:00Z'
description: 2026-05-27 수집된 repomesh/claude-code-templates, dolunayozerennn/antigravity-egitim, nearai/ironclaw 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- claude-md
- supabase
- stripe
draft: false
---

2026-05-27 수집된 오픈소스 저장소들에서는 Python, Claude Code, Supabase, Stripe 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜 | `repomesh/claude-code-templates`, `dolunayozerennn/antigravity-egitim`, `lopadova/AskMyDocs`, `twowhy-prog/modu-parking`, `mangowhoiscloud/geode` | 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, MCP 도구 스키마 분리 및 런타임 세션 격리, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 |
| 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처 | `nearai/ironclaw` | Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 |

---

## 2. 계층형 서브에이전트 오케스트레이션 및 상태 인계 프로토콜

### 2.1 Python 기반 `npm test` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`repomesh/claude-code-templates`)

- **출처**: [`repomesh/claude-code-templates`](https://github.com/repomesh/claude-code-templates) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `Stripe`, `Pydantic`, `LangGraph` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `cli-tool/components/skills/ai-research/loki-mode/CLAUDE.md` 발췌본을 기반으로 확인되는 `repomesh/claude-code-templates` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `npm test` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/generate_components_json.py`, `docs/components.json`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`npm test`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `repomesh/claude-code-templates`(TO-BE)에서는 `CLAUDE.md`, `cli-tool/components/skills/ai-research/loki-mode/CLAUDE.md`, `npm test` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.2 FastAPI 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`dolunayozerennn/antigravity-egitim`)

- **출처**: [`dolunayozerennn/antigravity-egitim`](https://github.com/dolunayozerennn/antigravity-egitim) · **핵심 스택**: `FastAPI`, `Python`, `MCP`, `Claude Code`, `Cursor Rules`, `Supabase` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `dolunayozerennn/antigravity-egitim` 저장소는 FastAPI, Python, MCP 스택 위에서 FastAPI 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Antigravity — Global AI Kuralları (Tüm Modeller)`, `ZORUNLU İLK ADIM`, `KRİTİK KURALLAR (ÖZET)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `dolunayozerennn/antigravity-egitim`(TO-BE)에서는 `.cursorrules`, `CLAUDE.md` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.3 Claude Code 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`lopadova/AskMyDocs`)

- **출처**: [`lopadova/AskMyDocs`](https://github.com/lopadova/AskMyDocs) · **핵심 스택**: `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.claude/COMPANY-CLAUDE.md`, `.claude/COMPANY-laravel-CLAUDE.md` 발췌본을 기반으로 확인되는 `lopadova/AskMyDocs` 저장소는 Claude Code, OpenAI SDK, Anthropic SDK 스택 위에서 Claude Code 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Company AI Conventions`, `Principi`, `Stile`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `lopadova/AskMyDocs`(TO-BE)에서는 `.claude/COMPANY-CLAUDE.md`, `.claude/COMPANY-laravel-CLAUDE.md` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.4 Python 기반 `docs/index.html` 모듈 분리와 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`twowhy-prog/modu-parking`)

- **출처**: [`twowhy-prog/modu-parking`](https://github.com/twowhy-prog/modu-parking) · **핵심 스택**: `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `main.py` 발췌본을 기반으로 확인되는 `twowhy-prog/modu-parking` 저장소는 Python, Claude Code 스택 위에서 Python 기반 `docs/index.html` 모듈 분리와 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/index.html`)를 분리해 구성하며 문서 내 주요 섹션(`프로젝트 개요`, `실행 방법`, `아키텍처`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `twowhy-prog/modu-parking`(TO-BE)에서는 `CLAUDE.md`, `main.py`, `docs/index.html` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.5 Next.js 기반 `uv sync` 워크플로우 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`mangowhoiscloud/geode`)

- **출처**: [`mangowhoiscloud/geode`](https://github.com/mangowhoiscloud/geode) · **핵심 스택**: `Next.js`, `React`, `Python`, `Claude Code`, `LangGraph`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `site/CLAUDE.md` 발췌본을 기반으로 확인되는 `mangowhoiscloud/geode` 저장소는 Next.js, React, Python 스택 위에서 Next.js 기반 `uv sync` 워크플로우 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/design-md/overview`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`uv sync`, `uv run`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `mangowhoiscloud/geode`(TO-BE)에서는 `CLAUDE.md`, `site/CLAUDE.md`, `uv sync` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

## 3. 풀스택 SaaS 인프라·결제 파이프라인 및 서비스 아키텍처

### 3.1 Rust 기반 `cargo test` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처 (`nearai/ironclaw`)

- **출처**: [`nearai/ironclaw`](https://github.com/nearai/ironclaw) · **핵심 스택**: `Rust`, `Claude Code`, `Stripe`, `PostgreSQL`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `crates/ironclaw_approvals/CLAUDE.md` 발췌본을 기반으로 확인되는 `nearai/ironclaw` 저장소는 Rust, Claude Code, Stripe 스택 위에서 Rust 기반 `cargo test` 워크플로우 기반 관리형 인증·데이터베이스와 결제 웹훅 결합 SaaS 아키텍처을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`tests/e2e/CLAUDE.md`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`cargo test`, `cargo run`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 초기 프로덕션 서비스에서 인증, 데이터베이스 스키마, 결제 상태 동기화 및 AI 기능을 각각 별도 보일러플레이트로 구축하면 트랜잭션 정합성 관리와 배포 리드타임이 길어집니다. 반면 `nearai/ironclaw`(TO-BE)에서는 `CLAUDE.md`, `crates/ironclaw_approvals/CLAUDE.md`, `cargo test` 등 명시적 아티팩트를 기준으로 Supabase 기반 데이터·인증 계층과 Stripe 결제 파이프라인을 모듈 단위로 통합하고 에이전트 지침 파일로 스키마 마이그레이션 및 환경변수 분리 규칙을 강제해 상용화 속도를 높입니다. 다만 외부 관리형 서비스와 결제 웹훅에 의존하는 구조이므로 로컬 테스트 시 웹훅 재시도 멱등성(Idempotency)과 역할 기반 접근 제어(RBAC) 정책을 별도로 검증해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `repomesh/claude-code-templates`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `dolunayozerennn/antigravity-egitim`의 `.cursorrules` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `nearai/ironclaw`의 `CLAUDE.md` 구성처럼 Supabase·Stripe 기반 상태 동기화 및 에이전트 개발 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-05-27 수집 시점의 공개 저장소 `CLAUDE.md`, `.cursorrules`, `.claude/COMPANY-CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
