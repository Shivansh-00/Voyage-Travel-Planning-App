"""
Agent — Hotel / Stay Intelligence

Searches accommodation options per destination and picks the best match
for the user's budget and accommodation preferences.
"""

from __future__ import annotations

import math
from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.schemas.travel import StayRecommendation
from app.tools.mock_apis import search_hotels


class HotelIntelligenceAgent(BaseAgent):
    name = 'HotelIntelligenceAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        intent = state['intent']
        destinations = intent.destinations or ['Unknown']
        duration = intent.duration_days
        prefs = {p.lower() for p in intent.accommodation_preferences}

        all_options: list[dict] = []
        stays: list[StayRecommendation] = []
        total_accommodation = 0.0

        n_dest = len(destinations)
        base_nights = duration // n_dest
        remainder = duration % n_dest

        for idx, dest in enumerate(destinations):
            nights = base_nights + (1 if idx < remainder else 0)
            hotels = await search_hotels(dest)
            all_options.extend(hotels)

            # pick hotel matching preferences
            chosen = self._pick_hotel(hotels, prefs)
            cost = chosen['nightly_rate_inr'] * nights
            total_accommodation += cost

            stays.append(StayRecommendation(
                city=dest,
                stay_type=chosen.get('type', 'hotel'),
                budget_per_night_inr=chosen['nightly_rate_inr'],
            ))

        state['hotel_options'] = all_options
        state['stay_recommendations'] = stays
        state['cost_breakdown'].accommodation_estimated = total_accommodation

        self.log(
            state,
            f'Selected stays for {n_dest} destination(s). '
            f'Total accommodation: ₹{total_accommodation:,.0f}.'
        )
        return state

    @staticmethod
    def _pick_hotel(hotels: list[dict], prefs: set[str]) -> dict:
        """Choose the hotel that best matches user preferences."""
        if 'luxury hotel' in prefs or '5-star hotel' in prefs:
            return max(hotels, key=lambda h: h['nightly_rate_inr'])
        if 'hostel' in prefs or 'budget hotel' in prefs:
            return min(hotels, key=lambda h: h['nightly_rate_inr'])
        # default: best value (mid-range)
        sorted_h = sorted(hotels, key=lambda h: h['nightly_rate_inr'])
        return sorted_h[len(sorted_h) // 2] if sorted_h else hotels[0]
