from datetime import datetime, timezone

from app.db import db


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StockData(db.Model):
    __tablename__ = "stock_data"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=False)
    market_cap = db.Column(db.BigInteger, nullable=True)
    pe_ratio = db.Column(db.Float, nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)


class StockAnalysis(db.Model):
    __tablename__ = "stock_analysis"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=False)
    analysis_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
