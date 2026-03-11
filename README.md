# 🏠 Real Estate & Property Intelligence Database API

**Query pre-analyzed, historical, and market-moving property intelligence, backed by a daily AI-scraping pipeline.**

*Note: This Actor provides instant access to premium real estate data without the wait. Our backend pipeline performs heavy-duty scraping and LLM analysis (Senior Analyst level) on global property news and market trends, storing them in a high-performance database for your immediate consumption.*

---

## 🚀 Why Use This Database?

When you run this Actor in **SEARCH_ARTICLES** mode, you gain access to deeply enriched property data points:
* **🏘️ Property Specifics:** Automatically extracts property types (Residential, Commercial, Industrial), listing prices, and square footage.
* **📍 Location Intelligence:** Identifies specific cities, regions, and countries mentioned.
* **📈 Sentiment & Dynamics:** immediate `Bullish` / `Bearish` / `Neutral` classification along with narrated market dynamics (e.g., "Rising Interest Rates," "Supply Shortage").
* **📊 Market Status:** Tracks if properties/markets are `Active`, `Sold`, `Under Construction`, or `Developing`.

---

## 🛠️ Usage & Configuration

Your setup is straightforward. Select a mode and start querying.

### **Configure Inputs**
| Field | Description |
| :--- | :--- |
| **Operation Mode** | Select `SEARCH_ARTICLES` to fetch property news, or `PROPERTY_REPORT` for aggregate summaries. |
| **Search Term** | (Optional) Query keywords like "Luxury," "New York," "Interest Rates," or "Condos." |
| **Category** | (Optional) Filter by `Major News`, `Market Data`, `PropTech & Trends`, etc. |
| **Max Articles** | Limit the number of parsed events returned (Default: 20). |

---

## 📅 Operation Modes

1.  **`SEARCH_ARTICLES` (Monetized)**: The primary query mode. Fetch AI-annotated property news matching your criteria.
2.  **`PROPERTY_REPORT` (Monetized)**: Generates a high-level market summary combining recent sentiments and trends.
3.  **`DAILY_UPDATE` (Admin)**: Scheduled background task that scrapes 17+ RSS feeds and populates the database.

---

## 💰 Pricing & Monetization

This Actor uses a transparent **Pay-Per-Event (PPE)** model:
* **`article-summary`**: Charged **$0.01** per article returned in `SEARCH_ARTICLES` mode.
* **`report-generated`**: Charged **$0.05** per generated `PROPERTY_REPORT`.

---

## 🏢 Platform Architecture

Refer to [AGENTS.md](AGENTS.md) for details on the LangGraph workflow, Supabase schema, and LLM extraction logic.