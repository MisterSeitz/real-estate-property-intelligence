import requests
from apify import Actor

def send_discord_alert(webhook_url: str, record: dict, is_test: bool):
    if is_test: return
    
    # Send all moderate-to-high impact (>=5) or specific categories
    impact = record.get('impact_score', 0)
    if impact < 5:
        return

    color = 3447003 # Blue
    sent = record.get('sentiment', 'Neutral')
    if sent == "Bullish": color = 5763719 # Green
    if sent == "Bearish": color = 15548997 # Red
    
    # Determine summary and source
    summary = record.get('ai_summary') or record.get('summary', 'No summary available.')
    source = record.get('source_feed') or record.get('source', 'Unknown')
    companies = record.get('companies', []) or []
    locations = record.get('locations', []) or []

    embed = {
        "title": record.get('title'),
        "url": record.get('url'),
        "description": f"{summary}\n\n**Impact:** {impact}/10 | **Sentiment:** {sent}",
        "color": color,
        "fields": [
             {"name": "Focus Area", "value": f"📍 {', '.join(locations[:3]) if locations else 'Global'}", "inline": True},
             {"name": "Key Entities", "value": f"🏢 {', '.join(companies[:3]) if companies else 'N/A'}", "inline": True}
        ],
        "footer": {"text": f"Source: {source} | Sector: {record.get('category', 'Real Estate')}"}
    }
    
    try:
        requests.post(webhook_url, json={"embeds": [embed]})
    except Exception: pass