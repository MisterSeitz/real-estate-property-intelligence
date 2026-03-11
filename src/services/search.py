import os
import requests
from apify import Actor

def fetch_brave_fallback(query: str, is_test_mode: bool, country: str = "ALL") -> str:
    if is_test_mode: return "Source: Brave Test\nSnippet: Market is up today."

    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        Actor.log.warning("⚠️ No BRAVE_API_KEY. Skipping fallback.")
        return ""

    url = "https://api.search.brave.com/res/v1/web/search"
    params = {
        "q": query,
        "country": country if country != "ALL" else "US",
        "count": 5, 
        "extra_snippets": True 
    }
    headers = {"X-Subscription-Token": api_key}

    try:
        Actor.log.info(f"🦁 Searching Brave for: {query[:30]}...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200: return ""
        
        data = response.json()
        results = data.get('web', {}).get('results', [])
        
        context = "BRAVE SEARCH CONTEXT (Use for analysis):\n"
        for item in results[:4]:
            context += f"- Source: {item.get('meta_url', {}).get('netloc')}\n- Content: {item.get('description')}\n\n"
        return context

    except Exception as e:
        Actor.log.warning(f"Brave error: {e}")
        return ""