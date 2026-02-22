"""
Comprehensive mock API layer.

Every function returns deterministic data so the multi-agent pipeline
works end-to-end without external API keys.  Replace individual
functions with real HTTP calls (Amadeus, Booking, Mapbox, …) when ready.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any


# ── helpers ────────────────────────────────────────────────────────────────

def _city_hash(city: str) -> int:
    """Stable numeric hash for a city name (used for deterministic variance)."""
    return int(hashlib.md5(city.lower().encode()).hexdigest()[:8], 16)


# ── flights ────────────────────────────────────────────────────────────────

_FLIGHT_BASES_INR: dict[str, float] = {
    'tokyo': 52000, 'paris': 48000, 'london': 45000, 'new york': 62000,
    'dubai': 22000, 'singapore': 28000, 'bangkok': 18000, 'bali': 30000,
    'rome': 46000, 'barcelona': 44000, 'amsterdam': 43000, 'berlin': 42000,
    'sydney': 58000, 'toronto': 60000, 'seoul': 38000, 'istanbul': 35000,
    'cairo': 32000, 'cape town': 55000, 'goa': 5500, 'jaipur': 4500,
    'mumbai': 4000, 'delhi': 3500, 'bangalore': 4200, 'chennai': 4800,
    'kolkata': 5200, 'hyderabad': 4600, 'kochi': 6000, 'varanasi': 4400,
    'udaipur': 5800, 'shimla': 5000, 'manali': 5200, 'leh': 8500,
    'srinagar': 7500, 'amritsar': 4300, 'rishikesh': 4800,
    'kuala lumpur': 24000, 'hanoi': 26000, 'maldives': 25000,
    'kathmandu': 15000, 'colombo': 14000, 'phuket': 20000,
    'prague': 41000, 'vienna': 43000, 'zurich': 55000,
    'lisbon': 47000, 'athens': 42000, 'santorini': 44000,
    'budapest': 40000, 'dublin': 46000,
}


async def search_flights(origin: str, destination: str) -> list[dict[str, Any]]:
    base = _FLIGHT_BASES_INR.get(destination.lower(), 35000)
    h = _city_hash(origin + destination)
    return [
        {
            'carrier': 'SkyFast',
            'price_inr': round(base * 0.92 + (h % 2000)),
            'duration_hours': round(5 + (h % 8), 1),
            'stops': 1,
        },
        {
            'carrier': 'AeroMax',
            'price_inr': round(base * 1.05 + (h % 1500)),
            'duration_hours': round(4 + (h % 6), 1),
            'stops': 0,
        },
        {
            'carrier': 'BudgetWings',
            'price_inr': round(base * 0.78 + (h % 1000)),
            'duration_hours': round(7 + (h % 10), 1),
            'stops': 2,
        },
    ]


# ── hotels ─────────────────────────────────────────────────────────────────

_HOTEL_BASES_INR: dict[str, float] = {
    'tokyo': 8500, 'paris': 9500, 'london': 10000, 'new york': 12000,
    'dubai': 7500, 'singapore': 7000, 'bangkok': 3500, 'bali': 4000,
    'rome': 7500, 'barcelona': 7000, 'goa': 3500, 'jaipur': 3000,
    'mumbai': 4500, 'delhi': 4000, 'bangalore': 3800, 'udaipur': 5000,
    'shimla': 3200, 'manali': 2800, 'varanasi': 2200, 'kochi': 3000,
    'rishikesh': 2500, 'leh': 3500, 'amritsar': 2500,
    'kuala lumpur': 4000, 'hanoi': 2500, 'phuket': 3800,
    'prague': 5500, 'budapest': 4500, 'lisbon': 6000,
    'athens': 5000, 'istanbul': 4000, 'maldives': 15000,
}


async def search_hotels(destination: str) -> list[dict[str, Any]]:
    base = _HOTEL_BASES_INR.get(destination.lower(), 4500)
    h = _city_hash(destination)
    return [
        {
            'name': f'{destination.title()} Grand Palace',
            'nightly_rate_inr': round(base * 1.8 + (h % 500)),
            'rating': 4.7,
            'type': 'luxury hotel',
        },
        {
            'name': f'{destination.title()} Central Suites',
            'nightly_rate_inr': round(base * 1.15 + (h % 300)),
            'rating': 4.4,
            'type': 'boutique hotel',
        },
        {
            'name': f'{destination.title()} Budget Inn',
            'nightly_rate_inr': round(base * 0.65 + (h % 200)),
            'rating': 4.0,
            'type': 'budget hotel',
        },
        {
            'name': f'{destination.title()} Backpacker Hostel',
            'nightly_rate_inr': round(base * 0.3 + (h % 150)),
            'rating': 3.8,
            'type': 'hostel',
        },
    ]


# ── activities / experiences ───────────────────────────────────────────────

_CITY_ACTIVITIES: dict[str, list[dict[str, Any]]] = {
    'tokyo': [
        {'name': 'Shibuya Crossing & Harajuku walk', 'cost_inr': 0, 'score': 9.3, 'type': 'free'},
        {'name': 'Tsukiji Outer Market food tour', 'cost_inr': 3500, 'score': 9.5, 'type': 'food'},
        {'name': 'TeamLab Borderless', 'cost_inr': 2800, 'score': 9.0, 'type': 'culture'},
        {'name': 'Meiji Shrine & Yoyogi Park', 'cost_inr': 0, 'score': 8.8, 'type': 'free'},
        {'name': 'Akihabara electronics district', 'cost_inr': 500, 'score': 8.2, 'type': 'shopping'},
        {'name': 'Senso-ji Temple, Asakusa', 'cost_inr': 0, 'score': 9.1, 'type': 'culture'},
        {'name': 'Robot Restaurant show', 'cost_inr': 6500, 'score': 8.5, 'type': 'entertainment'},
        {'name': 'Day trip to Mt. Fuji', 'cost_inr': 5000, 'score': 9.4, 'type': 'adventure'},
    ],
    'paris': [
        {'name': 'Eiffel Tower visit', 'cost_inr': 2200, 'score': 9.5, 'type': 'landmark'},
        {'name': 'Louvre Museum', 'cost_inr': 1500, 'score': 9.6, 'type': 'culture'},
        {'name': 'Montmartre walking tour', 'cost_inr': 0, 'score': 9.0, 'type': 'free'},
        {'name': 'Seine River cruise', 'cost_inr': 1800, 'score': 8.9, 'type': 'experience'},
        {'name': 'Croissant & café hopping', 'cost_inr': 800, 'score': 9.2, 'type': 'food'},
        {'name': 'Versailles Palace day trip', 'cost_inr': 3000, 'score': 9.3, 'type': 'culture'},
    ],
    'goa': [
        {'name': 'Baga Beach sunset', 'cost_inr': 0, 'score': 8.5, 'type': 'free'},
        {'name': 'Old Goa churches tour', 'cost_inr': 300, 'score': 8.8, 'type': 'culture'},
        {'name': 'Dudhsagar Falls trek', 'cost_inr': 2500, 'score': 9.2, 'type': 'adventure'},
        {'name': 'Spice plantation visit', 'cost_inr': 800, 'score': 8.3, 'type': 'experience'},
        {'name': 'Seafood beach shack dinner', 'cost_inr': 1200, 'score': 9.0, 'type': 'food'},
        {'name': 'Scuba diving at Grande Island', 'cost_inr': 4500, 'score': 9.1, 'type': 'adventure'},
    ],
    'jaipur': [
        {'name': 'Amber Fort tour', 'cost_inr': 500, 'score': 9.4, 'type': 'culture'},
        {'name': 'Hawa Mahal photography', 'cost_inr': 200, 'score': 9.0, 'type': 'free'},
        {'name': 'City Palace museum', 'cost_inr': 700, 'score': 8.8, 'type': 'culture'},
        {'name': 'Nahargarh Fort sunset', 'cost_inr': 300, 'score': 9.1, 'type': 'experience'},
        {'name': 'Chokhi Dhani cultural dinner', 'cost_inr': 1500, 'score': 8.9, 'type': 'food'},
        {'name': 'Johari Bazaar shopping', 'cost_inr': 0, 'score': 8.0, 'type': 'shopping'},
    ],
    'dubai': [
        {'name': 'Burj Khalifa observation deck', 'cost_inr': 3200, 'score': 9.3, 'type': 'landmark'},
        {'name': 'Desert safari with BBQ dinner', 'cost_inr': 4500, 'score': 9.5, 'type': 'adventure'},
        {'name': 'Dubai Mall & Aquarium', 'cost_inr': 1500, 'score': 8.8, 'type': 'shopping'},
        {'name': 'Dhow cruise dinner, Dubai Creek', 'cost_inr': 2800, 'score': 8.7, 'type': 'experience'},
        {'name': 'Old Dubai & Gold Souk walk', 'cost_inr': 0, 'score': 8.5, 'type': 'free'},
        {'name': 'Palm Jumeirah beach day', 'cost_inr': 0, 'score': 8.9, 'type': 'free'},
    ],
    'bali': [
        {'name': 'Ubud rice terrace walk', 'cost_inr': 0, 'score': 9.4, 'type': 'free'},
        {'name': 'Uluwatu Temple sunset & Kecak dance', 'cost_inr': 1500, 'score': 9.5, 'type': 'culture'},
        {'name': 'Snorkeling at Nusa Penida', 'cost_inr': 3500, 'score': 9.3, 'type': 'adventure'},
        {'name': 'Balinese cooking class', 'cost_inr': 2000, 'score': 8.8, 'type': 'food'},
        {'name': 'Mt. Batur sunrise trek', 'cost_inr': 3000, 'score': 9.6, 'type': 'adventure'},
        {'name': 'Seminyak beach clubs', 'cost_inr': 1800, 'score': 8.2, 'type': 'entertainment'},
    ],
    'london': [
        {'name': 'British Museum (free entry)', 'cost_inr': 0, 'score': 9.4, 'type': 'free'},
        {'name': 'Tower of London', 'cost_inr': 3000, 'score': 9.2, 'type': 'culture'},
        {'name': 'West End theatre show', 'cost_inr': 5500, 'score': 9.0, 'type': 'entertainment'},
        {'name': 'Borough Market food tour', 'cost_inr': 2000, 'score': 9.1, 'type': 'food'},
        {'name': 'Hyde Park & Kensington walk', 'cost_inr': 0, 'score': 8.5, 'type': 'free'},
        {'name': 'Camden Town markets', 'cost_inr': 500, 'score': 8.3, 'type': 'shopping'},
    ],
    'singapore': [
        {'name': 'Gardens by the Bay', 'cost_inr': 1500, 'score': 9.3, 'type': 'landmark'},
        {'name': 'Hawker centre food crawl', 'cost_inr': 800, 'score': 9.5, 'type': 'food'},
        {'name': 'Sentosa Island day', 'cost_inr': 3000, 'score': 8.7, 'type': 'entertainment'},
        {'name': 'Marina Bay Sands skypark', 'cost_inr': 2000, 'score': 9.0, 'type': 'landmark'},
        {'name': 'Little India & Chinatown walk', 'cost_inr': 0, 'score': 8.6, 'type': 'free'},
        {'name': 'Night Safari', 'cost_inr': 3500, 'score': 8.9, 'type': 'adventure'},
    ],
    'bangkok': [
        {'name': 'Grand Palace & Wat Phra Kaew', 'cost_inr': 500, 'score': 9.5, 'type': 'culture'},
        {'name': 'Chatuchak Weekend Market', 'cost_inr': 0, 'score': 9.0, 'type': 'shopping'},
        {'name': 'Street food tour (Yaowarat)', 'cost_inr': 600, 'score': 9.4, 'type': 'food'},
        {'name': 'Wat Arun at sunset', 'cost_inr': 200, 'score': 9.2, 'type': 'culture'},
        {'name': 'Floating market day trip', 'cost_inr': 1500, 'score': 8.8, 'type': 'experience'},
        {'name': 'Thai massage experience', 'cost_inr': 400, 'score': 8.7, 'type': 'wellness'},
    ],
    'kyoto': [
        {'name': 'Fushimi Inari Shrine (1000 torii gates)', 'cost_inr': 0, 'score': 9.7, 'type': 'free'},
        {'name': 'Arashiyama Bamboo Grove walk', 'cost_inr': 0, 'score': 9.5, 'type': 'free'},
        {'name': 'Kinkaku-ji (Golden Pavilion)', 'cost_inr': 350, 'score': 9.4, 'type': 'culture'},
        {'name': 'Nishiki Market food tour', 'cost_inr': 2500, 'score': 9.3, 'type': 'food'},
        {'name': 'Geisha district (Gion) evening walk', 'cost_inr': 0, 'score': 9.2, 'type': 'free'},
        {'name': 'Traditional tea ceremony', 'cost_inr': 2000, 'score': 9.0, 'type': 'culture'},
        {'name': 'Philosopher\'s Path & Nanzen-ji', 'cost_inr': 300, 'score': 8.8, 'type': 'free'},
        {'name': 'Nijo Castle tour', 'cost_inr': 500, 'score': 8.6, 'type': 'culture'},
    ],
    'osaka': [
        {'name': 'Dotonbori food crawl', 'cost_inr': 2000, 'score': 9.6, 'type': 'food'},
        {'name': 'Osaka Castle visit', 'cost_inr': 500, 'score': 9.2, 'type': 'culture'},
        {'name': 'Kuromon Market breakfast', 'cost_inr': 1500, 'score': 9.1, 'type': 'food'},
        {'name': 'Shinsekai & Tsutenkaku Tower', 'cost_inr': 600, 'score': 8.7, 'type': 'culture'},
        {'name': 'Universal Studios Japan', 'cost_inr': 7000, 'score': 9.0, 'type': 'entertainment'},
        {'name': 'Namba & Shinsaibashi shopping', 'cost_inr': 0, 'score': 8.5, 'type': 'shopping'},
    ],
    'mumbai': [
        {'name': 'Gateway of India & Colaba walk', 'cost_inr': 0, 'score': 9.0, 'type': 'free'},
        {'name': 'Dhobi Ghat & Dharavi tour', 'cost_inr': 800, 'score': 8.8, 'type': 'culture'},
        {'name': 'Marine Drive sunset stroll', 'cost_inr': 0, 'score': 9.2, 'type': 'free'},
        {'name': 'Street food trail (Vada Pav, Pav Bhaji)', 'cost_inr': 500, 'score': 9.5, 'type': 'food'},
        {'name': 'Elephanta Caves ferry trip', 'cost_inr': 1500, 'score': 8.7, 'type': 'culture'},
        {'name': 'Bollywood studio tour', 'cost_inr': 2500, 'score': 8.4, 'type': 'entertainment'},
    ],
    'delhi': [
        {'name': 'Red Fort & Chandni Chowk walk', 'cost_inr': 500, 'score': 9.3, 'type': 'culture'},
        {'name': 'Qutub Minar visit', 'cost_inr': 200, 'score': 9.0, 'type': 'culture'},
        {'name': 'Old Delhi street food tour', 'cost_inr': 600, 'score': 9.5, 'type': 'food'},
        {'name': 'Humayun\'s Tomb', 'cost_inr': 300, 'score': 9.1, 'type': 'culture'},
        {'name': 'India Gate & Connaught Place', 'cost_inr': 0, 'score': 8.7, 'type': 'free'},
        {'name': 'Lotus Temple & Akshardham', 'cost_inr': 0, 'score': 8.9, 'type': 'free'},
    ],
}

_DEFAULT_ACTIVITIES: list[dict[str, Any]] = [
    {'name': 'City walking tour', 'cost_inr': 0, 'score': 8.5, 'type': 'free'},
    {'name': 'Cultural heritage museum', 'cost_inr': 800, 'score': 8.2, 'type': 'culture'},
    {'name': 'Local food market exploration', 'cost_inr': 1200, 'score': 9.0, 'type': 'food'},
    {'name': 'Historical landmark visit', 'cost_inr': 600, 'score': 8.6, 'type': 'culture'},
    {'name': 'Sunset viewpoint', 'cost_inr': 0, 'score': 8.8, 'type': 'free'},
    {'name': 'Local cooking class', 'cost_inr': 2000, 'score': 8.4, 'type': 'experience'},
    {'name': 'Day trip to nearby attraction', 'cost_inr': 3000, 'score': 8.7, 'type': 'adventure'},
    {'name': 'Street art & café hopping', 'cost_inr': 500, 'score': 8.1, 'type': 'free'},
]


async def search_activities(destination: str) -> list[dict[str, Any]]:
    key = destination.lower().strip()
    return list(_CITY_ACTIVITIES.get(key, _DEFAULT_ACTIVITIES))


# ── weather & risk ─────────────────────────────────────────────────────────

_WEATHER_PROFILES: dict[str, dict[str, Any]] = {
    'tokyo': {'avg_temp_c': 22, 'rain_chance': 0.3, 'storm_probability': 0.08, 'advisory_level': 'low', 'best_months': ['March', 'April', 'October', 'November']},
    'kyoto': {'avg_temp_c': 23, 'rain_chance': 0.28, 'storm_probability': 0.06, 'advisory_level': 'low', 'best_months': ['March', 'April', 'October', 'November']},
    'osaka': {'avg_temp_c': 24, 'rain_chance': 0.30, 'storm_probability': 0.07, 'advisory_level': 'low', 'best_months': ['March', 'April', 'October', 'November']},
    'mumbai': {'avg_temp_c': 30, 'rain_chance': 0.45, 'storm_probability': 0.12, 'advisory_level': 'moderate', 'best_months': ['November', 'December', 'January', 'February']},
    'delhi': {'avg_temp_c': 28, 'rain_chance': 0.20, 'storm_probability': 0.05, 'advisory_level': 'low', 'best_months': ['October', 'November', 'February', 'March']},
    'paris': {'avg_temp_c': 18, 'rain_chance': 0.25, 'storm_probability': 0.05, 'advisory_level': 'low', 'best_months': ['April', 'May', 'June', 'September']},
    'london': {'avg_temp_c': 15, 'rain_chance': 0.45, 'storm_probability': 0.04, 'advisory_level': 'low', 'best_months': ['June', 'July', 'August', 'September']},
    'dubai': {'avg_temp_c': 35, 'rain_chance': 0.02, 'storm_probability': 0.01, 'advisory_level': 'low', 'best_months': ['November', 'December', 'January', 'February', 'March']},
    'bali': {'avg_temp_c': 28, 'rain_chance': 0.35, 'storm_probability': 0.12, 'advisory_level': 'moderate', 'best_months': ['April', 'May', 'June', 'July', 'August', 'September']},
    'goa': {'avg_temp_c': 30, 'rain_chance': 0.40, 'storm_probability': 0.10, 'advisory_level': 'low', 'best_months': ['November', 'December', 'January', 'February', 'March']},
    'bangkok': {'avg_temp_c': 32, 'rain_chance': 0.35, 'storm_probability': 0.08, 'advisory_level': 'low', 'best_months': ['November', 'December', 'January', 'February']},
    'singapore': {'avg_temp_c': 30, 'rain_chance': 0.40, 'storm_probability': 0.06, 'advisory_level': 'low', 'best_months': ['February', 'March', 'April', 'July', 'August']},
    'jaipur': {'avg_temp_c': 28, 'rain_chance': 0.15, 'storm_probability': 0.03, 'advisory_level': 'low', 'best_months': ['October', 'November', 'December', 'January', 'February']},
    'maldives': {'avg_temp_c': 29, 'rain_chance': 0.30, 'storm_probability': 0.10, 'advisory_level': 'moderate', 'best_months': ['January', 'February', 'March', 'April']},
}


async def get_weather_risk(destination: str) -> dict[str, Any]:
    key = destination.lower().strip()
    if key in _WEATHER_PROFILES:
        return {'destination': destination, **_WEATHER_PROFILES[key]}
    h = _city_hash(destination)
    return {
        'destination': destination,
        'avg_temp_c': 22 + (h % 12),
        'rain_chance': round(0.1 + (h % 40) / 100, 2),
        'storm_probability': round(0.02 + (h % 15) / 100, 2),
        'advisory_level': 'low',
        'best_months': ['March', 'April', 'October', 'November'],
    }


# ── visa ───────────────────────────────────────────────────────────────────

_VISA_DATA: dict[str, dict[str, Any]] = {
    'japan': {'required': True, 'details': 'Indian citizens need a tourist visa. Apply at VFS Global. Processing takes 5-7 business days. Visa fee ~₹700.'},
    'france': {'required': True, 'details': 'Schengen visa required. Apply via VFS Global France. Processing 15 calendar days. Visa fee ~₹6,800.'},
    'uk': {'required': True, 'details': 'UK Standard Visitor visa required. Apply online and attend biometrics appointment. Fee ~₹9,800.'},
    'usa': {'required': True, 'details': 'US B1/B2 tourist visa required. Attend interview at US Embassy. Fee ~₹13,500.'},
    'uae': {'required': False, 'details': 'Indian passport holders can get visa on arrival for 14 days or apply for 30-day e-visa (~₹6,000).'},
    'singapore': {'required': True, 'details': 'Indian citizens need a Singapore tourist visa. Apply via authorized agents. Fee ~₹2,500.'},
    'thailand': {'required': False, 'details': 'Indian citizens get visa on arrival for 15 days at Suvarnabhumi and Don Mueang airports. Fee ~₹1,700.'},
    'indonesia': {'required': False, 'details': 'Visa on arrival for 30 days available at major airports. Fee ~₹2,800.'},
    'sri lanka': {'required': True, 'details': 'ETA (Electronic Travel Authorization) required. Apply online. Fee ~₹1,500.'},
    'nepal': {'required': False, 'details': 'No visa required for Indian citizens. Just carry valid passport or Voter ID.'},
    'maldives': {'required': False, 'details': 'Free visa on arrival for 30 days for all nationalities.'},
    'italy': {'required': True, 'details': 'Schengen visa required. Apply via VFS Global Italy. Processing 15 calendar days. Fee ~₹6,800.'},
    'spain': {'required': True, 'details': 'Schengen visa required. Apply via BLS Spain. Processing 15 calendar days. Fee ~₹6,800.'},
    'germany': {'required': True, 'details': 'Schengen visa required. Apply via VFS Global Germany. Fee ~₹6,800.'},
    'australia': {'required': True, 'details': 'Visitor visa (subclass 600) required. Apply online. Fee ~₹10,500. Processing 20-30 days.'},
    'turkey': {'required': True, 'details': 'e-Visa available online. Processing is instant. Fee ~₹4,200.'},
    'egypt': {'required': True, 'details': 'Visa on arrival available at Cairo airport. Fee ~₹2,100.'},
    'malaysia': {'required': False, 'details': 'eNTRI (free) or e-Visa available. Indian citizens can get 30-day eNTRI.'},
    'vietnam': {'required': True, 'details': 'e-Visa available online. Fee ~₹2,100. Processing 3 business days.'},
    'south korea': {'required': True, 'details': 'Tourist visa required. Apply at Korean Embassy. Fee ~₹3,200.'},
    'india': {'required': False, 'details': 'No visa required for Indian citizens for domestic travel.'},
}

# map cities to countries for visa lookup
_CITY_TO_COUNTRY: dict[str, str] = {
    'tokyo': 'japan', 'osaka': 'japan', 'kyoto': 'japan',
    'paris': 'france', 'london': 'uk', 'edinburgh': 'uk',
    'new york': 'usa', 'san francisco': 'usa', 'los angeles': 'usa', 'las vegas': 'usa', 'miami': 'usa',
    'dubai': 'uae', 'abu dhabi': 'uae',
    'singapore': 'singapore',
    'bangkok': 'thailand', 'phuket': 'thailand', 'chiang mai': 'thailand',
    'bali': 'indonesia',
    'rome': 'italy', 'florence': 'italy', 'venice': 'italy', 'milan': 'italy',
    'barcelona': 'spain', 'madrid': 'spain',
    'berlin': 'germany', 'munich': 'germany',
    'amsterdam': 'netherlands',
    'sydney': 'australia', 'melbourne': 'australia',
    'istanbul': 'turkey',
    'cairo': 'egypt',
    'kuala lumpur': 'malaysia',
    'hanoi': 'vietnam', 'ho chi minh': 'vietnam',
    'seoul': 'south korea',
    'colombo': 'sri lanka',
    'kathmandu': 'nepal',
    'maldives': 'maldives',
    'goa': 'india', 'jaipur': 'india', 'mumbai': 'india', 'delhi': 'india',
    'bangalore': 'india', 'chennai': 'india', 'kolkata': 'india',
    'hyderabad': 'india', 'varanasi': 'india', 'udaipur': 'india',
    'shimla': 'india', 'manali': 'india', 'rishikesh': 'india',
    'leh': 'india', 'srinagar': 'india', 'amritsar': 'india', 'kochi': 'india',
    'prague': 'czech republic', 'vienna': 'austria', 'zurich': 'switzerland',
    'lisbon': 'portugal', 'athens': 'greece', 'santorini': 'greece',
    'budapest': 'hungary', 'dublin': 'ireland', 'cape town': 'south africa',
}


async def get_visa_info(destination: str, country: str | None = None) -> dict[str, Any]:
    key = destination.lower().strip()
    cntry = (country or _CITY_TO_COUNTRY.get(key, '')).lower().strip()
    if cntry in _VISA_DATA:
        return _VISA_DATA[cntry]
    return {'required': True, 'details': f'Visa requirements for {destination} — please check with the nearest embassy.'}


def get_country_for_city(city: str) -> str | None:
    return _CITY_TO_COUNTRY.get(city.lower().strip())


# ── currency conversion ───────────────────────────────────────────────────

_USD_TO_INR = 83.5

_RATES_TO_INR: dict[str, float] = {
    'usd': 83.5, 'eur': 91.0, 'gbp': 106.0, 'jpy': 0.56,
    'thb': 2.4, 'sgd': 62.0, 'aed': 22.7, 'aud': 54.0,
    'cad': 61.0, 'myr': 18.5, 'idr': 0.0054, 'krw': 0.063,
    'lkr': 0.26, 'npr': 0.52, 'inr': 1.0,
}


async def convert_currency(amount: float, from_currency: str, to_currency: str = 'INR') -> float:
    from_rate = _RATES_TO_INR.get(from_currency.lower(), 83.5)
    to_rate = _RATES_TO_INR.get(to_currency.lower(), 1.0)
    return round(amount * from_rate / to_rate, 2)


# ── remote-work spots ─────────────────────────────────────────────────────

_REMOTE_WORK: dict[str, list[str]] = {
    'tokyo': ['Starbucks Reserve Roastery Nakameguro', 'FabCafe Shibuya', 'WeWork Roppongi'],
    'kyoto': ['Len Kyoto Kawaramachi', 'Café Bibliotic Hello!', 'Impact Hub Kyoto'],
    'osaka': ['The Deck Coffee & Pie', 'WeWork Namba Skyo', 'Osaka Innovation Hub'],
    'paris': ['Le Peloton Café', 'Anticafé Beaubourg', 'WeWork La Fayette'],
    'bali': ['Dojo Bali (Canggu)', 'Outpost Coworking Ubud', 'Tropical Nomad Canggu'],
    'london': ['Second Home Spitalfields', 'The Hoxton Holborn Lobby', 'WeWork Moorgate'],
    'bangkok': ['Hubba-to Ekkamai', 'The Hive Thonglor', 'True Digital Park'],
    'goa': ['Clay Coworking Assagao', 'Workbay Panjim', 'Café Artjuna Anjuna'],
    'dubai': ['Nook Coworking JLT', 'WeWork One JLT', 'Letswork Dubai Marina'],
    'singapore': ['WeWork Beach Centre', 'The Hive Lavender', 'JustCo Raffles Place'],
    'mumbai': ['WeWork BKC', '91springboard Lower Parel', 'Ministry of New Mumbai'],
    'delhi': ['91springboard Okhla', 'Innov8 Connaught Place', 'WeWork Gurugram'],
}


async def get_remote_work_spots(destination: str) -> list[str]:
    return _REMOTE_WORK.get(destination.lower().strip(), [f'Coworking space in {destination.title()}', f'{destination.title()} public library WiFi zone'])


# ── local transport cost estimate ──────────────────────────────────────────

_DAILY_TRANSPORT_INR: dict[str, float] = {
    'tokyo': 800, 'kyoto': 600, 'osaka': 700, 'paris': 700, 'london': 900, 'new york': 850,
    'dubai': 500, 'singapore': 600, 'bangkok': 250, 'bali': 400,
    'goa': 350, 'jaipur': 300, 'mumbai': 200, 'delhi': 200,
    'istanbul': 350, 'prague': 400, 'budapest': 350,
}


async def get_daily_transport_cost(destination: str) -> float:
    return _DAILY_TRANSPORT_INR.get(destination.lower().strip(), 400)
