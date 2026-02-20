from abc import ABC, abstractmethod
from app.schemas.state import TravelGraphState


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def run(self, state: TravelGraphState) -> TravelGraphState:
        raise NotImplementedError

    def log(self, state: TravelGraphState, message: str) -> None:
        state['logs'].append(f'[{self.name}] {message}')
