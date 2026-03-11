from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Article(BaseModel):
    title: str
    url: str
    source: Optional[str] = None
    published: Optional[str] = None
    summary: Optional[str] = None

class InputConfig(BaseModel):
    source: str = "all"
    customFeedUrl: Optional[str] = None
    maxArticles: int = 20
    country: str = "ALL"
    discordWebhookUrl: Optional[str] = None
    runMode: str = "SEARCH_ARTICLES"
    searchQuery: Optional[str] = None
    startDate: Optional[str] = None
    runTestMode: bool = False

class DatasetRecord(BaseModel):
    source_feed: Optional[str] = Field(None, alias="source")
    title: str
    url: str
    published: Optional[str] = None
    ai_summary: Optional[str] = Field(None, description="AI-generated executive summary.")
    markdown_content: Optional[str] = Field(None, description="Scraped/Processed content.")
    
    # --- REAL ESTATE INTELLIGENCE FIELDS ---
    content_type: str = "Property News"
    sentiment: Optional[str] = None # Bullish/Bearish/Neutral
    market_dynamic: Optional[str] = Field(None, description="High-level market trend.")
    
    property_type: Optional[str] = None
    listing_price: Optional[str] = None
    sqft: Optional[str] = None
    market_status: Optional[str] = None
    
    locations: Optional[List[str]] = Field(default_factory=list)
    companies: Optional[List[str]] = Field(default_factory=list)
    statistics: Optional[List[str]] = Field(default_factory=list)
    
    category: Optional[str] = None
    image_url: Optional[str] = None
    data_source_method: str = Field(..., description="Scraper, Brave_Search, or Fallback")
    raw_context_source: Optional[str] = None

    class Config:
        populate_by_name = True