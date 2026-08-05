"""
Free Public Forex & Currency Conversion Module for TEKLİF-Sim (v3.0.0).
Fetches official daily exchange rates from European Central Bank (ECB)
XML/RSS feeds with zero API fees. Includes local fallback rates (USD, EUR, GBP, TRY).
"""

import xml.etree.ElementTree as ET
import urllib.request
import functools
from typing import Dict
from src.logger import logger

# Fallback exchange rates (relative to USD = 1.0) if network/ECB is unreachable
FALLBACK_RATES: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,   # 1 USD = 0.92 EUR
    "GBP": 0.78,   # 1 USD = 0.78 GBP
    "TRY": 35.50   # 1 USD = 35.50 TRY
}

CURRENCY_SYMBOLS: Dict[str, str] = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "TRY": "₺"
}


@functools.lru_cache(maxsize=1)
def fetch_ecb_rates() -> Dict[str, float]:
    """
    Fetches daily Euro reference exchange rates from ECB RSS feed.
    Converts rates relative to USD (USD = 1.0).
    """
    rates = dict(FALLBACK_RATES)
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TeklifSim/3.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            tree = ET.fromstring(response.read())
            namespaces = {'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
            raw_rates = {"EUR": 1.0}
            for cube in tree.findall('.//ecb:Cube[@currency]', namespaces):
                curr = cube.attrib.get('currency')
                rate_val = float(cube.attrib.get('rate'))
                raw_rates[curr] = rate_val
            
            # Rebase all currencies relative to USD = 1.0
            usd_in_eur = raw_rates.get("USD", 1.08)
            rates["USD"] = 1.0
            rates["EUR"] = round(1.0 / usd_in_eur, 4)
            if "GBP" in raw_rates:
                rates["GBP"] = round(raw_rates["GBP"] / usd_in_eur, 4)
            if "TRY" in raw_rates:
                rates["TRY"] = round(raw_rates["TRY"] / usd_in_eur, 4)
            logger.info(f"Successfully fetched ECB FX rates: {rates}")
    except Exception as e:
        logger.warning(f"Could not fetch ECB rates, using fallback rates: {e}")

    return rates


def convert_currency(amount_usd: float, target_currency: str = "USD") -> float:
    """
    Converts a USD amount to target currency (USD, EUR, GBP, TRY).
    """
    target_currency = target_currency.upper()
    rates = fetch_ecb_rates()
    rate = rates.get(target_currency, 1.0)
    return round(amount_usd * rate, 2)


def format_currency(amount: float, currency: str = "USD") -> str:
    """Formats amount with appropriate currency symbol."""
    curr = currency.upper()
    symbol = CURRENCY_SYMBOLS.get(curr, "$")
    return f"{symbol}{amount:,.2f} {curr}"
