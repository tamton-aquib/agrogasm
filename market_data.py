"""Kerala market price data (seed + static).

In production replace with scrape of Kerala Agricultural University,
SAMETI, or Agmarknet. Structure kept simple for hackathon demo.
"""

from datetime import date

# Per Kerala, per kg (INR), date of last observed price
SEED_PRICES = [
    {"crop": "Rice (atta)", "market": "Vaikom", "price": 42, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Rice (boiled)", "market": "Changanassery", "price": 38, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Coconut (whole)", "market": "Kottayam", "price": 22, "unit": "piece", "date": "2024-03-01"},
    {"crop": "Coconut (copra)", "market": "Kottayam", "price": 145, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Pepper (black)", "market": "Idukki", "price": 620, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Cardamom", "market": "Spice Board, Kochi", "price": 2400, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Rubber (TSR20)", "market": "Kottayam", "price": 185, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Banana (nendran)", "market": "Aluva", "price": 32, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Ginger (dry)", "market": "Idukki", "price": 280, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Turmeric", "market": "Ernakulam", "price": 165, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Onion", "market": "Ernakulam", "price": 34, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Tomato", "market": "Kottayam", "price": 42, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Potato", "market": "Ernakulam", "price": 28, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Green chilli", "market": "Kottayam", "price": 85, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Okra (vendakkai)", "market": "Kottayam", "price": 48, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Cucumber", "market": "Kottayam", "price": 24, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Mango (kadshan)", "market": "Malappuram", "price": 55, "unit": "kg", "date": "2024-03-01"},
    {"crop": "Jackfruit", "market": "Kottayam", "price": 18, "unit": "kg", "date": "2024-03-01"},
]


def get_prices() -> list:
    return SEED_PRICES


def search_prices(query: str) -> list:
    q = query.lower()
    return [p for p in SEED_PRICES if q in p["crop"].lower() or q in p["market"].lower()]
