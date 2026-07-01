from flask import Blueprint, current_app, jsonify, render_template, request

from app.db import db
from app.services.analysis_service import AnalysisService
from app.services.stock_service import StockLookupError


bp = Blueprint("main", __name__)
analysis_service = AnalysisService()


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/analyze")
def analyze():
    payload = request.get_json(silent=True) or request.form
    symbol = (payload.get("symbol") or "").strip().upper()

    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    try:
        result = analysis_service.analyze(symbol)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except StockLookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unexpected error while analyzing %s", symbol)
        return jsonify({"error": "unexpected backend error; check the server log"}), 500

    return jsonify(result), 201
