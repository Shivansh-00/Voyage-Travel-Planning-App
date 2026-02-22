"""
Agent 1 — Intent Extractor

Parses unstructured natural-language trip descriptions into a structured
``UserIntent`` schema.  Uses rule-based NLP (regex + keyword matching) so the
pipeline works without any LLM API key.  Drop in a ``ChatOpenAI`` +
``PydanticOutputParser`` call for production-grade extraction.
"""

from __future__ import annotations

import re
from typing import List, Optional

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.schemas.travel import BudgetRange, UserIntent


# ───────────────────────── reference data ──────────────────────────────────

MAJOR_CITIES: set[str] = {
    # India
    'mumbai', 'delhi', 'new delhi', 'bangalore', 'bengaluru', 'hyderabad',
    'chennai', 'kolkata', 'pune', 'ahmedabad', 'jaipur', 'lucknow',
    'goa', 'kochi', 'thiruvananthapuram', 'varanasi', 'agra', 'udaipur',
    'jodhpur', 'shimla', 'manali', 'rishikesh', 'darjeeling', 'gangtok',
    'leh', 'ladakh', 'srinagar', 'amritsar', 'chandigarh', 'mysore',
    'mysuru', 'ooty', 'munnar', 'alleppey', 'hampi',
    # International
    'tokyo', 'paris', 'london', 'new york', 'nyc', 'dubai', 'singapore',
    'bangkok', 'bali', 'rome', 'barcelona', 'amsterdam', 'berlin',
    'prague', 'vienna', 'zurich', 'geneva', 'sydney', 'melbourne',
    'toronto', 'vancouver', 'san francisco', 'los angeles', 'las vegas',
    'miami', 'orlando', 'seoul', 'osaka', 'kyoto', 'hong kong',
    'shanghai', 'beijing', 'istanbul', 'cairo', 'marrakech', 'cape town',
    'nairobi', 'rio de janeiro', 'buenos aires', 'lima', 'bogota',
    'mexico city', 'kuala lumpur', 'hanoi', 'ho chi minh', 'phnom penh',
    'siem reap', 'kathmandu', 'colombo', 'dhaka', 'thimphu', 'lisbon',
    'madrid', 'athens', 'santorini', 'florence', 'venice', 'milan',
    'munich', 'stockholm', 'copenhagen', 'oslo', 'helsinki', 'reykjavik',
    'dublin', 'edinburgh', 'brussels', 'budapest', 'phuket',
    'chiang mai', 'maldives', 'mauritius', 'seychelles', 'zanzibar',
    'petra', 'abu dhabi', 'doha', 'muscat',
}

COUNTRIES: dict[str, str] = {
    'india': 'India', 'japan': 'Japan', 'france': 'France',
    'uk': 'UK', 'united kingdom': 'UK', 'england': 'UK',
    'usa': 'USA', 'united states': 'USA', 'america': 'USA',
    'uae': 'UAE', 'singapore': 'Singapore', 'thailand': 'Thailand',
    'indonesia': 'Indonesia', 'italy': 'Italy', 'spain': 'Spain',
    'germany': 'Germany', 'netherlands': 'Netherlands',
    'czech republic': 'Czech Republic', 'austria': 'Austria',
    'switzerland': 'Switzerland', 'australia': 'Australia',
    'canada': 'Canada', 'south korea': 'South Korea', 'china': 'China',
    'turkey': 'Turkey', 'egypt': 'Egypt', 'morocco': 'Morocco',
    'south africa': 'South Africa', 'kenya': 'Kenya', 'brazil': 'Brazil',
    'argentina': 'Argentina', 'peru': 'Peru', 'colombia': 'Colombia',
    'mexico': 'Mexico', 'malaysia': 'Malaysia', 'vietnam': 'Vietnam',
    'cambodia': 'Cambodia', 'nepal': 'Nepal', 'sri lanka': 'Sri Lanka',
    'portugal': 'Portugal', 'greece': 'Greece', 'sweden': 'Sweden',
    'denmark': 'Denmark', 'norway': 'Norway', 'finland': 'Finland',
    'iceland': 'Iceland', 'ireland': 'Ireland', 'scotland': 'Scotland',
    'belgium': 'Belgium', 'hungary': 'Hungary', 'maldives': 'Maldives',
    'mauritius': 'Mauritius', 'qatar': 'Qatar', 'oman': 'Oman',
}

MONTHS: dict[str, str] = {
    'january': 'January', 'jan': 'January', 'february': 'February',
    'feb': 'February', 'march': 'March', 'mar': 'March',
    'april': 'April', 'apr': 'April', 'may': 'May',
    'june': 'June', 'jun': 'June', 'july': 'July', 'jul': 'July',
    'august': 'August', 'aug': 'August', 'september': 'September',
    'sep': 'September', 'october': 'October', 'oct': 'October',
    'november': 'November', 'nov': 'November', 'december': 'December',
    'dec': 'December',
}

TRIP_TYPES: dict[str, str] = {
    'honeymoon': 'honeymoon', 'romantic': 'romantic',
    'adventure': 'adventure', 'backpacking': 'backpacking',
    'luxury': 'luxury', 'budget': 'budget trip', 'solo': 'solo',
    'family': 'family', 'business': 'business',
    'pilgrimage': 'pilgrimage', 'spiritual': 'spiritual',
    'cultural': 'cultural', 'beach': 'beach', 'mountain': 'mountain',
    'trekking': 'trekking', 'hiking': 'hiking',
    'road trip': 'road trip', 'workcation': 'workcation',
    'digital nomad': 'digital nomad', 'remote work': 'remote work',
    'foodie': 'food & culinary', 'culinary': 'food & culinary',
    'photography': 'photography', 'wildlife': 'wildlife',
    'safari': 'safari', 'cruise': 'cruise', 'wellness': 'wellness',
    'spa': 'wellness', 'party': 'nightlife & party',
    'nightlife': 'nightlife & party',
}

INTERESTS_KEYWORDS: dict[str, str] = {
    'food': 'food', 'cuisine': 'food', 'eat': 'food', 'restaurant': 'food',
    'culture': 'culture', 'museum': 'museums', 'art': 'art',
    'history': 'history', 'temple': 'temples', 'church': 'churches',
    'beach': 'beaches', 'mountain': 'mountains', 'nature': 'nature',
    'shopping': 'shopping', 'market': 'markets', 'nightlife': 'nightlife',
    'adventure': 'adventure sports', 'diving': 'scuba diving',
    'snorkeling': 'snorkeling', 'surfing': 'surfing',
    'trekking': 'trekking', 'wildlife': 'wildlife',
    'photography': 'photography', 'yoga': 'yoga',
    'meditation': 'meditation', 'wine': 'wine tasting',
}

ACCOMMODATION_KEYWORDS: dict[str, str] = {
    'luxury': 'luxury hotel', 'boutique': 'boutique hotel',
    '5 star': '5-star hotel', '5-star': '5-star hotel',
    '4 star': '4-star hotel', '4-star': '4-star hotel',
    'hostel': 'hostel', 'backpacker': 'hostel',
    'airbnb': 'Airbnb / rental', 'apartment': 'serviced apartment',
    'resort': 'resort', 'villa': 'private villa',
    'homestay': 'homestay', 'guest house': 'guest house',
    'budget': 'budget hotel', 'cheap': 'budget hotel',
    'camp': 'camping', 'tent': 'camping',
}

TRANSPORT_KEYWORDS: dict[str, str] = {
    'train': 'train', 'rail': 'train', 'bullet train': 'bullet train',
    'shinkansen': 'bullet train', 'bus': 'bus', 'cab': 'cab/taxi',
    'taxi': 'cab/taxi', 'uber': 'ride-hailing', 'ola': 'ride-hailing',
    'rental car': 'rental car', 'self drive': 'self-drive',
    'bike': 'bike rental', 'scooter': 'scooter rental',
    'metro': 'metro', 'flight': 'domestic flights',
    'ferry': 'ferry', 'cruise': 'cruise',
}

SPECIAL_KEYWORDS: list[tuple[str, str]] = [
    (r'vegetarian|vegan|veg food', 'vegetarian/vegan food'),
    (r'wheelchair|disabled|accessibility', 'wheelchair accessibility'),
    (r'kid|child|infant|baby|toddler', 'child-friendly'),
    (r'pet|dog|cat', 'pet-friendly'),
    (r'halal', 'halal food'),
    (r'gluten.?free', 'gluten-free food'),
    (r'senior|elderly|old age', 'senior-friendly'),
    (r'wifi|internet|remote work|work from', 'reliable WiFi / remote work'),
]


# ───────────────────────── extraction helpers ──────────────────────────────

def _extract_cities(text: str) -> list[str]:
    text_lower = text.lower()
    found: list[str] = []
    # sort by length descending so "new york" matches before "york"
    for city in sorted(MAJOR_CITIES, key=len, reverse=True):
        pattern = r'\b' + re.escape(city) + r'\b'
        if re.search(pattern, text_lower):
            found.append(city.title())
            text_lower = re.sub(pattern, '', text_lower)
    return found


def _extract_country(text: str) -> Optional[str]:
    text_lower = text.lower()
    for key, value in sorted(COUNTRIES.items(), key=lambda x: len(x[0]), reverse=True):
        if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
            return value
    return None


def _extract_duration(text: str) -> int:
    # "5 days", "10-day", "a week", "2 weeks"
    m = re.search(r'(\d+)\s*(?:days?|nights?)', text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r'(\d+)\s*weeks?', text, re.I)
    if m:
        return int(m.group(1)) * 7
    if re.search(r'\ba\s+week\b', text, re.I):
        return 7
    if re.search(r'\btwo\s+weeks?\b', text, re.I):
        return 14
    if re.search(r'\bthree\s+weeks?\b', text, re.I):
        return 21
    if re.search(r'\blong\s+weekend\b', text, re.I):
        return 4
    if re.search(r'\bweekend\b', text, re.I):
        return 3
    return 5  # default


def _extract_month(text: str) -> Optional[str]:
    text_lower = text.lower()
    for key, value in MONTHS.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
            return value
    return None


def _extract_year(text: str) -> Optional[int]:
    m = re.search(r'\b(202[4-9]|203\d)\b', text)
    return int(m.group(1)) if m else None


def _extract_budget(text: str) -> tuple[Optional[float], BudgetRange]:
    # "budget of 50000" / "₹50,000" / "50k" / "1 lakh"
    budget: Optional[float] = None
    brange = BudgetRange()

    def _safe_float(s: str) -> Optional[float]:
        cleaned = s.replace(',', '').strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    # INR patterns
    for m in re.finditer(r'(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lac|l)?', text, re.I):
        val = _safe_float(m.group(1))
        if val is None:
            continue
        if re.search(r'lakh|lac|l\b', m.group(0), re.I):
            val *= 100_000
        budget = val

    if budget is None:
        m = re.search(r'([\d,]+(?:\.\d+)?)\s*(?:k)\b', text, re.I)
        if m:
            val = _safe_float(m.group(1))
            if val is not None:
                budget = val * 1000

    if budget is None:
        m = re.search(r'([\d,]+)\s*(?:lakh|lac)', text, re.I)
        if m:
            val = _safe_float(m.group(1))
            if val is not None:
                budget = val * 100_000

    if budget is None:
        m = re.search(r'budget\s+(?:of\s+)?(?:around\s+)?(?:₹|rs\.?|inr)?\s*([\d,]+)', text, re.I)
        if m:
            val = _safe_float(m.group(1))
            if val is not None:
                if val < 500:
                    val *= 1000  # likely in thousands
                budget = val

    # range: "50k - 80k", "between 50000 and 80000"
    m = re.search(r'([\d,]+)\s*(?:k)?\s*(?:-|to|and)\s*([\d,]+)\s*(?:k)?', text, re.I)
    if m:
        lo = _safe_float(m.group(1))
        hi = _safe_float(m.group(2))
        if lo is not None and hi is not None:
            if lo < 500:
                lo *= 1000
            if hi < 500:
                hi *= 1000
            brange = BudgetRange(min=lo, max=hi)
            if budget is None:
                budget = hi

    return budget, brange


def _extract_travelers(text: str) -> int:
    m = re.search(r'(\d+)\s*(?:people|persons?|travelers?|travellers?|friends?|adults?|pax)', text, re.I)
    if m:
        return int(m.group(1))
    if re.search(r'\bcouple\b', text, re.I):
        return 2
    if re.search(r'\bsolo\b', text, re.I):
        return 1
    if re.search(r'\bfamily\b', text, re.I):
        return 4
    if re.search(r'\bgroup\b', text, re.I):
        return 6
    return 1


def _extract_origin(text: str, destinations: list[str]) -> Optional[str]:
    # Try several patterns for origin detection
    patterns = [
        r'(?:from|departing|leaving|starting)\s+(\w[\w\s]{2,20}?)(?:\s+to\b|\s*,|\s*\.|\s+in\b)',
        r'(?:from|departing|leaving|starting)\s+(\w[\w\s]{2,20}?)(?:\s+with\b|\s+for\b|\s+on\b|\s*$)',
        r'(?:from|departing|leaving|starting)\s+(\w[\w\s]{2,20}?)(?:\s+budget\b|\s+around\b)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            candidate = m.group(1).strip().title()
            # validate it's a known city
            if candidate.lower() in MAJOR_CITIES:
                return candidate
    return None


def _extract_set(text: str, mapping: dict[str, str]) -> list[str]:
    text_lower = text.lower()
    found: list[str] = []
    for key, value in mapping.items():
        # Skip "budget" keyword when it's part of "budget of" (budget amount context)
        if key == 'budget' and re.search(r'budget\s+(?:of|around|is|under|below|above)', text_lower):
            continue
        if re.search(r'\b' + re.escape(key) + r'\b', text_lower) and value not in found:
            found.append(value)
    return found


def _extract_special(text: str) -> list[str]:
    text_lower = text.lower()
    found: list[str] = []
    for pattern, label in SPECIAL_KEYWORDS:
        if re.search(pattern, text_lower) and label not in found:
            found.append(label)
    return found


# ───────────────────────── agent ───────────────────────────────────────────

class IntentExtractorAgent(BaseAgent):
    """Agent 1 — Intent Extractor.
    Parses the raw prompt into a ``UserIntent`` object."""

    name = 'IntentExtractorAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        prompt = state['raw_prompt']

        destinations = _extract_cities(prompt)
        country = _extract_country(prompt)
        origin = _extract_origin(prompt, destinations)
        duration = _extract_duration(prompt)
        month = _extract_month(prompt)
        year = _extract_year(prompt)
        budget, brange = _extract_budget(prompt)
        travelers = _extract_travelers(prompt)
        trip_types = _extract_set(prompt, TRIP_TYPES)
        interests = _extract_set(prompt, INTERESTS_KEYWORDS)
        accommodation = _extract_set(prompt, ACCOMMODATION_KEYWORDS)
        transport = _extract_set(prompt, TRANSPORT_KEYWORDS)
        special = _extract_special(prompt)

        # If no destinations found, treat whole trimmed prompt as one destination
        if not destinations:
            # take first "word(s)" that look like a place (fallback)
            cleaned = re.sub(r'[^\w\s]', '', prompt).strip()
            if cleaned:
                destinations = [cleaned.title()]

        # Remove origin from destinations if it got picked up
        if origin:
            destinations = [d for d in destinations if d.lower() != origin.lower()]

        intent = UserIntent(
            origin_city=origin,
            destinations=destinations,
            country=country,
            duration_days=duration,
            travel_month=month,
            travel_year=year,
            budget_total_inr=budget,
            budget_range_inr=brange,
            trip_type=trip_types,
            traveler_count=travelers,
            accommodation_preferences=accommodation,
            interests=interests,
            transport_preferences=transport,
            special_requirements=special,
        )

        state['intent'] = intent
        self.log(state, (
            f'Extracted intent — {len(destinations)} destination(s): '
            f'{", ".join(destinations)}, {duration} days, '
            f'budget ₹{budget or "unspecified"}, '
            f'{travelers} traveler(s).'
        ))
        return state
