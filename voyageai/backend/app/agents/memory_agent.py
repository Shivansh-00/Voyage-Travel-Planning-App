"""
Agent — Memory / Session Context

Embeds the current query into the vector store and retrieves similar past
trip patterns for context enrichment.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.tools.embeddings import DeterministicEmbeddingProvider
from app.tools.vector_store import VectorStore


class MemoryAgent(BaseAgent):
    name = 'MemoryAgent'

    def __init__(self, store: VectorStore):
        self.store = store
        self.embedder = DeterministicEmbeddingProvider()

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        intent = state['intent']
        destinations = ' '.join(intent.destinations)
        interests = ' '.join(intent.interests)
        query = f'{destinations} {interests} {" ".join(intent.trip_type)}'

        vector = await self.embedder.embed(query)
        similar = await self.store.query(vector, top_k=2)
        state['memory_context'] = ' | '.join(
            item['metadata'].get('summary', '') for item in similar
        )

        origin = intent.origin_city or 'unknown'
        await self.store.upsert(
            key=f'trip-{origin}-{destinations}',
            values=vector,
            metadata={'summary': f'Trip pattern: {origin} → {destinations}'},
        )
        self.log(state, 'Memory context loaded and refreshed.')
        return state
