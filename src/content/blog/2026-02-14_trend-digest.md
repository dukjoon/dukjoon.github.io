---
title: "[Trend] 2026-02-14: 양시간축 지식 그래프와 AGENTS.md 단일 진실 공급원"
pubDatetime: 2026-02-14T00:00:00Z
description: "Graphiti 양시간축 메모리 MCP, Claude Agent SDK 엔진 교체, AGENTS.md 심볼릭 링크 통합 및 LLM 평가 분석 CLI를 다룹니다."
category: trend
tags:
  - trend
  - knowledge-graph
  - claude-agent-sdk
  - mcp-server
  - fastapi
draft: false
---

코딩 에이전트와 메모리 계층이 성숙하면서 여러 도구 설정 파일(`CLAUDE.md`, `.cursorrules`)의 드리프트를 `AGENTS.md` 심볼릭 링크로 통합하거나, 기존 어댑터 계층을 유지한 채 실행 엔진만 Claude Agent SDK로 교체하는 실용적 리팩터링이 나타납니다. 백엔드 측에서는 증분 지식 그래프, 평가 트랜스크립트 분석기, 물리 시뮬레이터 등 도메인별 수명주기와 엄격한 타입 경계가 강조됩니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 | 실무 적용 포인트 |
|---|---|---|
| 시간축 지식 그래프·에이전트 SDK 전환 및 컨텍스트 단일화 | `getzep/graphiti`, `remoteclaw/remoteclaw`, `Mirascope/mirascope` | 비배치 양시간축 그래프와 MCP 래퍼, 채널 어댑터 보존형 SDK 교체, `AGENTS.md` 심볼릭 링크 |
| 평가 트랜스크립트 분석과 도메인 백엔드 수명주기 설계 | `tbroadley/inspect_scout`, `avallavall/ballistic-reloading-simulator`, `Edjavier-collab/Main2MI` | 엄격 타입 기반 평가 스캐너 CLI, FastAPI `lifespan` 모델 등록, 단일 파일 승인형 변경 규율 |

---

## 2. 시간축 지식 그래프·에이전트 SDK 전환 및 컨텍스트 단일화

### 2.1 양시간축 지식 그래프와 하위 호환 MCP 래퍼 (`getzep/graphiti`)

- **출처**: [`getzep/graphiti`](https://github.com/getzep/graphiti) · **핵심 스택**: `Python`, `Neo4j`, `FalkorDB`, `Pydantic`, `OpenTelemetry` · **적용 판단**: `Trial`
- **기술 개요**: 이벤트 발생 시점을 추적하는 양시간축(bi-temporal) 데이터 모델과 임베딩·BM25·그래프 순회를 결합한 하이브리드 검색 프레임워크로, `mcp_server/main.py`는 기존 `graphiti_mcp_server.py`로 인자를 그대로 전달하는 하위 호환 래퍼를 유지합니다.

**실무 적용 해설**: 에이전트 메모리를 정적 벡터 DB에만 저장(AS-IS)하면 과거 사실과 갱신된 최신 상태가 섞여 시간 의존적 질의에서 오답이 발생합니다. `graphiti`처럼 배치 재계산 없이 증분 업데이트되는 양시간축 모델과 Pydantic 커스텀 엔티티를 결합하고, 배포 스크립트 호환을 위해 `mcp_server/main.py` 진입점 래퍼를 유지(TO-BE)하면 운영 중단 없이 그래프 검색과 OpenTelemetry 추적을 도입할 수 있습니다. 다만 Neo4j/FalkorDB 운영과 함께 `ruff` + `pyright` 검사가 필수이므로 소규모 단기 상태만 다루는 봇에는 과도한 인프라가 될 수 있습니다.

---

### 2.2 어댑터 계층 보존형 Claude Agent SDK 전환 (`remoteclaw/remoteclaw`)

- **출처**: [`remoteclaw/remoteclaw`](https://github.com/remoteclaw/remoteclaw) · **핵심 스택**: `TypeScript (ESM)`, `Claude Agent SDK`, `Oxlint`, `Oxfmt` · **적용 판단**: `Trial`
- **기술 개요**: 기존 채널 어댑터 계층(`extensions/*`)과 스킬 인터페이스는 유지한 채 코어 실행 엔진을 Claude Agent SDK로 교체한 포크로, `no-explicit-any`, 파일당 약 500LOC 제한, `Oxlint`/`Oxfmt`(`pnpm check`) 규율을 강제합니다.

**실무 적용 해설**: 에이전트 런타임 엔진을 교체할 때 채널 연동·인증·플러그인 코드까지 한꺼번에 재작성(AS-IS)하면 회귀 범위가 통제 불능으로 커집니다. `RemoteClaw`처럼 `extensions/*` 패키지 경계와 kebab-case 파일 규칙을 보존한 채 실행 코어만 교체하고, `git log` 트레일러로 업스트림·로컬 커밋 기원을 구분하며 500LOC 상한을 강제(TO-BE)하면 점진적 마이그레이션과 업스트림 패치 추적이 가능해집니다. 반면 업스트림과 코어 엔진이 달라진 만큼 머지 충돌 해소 시 어댑터 계약 테스트(`*.test.ts`, `*.e2e.test.ts`)가 반드시 선행되어야 합니다.

---

### 2.3 `AGENTS.md` 단일 진실 공급원과 심볼릭 링크 통합 (`Mirascope/mirascope`)

- **출처**: [`Mirascope/mirascope`](https://github.com/Mirascope/mirascope) · **핵심 스택**: `Python SDK`, `TypeScript SDK`, `AGENTS.md` · **적용 판단**: `Trial`
- **기술 개요**: `AGENTS.md`를 유일한 원천 문서(single source of truth)로 삼아 `.claude/CLAUDE.md`와 `.cursorrules`를 심볼릭 링크로 연결하고, 세부 구조는 `STRUCTURE.md` 및 `cloud/AGENTS.md`·`python/AGENTS.md`로 계층화했습니다.

**실무 적용 해설**: 팀에서 Claude Code와 Cursor를 병행하면서 `.claude/CLAUDE.md`와 `.cursorrules`를 각각 따로 수정(AS-IS)하면 며칠 만에 규칙이 어긋나 도구마다 다른 아키텍처 관습을 생성하게 됩니다. 루트 `AGENTS.md`에 공통 원칙을 두고 에이전트별 설정 경로를 심볼릭 링크로 묶은 뒤 언어별 하위 디렉터리에만 `AGENTS.md`를 추가(TO-BE)하면 다중 SDK 모노레포에서도 지침 동기화 비용이 사라집니다. 단, Windows 환경이나 일부 Git 설정에서는 심볼릭 링크가 일반 텍스트 파일로 체크아웃될 수 있어 `core.symlinks` 설정 확인이 필요합니다.

---

## 3. 평가 트랜스크립트 분석과 도메인 백엔드 수명주기 설계

### 3.1 LLM 평가 로그 스캐너와 엄격 타입·행위 테스트 원칙 (`tbroadley/inspect_scout`)

- **출처**: [`tbroadley/inspect_scout`](https://github.com/tbroadley/inspect_scout) · **핵심 스택**: `Python`, `Click`, `FastAPI`, `React`, `TypeScript` · **적용 판단**: `Trial`
- **기술 개요**: LLM 평가 실행 로그(transcript)를 스캔·분석하는 라이브러리(`src/inspect_scout/`)와 React 뷰어를 제공하며, `scout scan resume/complete/list/status` 등 상태 관리 CLI 서브커맨드와 `any`/타입 단언 금지 규칙을 적용했습니다.

**실무 적용 해설**: 대규모 LLM 평가 배치 실행 중 오류가 나면 처음부터 재실행하거나 원시 JSON 로그를 수작업으로 뒤지는 경우(AS-IS)가 많습니다. `scan_resume_command`와 `trace` 서브커맨드처럼 스캔 작업을 DB 상태로 관리해 중단 지점부터 재개할 수 있게 하고, `CLAUDE.md`에 "내부 구현이 아닌 관찰 가능한 행위" 중심의 테이블 주도 테스트와 `X | None`·무단언 TypeScript 규칙을 고정(TO-BE)하면 평가 분석기 자체의 신뢰성을 높일 수 있습니다. FastAPI 뷰어와 Python 코어가 한 저장소에 묶여 있어 변경된 계층에 맞춰 린트·타입체크를 분리 실행하는 습관이 중요합니다.

---

### 3.2 내부 탄도학 시뮬레이터의 `lifespan` 수명주기 및 모델 명시 등록 (`avallavall/ballistic-reloading-simulator`)

- **출처**: [`avallavall/ballistic-reloading-simulator`](https://github.com/avallavall/ballistic-reloading-simulator) · **핵심 스택**: `Next.js 14`, `FastAPI`, `Python 3.12`, `PostgreSQL 16`, `SQLAlchemy` · **적용 판단**: `Assess`
- **기술 개요**: 정밀 탄약 재장전용 내부 탄도학(internal ballistics) 웹 시뮬레이터로, `docs/physics_core.md` 물리 명세와 4개 Docker Compose 서비스를 갖추고 `backend/app/main.py`에서 `asynccontextmanager` `lifespan` 및 전체 ORM 모델 사전 임포트로 `Base.metadata` 등록을 보장합니다.

**실무 적용 해설**: SQLAlchemy 비동기 백엔드에서 모델 모듈이 지연 임포트(AS-IS)되면 Alembic 마이그레이션이나 초기 테이블 시딩 시 일부 테이블이 `Base.metadata`에서 누락되는 오류가 발생합니다. `main.py` 진입점에 `# noqa: F401`로 `powder`, `bullet`, `simulation` 등 도메인 모델을 명시 등록하고 `CORS_ORIGINS`를 콤마 구분 환경 변수로 제어(TO-BE)하면 컨테이너 기동 시 메타데이터 불일치를 원천 차단할 수 있습니다. 또한 천 줄이 넘는 `physics_core.md`와 테스트(`test_thermodynamics.py`)를 분리 유지해 수치 시뮬레이션 코드의 검증 근거를 명확히 남긴 점이 특징입니다.

---

### 3.3 단일 파일 승인형 변경 규율과 서버 전용 API 키 격리 (`Edjavier-collab/Main2MI`)

- **출처**: [`Edjavier-collab/Main2MI`](https://github.com/Edjavier-collab/Main2MI) · **핵심 스택**: `React`, `TypeScript`, `Supabase Edge Functions`, `Stripe`, `Gemini API` · **적용 판단**: `Assess`
- **기술 개요**: 의료인의 동기면담(MI) 훈련을 돕는 PWA 웹앱으로, `.cursorrules`에 한 번에 한 파일만 수정·승인 후 진행 규율과 CSS 변수 강제를 두고, `CLAUDE.md`에서 `GEMINI_API_KEY`를 클라이언트 접두사 없는 서버 전용 환경 변수로 분리했습니다.

**실무 적용 해설**: 프론트엔드 중심 풀스택 프로젝트에서 AI 에이전트가 한 번에 10여 개 파일을 수정하고 `VITE_` 접두사 환경 변수에 LLM 키를 노출(AS-IS)하면 번들 보안 사고와 대규모 롤백이 발생하기 쉽습니다. `.cursorrules`에 단일 파일 변경·사전 diff 확인 원칙을 박아 두고 Supabase Edge Functions 경계 뒤에만 `GEMINI_API_KEY`를 배치(TO-BE)하면 바이브 코딩 속도와 보안 경계를 동시에 지킬 수 있습니다. 다만 1파일 단위 승인 루프는 리팩터링 속도를 늦추므로 초기 프로토타입 이후 안정화 단계에 더 적합합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - `.claude/CLAUDE.md`와 `.cursorrules`를 별도 유지하는 저장소에서 `AGENTS.md` 단일 파일 + 심볼릭 링크 구조로 전환 검토.
  - LLM 배치 평가·시뮬레이션 CLI에 `scan resume` 같은 체크포인트 재개 커맨드와 `Base.metadata` 사전 등록 검증 추가.
  - 프론트엔드/Edge Functions 혼합 프로젝트에서 LLM API 키에 `VITE_`/`NEXT_PUBLIC_` 클라이언트 노출 접두사가 붙지 않았는지 환경 변수 감사 수행.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-02-14 수집 시점의 공개 저장소 `CLAUDE.md`, `.cursorrules`, `main.py` 발췌본(최대 1,000자)에 근거하며, 전체 구현 코드와 실제 배포 환경의 부하 특성은 별도 확인이 필요합니다.
