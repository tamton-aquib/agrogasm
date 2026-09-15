"""Kerala agricultural calendar, spraying, irrigation advice.

Pure functions - no network calls. Kerala south-west monsoon is Jun-Sep,
north-east monsoon Oct-Dec. Kuttanad (Alappuzha) / central Kerala assumed.
"""

from datetime import date, datetime


# Crop calendar: month -> list of {crop, action}
CROP_CALENDAR = {
    1: [
        {"crop": "Rice (paddy)", "action": "Transplant rabi seedlings"},
        {"crop": "Vegetables", "action": "Okra, chilli, brinjal grow well"},
        {"crop": "Coconut", "action": "Apply potash - 1st round"},
    ],
    2: [
        {"crop": "Vegetables", "action": "Harvest okra, tomato, cucumber"},
        {"crop": "Spices", "action": "Turmeric harvest window"},
        {"crop": "Coconut", "action": "Apply potash - 2nd round"},
    ],
    3: [
        {"crop": "Water", "action": "Irrigation demand rises - plan drips"},
        {"crop": "Fruit", "action": "Mango flowering - watch for powdery mildew"},
        {"crop": "Rice", "action": "Summer fallow - plan water saving"},
    ],
    4: [
        {"crop": "Vegetables", "action": "Heat tolerant okra, cowpea"},
        {"crop": "Fruit", "action": "Mango, jackfruit - shade young trees"},
        {"crop": "Rice", "action": "Direct seed if water available"},
    ],
    5: [
        {"crop": "Water", "action": "Peak summer irrigation"},
        {"crop": "Rice", "action": "Vayal seed bed prep"},
        {"crop": "Vegetables", "action": "Shade net for nurseries"},
    ],
    6: [
        {"crop": "Rice", "action": "Transplant paddy - aaduthippu"},
        {"crop": "Vegetables", "action": "Okra, cowpea, ridge gourd"},
        {"crop": "Spices", "action": "Pepper, cardamom - mulch heavily"},
        {"crop": "Coconut", "action": "Apply potash before monsoon"},
    ],
    7: [
        {"crop": "Rice", "action": "Transplant continues, weed control"},
        {"crop": "Vegetables", "action": "Cole crops - watch diamondback moth"},
        {"crop": "Coconut", "action": "Disease watch - bud rot after rain"},
    ],
    8: [
        {"crop": "Rice", "action": "Leaf spot watch - spray only if needed"},
        {"crop": "Vegetables", "action": "Stake plants, improve drainage"},
        {"crop": "Coconut", "action": "Harvest tender nuts"},
    ],
    9: [
        {"crop": "Rice", "action": "Blast watch - avoid excess nitrogen"},
        {"crop": "Vegetables", "action": "Harvest monsoon vegetables"},
        {"crop": "Spices", "action": "Pepper - harvest spikes"},
    ],
    10: [
        {"crop": "Rice", "action": "Harvest rabi paddy"},
        {"crop": "Vegetables", "action": "Post-monsoon planting begins"},
        {"crop": "Fruit", "action": "Prune mango, jackfruit"},
    ],
    11: [
        {"crop": "Vegetables", "action": "Spinach, amaranth, okra, cowpea"},
        {"crop": "Rice", "action": "Summer paddy seed prep"},
        {"crop": "Spices", "action": "Turmeric planting"},
    ],
    12: [
        {"crop": "Vegetables", "action": "Winter crops - onion, cabbage, carrot"},
        {"crop": "Fruit", "action": "Banana - deleafing, desuckering"},
        {"crop": "Coconut", "action": "Apply potash - 1st winter round"},
    ],
}

# Pest watch: month -> list of {crop, pest, action}
PEST_WATCH = {
    1: [
        {"crop": "Rice", "pest": "Gall midge", "action": "Remove stubble, flood field"},
        {"crop": "Vegetables", "pest": "Aphids", "action": "Neem oil spray"},
    ],
    2: [
        {"crop": "Vegetables", "pest": "Fruit borer", "action": "Pheromone traps"},
        {"crop": "Spices", "pest": "Tubers moth", "action": "Ecart set < 1.5 mm"},
    ],
    3: [
        {"crop": "Fruit", "pest": "Mango hopper", "action": "Dimethoate 2 ml/l"},
        {"crop": "Coconut", "pest": "Red palm weevil", "action": "Trunk injection, cut infected"},
    ],
    4: [
        {"crop": "Fruit", "pest": "Fruit fly", "action": "Methyl eugenol traps"},
        {"crop": "Vegetables", "pest": "Whitefly", "action": "Yellow sticky traps"},
    ],
    5: [
        {"crop": "Vegetables", "pest": "Thrips", "action": "Spinosad spray, water stress"},
    ],
    6: [
        {"crop": "Rice", "pest": "Stem borer", "action": "Traps, remove hoppers"},
        {"crop": "Vegetables", "pest": "Diamondback moth", "action": "Bacillus thuringiensis"},
    ],
    7: [
        {"crop": "Rice", "pest": "Leaf blast", "action": "Tricyclazole 1 ml/l"},
        {"crop": "Coconut", "pest": "Bud rot", "action": "Remove crown, apply Bordeaux"},
    ],
    8: [
        {"crop": "Rice", "pest": "Brown plant hopper", "action": "Imidacloprid 5 ml/10l"},
        {"crop": "Vegetables", "pest": "Red spider mite", "action": "Abaamectin 1 ml/l"},
    ],
    9: [
        {"crop": "Rice", "pest": "False smut", "action": "Remove infected grains"},
        {"crop": "Coconut", "pest": "Rhinoceros beetle", "action": "Pheromone traps"},
    ],
    10: [
        {"crop": "Vegetables", "pest": "Caterpillars", "action": "Hand pick, neem oil"},
        {"crop": "Spices", "pest": "Scale insects", "action": "Fenitrothion 10 ml/l"},
    ],
    11: [
        {"crop": "Vegetables", "pest": "Leaf miners", "action": "Neem oil, remove damaged"},
        {"crop": "Rice", "pest": "Gall midge", "action": "Water management"},
    ],
    12: [
        {"crop": "Vegetables", "pest": "Aphids", "action": "Neem oil, soap solution"},
        {"crop": "Fruit", "pest": "Banana corm weevil", "action": "Destroy infected corms"},
    ],
}

# Insecticide / pesticide recommendations (safe lists, rotate)
PESTICIDES = {
    "neem_oil": {
        "name": "Neem oil",
        "dose_ml_per_l": 5,
        "target": "aphids, whitefly, leaf miners, caterpillars",
        "preharvest_days": 7,
    },
    "spinosad": {
        "name": "Spinosad",
        "dose_ml_per_l": 2,
        "target": "thrips, fruit borer, caterpillars",
        "preharvest_days": 7,
    },
    "bt": {
        "name": "Bacillus thuringiensis",
        "dose_g_per_l": 1.0,
        "target": "diamondback moth, caterpillars",
        "preharvest_days": 1,
    },
    "imidacloprid": {
        "name": "Imidacloprid",
        "dose_ml_per_10l": 5,
        "target": "brown plant hopper, aphids",
        "preharvest_days": 21,
        "restriction": "Not during bloom - pollinator risk",
    },
    "mancozeb": {
        "name": "Mancozeb",
        "dose_g_per_l": 2.5,
        "target": "leaf spot, downy mildew, blast",
        "preharvest_days": 20,
    },
    "tricyclazole": {
        "name": "Tricyclazole",
        "dose_ml_per_l": 1,
        "target": "rice blast",
        "preharvest_days": 50,
    },
}


def get_crop_calendar(d: date | None = None) -> list:
    d = d or date.today()
    return CROP_CALENDAR.get(d.month, [])


def get_pest_watch(d: date | None = None) -> list:
    d = d or date.today()
    return PEST_WATCH.get(d.month, [])


def is_pest_season(d: date | None = None) -> bool:
    """Monsoon months and peak winter veg season have more pest pressure."""
    d = d or date.today()
    return d.month in (6, 7, 8, 9, 11, 12)


def is_kerala_monsoon(d: date | None = None) -> bool:
    """SW monsoon Jun-Sep, NE monsoon Oct-Dec."""
    d = d or date.today()
    return d.month in (6, 7, 8, 9, 10, 11, 12)


def get_seasonal_advisory(condition: str, humidity: int, wind_speed: float,
                          temp: float) -> dict:
    """Simple advisory based on current weather and season. No ML, pure rule."""
    c = condition.lower()
    m = datetime.now().month
    items = []

    if wind_speed > 10:
        items.append({"severity": "orange", "text": "Wind too high - avoid spraying today."})
    if humidity > 80:
        items.append({"severity": "orange", "text": "High humidity - fungal risk. Ensure good drainage."})
    if "rain" in c or "drizzle" in c:
        items.append({"severity": "orange", "text": "Rain expected - postpone spray by 4-6 hours."})
    if temp > 35:
        items.append({"severity": "orange", "text": "Very hot - irrigate early morning or evening."})
    if is_pest_season() and humidity > 70:
        items.append({"severity": "orange", "text": "Peak pest pressure. Check undersides of leaves."})

    # Irrigation: Kerala receives monsoon Jun-Dec; Jan-May is dry
    if m in (1, 2, 3, 4, 5) and temp > 30:
        items.append({"severity": "orange", "text": "Dry season, high temp - irrigate if soil dry at 5 cm."})
    if m in (6, 7, 8) and "rain" not in c:
        items.append({"severity": "orange", "text": "Rain-fed season - check soil moisture before irrigating."})

    return {"items": items}


def should_spray(wind_speed: float, humidity: int, condition: str,
                 forecast_rain_4h: bool) -> dict:
    """Return verdict: ok / caution / avoid with reasons."""
    reasons = []
    verdict = "ok"
    c = condition.lower()

    if wind_speed > 10:
        verdict = "avoid"
        reasons.append(f"Wind {wind_speed:.1f} km/h > 10 - drift risk.")
    if humidity > 85:
        if verdict != "avoid":
            verdict = "caution"
        reasons.append(f"Humidity {humidity}% > 85 - slow drying.")
    if forecast_rain_4h or "rain" in c or "drizzle" in c:
        verdict = "avoid"
        reasons.append("Rain expected within 4h.")
    if "thunder" in c or "storm" in c:
        verdict = "avoid"
        reasons.append("Storm - unsafe.")

    if verdict == "ok":
        reasons.append("Wind, humidity, rain OK for spraying.")

    return {"verdict": verdict, "reasons": reasons}


def pesticide_advisory(target: str) -> dict | None:
    t = target.lower()
    for key, val in PESTICIDES.items():
        if t in val["target"]:
            return {"key": key, **val}
    return None
