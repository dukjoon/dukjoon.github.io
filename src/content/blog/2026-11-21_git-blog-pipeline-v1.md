---
title: "Git Blog Pipeline V1: 실무 엔지니어링 아키텍처 및 가드레일 설계 노트"
pubDatetime: 2026-11-21T00:00:00Z
description: "다중 LLM 및 자동화 워크플로우를 실무에 도입할 때 가장 흔히 겪는 문제는 생성 결과물의 환각과 인공지능 특유의 상투적 어조입니다."
category: ai-engineering
tags:
  - ai-engineering
  - engineering
  - architecture
draft: false
---

## 1. 배경 및 문제 정의
다중 LLM 및 자동화 워크플로우를 실무에 도입할 때 가장 흔히 겪는 문제는 생성 결과물의 환각과 인공지능 특유의 상투적 어조입니다.
자동화 파이프라인이 아무리 빠르게 초안을 생성해도, 실무자의 검증을 거치지 않으면 프로덕션 배포 단계에서 병목이 발생합니다.

## 2. 관찰된 사실과 데이터 한계
본 문서는 로컬 프로젝트에서 수집된 실제 관찰 데이터를 바탕으로 작성되었습니다:

- **사실 관찰 (이원화 가드레일 설계)**: 팩트 검증(Hard Gate)과 문체 경고(Soft Warning)를 분리하여 오탐 피로도를 최소화함.
- **사실 관찰 (코드 블록 마스킹)**: 마크다운 코드 블록과 인라인 코드를 검사 대상에서 사전 마스킹하여 기술 용어 오탐 방지.
- **사실 관찰 (원문 수치 화이트리스트)**: `sources/` 원문에 이미 존재하는 숫자는 자동으로 검증 통과 처리.
- **사실 관찰 (상투어 자동 절삭 Auto-Trim)**: 상투적인 인사말과 맺음말을 태깅하지 않고 자동 제거.
- 현재 다수 프로젝트에서 `CLAUDE.md` 및 `.cursorrules`를 통한 프로젝트 레벨 컨텍스트 주입 패턴이 확산되고 있는 추세입니다.

```
[Raw Sources] ──► [Pipeline Orchestrator] ──► [Deterministic PostBalancer] ──► [Pending Review Queue]
                         │                             │                                 │
                         ▼                             ▼                                 ▼
                 Multi-Model Routing           Anti-AI & Fact Tagging              Human Gatekeeper
```

## 3. 핵심 아키텍처 및 설계 트레이드오프
1. **상태 머신 기반의 발행 잠금(Publish Lock)**:
   - 모델이 임의로 `published: true` 상태를 쓰거나 외부 채널로 다이렉트 푸시하지 못하도록 코드 레벨에서 차단합니다.
   - 모든 생성물은 `status: approved`로 고정되며, `guardrails/approve.py`를 거쳐야만 릴리즈 스테이지로 승격됩니다.
2. **결정론적 후처리(Post-Balancer)**:
   - LLM 프롬프트에만 의존하지 않고 정규식 및 금지어 사전을 통해 기계적으로 스코어링합니다.
   - 코드 블록(```) 영역은 마스킹하여 오탐을 방지하고, 팩트 오류만 승인을 차단합니다.

## 4. 실무 검증 결과
3분 이내에 팩트를 확인할 수 있는 Review Brief를 매 실행마다 생성하도록 파이프라인을 고정했습니다.
