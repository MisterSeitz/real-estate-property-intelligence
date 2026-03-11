# Real Estate Schema: Tables and Columns Overview

Primary table for the Real Estate & Property Intelligence Pipeline.

## ai_intelligence.real_estate

- **RLS**: Enabled
- **Primary key**: `id` (bigint identity)
- **Unique**: `url`

### Columns:
| Column | Type | Description |
|---|---|---|
| id | bigint | Primary Key |
| created_at | timestamptz | Ingestion timestamp |
| title | text | Article title |
| url | text | Source URL (Unique) |
| source_feed | text | The origin feed name |
| published | text | Publication date string |
| ai_summary | text | AI-generated summary |
| sentiment | text | Market sentiment (Bullish/Bearish/Neutral) |
| category | text | Logic category (e.g., Luxury, PropTech) |
| market_dynamic | text | High-level market trend description |
| property_type | text | Residential, Commercial, Industrial, etc. |
| listing_price | text | Extracted price info |
| sqft | text | Square footage where available |
| market_status | text | Active, Sold, Under Offer, etc. |
| locations | text[] | Array of extracted cities/regions |
| companies | text[] | Array of mentioned companies |
| statistics | text[] | Array of extracted data points |
| image_url | text | Featured image link |
| method | text | Retrieval method (Direct/Brave) |
| raw_context_source | text | Full context for LLM |
