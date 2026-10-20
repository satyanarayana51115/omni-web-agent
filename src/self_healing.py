"""Semantic self-healing matcher for broken and mutated UI locators."""

from __future__ import annotations
import difflib
from typing import List, Optional
from src.models import ElementFingerprint, HealingMatch

WEIGHTS = {
    "data_testid": 0.40,
    "id": 0.20,
    "name": 0.15,
    "text_content": 0.10,
    "classes": 0.10,
    "tag_name": 0.05,
}


def _str_similarity(s1: Optional[str], s2: Optional[str]) -> float:
    if not s1 or not s2:
        return 0.0
    return difflib.SequenceMatcher(None, str(s1).strip().lower(), str(s2).strip().lower()).ratio()


def _list_overlap(l1: List[str], l2: List[str]) -> float:
    if not l1 or not l2:
        return 0.0
    set1, set2 = set(l1), set(l2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


class SelfHealingEngine:
    def __init__(self, high_confidence_threshold: float = 0.50, min_threshold: float = 0.20):
        self.high_confidence_threshold = high_confidence_threshold
        self.min_threshold = min_threshold

    def calculate_similarity(
        self, target: ElementFingerprint, candidate: ElementFingerprint
    ) -> tuple[float, List[str]]:
        score = 0.0
        reasons: List[str] = []

        # Tag Name Check
        if target.tag_name and candidate.tag_name:
            if target.tag_name.lower() == candidate.tag_name.lower():
                score += WEIGHTS["tag_name"]
                reasons.append("Exact tag match")
            else:
                return 0.0, ["Mismatched tag types"]

        # Data Test ID (Strongest Match)
        test_sim = _str_similarity(target.data_testid, candidate.data_testid)
        if test_sim > 0.3:
            score += WEIGHTS["data_testid"] * test_sim
            reasons.append(f"Test-ID match: {test_sim:.2f}")

        # ID Similarity
        id_sim = _str_similarity(target.id, candidate.id)
        if id_sim > 0.3:
            score += WEIGHTS["id"] * id_sim
            reasons.append(f"ID match: {id_sim:.2f}")

        # Name Attribute
        name_sim = _str_similarity(target.name, candidate.name)
        if name_sim > 0.3:
            score += WEIGHTS["name"] * name_sim
            reasons.append(f"Name match: {name_sim:.2f}")

        # Text Content
        text_sim = _str_similarity(target.text_content, candidate.text_content)
        if text_sim > 0.3:
            score += WEIGHTS["text_content"] * text_sim
            reasons.append(f"Text match: {text_sim:.2f}")

        # Classes Overlap
        cls_sim = _list_overlap(target.classes, candidate.classes)
        if cls_sim > 0.0:
            score += WEIGHTS["classes"] * cls_sim
            reasons.append(f"Class match: {cls_sim:.2f}")

        return round(score, 3), reasons

    def find_best_match(
        self, target: ElementFingerprint, candidates: List[ElementFingerprint]
    ) -> Optional[HealingMatch]:
        ranked: List[HealingMatch] = []

        for cand in candidates:
            score, reasons = self.calculate_similarity(target, cand)
            if score >= self.min_threshold:
                tier = "HIGH" if score >= self.high_confidence_threshold else "MEDIUM"
                ranked.append(
                    HealingMatch(
                        candidate_fingerprint=cand,
                        match_score=score,
                        selector_used=cand.css_selector,
                        confidence_tier=tier,
                        reasons=reasons,
                    )
                )

        if not ranked:
            return None

        ranked.sort(key=lambda m: m.match_score, reverse=True)
        return ranked[0]