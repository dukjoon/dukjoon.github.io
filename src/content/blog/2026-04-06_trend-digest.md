---
title: "[Trend] 2026-04-06: 계약 기반 아키텍처 경계와 에이전트 규칙 계층화"
pubDatetime: 2026-04-06T00:00:00Z
description: "CI 20개 계약 스캐너를 통한 엔진 격리, git worktree 대기 브랜치 규율, 지연 임포트 및 계층형 에이전트 규칙까지 2026년 4월 6일 핵심 패턴을 정리합니다."
category: trend
tags:
  - trend
  - architecture-contracts
  - git-worktree
  - agent-rules
  - monorepo
draft: false
---

2026년 4월 6일 수집된 저장소에서는 코딩 에이전트에게 "잘 짜 달라"고 추상적으로 지시하는 수준을 넘어, CI 계약 스캐너(`contract_scanner.py`)나 `git worktree` 대기 브랜치 규약, 추측 구현 금지 규칙 등 구조적 경계를 강제하는 엔지니어링 접근이 돋보입니다. 레거시 호환성 격리와 런타임 도구 호출 경계에 관한 실무 시사점도 함께 확인됩니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 / 시그널 | 실무 적용 포인트 |
|---|---|---|
| 계약 기반 아키텍처 경계와 워크트리·레거시 격리 | `cryptoxdog/Enrichment.Inference.Engine`, `gannonh/kata`, `goingforstudying-ctrl/langchain` | 도메인 핸들러 HTTP 임포트 차단(`contract_scanner.py`), `*-standby` 워크트리 브랜치, `__getattr__` 레거시 지연 임포트 |
| 에이전트 규칙 계층화와 런타임·도구 경계 준수 | `TItabashBoilerplates/shadcn-boilerplate`, `binaryblitz10/extensions`, `bitbyzen/kb` | `.claude/rules/`+Context7 MCP 선행 검증, 확장별 `CLAUDE.md` 컨텍스트 격리, `pip._internal` 인프로세스 호출 지양 |

---

## 2. 계약 기반 아키텍처 경계와 워크트리·레거시 격리

### 2.1 단일 인그레스 섀시와 20개 CI 계약 스캐너 (`cryptoxdog/Enrichment.Inference.Engine`)

- **출처**: [`cryptoxdog/Enrichment.Inference.Engine`](https://github.com/cryptoxdog/Enrichment.Inference.Engine) · **핵심 스택**: `Python`, `FastAPI`, `contract_scanner.py` · **적용 판단**: `Trial`
- **기술 개요**: 인증·레이트 리미팅·테넌트 해석·로깅을 담당하는 L9 FastAPI 섀시(`POST /v1/execute`, `GET /v1/health`)와 순수 도메인 엔진(`engine/handlers.py`)을 분리하고, `.cursorrules`와 `CLAUDE.md`에 명시된 20개 아키텍처 계약을 `contract_scanner.py`와 CI로 강제하는 저장소입니다.

**실무 적용 해설**: AI가 생성한 백엔드 코드가 늘어나면 도메인 핸들러 내부에 FastAPI `Request` 객체나 커스텀 라우터, 인증 우회 코드가 섞여 들어와 아키텍처 경계가 빠르게 무너집니다. 기존(AS-IS)에는 PR 리뷰어의 눈으로 프레임워크 침투를 막아야 했으나, 도메인 엔진의 인터페이스를 `async def handle_<action>(tenant: str, payload: dict) -> dict`로 고정하고 FastAPI·Starlette 임포트 자체를 `contract_scanner.py`로 자동 차단하면(TO-BE) 에이전트가 작성한 코드라도 섀시의 횡단 관심사(보안·메트릭·라우팅)를 훼손할 수 없습니다. "당신은 엔진만 만든다"는 명확한 책임 분리는 에이전트 오작동 범위를 좁히는 데 매우 효과적입니다. 다만 20개 계약이 과도하게 경직되면 도메인 특화 스트리밍이나 웹훅 예외 처리 시 섀시 인터페이스를 함께 확장해야 하는 협업 비용이 발생합니다.

### 2.2 Bun·Rust 모노레포와 Worktree 대기 브랜치 규약 (`gannonh/kata`)

- **출처**: [`gannonh/kata`](https://github.com/gannonh/kata) · **핵심 스택**: `Bun 1.3.8`, `Turborepo`, `Rust`, `Electron`, `Vitest` · **적용 판단**: `Trial`
- **기술 개요**: Rust 바이너리(`apps/symphony`), CLI(`apps/cli`), Electron 앱(`apps/electron`), 네이티브 컨텍스트 인덱서(`apps/context`), 오케스트레이터(`apps/orchestrator`)를 결합한 Bun/Turborepo 모노레포입니다. `apps/cli/CLAUDE.md`에서 `--no-verify` 플래그 사용을 금지하고 워크트리별 대기 브랜치(`wt-cli-standby`) 운영 규칙을 정의합니다.

**실무 적용 해설**: 여러 AI 에이전트 세션을 `git worktree`로 병렬 실행할 때 Git은 동일 브랜치(`main`)를 복수 워크트리에서 동시에 체크아웃하는 것을 허용하지 않아 브랜치 충돌과 잘못된 직접 커밋이 빈번합니다. 기존(AS-IS)처럼 임시 분리 HEAD 상태에서 작업하거나 푸시 훅을 `--no-verify`로 우회하는 대신, 각 워크트리에 `main`을 추적하는 `*-standby` 대기 브랜치를 둔 뒤 세션 시작 시 반드시 피처 브랜치(`kata/M00X/S0X`)를 분기하도록 강제하면(TO-BE) 병렬 작업 안전성과 프리커밋 품질 게이트를 동시에 지킬 수 있습니다. 또한 루트에서 `bun run validate:affected`로 변경 패키지만 린트·타입체크·테스트하는 구성도 실용적입니다. 도입 시에는 대기 브랜치의 `main` 동기화 스크립트를 자동화해 오래된 베이스 위에서 작업하는 실수를 예방해야 합니다.

### 2.3 `uv` 모노레포 패키징과 `__getattr__` 레거시 지연 임포트 (`goingforstudying-ctrl/langchain`)

- **출처**: [`goingforstudying-ctrl/langchain`](https://github.com/goingforstudying-ctrl/langchain) · **핵심 스택**: `Python`, `uv`, `langchain-core`, `langchain_v1`, `langchain-classic` · **적용 판단**: `Trial`
- **기술 개요**: 핵심 추상화(`libs/core`), 현행 패키지(`libs/langchain_v1`), 레거시 격리 패키지(`libs/langchain`), 파트너 통합(`libs/partners/*`), 공통 테스트(`libs/standard-tests`)를 독립 버전으로 관리하는 `uv` 기반 Python 모노레포입니다. `whatsapp.py`에서는 `TYPE_CHECKING` 분기와 `DEPRECATED_LOOKUP` + `__getattr__` 동적 임포터(`create_importer`)로 하위 호환 심을 유지합니다.

**실무 적용 해설**: 대규모 오픈소스나 사내 공통 SDK가 메이저 버전 전환기를 거칠 때 레거시 경로를 즉시 삭제하면 기존 사용자 코드가 깨지고, 반대로 모든 구형 모듈을 상시 로딩하면 임포트 속도와 의존성 결합도가 악화됩니다. 기존(AS-IS)처럼 구버전과 신버전 코드를 한 패키지에 혼재시키는 대신 신규 기능 추가가 중단된 `langchain-classic` 영역을 분리하고 `DEPRECATED_LOOKUP`과 모듈 레벨 `__getattr__`로 실제 접근 시점에만 지연 임포트 및 경고를 발생시키면(TO-BE) 타입 체커(`TYPE_CHECKING`) 지원과 런타임 경량화를 동시에 유지할 수 있습니다. 또한 `libs/standard-tests`로 모든 모델 프로바이더 통합이 동일한 규약 테스트를 통과하게 만든 구조는 멀티 벤더 어댑터 설계에 좋은 기준이 됩니다. 다만 `__getattr__` 기반 동적 프록시는 정적 번들러나 트리 셰이킹 도구가 의존성을 추적하기 어렵게 만들므로 마이그레이션 종료 시점을 명확히 공지해야 합니다.

---

## 3. 에이전트 규칙 계층화와 런타임·도구 경계 준수

### 3.1 추측 구현 금지(Research-First)와 `.claude/rules/` 모듈화 (`TItabashBoilerplates/shadcn-boilerplate`)

- **출처**: [`TItabashBoilerplates/shadcn-boilerplate`](https://github.com/TItabashBoilerplates/shadcn-boilerplate) · **핵심 스택**: `Supabase`, `PostgreSQL`, `Makefile`, `Context7 MCP` · **적용 판단**: `Trial`
- **기술 개요**: `.claude/CLAUDE.md`에서 추측·기억 기반 구현을 금지하고 구현 전 Context7 MCP나 공식 문서 검색을 선행하도록 규정하며, `.claude/rules/` 아래에 `tdd.md`, `research.md`, `supabase-first.md`, `database.md`, `auto-generated.md` 등으로 규칙을 세분화한 템플릿입니다. 함께 포함된 `.agents/skills/supabase-postgres-best-practices/CLAUDE.md`는 `SKILL.md`와 `references/` 온디맨드 로딩 구조를 제공합니다.

**실무 적용 해설**: LLM이 학습 시점의 구버전 라이브러리 API나 임의의 설정 키를 기억에 의존해 작성하면 마이그레이션·RLS(Row-Level Security) 보안 설정에서 미묘한 장애가 발생합니다. 기존(AS-IS)의 장문 단일 지침 파일 대신 "추측 금지 + 공식 문서 선행 확인" 원칙을 최상위에 고정하고 `.claude/rules/`와 `references/`를 필요 시에만 온디맨드 로딩하도록 계층화하면(TO-BE) 컨텍스트 오염을 줄이면서도 최신 API 정합성과 Makefile 기반 실행 통제를 지킬 수 있습니다. 특히 `database.md`의 마이그레이션 승인 필수 규칙과 `auto-generated.md`의 자동 생성 파일 수정 금지 규칙은 실무 사고 예방에 직결됩니다. 다만 Context7 MCP·웹 검색 선행 절차가 모든 사소한 수정에 강제되면 작업 지연이 커질 수 있어 적용 범위를 신규 API·스키마 변경으로 한정하는 운용이 합리적입니다.

### 3.2 확장별 `CLAUDE.md` 컨텍스트 스코핑 (`binaryblitz10/extensions`)

- **출처**: [`binaryblitz10/extensions`](https://github.com/binaryblitz10/extensions) · **핵심 스택**: `TypeScript`, `React`, `Raycast API`, `Vitest`, `ESLint`, `Prettier` · **적용 판단**: `Assess`
- **기술 개요**: 개별 Raycast 확장 디렉터리(`extensions/anytype/CLAUDE.md`, `extensions/area-code-lookup/CLAUDE.md`)마다 로컬 API 레이어(`src/api/`), 정적 코드 테이블(`areaCodes.ts`, `countryCodes.ts`), 단일 파일 테스트(`npx vitest run src/utils/api.test.ts`) 명령을 독립 배치한 저장소입니다.

**실무 적용 해설**: 모노레포 루트에 모든 하위 프로젝트의 빌드·테스트 문서를 몰아넣는 기존(AS-IS) 방식에서는 특정 확장만 수정할 때도 무관한 도메인 지식이 에이전트 컨텍스트를 점유합니다. `binaryblitz10/extensions` 사례처럼 각 확장 폴더 안에 자체 아키텍처와 최소 검증 명령만 담은 `CLAUDE.md`를 스코핑해 두면(TO-BE) 에이전트가 해당 디렉터리로 이동했을 때 즉시 필요한 로컬 API 경계와 스마트 입력 분기(`lookup.tsx`) 규칙만 적재할 수 있습니다. 이는 다수의 독립 위젯이나 마이크로서비스가 공존하는 사내 저장소에 그대로 이식 가능한 구조입니다. 단, 개별 확장 파일 간 공통 ESLint/TypeScript 설정이 바뀔 때는 일괄 동기화 점검 스크립트가 필요합니다.

### 3.3 `pip._internal` 인프로세스 호출 지양과 서브프로세스 격리 (`bitbyzen/kb`)

- **출처**: [`bitbyzen/kb`](https://github.com/bitbyzen/kb) · **핵심 스택**: `Python 3.10`, `pip` · **적용 판단**: `Assess`
- **기술 개요**: 수집된 발췌본(`.venv/lib/python3.10/site-packages/pip/_internal/cli/main.py` 및 `pip/_internal/main.py`)은 `pip._internal`의 `main()` 함수를 애플리케이션 프로세스 내부에서 직접 임포트·호출하지 말 것을 경고하는 `pip` 공식 내부 구현 및 레퍼런스 래퍼(`_wrapper`)에 해당합니다.

**실무 적용 해설**: Python 자동화 도구나 에이전트 런타임이 동적으로 패키지를 설치해야 할 때 편의상 `from pip._internal.cli.main import main`을 직접 호출하면 전역 로깅·로케일·시그널 상태가 오염되고 `pip` 버전 업그레이드 시 비공개 API 변경으로 즉시 깨지는 문제가 생깁니다. 기존(AS-IS)의 인프로세스 임포트 호출 대신 `subprocess.run([sys.executable, "-m", "pip", ...])`처럼 명시적인 서브프로세스 경계로 CLI를 호출하면(TO-BE) 프로세스 격리와 버전 이식성을 안전하게 확보할 수 있습니다. 또한 저장소 인덱싱·패키징 파이프라인을 운영할 때는 `.venv` 같은 가상환경 디렉터리가 `.gitignore`나 스캐너 제외 목록에서 누락되지 않도록 관리해야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - FastAPI 기반 도메인 서비스에서 프레임워크 종속성이 도메인 로직으로 새어 나가는 것을 막으려면 `cryptoxdog/Enrichment.Inference.Engine`처럼 `contract_scanner.py` 수준의 정적 임포트 검사 스크립트를 CI에 추가합니다.
  - 다중 에이전트 `git worktree` 환경에 `gannonh/kata` 방식의 `*-standby` 브랜치 규칙과 `--no-verify` 금지 조항을 도입합니다.
  - Python 코드베이스에서 패키지 설치 자동화가 필요할 때 `pip._internal` 직접 임포트 대신 `sys.executable -m pip` 서브프로세스 실행을 강제하고, `.venv`가 저장소에 추적되지 않았는지 점검합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-04-06 수집 시점의 공개 저장소 발췌본(`CLAUDE.md`, `.cursorrules`, `whatsapp.py`, `.venv/.../pip/_internal/*.py`)에 근거하며, `bitbyzen/kb`의 경우 발췌된 `.venv` 내부 파일 외의 상위 애플리케이션 구조는 관찰 범위에 포함되지 않았습니다.
