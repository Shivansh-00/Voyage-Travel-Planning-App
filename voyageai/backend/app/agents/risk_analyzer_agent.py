"""
Agent 5 — Risk Analyzer + Visa Intelligence + Weather Insights

Computes a multi-dimensional composite risk score and produces
weather insights with per-city recommendations.

Risk factors (each normalised to 0-10, then weighted):
  • Weather / storm risk    — 30 %
  • Budget exposure         — 25 %
  • Visa complexity         — 20 %
  • Rain disruption risk    — 15 %
  • Temperature extremes    — 10 %
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.schemas.travel import VisaInformation, WeatherInsight
from app.tools.mock_apis import get_weather_risk, get_visa_info, get_country_for_city


class RiskAnalyzerAgent(BaseAgent):
    name = 'RiskAnalyzerAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        intent = state['intent']
        destinations = intent.destinations or ['Unknown']

        # ── weather risk + insights ────────────────────────────────────
        max_storm = 0.0
        max_rain = 0.0
        max_temp_extreme = 0.0
        weather_data: dict = {}
        weather_insights: list[WeatherInsight] = []

        for dest in destinations:
            w = await get_weather_risk(dest)
            weather_data[dest] = w
            storm_prob = w.get('storm_probability', 0)
            rain_chance = w.get('rain_chance', 0.2)
            avg_temp = w.get('avg_temp_c', 22)

            max_storm = max(max_storm, storm_prob)
            max_rain = max(max_rain, rain_chance)
            # Temperature extremity: how far from comfort zone (18-28°C)
            if avg_temp > 28:
                max_temp_extreme = max(max_temp_extreme, (avg_temp - 28) / 20)
            elif avg_temp < 18:
                max_temp_extreme = max(max_temp_extreme, (18 - avg_temp) / 20)

            # Build weather insight
            best = w.get('best_months', [])
            travel_month = intent.travel_month
            if travel_month and best:
                if travel_month in best:
                    rec = f"Great choice! {travel_month} is one of the best months to visit {dest}."
                else:
                    alt = ' or '.join(best[:2])
                    rec = f"Consider visiting in {alt} for better weather. {travel_month} may have {'heavy rain' if rain_chance > 0.35 else 'less ideal conditions'}."
            elif best:
                rec = f"Best months to visit: {', '.join(best[:3])}."
            else:
                rec = "Weather data limited — check local forecasts closer to travel."

            weather_insights.append(WeatherInsight(
                city=dest,
                avg_temp_c=w.get('avg_temp_c', 22),
                rain_chance=rain_chance,
                advisory=w.get('advisory_level', 'low'),
                best_months=best,
                recommendation=rec,
            ))

        state['weather_data'] = weather_data
        state['weather_insights'] = weather_insights

        # Add weather notes to itinerary days
        dest_weather = {wi.city.lower(): wi for wi in weather_insights}
        for day_item in state.get('day_by_day_itinerary', []):
            wi = dest_weather.get(day_item.city.lower())
            if wi:
                if wi.rain_chance > 0.5:
                    day_item.weather_note = f"🌧️ Very likely rain ({wi.rain_chance:.0%}) — plan indoor activities"
                elif wi.rain_chance > 0.35:
                    day_item.weather_note = f"🌦️ Possible rain ({wi.rain_chance:.0%}) — carry umbrella"
                elif wi.avg_temp_c > 38:
                    day_item.weather_note = f"🔥 Extreme heat ({wi.avg_temp_c}°C) — stay hydrated, avoid midday sun"
                elif wi.avg_temp_c > 33:
                    day_item.weather_note = f"🌡️ Hot ({wi.avg_temp_c}°C) — plan indoor activities midday"
                elif wi.avg_temp_c < 5:
                    day_item.weather_note = f"❄️ Very cold ({wi.avg_temp_c}°C) — pack heavy layers"
                elif wi.avg_temp_c < 15:
                    day_item.weather_note = f"🧥 Cool ({wi.avg_temp_c}°C) — bring a jacket"
                else:
                    day_item.weather_note = f"☀️ Pleasant ({wi.avg_temp_c}°C) — ideal for outdoor activities"

        # ── visa intelligence ──────────────────────────────────────────
        visa_required = False
        visa_count = 0
        visa_details: list[str] = []
        seen_countries: set[str] = set()

        for dest in destinations:
            country = intent.country or get_country_for_city(dest)
            if country and country.lower() not in seen_countries:
                seen_countries.add(country.lower())
                info = await get_visa_info(dest, country)
                if info.get('required'):
                    visa_required = True
                    visa_count += 1
                visa_details.append(f"{country}: {info.get('details', 'N/A')}")

        state['visa_information'] = VisaInformation(
            required=visa_required,
            details=' | '.join(visa_details) if visa_details else 'No visa information available.',
        )
        state['visa_data'] = {'required': visa_required, 'details': visa_details}

        # ── composite risk score (0-10) ────────────────────────────────
        # Weather / storm risk (0-10): scale storm probability to useful range
        weather_risk = min(max_storm * 50, 10.0)  # 0.20 storm → 10.0

        # Budget exposure (0-10)
        budget_max = intent.budget_range_inr.max or intent.budget_total_inr or 0
        if budget_max > 0:
            ratio = state['total_cost'] / budget_max
            if ratio <= 0.8:
                budget_risk = 1.0
            elif ratio <= 1.0:
                budget_risk = 1.0 + (ratio - 0.8) * 20   # 0.8→1, 1.0→5
            elif ratio <= 1.3:
                budget_risk = 5.0 + (ratio - 1.0) * 16.7  # 1.0→5, 1.3→10
            else:
                budget_risk = 10.0
        else:
            budget_risk = 3.0  # unknown budget

        # Visa complexity (0-10)
        visa_risk = min(visa_count * 3.3, 10.0)

        # Rain disruption (0-10)
        rain_risk = min(max_rain * 15, 10.0)  # 0.5 rain → 7.5

        # Temperature extremes (0-10)
        temp_risk = min(max_temp_extreme * 10, 10.0)

        # Weighted composite
        composite = (
            weather_risk * 0.30
            + budget_risk * 0.25
            + visa_risk * 0.20
            + rain_risk * 0.15
            + temp_risk * 0.10
        )
        state['risk_score'] = round(min(composite, 10.0), 1)

        self.log(
            state,
            f"Risk score: {state['risk_score']}/10 "
            f"(weather={weather_risk:.1f}, budget={budget_risk:.1f}, "
            f"visa={visa_risk:.1f}, rain={rain_risk:.1f}, temp={temp_risk:.1f}). "
            f"Visa required: {visa_required}. "
            f"{len(weather_insights)} weather insight(s)."
        )
        return state
