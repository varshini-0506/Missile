# Product Discovery Pipeline

Complete automated pipeline for discovering and extracting products from e-commerce sites.

## Overview

This pipeline integrates three main components:
1. **ecomFinding.py** - Discovers e-commerce sites selling products via Google Custom Search API
2. **universalSearch.py** - Discovers search URL templates for e-commerce sites
3. **universalProductExtractor.py** - Extracts product data from search result pages

## Pipeline Flow

```
Products List
    ↓
[Step 1] Discover E-Commerce Sites (ecomFinding.py)
    ↓
[Step 2] Discover Search URL Templates (universalSearch.py)
    ↓
[Step 3] Store Templates in Supabase DB
    ↓
[Step 4] Retrieve Templates & Embed Product Names
    ↓
[Step 5] Extract Products (universalProductExtractor.py)
    ↓
[Step 6] Store Products in Supabase DB
```

## Setup

### 1. Install Dependencies

```bash
pip install supabase selenium requests
```

### 2. Configure Supabase

Get your Supabase credentials:
1. Go to https://app.supabase.com/project/_/settings/api
2. Copy your Project URL and anon public key

Set environment variables:
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

Or create a `.env` file:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 3. Database Schema

The pipeline uses a `search_url_templates` table in Supabase. The migration has already been applied if you see the table. If not, run:

```sql
-- Table is created automatically via migration
-- See: create_search_url_templates_table migration
```

## Usage

### Basic Usage

```python
from productPipeline import ProductDiscoveryPipeline

# Initialize pipeline
pipeline = ProductDiscoveryPipeline()

# List of products to search
products = ["laptop", "smartphone", "headphones"]

# Run full pipeline
pipeline.run_pipeline(
    products=products,
    skip_discovery=False,  # Set True to use existing templates only
    max_items_per_site=50
)
```

### Command Line Usage

```bash
# Search for specific products
python productPipeline.py laptop smartphone headphones

# Or edit the script to set products list
```

### Skip Discovery Phase

If you already have search templates in the database:

```python
pipeline.run_pipeline(
    products=["laptop"],
    skip_discovery=True,  # Use existing templates from DB
    max_items_per_site=50
)
```

## Database Tables

### `search_url_templates`
Stores discovered search URL templates:
- `platform` - E-commerce site domain
- `site_url` - Original site URL
- `url_template` - Template with `{query}` placeholder
- `product_name` - Product associated with discovery
- `is_active` - Whether template is currently usable

### `universal_products`
Stores extracted product data:
- `name` - Product title
- `current_price` - Price
- `rating` - Star rating
- `reviews` - Review count
- `image_url` - Product image
- `site` - Platform source
- `search_query` - Original search term

## Features

- **Automated Discovery**: Finds e-commerce sites automatically
- **Template Storage**: Reuses search URL templates across products
- **Multi-Platform**: Works with any e-commerce site
- **Error Handling**: Continues processing even if some sites fail
- **Database Integration**: Stores templates and products in Supabase
- **Configurable**: Adjust max items, skip phases, etc.

## Example Output

```
================================================================================
PRODUCT DISCOVERY PIPELINE - STARTING
================================================================================

[#] PROCESSING PRODUCT: laptop
    ↓
[Step 1] Discovered 10 e-commerce sites
[Step 2] Discovered 8 search templates
[Step 3] Stored 8 templates in database
[Step 4] Retrieved 8 search URLs
[Step 5] Extracted 387 products
[Step 6] Stored 387 products in database

================================================================================
PIPELINE SUMMARY
================================================================================
Products processed: 1
Templates stored: 8
Products extracted: 387
Products stored in DB: 387
```

## Troubleshooting

### No Supabase Connection
- Check `SUPABASE_URL` and `SUPABASE_KEY` environment variables
- Verify your Supabase project is active

### No E-Commerce Sites Found
- Check Google Custom Search API quota (100 free queries/day)
- Verify `API_KEY` and `SEARCH_ENGINE_ID` in `ecomFinding.py`

### Search Templates Not Found
- Run with `skip_discovery=False` to discover new templates
- Check database for existing templates: `SELECT * FROM search_url_templates`

### Products Not Extracting
- Verify search URLs are valid and accessible
- Check if sites require JavaScript rendering (handled by Selenium)
- Review logs for specific error messages

## Next Steps

- Monitor template usage with `last_used_at` timestamp
- Clean up inactive templates periodically
- Add product deduplication by URL or SKU
- Implement scheduled pipeline runs
- Add email/notification alerts

