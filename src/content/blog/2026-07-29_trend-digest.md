---
title: '[Trend] 2026-07-29: Python, MCP 기반 MCP 도구 스키마 분리와 모듈형 런타임'
pubDatetime: '2026-07-29T00:00:00Z'
description: 2026-07-29 수집된 mangowhoiscloud/geode, Misael-art/PhaseZero, joly-os/mmllm 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- python
- mcp
- claude-md
- openai
draft: false
---

2026-07-29 수집된 오픈소스 저장소들에서는 Python, MCP, Claude Code, OpenAI SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처 | `mangowhoiscloud/geode`, `Misael-art/PhaseZero`, `joly-os/mmllm` | MCP 도구 스키마 분리 및 런타임 세션 격리, 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 |
| 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임 | `AnthonyBuisset/domotix`, `techcsd/SGC`, `Open-Locker/Open-Locker` | 네이티브 UI·AI SDK 모듈 분리 및 로컬 리소스 자동화, 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조, 모노레포 패키지 경계 및 공유 상수·타입체크 파이프라인 |

---

## 2. MCP 도구 프로토콜 및 멀티 에이전트 런타임 아키텍처

### 2.1 Python 기반 `uv sync` 워크플로우 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`mangowhoiscloud/geode`)

- **출처**: [`mangowhoiscloud/geode`](https://github.com/mangowhoiscloud/geode) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `uv` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `core/cli/fullscreen_app.py` 발췌본을 기반으로 확인되는 `mangowhoiscloud/geode` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 `uv sync` 워크플로우 기반 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. `CLAUDE.md` 등에 명시된 실행·검증 명령(`uv sync`, `uv run`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `mangowhoiscloud/geode`(TO-BE)에서는 `CLAUDE.md`, `core/cli/fullscreen_app.py`, `uv sync` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.2 Python 기반 `_init_icon_theme` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`Misael-art/PhaseZero`)

- **출처**: [`Misael-art/PhaseZero`](https://github.com/Misael-art/PhaseZero) · **핵심 스택**: `Python`, `Claude Code`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `linux/ui_native/app.py` 발췌본을 기반으로 확인되는 `Misael-art/PhaseZero` 저장소는 Python, Claude Code, Gemini SDK 스택 위에서 Python 기반 `_init_icon_theme` 중심의 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. 핵심 심볼(`_init_icon_theme`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Project shape`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `Misael-art/PhaseZero`(TO-BE)에서는 `CLAUDE.md`, `linux/ui_native/app.py`, `_init_icon_theme` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.3 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`joly-os/mmllm`)

- **출처**: [`joly-os/mmllm`](https://github.com/joly-os/mmllm) · **핵심 스택**: `Python`, `Claude Code` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `modal_app.py` 발췌본을 기반으로 확인되는 `joly-os/mmllm` 저장소는 Python, Claude Code 스택 위에서 Python 기반 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 문서 내 주요 섹션(`Working notes for Claude on this repo`, `Baseline conduct`, `Reporting discipline (post-it note)`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `joly-os/mmllm`(TO-BE)에서는 `CLAUDE.md`, `modal_app.py` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

## 3. 크로스 플랫폼·모바일 에이전트 클라이언트 및 내장 런타임

### 3.1 React 기반 `docs/handbook` 모듈 분리와 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화 (`AnthonyBuisset/domotix`)

- **출처**: [`AnthonyBuisset/domotix`](https://github.com/AnthonyBuisset/domotix) · **핵심 스택**: `React`, `TypeScript`, `Rust`, `Claude Code`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `docs/handbook/CLAUDE.md` 발췌본을 기반으로 확인되는 `AnthonyBuisset/domotix` 저장소는 React, TypeScript, Rust 스택 위에서 React 기반 `docs/handbook` 모듈 분리와 모바일·데스크톱 네이티브 UI와 다중 AI 프로바이더 추상화을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/handbook`, `scripts/deploy.mts`)를 분리해 구성하며 문서 내 주요 섹션(`What this is`, `Commands`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 모바일이나 데스크톱 클라이언트에서 UI 화면 코드 안에 각 AI 벤더 호출과 문서 파싱, 다국어 번역 리소스를 직접 결합하면 앱 빌드 시간과 유지보수 복잡도가 크게 증가합니다. 반면 `AnthonyBuisset/domotix`(TO-BE)에서는 `CLAUDE.md`, `docs/handbook/CLAUDE.md`, `docs/handbook` 등 명시적 아티팩트를 기준으로 UI·AI SDK 추상화·문서 파서·검색 모듈을 다중 모듈 아키텍처로 격리하고 터미널 기반 번역·검증 도구나 시뮬레이터 테스트 규칙을 병행하여 클라이언트 품질을 관리합니다. 다만 네이티브 모듈과 내장 웹/TUI 도구 간 빌드 파이프라인이 나뉘므로 릴리스 아티팩트 패키징과 CI 러너의 리소스 제약을 고려한 테스트 설계가 요구됩니다.

---

### 3.2 TypeScript 기반 `npm run build` 워크플로우 기반 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`techcsd/SGC`)

- **출처**: [`techcsd/SGC`](https://github.com/techcsd/SGC) · **핵심 스택**: `TypeScript`, `Claude Code`, `Supabase`, `Vitest` · **적용 판단**: `Trial`
- **기술 개요**: `.claude/CLAUDE.md`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `techcsd/SGC` 저장소는 TypeScript, Claude Code, Supabase 스택 위에서 TypeScript 기반 `npm run build` 워크플로우 기반 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. `.claude/CLAUDE.md` 등에 명시된 실행·검증 명령(`npm run build`, `npm test`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `techcsd/SGC`(TO-BE)에서는 `.claude/CLAUDE.md`, `CLAUDE.md`, `npm run build` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

### 3.3 React 기반 `packages/locker_api` 모듈 분리와 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리 (`Open-Locker/Open-Locker`)

- **출처**: [`Open-Locker/Open-Locker`](https://github.com/Open-Locker/Open-Locker) · **핵심 스택**: `React`, `TypeScript`, `Claude Code`, `Cursor Rules`, `Docker` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `locker-backend/CLAUDE.md` 발췌본을 기반으로 확인되는 `Open-Locker/Open-Locker` 저장소는 React, TypeScript, Claude Code 스택 위에서 React 기반 `packages/locker_api` 모듈 분리와 모노레포 기반 에이전트 확장 UI와 백그라운드 워커 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`packages/locker_api`)를 분리해 구성하며 문서 내 주요 섹션(`Repository Reality Check`, `CLAUDE.md — locker-backend`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 브라우저 사이드패널, 백그라운드 워커, 콘텐츠 스크립트와 MCP 서버를 개별 저장소나 매직 넘버 위주로 작성하면 포트·타임아웃 불일치와 타입 오류가 빈번하게 발생합니다. 반면 `Open-Locker/Open-Locker`(TO-BE)에서는 `CLAUDE.md`, `locker-backend/CLAUDE.md`, `packages/locker_api` 등 명시적 아티팩트를 기준으로 단일 모노레포 워크스페이스 안에서 엔트리포인트별 역할을 나누고 포트·타임아웃 상수를 공유 패키지로 중앙화하며 푸시 전 통합 린트·타입체크 게이트를 강제합니다. 다만 공유 패키지 수정이 전체 앱 빌드에 영향을 줄 수 있으므로 워크스페이스 패키지 간 의존성 방향을 단방향으로 유지해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `mangowhoiscloud/geode`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `Misael-art/PhaseZero`의 `CLAUDE.md` 구성처럼 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `joly-os/mmllm`의 `CLAUDE.md` 구성처럼 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-07-29 수집 시점의 공개 저장소 `CLAUDE.md` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
