---
title: '[Trend] 2026-05-14: Next.js, React 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-05-14T00:00:00Z'
description: 2026-05-14 수집된 elizaOS/eliza, AoYuharu/Goharu, jesposito/translarr 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- nextjs
- react
- typescript
- mcp
draft: false
---

2026-05-14 수집된 오픈소스 저장소들에서는 Next.js, React, TypeScript, MCP 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `elizaOS/eliza`, `jyoung122/vss-rt-cv-pot`, `thealtoclef/risingwave`, `A-Ginger-Fox/Remo-World` | MCP 도구 스키마 분리 및 런타임 세션 격리, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 |
| 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임 | `AoYuharu/Goharu`, `jesposito/translarr` | 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화, FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 Next.js 기반 `make comments` 워크플로우 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`elizaOS/eliza`)

- **출처**: [`elizaOS/eliza`](https://github.com/elizaOS/eliza) · **핵심 스택**: `Next.js`, `React`, `TypeScript`, `MCP`, `Claude Code`, `Cursor Rules` · **적용 판단**: `Trial`
- **기술 개요**: `cloud/.cursorrules`, `cloud/CLAUDE.md` 발췌본을 기반으로 확인되는 `elizaOS/eliza` 저장소는 Next.js, React, TypeScript 스택 위에서 Next.js 기반 `make comments` 워크플로우 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. `cloud/.cursorrules` 등에 명시된 실행·검증 명령(`make comments`, `bun run dev`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `elizaOS/eliza`(TO-BE)에서는 `cloud/.cursorrules`, `cloud/CLAUDE.md`, `make comments` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 Python 기반 `EndpointError` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`jyoung122/vss-rt-cv-pot`)

- **출처**: [`jyoung122/vss-rt-cv-pot`](https://github.com/jyoung122/vss-rt-cv-pot) · **핵심 스택**: `Python`, `Claude Code`, `Supabase`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `_Trash/main.py` 발췌본을 기반으로 확인되는 `jyoung122/vss-rt-cv-pot` 저장소는 Python, Claude Code, Supabase 스택 위에서 Python 기반 `EndpointError` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`frontend/.next`, `frontend/tsconfig.json`)를 분리해 구성하며 핵심 심볼(`EndpointError`, `__init__`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run build`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `jyoung122/vss-rt-cv-pot`(TO-BE)에서는 `CLAUDE.md`, `_Trash/main.py`, `npm run build` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.3 Python 기반 `create_benchmark_script` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`thealtoclef/risingwave`)

- **출처**: [`thealtoclef/risingwave`](https://github.com/thealtoclef/risingwave) · **핵심 스택**: `Python`, `Rust`, `Claude Code`, `PostgreSQL`, `OpenAI SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `develop/sql_bench/main.py` 발췌본을 기반으로 확인되는 `thealtoclef/risingwave` 저장소는 Python, Rust, Claude Code 스택 위에서 Python 기반 `create_benchmark_script` 중심의 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`create_benchmark_script`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Coding Agent Instructions for RisingWave`, `Coding Style`, `Benchmark configuration`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `thealtoclef/risingwave`(TO-BE)에서는 `CLAUDE.md`, `develop/sql_bench/main.py`, `create_benchmark_script` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.4 Claude Code 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`A-Ginger-Fox/Remo-World`)

- **출처**: [`A-Ginger-Fox/Remo-World`](https://github.com/A-Ginger-Fox/Remo-World) · **핵심 스택**: `Claude Code`, `Supabase`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `memory/synthesis/normalized/CLAUDE.md.json` 발췌본을 기반으로 확인되는 `A-Ginger-Fox/Remo-World` 저장소는 Claude Code, Supabase, OpenAI SDK 스택 위에서 Claude Code 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`REMO-WORLD — Claude Code Harness Instructions`, `System Identity`, `Governing Documents`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `A-Ginger-Fox/Remo-World`(TO-BE)에서는 `CLAUDE.md`, `memory/synthesis/normalized/CLAUDE.md.json` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

## 3. 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임

### 3.1 Python 기반 `TableHelperTUI` 중심의 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화 (`AoYuharu/Goharu`)

- **출처**: [`AoYuharu/Goharu`](https://github.com/AoYuharu/Goharu) · **핵심 스택**: `Python`, `Claude Code`, `Docker`, `OpenAI SDK`, `Anthropic SDK`, `pytest` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `TUI/app.py` 발췌본을 기반으로 확인되는 `AoYuharu/Goharu` 저장소는 Python, Claude Code, Docker 스택 위에서 Python 기반 `TableHelperTUI` 중심의 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화을(를) 구현한 프로젝트입니다. 핵심 심볼(`TableHelperTUI`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`pytest`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 모바일이나 데스크톱 클라이언트에서 UI 화면 코드 안에 각 AI 벤더 호출과 문서 파싱, 다국어 번역 리소스를 직접 결합하면 앱 빌드 시간과 유지보수 복잡도가 크게 증가합니다. 반면 `AoYuharu/Goharu`(TO-BE)에서는 `CLAUDE.md`, `TUI/app.py`, `pytest` 등 명시적 아티팩트를 기준으로 UI·AI SDK 추상화·문서 파서·검색 모듈을 다중 모듈 아키텍처로 격리하고 터미널 기반 번역·검증 도구나 시뮬레이터 테스트 규칙을 병행하여 클라이언트 품질을 관리합니다. 다만 네이티브 모듈과 내장 웹/TUI 도구 간 빌드 파이프라인이 나뉘므로 릴리스 아티팩트 패키징과 CI 러너의 리소스 제약을 고려한 테스트 설계가 요구됩니다.

---

### 3.2 FastAPI 기반 `lifespan` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화 (`jesposito/translarr`)

- **출처**: [`jesposito/translarr`](https://github.com/jesposito/translarr) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `SQLite`, `Docker`, `OpenAI SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `server/main.py` 발췌본을 기반으로 확인되는 `jesposito/translarr` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `lifespan` 중심의 비동기 API 엔트리포인트와 코어 도메인 엔진 모듈화을(를) 구현한 프로젝트입니다. 핵심 심볼(`lifespan`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Translarr — Project Instructions`, `Stance — read before doing anything`, `Hard constraints`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 HTTP 라우터 안에 무거운 추론·데이터 수집·비즈니스 규칙을 한꺼번에 배치하면 요청 블로킹이 발생하고 선택적 모듈 장애가 전체 API 서버 중단으로 번지기 쉽습니다. 반면 `jesposito/translarr`(TO-BE)에서는 `CLAUDE.md`, `server/main.py`, `lifespan` 등 명시적 아티팩트를 기준으로 API 엔트리포인트와 코어 도메인 엔진·비동기 태스크를 분리하고 의존성 로드 실패 시의 폴백(Fallback) 및 요청 검증 예외 핸들러를 명시하여 운영 복원력을 확보합니다. 다만 비동기 태스크와 외부 스토리지 간 커넥션 풀 관리나 백그라운드 예외 전파가 누락될 수 있어 기동 시점 헬스체크와 구조화된 로깅 설정을 반드시 동반해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `elizaOS/eliza`의 `cloud/.cursorrules` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `AoYuharu/Goharu`의 `CLAUDE.md` 구성처럼 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `jesposito/translarr`의 `CLAUDE.md` 구성처럼 FastAPI 비동기 계층 분리 및 모듈별 예외·기동 가드레일 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-05-14 수집 시점의 공개 저장소 `cloud/.cursorrules`, `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
