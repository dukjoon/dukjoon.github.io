"""Deterministic AI-Tone Detector and Post-Balancing Validator (v1.1).

Features:
1. Code block (```) and inline code (`) masking to prevent false positives in code/logs.
2. Auto-trimming of chatbot cliches instead of tag clutter.
3. Two-tier tag bifurcation:
   - Hard Gate [검수필요: 사유]: unverified metrics, unsupported absolute assertions. (Blocks approval)
   - Soft Warning [문체점검: 사유]: tone/superlative suggestions. (Advisory only)
4. Source-grounded metric whitelisting: numbers present in source material are not flagged.
5. Channel-aware rules (git, naver, shortform).
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml


@dataclass
class ToneViolation:
    rule_type: str
    matched_text: str
    line_number: int
    suggestion: str
    severity: str = "warning"  # 'error' (Hard Block) or 'warning' (Soft Warning)
    is_blocking: bool = False


@dataclass
class BalancingResult:
    original_text: str
    balanced_text: str
    violations: List[ToneViolation] = field(default_factory=list)
    hard_block_count: int = 0
    soft_warning_count: int = 0
    ai_tone_score: float = 0.0
    passed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "ai_tone_score": round(self.ai_tone_score, 3),
            "hard_block_count": self.hard_block_count,
            "soft_warning_count": self.soft_warning_count,
            "violations_count": len(self.violations),
            "violations": [
                {
                    "rule": v.rule_type,
                    "text": v.matched_text,
                    "line": v.line_number,
                    "suggestion": v.suggestion,
                    "is_blocking": v.is_blocking,
                }
                for v in self.violations
            ],
        }


class PostBalancer:
    def __init__(self, policy_path: Optional[Path] = None):
        if policy_path is None:
            policy_path = Path(__file__).parent / "policy.yaml"
        self.policy_path = policy_path
        self.policy = self._load_policy()
        self.anti_ai = self.policy.get("anti_ai_tone", {})
        self.auto_trim_phrases = self.anti_ai.get("auto_trim_phrases", [])
        self.fact_anchoring = self.policy.get("fact_anchoring", {})
        self.unverified_claims = self.fact_anchoring.get("unverified_claims_patterns", [])
        self.channels_cfg = self.anti_ai.get("channels", {})

    def _load_policy(self) -> Dict[str, Any]:
        if not self.policy_path.exists():
            return {}
        with open(self.policy_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _mask_code_regions(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Mask fenced code blocks and inline code to prevent false positives."""
        placeholders: Dict[str, str] = {}
        counter = 0

        # 1. Mask fenced code blocks (```...```)
        def replace_fenced(match):
            nonlocal counter
            key = f"__CODE_FENCE_BLOCK_{counter}__"
            placeholders[key] = match.group(0)
            counter += 1
            return key

        masked = re.sub(r"```[\s\S]*?```", replace_fenced, text)

        # 2. Mask inline code (`...`)
        def replace_inline(match):
            nonlocal counter
            key = f"__CODE_INLINE_{counter}__"
            placeholders[key] = match.group(0)
            counter += 1
            return key

        masked = re.sub(r"`[^`\n]+`", replace_inline, masked)
        return masked, placeholders

    def _unmask_code_regions(self, text: str, placeholders: Dict[str, str]) -> str:
        for key, orig in placeholders.items():
            text = text.replace(key, orig)
        return text

    def _extract_source_numbers(self, source_text: str) -> Set[str]:
        """Extract all numbers and metric patterns from source text."""
        if not source_text:
            return set()
        # Find raw digits and numbers with common suffixes
        found = set(re.findall(r"\b\d+(?:\.\d+)?\b", source_text))
        return found

    def analyze(
        self,
        text: str,
        channel: str = "git",
        source_text: str = "",
    ) -> BalancingResult:
        # Step 1: Mask code blocks
        masked_text, placeholders = self._mask_code_regions(text)

        # Step 2: Auto-trim cliches (Remove completely without tag clutter)
        for pat in self.auto_trim_phrases:
            masked_text = re.sub(pat, "", masked_text)

        # Step 3: Get channel config
        chan_cfg = self.channels_cfg.get(channel, self.channels_cfg.get("git", {}))
        soft_adjectives = chan_cfg.get("soft_warn_adjectives", [])
        banned_openings = chan_cfg.get("banned_openings", [])
        max_emojis = chan_cfg.get("max_emoji_per_line", 1)

        source_numbers = self._extract_source_numbers(source_text)

        violations: List[ToneViolation] = []
        lines = masked_text.split("\n")
        balanced_lines: List[str] = []
        hard_block_count = 0
        soft_warning_count = 0

        emoji_pattern = re.compile(
            r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]",
            flags=re.UNICODE,
        )

        for idx, line in enumerate(lines, 1):
            curr_line = line.strip("\r")

            # Check for Banned Openings in shortform (Hard Gate)
            if channel == "shortform" and idx <= 8:
                for b_op in banned_openings:
                    if re.search(b_op, curr_line.strip()):
                        violations.append(
                            ToneViolation(
                                rule_type="shortform_boring_opening",
                                matched_text=curr_line.strip()[:20],
                                line_number=idx,
                                suggestion="숏폼 0~3초 훅에서 인사/설명 생략 및 즉각적 문제 제시로 시작",
                                severity="error",
                                is_blocking=True,
                            )
                        )
                        curr_line = f"[검수필요: 숏폼 지루한 오프닝 수정] " + curr_line
                        hard_block_count += 1

            # Check Unverified Absolute Claims (Hard Gate)
            for claim_pat in self.unverified_claims:
                if claim_pat in curr_line:
                    violations.append(
                        ToneViolation(
                            rule_type="unverified_absolute_claim",
                            matched_text=claim_pat,
                            line_number=idx,
                            suggestion=f"절대적 단정 표현 '{claim_pat}' 완화 및 예외/한계 명시",
                            severity="error",
                            is_blocking=True,
                        )
                    )
                    curr_line = curr_line.replace(
                        claim_pat, f"[검수필요: 단정표현 '{claim_pat}' 근거 확인]"
                    )
                    hard_block_count += 1

            # Check Unverified Metrics (% or 배수 not in source) (Hard Gate)
            if source_text:
                # Look for percentage claims like "300%", "99.9%"
                pct_matches = re.finditer(r"\b(\d+(?:\.\d+)?)\s*%", curr_line)
                for pm in pct_matches:
                    num_val = pm.group(1)
                    if num_val not in source_numbers:
                        # Exclude markdown formatting or standard headings
                        if f"{num_val}%" not in source_text:
                            violations.append(
                                ToneViolation(
                                    rule_type="unverified_metric",
                                    matched_text=pm.group(0),
                                    line_number=idx,
                                    suggestion=f"원문에 없는 수치 '{pm.group(0)}'는 근거 확인 필요",
                                    severity="error",
                                    is_blocking=True,
                                )
                            )
                            curr_line = curr_line.replace(
                                pm.group(0), f"{pm.group(0)}[검수필요: 원문 미기재 수치]"
                            )
                            hard_block_count += 1

            # Check Soft Warn Adjectives (Soft Warning only, NO blocking)
            for adj in soft_adjectives:
                if adj in curr_line:
                    violations.append(
                        ToneViolation(
                            rule_type="soft_warn_adjective",
                            matched_text=adj,
                            line_number=idx,
                            suggestion=f"과장 수식어 '{adj}' 담백한 표현으로 교체 권장",
                            severity="warning",
                            is_blocking=False,
                        )
                    )
                    curr_line = curr_line.replace(
                        adj, f"[문체점검: 수식어 '{adj}' 완화]"
                    )
                    soft_warning_count += 1

            # Check Excessive Emojis (Soft Warning)
            emojis = emoji_pattern.findall(curr_line)
            if len(emojis) > max_emojis:
                violations.append(
                    ToneViolation(
                        rule_type="excessive_emojis",
                        matched_text="".join(emojis),
                        line_number=idx,
                        suggestion=f"이모지 과다 사용 (허용치: {max_emojis}개)",
                        severity="warning",
                        is_blocking=False,
                    )
                )
                soft_warning_count += 1

            # Count existing manual tags
            if "[검수필요" in curr_line:
                hard_block_count += curr_line.count("[검수필요")
            if "[문체점검" in curr_line:
                soft_warning_count += curr_line.count("[문체점검")

            balanced_lines.append(curr_line)

        # Step 4: Unmask code blocks
        reconstructed = "\n".join(balanced_lines)
        final_balanced = self._unmask_code_regions(reconstructed, placeholders)

        # Calculate AI tone score
        total_words = max(1, len(re.findall(r"\w+", text)))
        ai_tone_score = len(violations) / (total_words / 25.0)

        # Passed check: no hard blocking violations
        passed = (hard_block_count == 0)

        return BalancingResult(
            original_text=text,
            balanced_text=final_balanced,
            violations=violations,
            hard_block_count=hard_block_count,
            soft_warning_count=soft_warning_count,
            ai_tone_score=ai_tone_score,
            passed=passed,
        )

    def extract_review_points(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract categorized review points: hard_blocks vs soft_warnings."""
        hard_blocks = []
        soft_warnings = []

        for idx, line in enumerate(text.split("\n"), 1):
            # 1. Hard Gate matches
            for m in re.finditer(r"\[검수필요:[^\]]+\]", line):
                hard_blocks.append({
                    "line": idx,
                    "tag": m.group(0),
                    "context": line.strip()[:90],
                    "type": "HARD_BLOCK",
                })
            # 2. Soft Warning matches
            for m in re.finditer(r"\[(문체점검:[^\]]+|추정)\]", line):
                soft_warnings.append({
                    "line": idx,
                    "tag": m.group(0),
                    "context": line.strip()[:90],
                    "type": "SOFT_WARNING",
                })

        return {
            "hard_blocks": hard_blocks,
            "soft_warnings": soft_warnings,
        }
