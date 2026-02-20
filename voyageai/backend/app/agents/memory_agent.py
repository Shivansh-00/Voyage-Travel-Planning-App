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
        query = f"{state['request'].destination} {' '.join(state['request'].preferences)}"
        vector = await self.embedder.embed(query)
        similar = await self.store.query(vector, top_k=2)
        state['memory_context'] = ' | '.join([item['metadata'].get('summary', '') for item in similar])
        await self.store.upsert(
            key=f"trip-{state['request'].origin}-{state['request'].destination}",
            values=vector,
            metadata={'summary': f"Trip pattern for {state['request'].destination}"},
        )
        self.log(state, 'Memory context loaded and refreshed.')
        return state
