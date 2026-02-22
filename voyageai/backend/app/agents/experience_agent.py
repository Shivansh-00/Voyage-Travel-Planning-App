"""
Agent 4 — Experience Curator

Populates each day in the itinerary with activities ranked by user
interests and scores.

Production-grade improvements:
  • Deduplicates activities across consecutive days in the same city
    even when the pool is small.
  • Caches API calls per-city so we don't hit mock APIs repeatedly.
  • Dynamically adjusts activities-per-day (2–4) based on
    trip style and available pool.
  • Adds arrival-day awareness: fewer activities on check-in days.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.tools.mock_apis import search_activities, get_daily_transport_cost, get_remote_work_spots
from app.schemas.travel import RemoteWorkSpot


class ExperienceAgent(BaseAgent):
    name = 'ExperienceAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        intent = state['intent']
        interests = {i.lower() for i in intent.interests}
        itinerary = state['day_by_day_itinerary']
        trip_type = intent.trip_type

        all_experiences: list[dict] = []
        total_activity_cost = 0.0
        total_transport_cost = 0.0
        remote_spots: list[RemoteWorkSpot] = []

        # Caches keyed by canonical city name
        city_key = lambda c: c.strip().lower()
        activity_cache: dict[str, list[dict]] = {}
        transport_cache: dict[str, float] = {}
        remote_cache: dict[str, list[dict]] = {}
        seen_remote: set[str] = set()

        # Track used activity names per city to eliminate cross-day duplicates
        city_used: dict[str, set[str]] = {}
        # Activity offset for deterministic rotation
        city_offset: dict[str, int] = {}

        for day_idx, day_item in enumerate(itinerary):
            city = day_item.city
            ck = city_key(city)

            # ── fetch & cache activities ────────────────────────────
            if ck not in activity_cache:
                acts = await search_activities(city)
                activity_cache[ck] = acts
                all_experiences.extend(acts)

            activities = activity_cache[ck]

            # ── rank by interest overlap then by quality score ──────
            def _sort_key(a: dict) -> tuple:
                type_match = 1 if a.get('type', '').lower() in interests else 0
                return (type_match, a.get('score', 0))

            ranked = sorted(activities, key=_sort_key, reverse=True)

            # ── decide how many activities this day ─────────────────
            is_arrival_day = (day_idx > 0 and
                              city_key(itinerary[day_idx - 1].city) != ck)
            is_relaxation = trip_type in ('relaxation', 'honeymoon')

            if is_arrival_day:
                n_per_day = 2  # lighter day
            elif is_relaxation:
                n_per_day = 2
            else:
                n_per_day = min(3, len(ranked)) if len(ranked) <= 4 else 3

            # ── pick activities with duplicate prevention ───────────
            used_names = city_used.setdefault(ck, set())
            offset = city_offset.get(ck, 0)
            chosen: list[dict] = []

            # First pass: pick unseen activities from offset position
            pool_len = len(ranked)
            for i in range(pool_len):
                if len(chosen) >= n_per_day:
                    break
                idx = (offset + i) % pool_len
                act = ranked[idx]
                if act['name'] not in used_names:
                    chosen.append(act)

            # If we still need more (pool exhausted), allow repeats
            # but pick highest-scored ones not already chosen today
            chosen_names = {a['name'] for a in chosen}
            if len(chosen) < n_per_day:
                for act in ranked:
                    if act['name'] not in chosen_names:
                        chosen.append(act)
                        chosen_names.add(act['name'])
                        if len(chosen) >= n_per_day:
                            break

            # Update tracking
            for a in chosen:
                used_names.add(a['name'])
            city_offset[ck] = offset + len(chosen)

            # ── If ALL activities in the pool have been used,
            #    reset so next cycle gets fresh picks ────────────────
            if len(used_names) >= pool_len:
                city_used[ck] = set()

            # ── assign to day ───────────────────────────────────────
            day_item.activities = [a['name'] for a in chosen]
            day_cost = sum(a.get('cost_inr', 0) for a in chosen)
            day_item.estimated_cost_inr = day_cost
            total_activity_cost += day_cost

            # ── transport cost (cached) ─────────────────────────────
            if ck not in transport_cache:
                transport_cache[ck] = await get_daily_transport_cost(city)
            total_transport_cost += transport_cache[ck]

            # ── remote work spots (once per city) ───────────────────
            if ck not in seen_remote:
                seen_remote.add(ck)
                if ck not in remote_cache:
                    remote_cache[ck] = await get_remote_work_spots(city)
                spots = remote_cache[ck]
                if spots:
                    remote_spots.append(RemoteWorkSpot(city=city, recommendations=spots))

        state['experiences'] = all_experiences
        state['cost_breakdown'].activities_estimated = total_activity_cost
        state['cost_breakdown'].transport_estimated = total_transport_cost
        state['remote_work_spots'] = remote_spots

        self.log(
            state,
            f'Curated {sum(len(d.activities) for d in itinerary)} activities '
            f'across {len(itinerary)} days. Activity cost: ₹{total_activity_cost:,.0f}.'
        )
        return state
