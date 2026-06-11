from datetime import datetime, time, timezone

from app.db import db
from app.integrations.openai_client import OpenAIAnalysisClient
from app.models import StockAnalysis, StockData
from app.services.stock_service import StockService


class AnalysisService:
    def __init__(
        self,
        stock_service: StockService | None = None,
        ai_client: OpenAIAnalysisClient | None = None,
    ) -> None:
        self.stock_service = stock_service or StockService()
        self.ai_client = ai_client or OpenAIAnalysisClient()

    def analyze(self, symbol: str) -> dict:
        symbol = symbol.strip().upper()
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, time.min, tzinfo=timezone.utc)
        today_end = datetime.combine(today, time.max, tzinfo=timezone.utc)

        cached_analysis = (
            StockAnalysis.query.filter(
                StockAnalysis.symbol == symbol,
                StockAnalysis.created_at >= today_start,
                StockAnalysis.created_at <= today_end,
            )
            .order_by(StockAnalysis.created_at.desc())
            .first()
        )

        if cached_analysis:
            cached_stock = (
                StockData.query.filter(
                    StockData.symbol == symbol,
                    StockData.created_at >= today_start,
                    StockData.created_at <= today_end,
                )
                .order_by(StockData.created_at.desc())
                .first()
            )

            if cached_stock is None or cached_stock.pe_ratio is None:
                stock = self.stock_service.get_stock_data(symbol)
                cached_stock = StockData(
                    symbol=stock["symbol"],
                    company_name=stock["company_name"],
                    market_cap=stock.get("market_cap"),
                    pe_ratio=stock.get("pe_ratio"),
                    current_price=stock.get("current_price"),
                )
                db.session.add(cached_stock)
                db.session.commit()

            return {
                "symbol": cached_analysis.symbol,
                "company_name": cached_analysis.company_name,
                "analysis": cached_analysis.analysis_text,
                "created_at": cached_analysis.created_at.isoformat(),
                "cached": True,
                "stock_data": {
                    "market_cap": cached_stock.market_cap if cached_stock else None,
                    "pe_ratio": cached_stock.pe_ratio if cached_stock else None,
                    "current_price": cached_stock.current_price if cached_stock else None,
                },
            }

        stock = self.stock_service.get_stock_data(symbol)
        analysis_text = self.ai_client.generate_analysis(stock)

        stock_record = StockData(
            symbol=stock["symbol"],
            company_name=stock["company_name"],
            market_cap=stock.get("market_cap"),
            pe_ratio=stock.get("pe_ratio"),
            current_price=stock.get("current_price"),
        )
        analysis_record = StockAnalysis(
            symbol=stock["symbol"],
            company_name=stock["company_name"],
            analysis_text=analysis_text,
        )
        db.session.add_all([stock_record, analysis_record])
        db.session.commit()

        return {
            "symbol": analysis_record.symbol,
            "company_name": analysis_record.company_name,
            "analysis": analysis_record.analysis_text,
            "created_at": analysis_record.created_at.isoformat(),
            "cached": False,
            "stock_data": {
                "market_cap": stock_record.market_cap,
                "pe_ratio": stock_record.pe_ratio,
                "current_price": stock_record.current_price,
            },
        }
