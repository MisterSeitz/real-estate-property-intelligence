# 🏠 Real Estate & Property Intelligence Pipeline

This document serves as the high-level system architecture and operational "Source of Truth" for the **Real Estate & Property Intelligence Pipeline**.

## System Overview
This project is an automated AI system that functions in two distinct phases: 
1. **Admin / Infrastructure Operations (Data Gathering)**
2. **User Operations (Data Querying)**

By separating the heavy lifting (scraping & AI analysis) from the user experience, users enjoy millisecond latency and predictable billing while having access to premium, AI-verified real estate intelligence.

## 1. Internal Agent Routines (Admin Scheduled)
The Actor is scheduled to run on the Apify platform in `DAILY_UPDATE` run mode periodically.

### A. Property News Agent (LangGraph Workflow)
- **Target:** Polls 17+ global RSS feeds across property news portals (Realtor, HousingWire, Inman, Zillow, etc.).
- **Scraping Engine:** Attempts direct HTML scraping first. If restricted, delegates to a search sub-agent via Brave Search APIs.
- **LLM Pipeline:** Passes text to an LLM (via OpenRouter/OpenAI API) and asks the agent to act as a *Senior Real Estate Analyst*.
- **Extraction:** Synthesizes a structured `DatasetRecord` containing:
  - Sentiments (Bullish/Bearish/Neutral)
  - Market Dynamics (Trends, Risk factors)
  - Property Details (Type, Price, Sqft, Status)
  - Arrays (Locations, Companies, Statistics)
- **Output:** Upserts clean entities into Supabase `ai_intelligence.real_estate`.

### B. Maintenance Agent
- **Target:** Aggregates recent LLM Sentiment Scores and Market Dynamics to update overarching property market risk indices.

## 2. User-Facing Operations (Monetized APIs)
Users are isolated from the raw scraping layer. They interact via predefined database query endpoints using a **Pay-Per-Event (PPE)** monetization model.

*   **`SEARCH_ARTICLES`**: Uses Supabase querying to fetch AI-annotated text records matching custom `searchQuery` and `startDate` constraints. Charges the `analyze_article_summary` event.
*   **`PROPERTY_REPORT`**: Generates an aggregated market summary combining current metrics with news sentiment. Charges the `report-generated` event.

## 3. Database Schema Overview (Supabase Postgres)
- **`ai_intelligence.real_estate`**: Primary table for processed articles with impact scores, sentiment, and property specifics.

See `real_estate.md` for strict relational schema.