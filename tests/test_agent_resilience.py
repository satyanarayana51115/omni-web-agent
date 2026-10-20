"""PyTest suite evaluating self-healing scoring resilience against broken selectors."""

import pytest
from src.models import ElementFingerprint
from src.self_healing import SelfHealingEngine


@pytest.fixture
def healing_engine():
    return SelfHealingEngine()


def test_heals_when_id_is_mutated(healing_engine):
    target = ElementFingerprint(
        tag_name="button",
        id="submit-v1-legacy",
        name="submit-btn",
        data_testid="submit-action",
        text_content="Submit Application",
        css_selector="#submit-v1-legacy",
    )

    candidates = [
        ElementFingerprint(
            tag_name="button",
            id="cancel-btn",
            text_content="Cancel",
            css_selector="#cancel-btn",
        ),
        ElementFingerprint(
            tag_name="button",
            id="submit-v2-dynamic-892",  # ID altered by frontend bundler
            name="submit-btn",
            data_testid="submit-action",
            text_content="Submit Application",
            css_selector="#submit-v2-dynamic-892",
        ),
    ]

    match = healing_engine.find_best_match(target, candidates)

    assert match is not None
    assert match.candidate_fingerprint.id == "submit-v2-dynamic-892"
    assert match.confidence_tier == "HIGH"
    assert match.match_score >= 0.80


def test_rejects_incompatible_elements(healing_engine):
    target = ElementFingerprint(
        tag_name="input",
        id="search-input",
        placeholder="Search documentation...",
        css_selector="#search-input",
    )

    candidates = [
        ElementFingerprint(
            tag_name="a",
            id="docs-link",
            text_content="Search documentation...",
            css_selector="a#docs-link",
        )
    ]

    match = healing_engine.find_best_match(target, candidates)
    assert match is None