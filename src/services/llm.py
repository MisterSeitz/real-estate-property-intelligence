import os
import json
from openai import OpenAI
from typing import Dict, Any
from apify import Actor

def analyze_content(text: str, is_test_mode: bool) -> Dict[str, Any]:
    if is_test_mode:
        return {
            "content_type": "Property News",
            "ai_summary": "TEST: US Mortgage rates hit 20-year low.",
            "sentiment": "Bullish",
            "property_type": "Residential",
            "listing_price": "$500,000",
            "market_status": "Active",
            "locations": ["New York", "London"],
            "category": "Market Data",
            "market_dynamic": "High demand, low inventory.",
            "entities": [{"name": "Compass", "type": "Agency"}, {"name": "Zillow", "type": "Company"}],
            "risk_factors": ["Interest Rate Hikes"],
            "impact_score": 8
        }

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = "https://openrouter.ai/api/v1" if os.getenv("OPENROUTER_API_KEY") else None
    
    if not api_key:
        Actor.log.error("Missing API Key for analysis.")
        return {"ai_summary": "Error: Missing API Key"}

    client = OpenAI(api_key=api_key, base_url=base_url)
    model = "openai/gpt-4o-mini" if os.getenv("OPENROUTER_API_KEY") else "gpt-3.5-turbo"

    prompt = f"""
    You are a Senior Real Estate & Property Analyst. Analyze the provided text and extract structured intelligence.
    TEXT: {text[:12000]}

    Tasks:
    1. Classify Content Type: "Property News", "Market Trends", "PropTech", "Regulatory", "Investment Strategy".
    2. Executive Summary: 2 concise, professional sentences.
    3. Sentiment: "Bullish", "Bearish", or "Neutral".
    4. Market Dynamic: Short description of the current trend (e.g., "Sellers Market", "Cooling Demand").
    5. Property Details (If available):
       - property_type: e.g., "Residential", "Commercial", "Industrial".
       - listing_price: e.g., "$1.2M", "£500k" (include currency).
       - sqft: Square footage/meters.
       - market_status: e.g., "Active", "Sold", "Foreclosure".
    6. Entities & Intelligence:
       - entities: A list of objects containing `name` and `type` (e.g., "Company", "Person", "Agency", "Location"). Extract all real estate firms, developers, and key people.
       - risk_factors: A list of potential risks mentioned (e.g., "High Interest Rates", "Regulatory Changes").
       - impact_score: An integer from 1 to 10 based on the article's importance to the global/local market.
    
    Return JSON:
    {{
        "content_type": "...",
        "ai_summary": "...",
        "sentiment": "...",
        "market_dynamic": "...",
        "property_type": "...",
        "listing_price": "...",
        "sqft": "...",
        "market_status": "...",
        "locations": ["..."],
        "companies": ["..."],
        "statistics": ["..."],
        "entities": [{{ "name": "...", "type": "..." }}],
        "risk_factors": ["..."],
        "impact_score": 5,
        "category": "..."
    }}
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        Actor.log.error(f"Analysis failed: {e}")
        return {"ai_summary": "Analysis Error"}