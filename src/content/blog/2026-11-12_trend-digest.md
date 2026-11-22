---
title: '[Trend] 2026-11-12: Claude Code, Supabase 기반 네이티브 UI·AI SDK 모듈 분리와 모듈형 런타임'
pubDatetime: '2026-11-12T00:00:00Z'
description: 2026-11-12 수집된 samuelclay/NewsBlur, mbadali25/useful-claude-add-ons, slopus/happy-agent 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- claude-md
- supabase
- stripe
- openai
draft: false
---

2026-11-12 수집된 오픈소스 저장소들에서는 Claude Code, Supabase, Stripe, OpenAI SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `mbadali25/useful-claude-add-ons`, `slopus/happy-agent`, `dlunev/criu` | MCP 도구 스키마 분리 및 런타임 세션 격리, 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 |
| 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임 | `samuelclay/NewsBlur`, `browseros-ai/BrowserOS`, `Xinbeok/Relax` | 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인, Ray 기반 분산 오케스트레이션 및 학습·추론 엔진 계층화 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 Python 기반 `scripts/check-marketplace.py` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`mbadali25/useful-claude-add-ons`)

- **출처**: [`mbadali25/useful-claude-add-ons`](https://github.com/mbadali25/useful-claude-add-ons) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `plugin/ai-connect/client/mcp_app.py` 발췌본을 기반으로 확인되는 `mbadali25/useful-claude-add-ons` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 `scripts/check-marketplace.py` 모듈 분리와 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`scripts/check-marketplace.py`, `scripts/gate-runner.py`)를 분리해 구성하며 문서 내 주요 섹션(`Commands - build, test, verify, regression, promote`, `Claude Code: the AI-Connect plugin's hooks run the watcher, `, `session when a message arrives. Other MCP clients call peer_`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `mbadali25/useful-claude-add-ons`(TO-BE)에서는 `CLAUDE.md`, `plugin/ai-connect/client/mcp_app.py`, `scripts/check-marketplace.py` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 TypeScript 기반 `docs/plans` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합 (`slopus/happy-agent`)

- **출처**: [`slopus/happy-agent`](https://github.com/slopus/happy-agent) · **핵심 스택**: `TypeScript`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `packages/happy-providers/VENDOR_CLAUDE.md` 발췌본을 기반으로 확인되는 `slopus/happy-agent` 저장소는 TypeScript, Claude Code, OpenAI SDK 스택 위에서 TypeScript 기반 `docs/plans` 모듈 분리와 다중 LLM 프로바이더 라우팅과 에이전트 작업 규약 통합을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/plans`, `tests/vendors/fixtures/claude-multiturn.json`, `tests/vendors/fixtures/claude-provider-multiturn`)를 분리해 구성하며 문서 내 주요 섹션(`Agent Instructions`, `Master plans`, `Claude Agent SDK transport`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 LLM 벤더 SDK에 비즈니스 로직이 강하게 결합되고 코딩 에이전트에게 구두 프롬프트로만 아키텍처 규칙을 전달하면 모델 전환이나 장기 세션에서 코드 일관성이 쉽게 무너집니다. 반면 `slopus/happy-agent`(TO-BE)에서는 `CLAUDE.md`, `packages/happy-providers/VENDOR_CLAUDE.md`, `docs/plans` 등 명시적 아티팩트를 기준으로 OpenAI·Anthropic·Gemini 등을 추상화한 프로바이더 계층을 두고 저장소 루트 규칙 파일에 빌드·테스트 명령과 모듈 경계를 명시하여 에이전트 협업의 재현성을 높입니다. 다만 다중 모델 지원에 따른 프롬프트·토큰 특성 차이와 규칙 문서 드리프트를 방지하기 위해 CI 파이프라인에서 계약 테스트와 문서 최신성 검증을 병행해야 합니다.

---

### 2.3 Python 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`dlunev/criu`)

- **출처**: [`dlunev/criu`](https://github.com/dlunev/criu) · **핵심 스택**: `Python`, `Claude Code`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `contrib/compression-benchmark/main.py` 발췌본을 기반으로 확인되는 `dlunev/criu` 저장소는 Python, Claude Code, Gemini SDK 스택 위에서 Python 기반 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`CRIU (Checkpoint/Restore In User-space)`, `Quick Start`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `dlunev/criu`(TO-BE)에서는 `CLAUDE.md`, `contrib/compression-benchmark/main.py` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

## 3. 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임

### 3.1 Claude Code 기반 `xcodebuild` 워크플로우 기반 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화 (`samuelclay/NewsBlur`)

- **출처**: [`samuelclay/NewsBlur`](https://github.com/samuelclay/NewsBlur) · **핵심 스택**: `Claude Code`, `Supabase`, `Stripe`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `clients/ios/CLAUDE.md` 발췌본을 기반으로 확인되는 `samuelclay/NewsBlur` 저장소는 Claude Code, Supabase, Stripe 스택 위에서 Claude Code 기반 `xcodebuild` 워크플로우 기반 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화을(를) 구현한 프로젝트입니다. `CLAUDE.md` 등에 명시된 실행·검증 명령(`xcodebuild`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 모바일이나 데스크톱 클라이언트에서 UI 화면 코드 안에 각 AI 벤더 호출과 문서 파싱, 다국어 번역 리소스를 직접 결합하면 앱 빌드 시간과 유지보수 복잡도가 크게 증가합니다. 반면 `samuelclay/NewsBlur`(TO-BE)에서는 `CLAUDE.md`, `clients/ios/CLAUDE.md`, `xcodebuild` 등 명시적 아티팩트를 기준으로 UI·AI SDK 추상화·문서 파서·검색 모듈을 다중 모듈 아키텍처로 격리하고 터미널 기반 번역·검증 도구나 시뮬레이터 테스트 규칙을 병행하여 클라이언트 품질을 관리합니다. 다만 네이티브 모듈과 내장 웹/TUI 도구 간 빌드 파이프라인이 나뉘므로 릴리스 아티팩트 패키징과 CI 러너의 리소스 제약을 고려한 테스트 설계가 요구됩니다.

---

### 3.2 React 기반 `bun run check` 워크플로우 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`browseros-ai/BrowserOS`)

- **출처**: [`browseros-ai/BrowserOS`](https://github.com/browseros-ai/BrowserOS) · **핵심 스택**: `React`, `TypeScript`, `MCP`, `Claude Code`, `Supabase`, `Stripe` · **적용 판단**: `Trial`
- **기술 개요**: `packages/browseros-agent/CLAUDE.md`, `packages/browseros-agent/apps/app/CLAUDE.md` 발췌본을 기반으로 확인되는 `browseros-ai/BrowserOS` 저장소는 React, TypeScript, MCP 스택 위에서 React 기반 `bun run check` 워크플로우 기반 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`apps/app`)를 분리해 구성하며 `packages/browseros-agent/CLAUDE.md` 등에 명시된 실행·검증 명령(`bun run check`, `bun run test`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `browseros-ai/BrowserOS`(TO-BE)에서는 `packages/browseros-agent/CLAUDE.md`, `packages/browseros-agent/apps/app/CLAUDE.md`, `bun run check` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

### 3.3 FastAPI 기반 `create_app` 중심의 분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리 (`Xinbeok/Relax`)

- **출처**: [`Xinbeok/Relax`](https://github.com/Xinbeok/Relax) · **핵심 스택**: `FastAPI`, `Python`, `Claude Code`, `Anthropic SDK`, `PyTorch`, `Ray` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `examples/nemo_gym_agentic/service/app.py` 발췌본을 기반으로 확인되는 `Xinbeok/Relax` 저장소는 FastAPI, Python, Claude Code 스택 위에서 FastAPI 기반 `create_app` 중심의 분산 액터 기반 롤아웃 생성과 학습·추론 백엔드 분리을(를) 구현한 프로젝트입니다. 핵심 심볼(`create_app`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Relax`, `Project Structure`, `Copyright (c) 2026 Relax Authors. All Rights Reserved`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 언어모델의 강화학습(RL)이나 고속 추론 서버에서 롤아웃 생성, 보상 계산, 가중치 동기화를 단일 스크립트로 묶으면 GPU 유휴 시간과 체크포인트 병목이 심각해집니다. 반면 `Xinbeok/Relax`(TO-BE)에서는 `CLAUDE.md`, `examples/nemo_gym_agentic/service/app.py`, `create_app` 등 명시적 아티팩트를 기준으로 오케스트레이션 코어, 추론 엔진(SGLang/vLLM), 학습 백엔드(Megatron), 분산 체크포인트 서비스를 계층별로 분리하고 게이트웨이 어댑터로 실험 프로토콜을 표준화합니다. 다만 다중 노드 클러스터와 GPU 메모리 토폴로지에 민감하므로 단위 컴포넌트 모킹 테스트와 실제 분산 환경의 가중치 변환 회귀 테스트를 이원화해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `samuelclay/NewsBlur`의 `CLAUDE.md` 구성처럼 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `mbadali25/useful-claude-add-ons`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `slopus/happy-agent`의 `CLAUDE.md` 구성처럼 멀티 LLM 어댑터 추상화 및 CLAUDE.md 작업 규율 고정 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-11-12 수집 시점의 공개 저장소 `CLAUDE.md`, `packages/browseros-agent/CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
