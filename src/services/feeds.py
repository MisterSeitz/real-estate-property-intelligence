import feedparser
import requests
import os
from datetime import datetime, timedelta
from apify import Actor
from typing import List
from ..models import Article

# --- FEED CATALOG ---
CATEGORIZED_FEEDS = {
    "Major News": [
        "https://www.realtor.com/news/feed/",
        "https://www.housingwire.com/feed/",
        "https://www.inman.com/feed/",
        "https://rismedia.com/feed/",
        "https://www.forbes.com/real-estate/feed/"
    ],
    "Market Data": [
        "https://www.worldpropertyjournal.com/rss/market-news-headlines.xml",
        "https://www.calculatedriskblog.com/feeds/posts/default",
        "https://www.biggerpockets.com/blog/feed",
        "https://www.realwealth.com/feed/",
        "https://noradarealestate.com/feed/"
    ],
    "Luxury & Niche": [
        "https://extraordinaryliving.sothebysrealty.com/feed/",
        "https://www.luxurypresence.com/feed/",
        "https://therealdeal.com/new-york/feed/"
    ],
    "PropTech & Trends": [
        "https://geekestateblog.com/feed/",
        "https://proptechweekly.com/feed/"
    ],
    "International": [
        "https://www.propertyweek.com/7001460.rss",
        "https://betterdwelling.com/feed/"
    ]
}

async def fetch_articles(source: str, custom_url: str, max_items: int, is_test: bool, existing_urls: set = None) -> List[Article]:
    """
    Main entry point to fetch articles via RSS.
    """
    if existing_urls is None:
        existing_urls = set()

    if is_test:
        return [Article(title="Test Market News", url="http://test.com", source="Test")]

    # Handle RSS Sources
    urls = []
    if source == "custom" and custom_url:
        urls = [custom_url]
    elif source == "all":
        urls = list(set(u for cat in CATEGORIZED_FEEDS.values() for u in cat))
    else:
        urls = CATEGORIZED_FEEDS.get(source, [])

    if not urls and source != "custom":
        Actor.log.warning(f"No feeds found for source: {source}")
        return []

    articles = []
    # Buffer fetch: Fetch 2x items to ensure we have enough after potential failures
    for url in urls:
        if len(articles) >= max_items * 2: 
            break
            
        try:
            Actor.log.info(f"Parsing RSS: {url}")
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                link = entry.get('link')
                if not link or link in existing_urls: 
                    continue

                articles.append(Article(
                    title=entry.get("title", "No Title"),
                    url=entry.get("link", ""),
                    source=feed.feed.get("title", "Unknown Source"),
                    published=entry.get("published"),
                    summary=entry.get("summary")
                ))
        except Exception as e:
            Actor.log.warning(f"Feed error {url}: {e}")
            
    return articles