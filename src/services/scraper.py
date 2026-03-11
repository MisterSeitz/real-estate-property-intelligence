import requests
from bs4 import BeautifulSoup
from apify import Actor
from typing import Optional, List

async def scrape_article_content(url: str, is_test_mode: bool) -> Optional[str]:
    """
    Attempts to scrape full text from a property news article.
    """
    if is_test_mode:
        return "TEST CONTENT: This is a placeholder for property article scraping."

    try:
        Actor.log.info(f"Scraping: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove noise
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
            
        # Common article body selectors
        body = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        if body:
            return body.get_text(separator=' ', strip=True)
        
        return soup.get_text(separator=' ', strip=True)
        
    except Exception as e:
        Actor.log.warning(f"Scrape failed for {url}: {e}")
        return None

def scrape_global_indices():
    """
    Stub for real estate metrics if needed (e.g., Mortgage rates, FHFA index).
    Legacy market index scraping removed.
    """
    return []

def backfill_historical_indices(days_back: int = 60):
    """
    Stub for historical property data backfills.
    """
    return []
