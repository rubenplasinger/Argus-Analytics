import re

import yfinance as yf
from requests.exceptions import RequestException


class StockLookupError(Exception):
    pass


class StockService:
    SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.\-]{1,16}$")

    def get_stock_data(self, symbol: str) -> dict:
        symbol = symbol.strip().upper()
        if not self.SYMBOL_PATTERN.fullmatch(symbol):
            raise ValueError("symbol must be 1-16 characters using letters, numbers, dots, or hyphens")

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
        except (RequestException, KeyError, ValueError, TypeError) as exc:
            raise StockLookupError(f"could not retrieve stock data for symbol {symbol}") from exc

        company_name = info.get("longName") or info.get("shortName")
        current_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )

        if not company_name or current_price is None:
            raise StockLookupError(f"could not find stock data for symbol {symbol}")

        return {
            "symbol": symbol,
            "company_name": company_name,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
            "current_price": current_price,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currency": info.get("currency"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }
