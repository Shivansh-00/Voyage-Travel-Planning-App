"""
Agent 2 — Cost Analyst / Budget Optimizer

Uses a mathematically rigorous proportional-allocation algorithm to fit
the trip plan within the user's budget.  Preserves relative category
weights while minimising quality loss.

Algorithm:
  1. Compute the raw total across all cost buckets.
  2. If over budget, calculate a scale factor (budget / total) and apply
     it proportionally — but protect flights (non-negotiable) and keep a
     minimum floor for accommodation and activities.
  3. Propagate reductions back into per-day and per-stay artefacts so the
     itinerary stays consistent with the breakdown.
  4. Score the optimisation on a 0-10 scale using the budget-fit ratio.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.schemas.travel import CostBreakdown


# Categories ordered by flexibility (last = most flexible)
_FLEX_ORDER = [
    'flights_estimated',
    'transport_estimated',
    'accommodation_estimated',
    'activities_estimated',
]

# Minimum share each flexible category can shrink to (fraction of original)
_MIN_SHARE = {
    'flights_estimated': 0.95,       # flights are nearly non-negotiable
    'transport_estimated': 0.60,     # can switch to public transit
    'accommodation_estimated': 0.40, # can downgrade significantly
    'activities_estimated': 0.25,    # many free alternatives
}


class BudgetOptimizerAgent(BaseAgent):
    name = 'BudgetOptimizerAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        intent = state['intent']
        cb = state['cost_breakdown']

        # ── 1. Compute raw total ───────────────────────────────────────
        cb.total_estimated = self._sum(cb)

        budget_max = (
            intent.budget_range_inr.max
            or intent.budget_total_inr
            or None
        )

        rounds = 0

        # ── 2. Proportional budget fitting ─────────────────────────────
        if budget_max and budget_max > 0 and cb.total_estimated > budget_max:
            overshoot = cb.total_estimated - budget_max

            # Build flexibility pool: how much each bucket CAN give back
            pool: list[tuple[str, float]] = []
            for cat in _FLEX_ORDER:
                original = getattr(cb, cat)
                floor = original * _MIN_SHARE[cat]
                headroom = original - floor
                if headroom > 0:
                    pool.append((cat, headroom))

            total_headroom = sum(h for _, h in pool)

            if total_headroom > 0:
                # Distribute reduction proportionally across flexible buckets
                scale = min(overshoot / total_headroom, 1.0)
                reductions: dict[str, float] = {}
                for cat, headroom in pool:
                    reduction = round(headroom * scale, 2)
                    reductions[cat] = reduction
                    setattr(cb, cat, getattr(cb, cat) - reduction)
                rounds = 1

                # Propagate reductions back to artefacts
                self._propagate_accommodation(state, cb)
                self._propagate_activities(state, cb)
            else:
                rounds = 0

            cb.total_estimated = self._sum(cb)

            # Second pass: if still over, do a hard trim
            if cb.total_estimated > budget_max:
                remaining = cb.total_estimated - budget_max
                for cat in ['activities_estimated', 'accommodation_estimated', 'transport_estimated']:
                    if remaining <= 0:
                        break
                    current = getattr(cb, cat)
                    floor = current * 0.20
                    can_cut = current - floor
                    cut = min(can_cut, remaining)
                    if cut > 0:
                        setattr(cb, cat, current - cut)
                        remaining -= cut
                        rounds += 1

                self._propagate_accommodation(state, cb)
                self._propagate_activities(state, cb)
                cb.total_estimated = self._sum(cb)

        state['total_cost'] = cb.total_estimated

        # ── 3. Optimisation score ──────────────────────────────────────
        if budget_max and budget_max > 0:
            ratio = cb.total_estimated / budget_max
            if ratio <= 1.0:
                # Slightly under budget is good; very under-budget still strong
                score = round(max(5.0, 10.0 - (1.0 - ratio) * 15), 1)
            else:
                # Over budget is penalised harder
                score = round(max(0, 10.0 - (ratio - 1.0) * 30), 1)
        else:
            score = 7.5
        state['optimization_score'] = score

        # ── 4. Summary ────────────────────────────────────────────────
        summary_parts = [f'Total: ₹{cb.total_estimated:,.0f}.']
        if budget_max:
            diff = budget_max - cb.total_estimated
            if diff >= 0:
                pct = round((diff / budget_max) * 100, 1)
                summary_parts.append(f'Under budget by ₹{diff:,.0f} ({pct}% savings).')
            else:
                summary_parts.append(f'Over budget by ₹{abs(diff):,.0f} — manual adjustments recommended.')
            if rounds:
                summary_parts.append(f'Auto-optimised in {rounds} pass(es).')
        summary_parts.append(f'Score: {score}/10.')
        state['optimization_summary'] = ' '.join(summary_parts)
        self.log(state, state['optimization_summary'])
        return state

    # ── helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _sum(cb: CostBreakdown) -> float:
        return round(
            cb.flights_estimated
            + cb.accommodation_estimated
            + cb.activities_estimated
            + cb.transport_estimated,
            2,
        )

    @staticmethod
    def _propagate_accommodation(state: TravelGraphState, cb: CostBreakdown) -> None:
        """Keep stay_recommendations consistent with accommodation_estimated."""
        stays = state.get('stay_recommendations', [])
        if not stays:
            return
        intent = state['intent']
        n_dest = len(stays)
        duration = intent.duration_days
        base_nights = duration // n_dest
        remainder = duration % n_dest
        total_nights = sum(base_nights + (1 if i < remainder else 0) for i in range(n_dest))
        if total_nights > 0:
            per_night = cb.accommodation_estimated / total_nights
            for s in stays:
                s.budget_per_night_inr = round(per_night, 0)

    @staticmethod
    def _propagate_activities(state: TravelGraphState, cb: CostBreakdown) -> None:
        """Distribute activity budget evenly across itinerary days."""
        days = state.get('day_by_day_itinerary', [])
        if not days:
            return
        per_day = cb.activities_estimated / len(days)
        for d in days:
            d.estimated_cost_inr = round(per_day, 0)
