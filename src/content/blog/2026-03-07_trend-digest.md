---
title: '[Trend] 2026-03-07: FastAPI, TypeScript 기반 독립 스킬 디렉터리 격리와 모듈형 런타임'
pubDatetime: '2026-03-07T00:00:00Z'
description: 2026-03-07 수집된 huajunzjg2019-ui/openclaw-cn, macaron-software/software-factory, ClaPalo/raycast-extensions 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- fastapi
- typescript
- python
- claude-md
draft: false
---

2026-03-07 수집된 오픈소스 저장소들에서는 FastAPI, TypeScript, Python, Claude Code 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트 | `huajunzjg2019-ui/openclaw-cn`, `ClaPalo/raycast-extensions`, `qixing-jk/all-api-hub`, `coder/coder` | 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임 | `macaron-software/software-factory`, `polarsource/polar` | 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인 |

---

## 2. 모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트

### 2.1 FastAPI 기반 `ping` 중심의 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`huajunzjg2019-ui/openclaw-cn`)

- **출처**: [`huajunzjg2019-ui/openclaw-cn`](https://github.com/huajunzjg2019-ui/openclaw-cn) · **핵심 스택**: `FastAPI`, `TypeScript`, `Python`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `skills/local-places/src/local_places/main.py` 발췌본을 기반으로 확인되는 `huajunzjg2019-ui/openclaw-cn` 저장소는 FastAPI, TypeScript, Python 스택 위에서 FastAPI 기반 `ping` 중심의 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/cli`, `src/commands`, `src/provider-web.ts`)를 분리해 구성하며 핵심 심볼(`ping`, `validation_exception_handler`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Repository Guidelines`, `Project Structure & Module Organization`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `huajunzjg2019-ui/openclaw-cn`(TO-BE)에서는 `CLAUDE.md`, `skills/local-places/src/local_places/main.py`, `ping` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.2 React 기반 `npm run dev` 워크플로우 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`ClaPalo/raycast-extensions`)

- **출처**: [`ClaPalo/raycast-extensions`](https://github.com/ClaPalo/raycast-extensions) · **핵심 스택**: `React`, `TypeScript`, `Claude Code`, `Supabase`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `extensions/anytype/CLAUDE.md`, `extensions/area-code-lookup/CLAUDE.md` 발췌본을 기반으로 확인되는 `ClaPalo/raycast-extensions` 저장소는 React, TypeScript, Claude Code 스택 위에서 React 기반 `npm run dev` 워크플로우 기반 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/utils/api.test.ts`, `src/api`, `src/components`)를 분리해 구성하며 `extensions/anytype/CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run dev`, `npm run build`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `ClaPalo/raycast-extensions`(TO-BE)에서는 `extensions/anytype/CLAUDE.md`, `extensions/area-code-lookup/CLAUDE.md`, `npm run dev` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 React 기반 `pnpm dev` 워크플로우 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`qixing-jk/all-api-hub`)

- **출처**: [`qixing-jk/all-api-hub`](https://github.com/qixing-jk/all-api-hub) · **핵심 스택**: `React`, `TypeScript`, `Python`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `docs_assistant/main.py` 발췌본을 기반으로 확인되는 `qixing-jk/all-api-hub` 저장소는 React, TypeScript, Python 스택 위에서 React 기반 `pnpm dev` 워크플로우 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. `CLAUDE.md` 등에 명시된 실행·검증 명령(`pnpm dev`, `pnpm dev:firefox`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `qixing-jk/all-api-hub`(TO-BE)에서는 `CLAUDE.md`, `docs_assistant/main.py`, `pnpm dev` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

### 2.4 Claude Code 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`coder/coder`)

- **출처**: [`coder/coder`](https://github.com/coder/coder) · **핵심 스택**: `Claude Code`, `Cursor Rules`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `coder/coder` 저장소는 Claude Code, Cursor Rules, OpenAI SDK 스택 위에서 Claude Code 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Coder Development Guidelines`, `Foundational rules`, `Our relationship`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `coder/coder`(TO-BE)에서는 `.cursorrules`, `CLAUDE.md` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임

### 3.1 FastAPI 기반 `pytest tests` 워크플로우 기반 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화 (`macaron-software/software-factory`)

- **출처**: [`macaron-software/software-factory`](https://github.com/macaron-software/software-factory) · **핵심 스택**: `FastAPI`, `Next.js`, `Python`, `Rust`, `Claude Code`, `Supabase` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `_FINARY/CLAUDE.md` 발췌본을 기반으로 확인되는 `macaron-software/software-factory` 저장소는 FastAPI, Next.js, Python 스택 위에서 FastAPI 기반 `pytest tests` 워크플로우 기반 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`frontend/web`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`pytest tests`, `cargo build`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 모바일이나 데스크톱 클라이언트에서 UI 화면 코드 안에 각 AI 벤더 호출과 문서 파싱, 다국어 번역 리소스를 직접 결합하면 앱 빌드 시간과 유지보수 복잡도가 크게 증가합니다. 반면 `macaron-software/software-factory`(TO-BE)에서는 `CLAUDE.md`, `_FINARY/CLAUDE.md`, `pytest tests` 등 명시적 아티팩트를 기준으로 UI·AI SDK 추상화·문서 파서·검색 모듈을 다중 모듈 아키텍처로 격리하고 터미널 기반 번역·검증 도구나 시뮬레이터 테스트 규칙을 병행하여 클라이언트 품질을 관리합니다. 다만 네이티브 모듈과 내장 웹/TUI 도구 간 빌드 파이프라인이 나뉘므로 릴리스 아티팩트 패키징과 CI 러너의 리소스 제약을 고려한 테스트 설계가 요구됩니다.

---

### 3.2 FastAPI 기반 `docker compose up` 워크플로우 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`polarsource/polar`)

- **출처**: [`polarsource/polar`](https://github.com/polarsource/polar) · **핵심 스택**: `FastAPI`, `Next.js`, `React`, `TypeScript`, `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `clients/CLAUDE.md` 발췌본을 기반으로 확인되는 `polarsource/polar` 저장소는 FastAPI, Next.js, React 스택 위에서 FastAPI 기반 `docker compose up` 워크플로우 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`server/polar`, `server/CLAUDE.md`, `apps/web`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`docker compose up`, `uv sync`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `polarsource/polar`(TO-BE)에서는 `CLAUDE.md`, `clients/CLAUDE.md`, `docker compose up` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `huajunzjg2019-ui/openclaw-cn`의 `CLAUDE.md` 구성처럼 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `macaron-software/software-factory`의 `CLAUDE.md` 구성처럼 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `ClaPalo/raycast-extensions`의 `extensions/anytype/CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-03-07 수집 시점의 공개 저장소 `CLAUDE.md`, `extensions/anytype/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
