# Argus Analytics

Flask application for AI-powered stock analysis.

The app accepts a stock ticker, retrieves company and market data with `yfinance`, extracts key metrics, asks OpenAI `gpt-4o` for a concise informational analysis, stores the request in MySQL with SQLAlchemy, and returns the result through `POST /analyze`.

This project is for stock analysis only. It does not trade, provide financial advice, or make automated investment decisions.

## Project Structure

```text
app/
  integrations/
    openai_client.py
  services/
    analysis_service.py
    stock_service.py
  templates/
    index.html
  __init__.py
  config.py
  db.py
  models.py
  routes.py
run.py
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

## API

### POST /analyze

Request:

```json
{
  "symbol": "AAPL"
}
```

Response:

```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "analysis": "...",
  "created_at": "...",
  "stock_data": {
    "market_cap": 123,
    "pe_ratio": 30.5,
    "current_price": 190.0
  }
}
```

## Setup With Docker

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Set your OpenAI API key in `.env`:

```text
OPENAI_API_KEY=sk-...
```

3. Start the application:

```bash
docker compose up --build
```

4. Open the test interface:

```text
http://localhost:5000
```

## Local Development

Install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables for a reachable MySQL database:

```text
DATABASE_URL=mysql+pymysql://argus:argus@localhost:3306/argus_analytics
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

Run the app:

```bash
python run.py
```

## Database Models

`StockData`

- `symbol`
- `company_name`
- `market_cap`
- `pe_ratio`
- `current_price`
- `created_at`

`StockAnalysis`

- `symbol`
- `company_name`
- `analysis_text`
- `created_at`
