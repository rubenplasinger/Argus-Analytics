from flask import current_app
from openai import OpenAI, OpenAIError


class OpenAIAnalysisClient:
    def generate_analysis(self, stock: dict) -> str:
        api_key = current_app.config.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        client = OpenAI(api_key=api_key, timeout=20.0, max_retries=1)
        model = current_app.config.get("OPENAI_MODEL", "gpt-4o")

        prompt = (
            "Generate a concise stock analysis under 300 words using exactly these "
            "sections: Summary, Strengths, Risks, Valuation, Conclusion.\n\n"
            "Do not provide financial advice, trading instructions, price targets, "
            "or automated investment decisions. This is informational stock analysis only.\n\n"
            f"Stock data:\n"
            f"Symbol: {stock.get('symbol')}\n"
            f"Company: {stock.get('company_name')}\n"
            f"Current price: {stock.get('current_price')} {stock.get('currency') or ''}\n"
            f"Market cap: {stock.get('market_cap')}\n"
            f"P/E ratio: {stock.get('pe_ratio')}\n"
            f"Sector: {stock.get('sector')}\n"
            f"Industry: {stock.get('industry')}\n"
            f"52-week high: {stock.get('fifty_two_week_high')}\n"
            f"52-week low: {stock.get('fifty_two_week_low')}\n"
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a careful stock analysis assistant for informational use only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=450,
            )
        except (OpenAIError, TypeError) as exc:
            raise RuntimeError(f"OpenAI analysis failed: {exc}") from exc

        return response.choices[0].message.content.strip()
