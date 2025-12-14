# conftest.py
import pytest
from core.models import PromptInspectionRequest, PromptInspectionResponse
from core.rules import analyze_prompt

@pytest.fixture
def run_with_detector():
    """Return a runner that executes analyze_prompt with exactly one detector."""
    def _run(detector, req: PromptInspectionRequest) -> PromptInspectionResponse:
        detector.warmup()
        return analyze_prompt(req, (detector,))
    return _run
