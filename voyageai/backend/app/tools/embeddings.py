from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class DeterministicEmbeddingProvider(EmbeddingProvider):
    async def embed(self, text: str) -> list[float]:
        base = [0.0] * 8
        for idx, char in enumerate(text[:64]):
            base[idx % 8] += (ord(char) % 97) / 100
        return base
