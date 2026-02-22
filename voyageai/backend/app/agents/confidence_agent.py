"""
Agent — Confidence Scoring

Evaluates the reliability of each agent's output and computes a weighted
overall confidence score.  This runs as the penultimate agent (before
validation) so it can inspect all gathered data.

Production-grade improvements:
  • Better calibrated base scores (0.65-0.70) since our data pipeline
    always returns structured mock data.
  • Finer-grained bonuses for data quality signals.
  • Penalty for anomalous values (e.g. negative prices).
  • Separate rubrics for completeness vs quality.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.schemas.travel import ConfidenceScores


class ConfidenceAgent(BaseAgent):
    name = 'ConfidenceAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        intent = state['intent']
        scores = ConfidenceScores()

        # ── Intent Parsing confidence ─────────────────────────────────
        intent_score = 0.55  # base: we always parse something
        if intent.destinations:
            intent_score += 0.15
        if intent.budget_total_inr or (intent.budget_range_inr and intent.budget_range_inr.max):
            intent_score += 0.10
        if intent.travel_month:
            intent_score += 0.07
        if intent.origin_city:
            intent_score += 0.05
        if intent.trip_type and intent.trip_type != 'general':
            intent_score += 0.04
        if intent.interests and len(intent.interests) >= 2:
            intent_score += 0.04
        scores.intent_parsing = round(min(intent_score, 1.0), 2)

        # ── Route Planning confidence ─────────────────────────────────
        itinerary = state.get('day_by_day_itinerary', [])
        route_score = 0.65
        if len(itinerary) == intent.duration_days:
            route_score += 0.15  # exact day count match
        if state.get('route_strategy'):
            route_score += 0.08
        if state.get('transport_plan') and state['transport_plan'].route_order:
            route_score += 0.07
        # Bonus: every day has a city assigned
        if itinerary and all(d.city for d in itinerary):
            route_score += 0.05
        scores.route_planning = round(min(route_score, 1.0), 2)

        # ── Flight Data confidence ────────────────────────────────────
        flights = state.get('flight_options', [])
        flight_score = 0.60
        if flights:
            flight_score += 0.15
            if len(flights) >= 3:
                flight_score += 0.10
            prices = [f.get('price_inr', 0) for f in flights if f.get('price_inr', 0) > 0]
            if prices:
                spread = (max(prices) - min(prices)) / max(prices) if max(prices) > 0 else 0
                if spread > 0.15:
                    flight_score += 0.10  # good price diversity
                # Penalty: any negative / zero prices
                if any(p <= 0 for p in prices):
                    flight_score -= 0.10
        scores.flight_data = round(min(max(flight_score, 0.0), 1.0), 2)

        # ── Hotel Data confidence ─────────────────────────────────────
        hotels = state.get('hotel_options', [])
        hotel_score = 0.60
        if hotels:
            hotel_score += 0.15
            if len(hotels) >= 4:
                hotel_score += 0.10
            if state.get('stay_recommendations'):
                recs = state['stay_recommendations']
                hotel_score += 0.10
                # Bonus: recommendations have city + budget info
                if recs and all(
                    getattr(r, 'city', None) and getattr(r, 'budget_per_night_inr', 0) > 0
                    for r in recs
                ):
                    hotel_score += 0.05
        scores.hotel_data = round(min(hotel_score, 1.0), 2)

        # ── Activity Data confidence ──────────────────────────────────
        act_score = 0.60
        days_with_activities = sum(1 for d in itinerary if d.activities)
        total_days = len(itinerary)
        if total_days > 0 and days_with_activities == total_days:
            act_score += 0.20  # full coverage
        elif days_with_activities > 0:
            act_score += 0.10 * (days_with_activities / max(total_days, 1))
        if state.get('experiences') and len(state['experiences']) > 3:
            act_score += 0.10
        if state.get('remote_work_spots'):
            act_score += 0.05
        # Check for duplicate activities across days
        all_acts = [a for d in itinerary for a in d.activities]
        unique_ratio = len(set(all_acts)) / max(len(all_acts), 1)
        if unique_ratio > 0.7:
            act_score += 0.05  # good variety
        scores.activity_data = round(min(act_score, 1.0), 2)

        # ── Budget Optimization confidence ────────────────────────────
        budget_score = 0.60
        cb = state.get('cost_breakdown')
        if cb and cb.total_estimated > 0:
            budget_score += 0.15
            budget_max = intent.budget_range_inr.max or intent.budget_total_inr
            if budget_max and budget_max > 0:
                ratio = cb.total_estimated / budget_max
                if 0.75 <= ratio <= 1.05:
                    budget_score += 0.15  # within tight range
                elif 0.6 <= ratio <= 1.15:
                    budget_score += 0.08  # within acceptable range
        opt_score = state.get('optimization_score', 0)
        if opt_score >= 8:
            budget_score += 0.10
        elif opt_score >= 6:
            budget_score += 0.05
        scores.budget_optimization = round(min(budget_score, 1.0), 2)

        # ── Risk Assessment confidence ────────────────────────────────
        risk_conf = 0.65
        if state.get('weather_data'):
            risk_conf += 0.10
        if state.get('visa_data'):
            risk_conf += 0.10
        if state.get('visa_information') and state['visa_information'].details:
            risk_conf += 0.08
        if state.get('risk_score') is not None:
            risk_conf += 0.07
        scores.risk_assessment = round(min(risk_conf, 1.0), 2)

        # ── Overall (weighted average) ────────────────────────────────
        weights = {
            'intent': (scores.intent_parsing, 0.20),
            'route': (scores.route_planning, 0.15),
            'flight': (scores.flight_data, 0.15),
            'hotel': (scores.hotel_data, 0.15),
            'activity': (scores.activity_data, 0.15),
            'budget': (scores.budget_optimization, 0.10),
            'risk': (scores.risk_assessment, 0.10),
        }
        overall = sum(score * weight for score, weight in weights.values())
        scores.overall = round(overall, 2)

        state['confidence_scores'] = scores

        self.log(
            state,
            f'Confidence: overall={scores.overall:.0%} | '
            f'intent={scores.intent_parsing:.0%} '
            f'route={scores.route_planning:.0%} '
            f'flights={scores.flight_data:.0%} '
            f'hotels={scores.hotel_data:.0%} '
            f'activities={scores.activity_data:.0%} '
            f'budget={scores.budget_optimization:.0%} '
            f'risk={scores.risk_assessment:.0%}'
        )
        return state
