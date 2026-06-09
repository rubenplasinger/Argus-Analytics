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
            "stock_data": {
                "market_cap": stock_record.market_cap,
                "pe_ratio": stock_record.pe_ratio,
                "current_price": stock_record.current_price,
            },
        }
