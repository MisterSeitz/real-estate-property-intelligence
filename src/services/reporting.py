import os
from supabase import create_client
from apify import Actor

async def generate_property_report():
    """
    Queries Supabase Views to generate a consolidated JSON report for Property Intelligence.
    """
    Actor.log.info("🏠 Generating Property Intelligence Report...")
    
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not (url and key):
        Actor.log.error("❌ Supabase credentials missing.")
        return {"error": "Missing credentials"}
        
    supabase = create_client(url, key)
    
    report = {}

    try:
        # 1. Recent Property Trends (Headlines)
        trends_res = supabase.schema("ai_intelligence").table("real_estate")\
            .select("title, ai_summary, sentiment, market_dynamic")\
            .order("created_at", desc=True).limit(5).execute()
        report["recent_trends"] = trends_res.data

        # 2. Market Sentiment Summary
        # Note: In a production environment, these would be dedicated Views
        report["market_overview"] = {
            "status": "Generating via AI...",
            "focus": "Global Property Markets"
        }
        
        # 3. Push to Apify Dataset
        await Actor.push_data(report)
        Actor.log.info("✅ Property report generated and pushed to dataset.")
        
        return report

    except Exception as e:
        Actor.log.error(f"❌ Reporting Error: {e}")
        return {"error": str(e)}