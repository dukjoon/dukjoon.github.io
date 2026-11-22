---
title: "[Trend] 2026-02-05: Git 안전 가드레일과 훅·Mock 모드 아키텍처"
pubDatetime: 2026-02-05T00:00:00Z
description: "파괴적 Git 명령 차단 규칙, Claude Code 훅·스킬 번들링, MOCK_MODE 로컬 대시보드, Bun·TSDoc 기반 워크플로우 규약을 분석합니다."
category: trend
tags:
  - trend
  - claude-md
  - git-safety
  - hooks
  - kubernetes
draft: false
---

코딩 에이전트의 자율성이 커지면서 단순 스타일 가이드를 넘어 파괴적 Git 명령을 명시적으로 봉쇄하거나, 스킬·에이전트·훅을 번들링해 수명주기를 자동화하는 저장소 규약이 뚜렷해지고 있습니다. 이번 일자에서는 에이전트 안전장치와 플러그인 구조, 그리고 클러스터 없이 동작하는 로컬 Mock 백엔드 설계 사례를 정리합니다.

## 1. 오늘의 핵심 패턴 요약

| 테마 | 대표 프로젝트 | 실무 적용 포인트 |
|---|---|---|
| 에이전트 안전장치 및 훅 아키텍처 | `helixml/helix`, `yonatangross/orchestkit`, `coder/coder` | 파괴적 Git 명령 차단, 컴파일된 TS 훅(`run-hook.mjs`), 비판적 코드 리뷰어 페르소나 |
| 풀스택 규약 및 무클러스터 개발 모드 | `simstudioai/sim`, `tambo-ai/tambo`, `sagi-l/ci-dashboard` | `bun`/`@sim/logger` 표준화, `@AGENTS.md` 위임과 `-w` DB 명령, `MOCK_MODE=true` 로컬 실행 |

---

## 2. 에이전트 안전장치 및 훅 아키텍처

### 2.1 파괴적 Git 명령 차단과 연도 컨텍스트 고정 (`helixml/helix`)

- **출처**: [`helixml/helix`](https://github.com/helixml/helix) · **핵심 스택**: `CLAUDE.md`, `.cursor/rules/*.mdc`, `Git Guardrails` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md` 상단에 현재 연도(`2026`) 검색 기준과 함께 `git checkout -- .`, `git reset --hard`, `git stash drop/pop`, `.git/index.lock` 삭제, `main` 직접 푸시 등 파괴적 Git 명령 금지 목록을 규정한 사례입니다.

**실무 적용 해설**: 멀티 세션이나 백그라운드 작업이 섞인 저장소에서 에이전트가 테스트 실패를 되돌리려고 `git reset --hard`나 `git stash pop`을 실행하면(AS-IS) 다른 작업자의 미커밋 변경분까지 복구 불가능하게 소실됩니다. `helix`처럼 `git stash apply`만 허용하고 파괴적 Git 명령과 `rm -rf *`를 금지 규칙으로 명시하며, 라이브러리 검색 시 최신 연도를 강제(TO-BE)하면 비가역적 손실과 구버전 API 참조를 함께 억제할 수 있습니다. 다만 프롬프트 규칙만으로는 명령 실행을 완전히 막기 어려우므로, 실무에서는 Pre-tool 훅이나 CI 브랜치 보호 규칙과 병행해 방어선을 이중화해야 합니다.

### 2.2 스킬·에이전트·TypeScript 훅 통합 플러그인 구조 (`yonatangross/orchestkit`)

- **출처**: [`yonatangross/orchestkit`](https://github.com/yonatangross/orchestkit) · **핵심 스택**: `Claude Code Plugin`, `TypeScript Hooks`, `SKILL.md` · **적용 판단**: `Trial`
- **기술 개요**: `src/skills/<name>/SKILL.md`, `src/agents/<name>.md`, TypeScript 기반 수명주기 훅(`hooks/src/` -> `dist/` 컴파일, `bin/run-hook.mjs`, `hooks.json`)으로 구성된 에이전트 확장 번들입니다.

**실무 적용 해설**: 팀 내 프롬프트 지침과 보안 검사 스크립트를 프로젝트마다 복사해 두면(AS-IS) 정책 변경 시 여러 저장소를 수동으로 동기화해야 합니다. `orchestkit`처럼 지식 모듈(`SKILL.md` + `references/`), 역할 정의(`agents/*.md`), 전역·스코프별 컴파일된 훅(`hooks.json` + `run-hook.mjs`)을 단일 소스 트리(`src/`)에서 빌드·배포하는 구조(TO-BE)를 취하면 수명주기 자동화와 품질 게이트를 일관되게 버전 관리할 수 있습니다. 반면 훅 수가 늘어날수록 매 도구 호출마다 지연 시간이 누적되므로, 비차단 로깅이나 알림 작업은 fire-and-forget 디스패처로 분리하는 설계가 동반되어야 합니다.

### 2.3 예외 승인 게이트와 비판적 리뷰어 규약 (`coder/coder`)

- **출처**: [`coder/coder`](https://github.com/coder/coder) · **핵심 스택**: `.cursorrules`, `CLAUDE.md` · **적용 판단**: `Assess`
- **기술 개요**: `.cursorrules`와 `CLAUDE.md`에 동일 규약을 배치해 규칙 예외 시 사전 명시적 승인을 요구하고, 에이전트가 사용자 의견에 무비판적으로 동조하지 않고 기술적 오류를 지적하도록 역할을 정의한 사례입니다.

**실무 적용 해설**: 에이전트가 사용자 프롬프트의 잘못된 가정을 그대로 수용해 우회 구현을 밀어붙이면(AS-IS) 잘못된 설계가 코드베이스에 고착됩니다. 규칙 예외 전 중단·승인 규칙과 함께 근거 없는 동조를 금지하고 즉시 불확실성을 보고하도록 지시(TO-BE)하면 초기 설계 오류를 조기에 걸러낼 수 있습니다. 다만 `.cursorrules`와 `CLAUDE.md`에 동일 본문을 중복 유지하면 한쪽 수정 시 규약 불일치가 생기기 쉬우므로, 단일 원본 문서 참조 구조로 통합 관리하는 편이 유지보수에 유리합니다.

---

## 3. 풀스택 규약 및 무클러스터 개발 모드

### 3.1 `bun`·`@sim/logger`·로컬 스타일 경계 강제 (`simstudioai/sim`)

- **출처**: [`simstudioai/sim`](https://github.com/simstudioai/sim) · **핵심 스택**: `Next.js (App Router)`, `Bun`, `TypeScript`, `Zustand` · **적용 판단**: `Trial`
- **기술 개요**: `apps/sim/` 모노레포에서 `npm`/`npx` 대신 `bun`/`bunx` 사용을 고정하고, `console.log` 대신 `@sim/logger`(`createLogger`), TSDoc 주석, 컴포넌트 로컬 스타일, 전역 상태용 `Zustand`를 명시한 규약입니다.

**실무 적용 해설**: Next.js 프로젝트에서 에이전트가 디버깅용 `console.log`를 남기거나 전역 CSS를 임의로 수정하면(AS-IS) 구조화 로그 수집이 깨지고 다른 페이지 레이아웃에 회귀가 발생합니다. `@sim/logger` 사용과 전역 스타일 수정 금지를 문서화하고 `Zustand`(전역 상태)와 `useState`(UI 전용 상태)의 경계를 명시(TO-BE)하면 생성 코드가 기존 관측성·스타일 파이프라인에 자연스럽게 편입됩니다. 단 `bun` 런타임과 Node 기반 CI 환경 간 패키지 호환성 차이가 발생할 수 있어 락파일과 실행 스크립트 기준을 팀 전체가 통일해야 합니다.

### 3.2 `@AGENTS.md` 위임과 워크스페이스 DB 명령 분리 (`tambo-ai/tambo`)

- **출처**: [`tambo-ai/tambo`](https://github.com/tambo-ai/tambo) · **핵심 스택**: `TypeScript Monorepo`, `React SDK`, `packages/db` · **적용 판단**: `Trial`
- **기술 개요**: `CLAUDE.md`를 `@AGENTS.md` 포인터와 핵심 실행 명령(`dev:cloud`, `dev`, `lint`, `check-types`, `packages/db` 워크스페이스 `-w` 플래그) 인덱스로만 구성해 단일 규약 파일로 충돌을 방지한 사례입니다.

**실무 적용 해설**: 클라우드 API(포트 8260/8261)와 React SDK, DB 마이그레이션 패키지가 한 저장소에 공존할 때 루트 명령만 안내하면(AS-IS) 에이전트가 잘못된 워크스페이스에서 마이그레이션을 실행하는 오류가 잦습니다. `CLAUDE.md`에는 앱별 개발 서버 진입점과 `-w packages/db` 같은 스코프 지정 명령만 요약하고 상세 규칙은 `@AGENTS.md`로 일원화(TO-BE)하면 규칙 충돌 시 우선순위 판단 비용이 사라집니다. 멀티 패키지 저장소에서는 이처럼 DB 변경 스크립트의 워크스페이스 플래그를 명확히 박아 두는 것이 실수를 줄이는 핵심입니다.

### 3.3 `MOCK_MODE` 기반 무클러스터 Kubernetes 대시보드 (`sagi-l/ci-dashboard`)

- **출처**: [`sagi-l/ci-dashboard`](https://github.com/sagi-l/ci-dashboard) · **핵심 스택**: `Python 3.12`, `Flask 3.0.0`, `Gunicorn`, `Jenkins/ArgoCD`, `Kubernetes` · **적용 판단**: `Trial`
- **기술 개요**: 베어메탈 Kubernetes 위 Jenkins·ArgoCD 파이프라인을 모니터링하고 웹에서 빌드를 트리거하는 Flask 대시보드이며, `MOCK_MODE=true` 환경변수로 `kubeconfig` 없이 로컬 UI/API를 검증할 수 있도록 `app.py`를 설계했습니다.

**실무 적용 해설**: 쿠버네티스 클러스터나 Jenkins 웹훅에 직접 연결해야만 대시보드를 띄울 수 있는 구조(AS-IS)는 로컬 개발 환경 구축과 UI 변경 검증을 지연시킵니다. `app.py`의 `get_mock_pipeline_status()`처럼 환경변수(`MOCK_MODE=true`) 하나로 단계별(`MOCK_STAGES`) 상태 전이를 시뮬레이션하는 분기를 내장(TO-BE)하면 클러스터 자격증명 없이도 Flask 개발 서버에서 프론트엔드와 엔드포인트를 즉시 테스트할 수 있습니다. 반면 Mock 경로와 실클러스터 경로의 응답 JSON 스키마가 어긋나면 운영 배포 시 장애로 이어지므로, 두 모드 모두 동일한 직렬화 모델을 공유하도록 계약 테스트를 두어야 합니다.

---

## 4. 엔지니어링 체크리스트 및 관찰 한계

- **실무 검토 포인트**:
  - 코딩 에이전트 저장소에는 `git reset --hard`, `git checkout -- .`, `git stash drop` 등 비가역적 Git 명령 금지 규칙과 브랜치 보호 정책을 함께 적용합니다.
  - 인프라·클러스터 연동 대시보드는 `MOCK_MODE` 환경변수로 자격증명 없는 로컬 실행 경로를 제공하되, Mock 응답과 실제 API 스키마 정합성을 검증합니다.
  - 다중 에이전트 도구(`.cursorrules`, `CLAUDE.md`, `AGENTS.md`)를 병행할 때는 동일 본문 복제 대신 `@AGENTS.md` 포인터 패턴으로 단일 원본을 유지합니다.
- **관찰 범위 및 한계**:
  - 본 정리는 2026-02-05 수집 시점의 `CLAUDE.md`, `.cursorrules`, `app.py` 최대 1,000자 발췌본에 기반합니다. 실제 운영 환경 배포 시에는 전체 훅 스크립트와 클러스터 연동 어댑터 코드를 별도 검토해야 합니다.
