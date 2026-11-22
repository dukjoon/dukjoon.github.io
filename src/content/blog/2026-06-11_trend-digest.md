---
title: '[Trend] 2026-06-11: TypeScript, Claude Code 기반 독립 스킬 디렉터리 격리와 모듈형 런타임'
pubDatetime: '2026-06-11T00:00:00Z'
description: 2026-06-11 수집된 henglihengli/openclaw, xiezg247/zak, lbliii/bengal 등 오픈소스 저장소의 아키텍처 경계, 에이전트 규칙 및 실무 적용 패턴을 분석합니다.
category: trend
tags:
- trend
- typescript
- claude-md
- openai
- anthropic
draft: false
---

2026-06-11 수집된 오픈소스 저장소들에서는 TypeScript, Claude Code, OpenAI SDK, Anthropic SDK 스택을 중심으로 에이전트 협업 규칙(`CLAUDE.md`, `.cursorrules`)을 코드베이스에 내재화하고, 비동기 API·도구 프로토콜·도메인 실행 모듈의 경계를 명확히 분리하는 엔지니어링 패턴이 확인됩니다. 각 저장소의 실제 설정과 엔트리포인트 발췌본을 바탕으로 실무 도입 시의 구조적 이점과 트레이드오프를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트 | `henglihengli/openclaw`, `xiezg247/zak`, `lbliii/bengal`, `VitorMRodovalho/ai-pm-research-hub`, `FOI-Bioinformatics/nanometa_live` | 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트, 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화, MCP 도구 스키마 분리 및 런타임 세션 격리, 계획·실행·검증 에이전트 역할 분리 및 컨텍스트 예산 관리, DDD 기반 API·워커 분리 및 RAG 파이프라인 모듈화 |
| 오픈소스 모듈러 아키텍처 및 도메인 워크플로우 자동화 | `fredericlepied/ai-assist` | 핵심 도메인 모듈 격리 및 표준화된 로컬 실행·검증 구조 |

---

## 2. 모듈형 에이전트 스킬·플러그인 레지스트리 및 검증 게이트

### 2.1 TypeScript 기반 `pnpm docs:list` 워크플로우 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증 (`henglihengli/openclaw`)

- **출처**: [`henglihengli/openclaw`](https://github.com/henglihengli/openclaw) · **핵심 스택**: `TypeScript`, `Claude Code`, `OpenAI SDK`, `Anthropic SDK`, `Gemini SDK`, `pnpm` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `docs/CLAUDE.md` 발췌본을 기반으로 확인되는 `henglihengli/openclaw` 저장소는 TypeScript, Claude Code, OpenAI SDK 스택 위에서 TypeScript 기반 `pnpm docs:list` 워크플로우 기반 플러그인·스킬 패키지 분리와 매니페스트 정합성 검증을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`src/index.ts`, `services/providers`)를 분리해 구성하며 `CLAUDE.md` 등에 명시된 실행·검증 명령(`pnpm docs:list`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트 확장 스킬과 훅 스크립트를 루트 프로젝트 의존성에 뒤섞어 관리하면 플러그인 간 패키지 충돌과 버전 드리프트를 추적하기 어렵습니다. 반면 `henglihengli/openclaw`(TO-BE)에서는 `CLAUDE.md`, `docs/CLAUDE.md`, `pnpm docs:list` 등 명시적 아티팩트를 기준으로 개별 스킬과 플러그인을 독립 워크스페이스 패키지로 격리하고 단일 매니페스트 검증 스크립트로 설치 스크립트 쌍과 종료 코드를 사전 점검해 확장 생태계의 안정성을 지킵니다. 다만 플러그인별 독립 매니페스트를 유지해야 하므로 공통 유틸리티 변경 시 버전 동기화 자동화 스크립트가 뒷받침되어야 합니다.

---

### 2.2 TypeScript 기반 `AshareCtaBacktesterApp` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화 (`xiezg247/zak`)

- **출처**: [`xiezg247/zak`](https://github.com/xiezg247/zak) · **핵심 스택**: `TypeScript`, `Python`, `Cursor Rules`, `Docker`, `WebSocket` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `packages/vnpy-ashare/vnpy_ashare/backtest/app.py` 발췌본을 기반으로 확인되는 `xiezg247/zak` 저장소는 TypeScript, Python, Cursor Rules 스택 위에서 TypeScript 기반 `AshareCtaBacktesterApp` 중심의 선언적 에이전트 규칙 파일과 디렉터리별 작업 경계 구조화을(를) 구현한 프로젝트입니다. 핵심 심볼(`AshareCtaBacktesterApp`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Commit Message Rules`, `language`, `format`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 대규모 코드베이스에서 AI 코딩 에이전트가 프로젝트 고유 컨벤션이나 테스트 실행 방식을 모른 채 수정을 반복하면 불필요한 전체 빌드와 회귀 버그가 누적됩니다. 반면 `xiezg247/zak`(TO-BE)에서는 `.cursorrules`, `packages/vnpy-ashare/vnpy_ashare/backtest/app.py`, `AshareCtaBacktesterApp` 등 명시적 아티팩트를 기준으로 저장소 내 에이전트 규칙 문서에 아키텍처 디렉터리 구조, 필수 검증 커맨드, 금지 패턴을 선언적으로 정의하여 에이전트가 최소 컨텍스트만으로 정확한 수정·검증 루프를 수행하게 합니다. 다만 코드 구조가 변경될 때 에이전트 규칙 문서가 함께 갱신되지 않으면 오히려 잘못된 경로·명령을 유도할 수 있으므로 PR 리뷰에서 규칙 파일 동기화를 함께 점검해야 합니다.

---

### 2.3 Python 기반 `BengalCLI` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계 (`lbliii/bengal`)

- **출처**: [`lbliii/bengal`](https://github.com/lbliii/bengal) · **핵심 스택**: `Python`, `MCP`, `Claude Code`, `Gemini SDK` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `bengal/cli/milo_app.py` 발췌본을 기반으로 확인되는 `lbliii/bengal` 저장소는 Python, MCP, Claude Code 스택 위에서 Python 기반 `BengalCLI` 중심의 MCP 도구 서버 인터페이스와 컨텍스트 경계 설계을(를) 구현한 프로젝트입니다. 핵심 심볼(`BengalCLI`)을 중심으로 실행 흐름을 정의하고 문서 내 주요 섹션(`Architecture: Site, Page, Section composition`, `------------------------------------------------------------`, `Root CLI`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 에이전트마다 외부 API 호출 래퍼와 도구 스키마를 개별 코드베이스에 중복 구현하면 프로토콜 변경이나 권한 제어 시 유지보수 병목이 발생합니다. 반면 `lbliii/bengal`(TO-BE)에서는 `CLAUDE.md`, `bengal/cli/milo_app.py`, `BengalCLI` 등 명시적 아티팩트를 기준으로 표준화된 MCP 서버 엔드포인트와 도구 등록 계층을 분리하고 프로젝트 규칙 문서로 입출력 스키마와 실행 명령을 고정하여 다양한 에이전트 클라이언트에서 재사용성을 확보합니다. 다만 도구 서버와 호스트 에이전트 간 프로세스·네트워크 통신 경계가 추가되므로 타임아웃, 세션 상태 정리 및 비신뢰 입력 검증 정책을 함께 구성해야 합니다.

---

### 2.4 MCP 기반 `npm test` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계 (`VitorMRodovalho/ai-pm-research-hub`)

- **출처**: [`VitorMRodovalho/ai-pm-research-hub`](https://github.com/VitorMRodovalho/ai-pm-research-hub) · **핵심 스택**: `MCP`, `Claude Code`, `Cursor Rules`, `Supabase`, `PostgreSQL`, `Tailwind CSS` · **적용 판단**: `Trial`
- **기술 개요**: `.cursorrules`, `CLAUDE.md` 발췌본을 기반으로 확인되는 `VitorMRodovalho/ai-pm-research-hub` 저장소는 MCP, Claude Code, Cursor Rules 스택 위에서 MCP 기반 `npm test` 워크플로우 기반 역할 기반 서브에이전트 분리와 핸드오프 게이트 설계을(를) 구현한 프로젝트입니다. `.cursorrules` 등에 명시된 실행·검증 명령(`npm test`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 단일 에이전트 세션에서 전략 수립, 코드 작성, 디버깅을 한꺼번에 수행하면 컨텍스트 윈도우가 빠르게 오염되고 실패 시 무작위 재시도 루프에 빠지기 쉽습니다. 반면 `VitorMRodovalho/ai-pm-research-hub`(TO-BE)에서는 `.cursorrules`, `CLAUDE.md`, `npm test` 등 명시적 아티팩트를 기준으로 계획(Plan)·실행(Exec)·원인 분석(RCA) 역할을 서브에이전트로 분리하고 명시적인 핸드오프 체크리스트와 컨텍스트 압축 임계치를 두어 장기 태스크의 정확도를 유지합니다. 다만 단계별 핸드오프 검증이 추가되면서 단순 수정 작업의 초기 레이턴시가 늘어날 수 있으므로 작업 복잡도에 따라 오케스트레이션 깊이를 분기해야 합니다.

---

### 2.5 Python 기반 `docs/audit-2026-04-28-throughput-gui.md` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리 (`FOI-Bioinformatics/nanometa_live`)

- **출처**: [`FOI-Bioinformatics/nanometa_live`](https://github.com/FOI-Bioinformatics/nanometa_live) · **핵심 스택**: `Python`, `Claude Code`, `Flask` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `nanometa_live/app/app.py` 발췌본을 기반으로 확인되는 `FOI-Bioinformatics/nanometa_live` 저장소는 Python, Claude Code, Flask 스택 위에서 Python 기반 `docs/audit-2026-04-28-throughput-gui.md` 모듈 분리와 도메인 주도(DDD) 에이전트 워크플로우와 비동기 큐 분리을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`docs/audit-2026-04-28-throughput-gui.md`)를 분리해 구성하며 문서 내 주요 섹션(`Architecture`, `Use 'spawn' instead of 'fork' to avoid BrokenPipeError on ma`, `when DiskcacheManager forks a process with a closed stderr p`)을 통해 아키텍처와 개발 규약을 안내합니다.

**실무 적용 해설**: 기존(AS-IS)에는 문서 수집, 임베딩, 에이전트 추론 루프를 동기식 웹 서버 프로세스 하나에서 처리하면 대용량 문서 색인이나 장시간 추론 시 API 응답 지연이 급증합니다. 반면 `FOI-Bioinformatics/nanometa_live`(TO-BE)에서는 `CLAUDE.md`, `nanometa_live/app/app.py`, `docs/audit-2026-04-28-throughput-gui.md` 등 명시적 아티팩트를 기준으로 백엔드 API와 비동기 태스크 큐(Celery/Worker), 프론트엔드 워크스페이스를 도메인 경계로 분리하고 마이그레이션 전용 엔트리포인트를 구분하여 대규모 RAG 워크플로우를 안정적으로 운영합니다. 다만 웹 서버와 워커 프로세스, 메시지 브로커를 함께 운영해야 하므로 로컬 개발 및 컨테이너 배포 시 헬스체크와 워커 동시성 튜닝이 필요합니다.

---

## 3. 오픈소스 모듈러 아키텍처 및 도메인 워크플로우 자동화

### 3.1 Python 기반 `handle_prompt_command_basic` 중심의 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성 (`fredericlepied/ai-assist`)

- **출처**: [`fredericlepied/ai-assist`](https://github.com/fredericlepied/ai-assist) · **핵심 스택**: `Python`, `Claude Code`, `uv`, `pytest` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`, `ai_assist/main.py` 발췌본을 기반으로 확인되는 `fredericlepied/ai-assist` 저장소는 Python, Claude Code, uv 스택 위에서 Python 기반 `handle_prompt_command_basic` 중심의 도메인 기능 모듈 분리와 재현 가능한 실행 환경 구성을(를) 구현한 프로젝트입니다. 주요 모듈 경로(`tests/test_file.py`, `server/prompt`)를 분리해 구성하며 핵심 심볼(`handle_prompt_command_basic`)을 중심으로 실행 흐름을 정의하고 `CLAUDE.md` 등에 명시된 실행·검증 명령(`uv sync`, `make pre-commit-install`)으로 개발 루프를 표준화합니다.

**실무 적용 해설**: 기존(AS-IS)에는 도메인 기능과 설정·외부 연동 코드가 단일 스크립트로 얽혀 있으면 기능 확장이나 타 시스템 이식 시 사이드 이펙트를 예측하기 어렵습니다. 반면 `fredericlepied/ai-assist`(TO-BE)에서는 `CLAUDE.md`, `ai_assist/main.py`, `uv sync` 등 명시적 아티팩트를 기준으로 핵심 실행 모듈과 설정·인터페이스 계층을 분리하고 명시적인 진입점 및 의존성 명세를 제공하여 로컬 개발과 자동화 파이프라인 양쪽에서 동일한 동작을 보장합니다. 다만 초기 모듈 분리 이후 실제 프로덕션 트래픽이나 엣지 케이스 입력에 대응하려면 단위 테스트 커버리지와 예외 처리 경계를 단계적으로 보강해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `henglihengli/openclaw`의 `CLAUDE.md` 구성처럼 독립 스킬 디렉터리 격리 및 등록·버전 드리프트 게이트 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `xiezg247/zak`의 `.cursorrules` 구성처럼 선언적 에이전트 컨텍스트 주입 및 검증 루프 표준화 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
  - `lbliii/bengal`의 `CLAUDE.md` 구성처럼 MCP 도구 스키마 분리 및 런타임 세션 격리 원칙을 사내 유사 서비스 모듈에 적용할 수 있는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-06-11 수집 시점의 공개 저장소 `CLAUDE.md`, `.cursorrules` 등 루트 설정 및 진입점 발췌본에 근거하며, 실제 프로덕션 트래픽 환경에서의 처리량·지연 시간 및 전체 테스트 스위트 통과 여부는 별도 검증이 필요합니다.
