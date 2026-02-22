"""
Agent — Validation / Guardrails

Final agent in the pipeline.  Validates the assembled plan for:
  • no budget overshoot (warns if still over)
  • no duplicate days
  • clean city names (not raw paragraphs)
  • all required fields present
  • cost_breakdown consistency

This is the equivalent of an ``OutputFixingParser`` /
``RetryWithErrorCorrectionChain`` layer.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState


class ValidationAgent(BaseAgent):
    name = 'ValidationAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        errors: list[str] = []

        itinerary = state.get('day_by_day_itinerary', [])
        cb = state.get('cost_breakdown')
        intent = state.get('intent')

        # 1 — No duplicate day numbers
        day_nums = [d.day for d in itinerary]
        if len(day_nums) != len(set(day_nums)):
            errors.append('Duplicate day numbers detected; deduplicated.')
            seen: set[int] = set()
            deduped = []
            for d in itinerary:
                if d.day not in seen:
                    seen.add(d.day)
                    deduped.append(d)
            state['day_by_day_itinerary'] = deduped

        # 2 — City names must be clean (not a raw paragraph)
        for d in state.get('day_by_day_itinerary', []):
            if len(d.city) > 50:
                d.city = d.city[:50].split()[0]
                errors.append(f'Day {d.day}: city name truncated.')

        # 3 — Cost breakdown consistency
        if cb:
            recalc = (
                cb.flights_estimated
                + cb.accommodation_estimated
                + cb.activities_estimated
                + cb.transport_estimated
            )
            if abs(recalc - cb.total_estimated) > 1:
                cb.total_estimated = recalc
                errors.append('Cost breakdown total was inconsistent; recalculated.')

        # 4 — Budget overshoot warning
        if intent and cb:
            budget_max = (
                intent.budget_range_inr.max
                or intent.budget_total_inr
            )
            if budget_max and cb.total_estimated > budget_max:
                errors.append(
                    f'Plan still exceeds budget (₹{cb.total_estimated:,.0f} > ₹{budget_max:,.0f}). '
                    'Consider further manual adjustments.'
                )

        # 5 — At least one destination
        if intent and not intent.destinations:
            errors.append('No destinations could be extracted from the prompt.')

        # 6 — Activities present
        empty_days = [d.day for d in state.get('day_by_day_itinerary', []) if not d.activities]
        if empty_days:
            errors.append(f'Days with no activities: {empty_days}.')

        state['validation_errors'] = errors
        if errors:
            self.log(state, f'Validation completed with {len(errors)} warning(s): {"; ".join(errors)}')
        else:
            self.log(state, 'Validation passed — plan is clean.')
        return state
