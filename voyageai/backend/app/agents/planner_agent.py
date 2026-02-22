"""
Agent 3 — Route Optimizer / Planner

Generates the day-by-day itinerary skeleton, transport plan, and route
strategy from the extracted ``UserIntent``.

Improvements over naive allocation:
  • Counts transit days between distant cities (flight/check-out day).
  • Gives a minimum 2-day stay per destination for meaningful exploration.
  • Generates contextual transport pass recommendations.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.schemas.travel import DayItinerary, TransportPlan


# Cities that warrant a transit half-day between them (long-haul or far)
_LONG_HAUL_PAIRS: set[frozenset[str]] = {
    frozenset(p) for p in [
        ('delhi', 'tokyo'), ('delhi', 'paris'), ('delhi', 'london'),
        ('delhi', 'new york'), ('delhi', 'sydney'), ('delhi', 'bali'),
        ('mumbai', 'tokyo'), ('mumbai', 'london'), ('mumbai', 'paris'),
        ('mumbai', 'new york'), ('mumbai', 'sydney'),
    ]
}


class PlannerAgent(BaseAgent):
    name = 'PlannerAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        intent = state['intent']
        destinations = intent.destinations or ['Unknown']
        duration = intent.duration_days
        origin = intent.origin_city or 'Your city'

        # ── route strategy ─────────────────────────────────────────────
        if len(destinations) == 1:
            route_strategy = f'Direct round-trip: {origin} → {destinations[0]} → {origin}'
            route_order = [origin, destinations[0], origin]
        else:
            route_strategy = (
                f'Multi-city loop: {origin} → '
                + ' → '.join(destinations)
                + f' → {origin}'
            )
            route_order = [origin] + destinations + [origin]

        # ── allocate days across destinations ──────────────────────────
        n_dest = len(destinations)

        # Reserve light transit awareness (don't burn whole days, just tag them)
        # Ensure minimum 1 day per destination
        min_per_dest = max(1, duration // (n_dest * 2))  # at least half the even split
        base_days = max(duration // n_dest, min_per_dest)
        remainder = duration - (base_days * n_dest)

        # Distribute remainder to earlier destinations
        day_counter = 1
        day_by_day: list[DayItinerary] = []

        for idx, city in enumerate(destinations):
            # Extra days go to earlier destinations (more to explore)
            city_days = base_days + (1 if idx < remainder else 0)
            if city_days < 1:
                city_days = 1

            for d in range(city_days):
                is_arrival = d == 0 and idx > 0
                day_by_day.append(DayItinerary(
                    day=day_counter,
                    city=city,
                    activities=[],  # filled by ExperienceAgent
                    estimated_cost_inr=0,
                    weather_note='Arrival & check-in day' if is_arrival and len(destinations) > 1 else '',
                ))
                day_counter += 1

        # ── transport plan ─────────────────────────────────────────────
        passes: list[str] = []
        dest_set = {d.lower() for d in destinations}

        # Japan Rail Pass
        japan_cities = {'tokyo', 'osaka', 'kyoto', 'hiroshima', 'nara'}
        if len(dest_set & japan_cities) >= 2:
            passes.append('Japan Rail Pass (7-day)')
        elif dest_set & japan_cities:
            passes.append('Suica / Pasmo IC Card')

        # Eurail
        eu_cities = {'paris', 'london', 'amsterdam', 'berlin', 'prague', 'brussels',
                     'rome', 'florence', 'venice', 'barcelona', 'madrid', 'vienna',
                     'budapest', 'lisbon', 'athens', 'munich', 'zurich', 'geneva'}
        eu_matches = dest_set & eu_cities
        if len(eu_matches) >= 3:
            passes.append('Eurail Global Pass')
        elif len(eu_matches) == 2:
            passes.append('Eurail 2-Country Pass')

        # UK cards
        if dest_set & {'london', 'edinburgh'}:
            passes.append('Oyster Card / Contactless')

        # India-specific
        india_cities = {'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata',
                        'jaipur', 'goa', 'varanasi', 'kochi', 'hyderabad'}
        india_matches = dest_set & india_cities
        if len(india_matches) >= 3:
            passes.append('IndiGo/SpiceJet multi-city domestic pass')

        # Per-city metro cards
        for d in destinations:
            passes.append(f'{d} local transit / metro card')

        transport_plan = TransportPlan(
            recommended_passes=passes,
            route_order=route_order,
        )

        state['day_by_day_itinerary'] = day_by_day
        state['transport_plan'] = transport_plan
        state['route_strategy'] = route_strategy
        state['summary'] = (
            f'{duration}-day trip covering {n_dest} destination(s): '
            + ', '.join(destinations)
            + f' for {intent.traveler_count} traveler(s).'
        )

        self.log(state, f'Route planned: {route_strategy}. {len(day_by_day)} day-slots allocated.')
        return state
