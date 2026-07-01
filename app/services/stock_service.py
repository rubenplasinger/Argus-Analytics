import re
import time

import requests
from requests.exceptions import RequestException


class StockLookupError(Exception):
    pass


class StockService:
    SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.\-]{1,16}$")

    def get_stock_data(self, symbol: str) -> dict:
        symbol = symbol.strip().upper()
        if not self.SYMBOL_PATTERN.fullmatch(symbol):
            raise ValueError("symbol must be 1-16 characters using letters, numbers, dots, or hyphens")

        chart_meta = self._get_chart_meta(symbol)
        if not chart_meta:
            raise StockLookupError(
                f"could not retrieve price data for symbol {symbol}; Yahoo Finance may be rate limiting requests"
            )

        current_price = (
            chart_meta.get("regularMarketPrice")
            or chart_meta.get("chartPreviousClose")
        )

        if current_price is None:
            raise StockLookupError(
                f"could not retrieve price data for symbol {symbol}; Yahoo Finance may be rate limiting requests"
            )

        eps = self._get_eps(symbol)
        pe_ratio = self._calculate_pe_ratio(current_price, eps)
        company_name = (
            chart_meta.get("longName")
            or chart_meta.get("shortName")
            or symbol
        )

        return {
            "symbol": symbol,
            "company_name": company_name,
            "market_cap": chart_meta.get("marketCap"),
            "pe_ratio": pe_ratio or chart_meta.get("trailingPE"),
            "current_price": float(current_price),
            "sector": None,
            "industry": None,
            "currency": chart_meta.get("currency"),
            "fifty_two_week_high": chart_meta.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": chart_meta.get("fiftyTwoWeekLow"),
        }

    def _get_chart_meta(self, symbol: str) -> dict:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"range": "5d", "interval": "1d"}
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            payload = response.json()
            results = payload.get("chart", {}).get("result") or []
            if not results:
                return {}
            return results[0].get("meta") or {}
        except (RequestException, KeyError, ValueError, TypeError):
            return {}

    def _get_eps(self, symbol: str) -> float | None:
        url = f"https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}"
        params = {
            "symbol": symbol,
            "type": "quarterlyDilutedEPS,annualDilutedEPS",
            "period1": 0,
            "period2": int(time.time()),
        }
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            payload = response.json()
            results = payload.get("timeseries", {}).get("result") or []
        except (RequestException, KeyError, ValueError, TypeError):
            return None

        quarterly_eps = []
        annual_eps = []

        for result in results:
            quarterly_eps.extend(result.get("quarterlyDilutedEPS") or [])
            annual_eps.extend(result.get("annualDilutedEPS") or [])

        quarterly_values = self._extract_eps_values(quarterly_eps)
        if len(quarterly_values) >= 4:
            return sum(quarterly_values[-4:])

        annual_values = self._extract_eps_values(annual_eps)
        if annual_values:
            return annual_values[-1]

        return None

    def _extract_eps_values(self, rows: list[dict]) -> list[float]:
        sorted_rows = sorted(rows, key=lambda row: row.get("asOfDate") or "")
        values = []

        for row in sorted_rows:
            raw_value = (row.get("reportedValue") or {}).get("raw")
            if raw_value is not None:
                values.append(float(raw_value))

        return values

    def _calculate_pe_ratio(self, current_price: float, eps: float | None) -> float | None:
        if eps in (None, 0):
            return None

        return round(float(current_price) / eps, 2)
