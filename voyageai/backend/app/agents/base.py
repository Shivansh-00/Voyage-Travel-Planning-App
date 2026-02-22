from __future__ import annotations

from abc import ABC, abstractmethod
from app.schemas.state import TravelGraphState


class BaseAgent(ABC):
    """Base class for every agent in the travel-intelligence pipeline."""

    name: str

    @abstractmethod
    async def run(self, state: TravelGraphState) -> TravelGraphState:
        raise NotImplementedError

    def log(self, state: TravelGraphState, message: str) -> None:
        state['logs'].append(f'[{self.name}] {message}')
