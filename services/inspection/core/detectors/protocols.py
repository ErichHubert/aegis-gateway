from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.models import Finding


@runtime_checkable
class IDetector(Protocol):
    """Base abstraction for any synchronous prompt detector.

    Implementations are expected to be side‑effect free and safe to reuse
    across requests. The detector takes a raw prompt string and returns
    zero or more :class:`Finding` instances.
    """

    def detect(self, prompt: str) -> list[Finding]:
        """Analyze the given prompt text and return all findings.

        Implementations must not mutate ``prompt`` and should avoid
        raising exceptions for "normal" input. Unexpected errors should
        be handled internally and surfaced as an empty list or logged
        appropriately, depending on the calling context.
        """
        ...

    def warmup(self) -> None:
        """Optional warmup hook to prepare any heavy resources.

        This is called once during service startup to allow the detector
        to initialize any heavy dependencies (ML models, Presidio engine,
        regex compilations, etc.) before handling requests.
        """
        ...


class IPiiDetector(IDetector, Protocol):
    """Marker protocol for detectors that focus on PII findings.

    This does not add new members beyond :class:`IDetector` but allows
    you to type specific collections such as ``list[IPiiDetector]``
    when wiring the rule engine.
    """

    ...


class ISecretDetector(IDetector, Protocol):
    """Marker protocol for detectors that focus on secret/credential findings."""

    ...


class IInjectionDetector(IDetector, Protocol):
    """Marker protocol for detectors that focus on prompt‑injection patterns."""

    ...