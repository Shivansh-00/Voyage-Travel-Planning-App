from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):
    @abstractmethod
    async def upsert(self, key: str, values: list[float], metadata: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def query(self, vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        raise NotImplementedError


class FaissVectorStore(VectorStore):
    def __init__(self) -> None:
        self._items: dict[str, tuple[list[float], dict[str, Any]]] = {}

    async def upsert(self, key: str, values: list[float], metadata: dict[str, Any]) -> None:
        self._items[key] = (values, metadata)

    async def query(self, vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        scored = []
        for key, (vals, meta) in self._items.items():
            score = sum(a * b for a, b in zip(vals, vector))
            scored.append({'id': key, 'score': score, 'metadata': meta})
        return sorted(scored, key=lambda x: x['score'], reverse=True)[:top_k]


class PineconeVectorStore(VectorStore):
    def __init__(self, api_key: str, index_name: str, environment: str) -> None:
        self.api_key = api_key
        self.index_name = index_name
        self.environment = environment
        self._fallback = FaissVectorStore()

    async def upsert(self, key: str, values: list[float], metadata: dict[str, Any]) -> None:
        await self._fallback.upsert(key, values, metadata)

    async def query(self, vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        return await self._fallback.query(vector, top_k=top_k)
