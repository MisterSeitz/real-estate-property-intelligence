import requests
from apify import Actor

def send_discord_alert(webhook_url: str, record: dict, is_test: bool):
    if is_test: return
    
    # Only send high impact (>60) or specific categories
    if record.get('market_impact_score', 0) < 60:
        return

    color = 3447003 # Blue
    sent = record.get('sentiment', 'Neutral')
    if sent == "Bullish": color = 5763719 # Green
    if sent == "Bearish": color = 15548997 # Red
    
    embed = {
        "title": record.get('title'),
        "url": record.get('url'),
        "description": f"{record.get('summary')}\n\n**Impact:** {record.get('market_impact_score')}/100 | **Sentiment:** {sent}",
        "color": color,
        "fields": [
             {"name": "Tickers", "value": ", ".join(record.get('affected_tickers', []) or []), "inline": True}
        ],
        "footer": {"text": f"Source: {record.get('source')}"}
    }
    
    try:
        requests.post(webhook_url, json={"embeds": [embed]})
    except Exception: pass