from __future__ import annotations

from abc import ABC, abstractmethod


class Warmable(ABC):
    """Explicit contract for components that support warmup."""

    @abstractmethod
    def warmup(self) -> None:
        ...
