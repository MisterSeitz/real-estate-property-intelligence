import asyncio
import os
from typing import TypedDict, List
from apify import Actor
from langgraph.graph import StateGraph
from dotenv import load_dotenv

# Load local env vars if present
load_dotenv(".env.local")
load_dotenv()

# Models & Services
from .models import InputConfig, Article, DatasetRecord
from .services.feeds import fetch_articles
from .services.scraper import scrape_article_content, scrape_global_indices
from .services.search import fetch_brave_fallback
from .services.llm import analyze_content
from .services.notifications import send_discord_alert
from supabase import create_client, Client

# --- HELPER: Sync to Supabase ---
def sync_to_supabase(record: DatasetRecord): 
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        Actor.log.warning("⚠️ Supabase credentials missing. Skipping sync.")
        return

    # Map DatasetRecord to 'ai_intelligence.real_estate' schema
    db_record = {
        "title": record.title,
        "url": record.url,
        "source_feed": record.source_feed,
        "published": record.published,
        "ai_summary": record.ai_summary,
        "sentiment": record.sentiment,
        "category": record.category,
        "market_dynamic": record.market_dynamic,
        "property_type": record.property_type,
        "listing_price": record.listing_price,
        "sqft": record.sqft,
        "market_status": record.market_status,
        "locations": record.locations,
        "companies": record.companies,
        "statistics": record.statistics,
        "image_url": record.image_url,
        "method": record.data_source_method,
        "raw_context_source": record.raw_context_source
    }

    try:
        supabase: Client = create_client(url, key)
        # Table: ai_intelligence.real_estate (schema prefix handled by .schema() or default)
        supabase.schema("ai_intelligence").table("real_estate").upsert(
            db_record, 
            on_conflict="url"
        ).execute()
        Actor.log.info(f"🔄 Synced to ai_intelligence.real_estate: {db_record.get('title', 'No Title')[:30]}...")
    except Exception as e:
        Actor.log.error(f"❌ Supabase Sync Failed: {e}")

# --- INTELLIGENCE GRAPH NODES ---
class State(TypedDict):
    config: InputConfig
    queue: List[Article]
    processed_count: int

async def load_config(state: State):
    input_data = await Actor.get_input() or {}
    config = InputConfig(**input_data)
    
    # Check keys only if scraping (Intelligence mode)
    if not config.runTestMode and config.runMode == "DAILY_UPDATE":
        if not (os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")):
            await Actor.fail("❌ Missing API Key (OPENROUTER/OPENAI).")
    return {"config": config, "processed_count": 0}

async def fetch_step(state: State):
    config = state["config"]
    
    # 1. Fetch from Supabase exactly what we already have for recent deduplication
    existing_urls = set()
    try:
        url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        if url and key:
            from supabase import create_client
            supabase = create_client(url, key)
            # Table: ai_intelligence.real_estate
            res = supabase.schema("ai_intelligence").table("real_estate").select("url").order("created_at", desc=True).limit(1000).execute()
            if res.data:
                existing_urls = {row.get("url") for row in res.data if row.get("url")}
                Actor.log.info(f"Loaded {len(existing_urls)} existing URLs for deduplication")
    except Exception as e:
        Actor.log.warning(f"Failed to fetch deduplication URLs: {e}")

    articles = await fetch_articles(config.source, config.customFeedUrl, config.maxArticles, config.runTestMode, existing_urls)
    return {"queue": articles[:config.maxArticles]}

async def processor(state: State):
    config = state["config"]
    queue = state["queue"]
    idx = state["processed_count"]
    if idx >= len(queue): return {"processed_count": idx}
    
    article = queue[idx]
    Actor.log.info(f"Processing {idx+1}: {article.title}")
    
    # Scrape & Analyze
    content = scrape_article_content(article.url, config.runTestMode)
    method = "Direct Scraper"
    if not content or len(content) < 200:
        content = fetch_brave_fallback(article.title, config.runTestMode, config.country)
        method = "Brave Search Fallback"
    if not content: content = "Content unavailable."

    analysis = analyze_content(content, config.runTestMode)
    
    record = DatasetRecord(
        source_feed=article.source, title=article.title, url=article.url,
        published=article.published, markdown_content=content,
        data_source_method=method, **analysis
    )
    
    # Output & Sync
    await Actor.push_data([record.model_dump(by_alias=True)])
    # Sync is now a direct record sync to the specified table
    sync_to_supabase(record)
    
    if config.discordWebhookUrl:
        send_discord_alert(config.discordWebhookUrl, record.model_dump(by_alias=True), config.runTestMode)
    
    return {"processed_count": idx + 1}

def should_continue(state: State):
    return "continue" if state["processed_count"] < len(state["queue"]) else "end"

# --- MAIN ENTRY POINT ---
async def main():
    async with Actor:
        raw_input = await Actor.get_input() or {}
        run_mode = raw_input.get("runMode", "SEARCH_ARTICLES")

        url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        supabase = create_client(url, key) if (url and key) else None

        # 1. MAINTENANCE MODE 
        if run_mode == "MAINTENANCE":
            Actor.log.info("🏠 Running Real Estate Maintenance...")
            from .services.maintenance import run_daily_maintenance
            await run_daily_maintenance()
            await Actor.set_status_message("Maintenance Complete")

        # 2. DAILY UPDATE (Admin: scrape property news, push to DB)
        elif run_mode == "DAILY_UPDATE":
            Actor.log.info("🏠 Running Daily Property Update...")
            
            Actor.log.info("🧠 Starting Property INTELLIGENCE scraping...")
            graph = StateGraph(State)
            graph.add_node("init", load_config)
            graph.add_node("fetch", fetch_step)
            graph.add_node("process", processor)
            graph.set_entry_point("init")
            graph.add_edge("init", "fetch")
            graph.add_edge("fetch", "process")
            graph.add_conditional_edges("process", should_continue, {"continue": "process", "end": "__end__"})
            app = graph.compile()
            limit = raw_input.get("maxArticles", 20) + 15
            await app.ainvoke({"config": None, "queue": [], "processed_count": 0}, config={"recursion_limit": limit})
            await Actor.set_status_message("Daily Property Update Complete")

        # 3. PROPERTY REPORT MODE (Monetized)
        elif run_mode == "PROPERTY_REPORT":
            if not raw_input.get("runTestMode"):
                charge_res = await Actor.charge(event_name="report-generated")
                if charge_res and getattr(charge_res, "eventChargeLimitReached", False):
                    await Actor.fail("User charge limit reached.")
                    return
            await generate_property_report()
            await Actor.set_status_message("Property Report Generated")

        # 4. SEARCH ARTICLES FROM DB (Monetized)
        elif run_mode == "SEARCH_ARTICLES":
            Actor.log.info("🔍 Querying Property Articles from DB...")
            if not supabase:
                await Actor.fail("Supabase credentials missing.")
                return
            
            query = supabase.schema("ai_intelligence").table("real_estate").select("*")
            if raw_input.get("startDate"):
                query = query.gte("created_at", raw_input.get("startDate"))
            if raw_input.get("searchQuery"):
                q = raw_input.get("searchQuery")
                # Search across title, summary, and locations
                query = query.or_(f"title.ilike.%{q}%,ai_summary.ilike.%{q}%,locations.cs.{{ \"{q}\" }}")
                
            res = query.order("created_at", desc=True).limit(raw_input.get("maxArticles", 20)).execute()
            
            if res.data:
                reformatted_data = res.data
                if not raw_input.get("runTestMode"):
                    charge_res = await Actor.charge(event_name="article-summary", count=len(reformatted_data))
                    if charge_res and getattr(charge_res, "eventChargeLimitReached", False):
                        await Actor.fail("User charge limit reached.")
                        return
                await Actor.push_data(reformatted_data)
            await Actor.set_status_message(f"Returned {len(res.data) if res.data else 0} articles")

if __name__ == "__main__":
    asyncio.run(main())