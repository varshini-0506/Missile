# Production Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

### 1. Dependencies
- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Verify Python version (3.8+)
- [ ] Verify Chrome browser is installed (for Selenium)

### 2. Environment Variables
- [ ] Set `SUPABASE_URL` environment variable
- [ ] Set `SUPABASE_KEY` environment variable
- [ ] Verify Google API keys in `LaunchPad/ecomFinding.py`

### 3. Database Setup

Run these SQL commands in Supabase:

- [ ] **products table**: Add `last_extracted` column
```sql
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS last_extracted TIMESTAMP WITH TIME ZONE;
CREATE INDEX IF NOT EXISTS idx_products_last_extracted ON products(last_extracted);
```

- [ ] **extracted_urls table**: Create tracking table
```sql
CREATE TABLE IF NOT EXISTS extracted_urls (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    constructed_url TEXT NOT NULL,
    products_found INTEGER DEFAULT 0,
    products_saved INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT FALSE,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES search_url_templates(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_extracted_urls_unique 
ON extracted_urls(product_id, template_id);

CREATE INDEX IF NOT EXISTS idx_extracted_urls_product_id ON extracted_urls(product_id);
CREATE INDEX IF NOT EXISTS idx_extracted_urls_template_id ON extracted_urls(template_id);
```

- [ ] **product_data table**: Verify exists with all columns
  - platform_url
  - product_name
  - original_price
  - current_price
  - product_url
  - product_image_url
  - description
  - rating
  - reviews
  - in_stock
  - brand

### 4. Initial Data
- [ ] Add at least one category using `inputDataHandler.py`
- [ ] Add at least one product to each category
- [ ] Verify data is saved correctly in database

### 5. File Structure
- [ ] Verify all Python files are present:
  - `main.py`
  - `LaunchPad/categorySearchPipeline.py`
  - `LaunchPad/productExtractionPipeline.py`
  - `LaunchPad/inputDataHandler.py`
  - `LaunchPad/ecomFinding.py`
  - `LaunchPad/universalSearch.py`
  - `Missile/universalProductExtractor.py`

### 6. Configuration
- [ ] Verify `SUPABASE_URL` in all files points to correct project
- [ ] Verify `SUPABASE_KEY` is set (can be in code or environment)
- [ ] Verify Google API keys in `ecomFinding.py`

## Testing

### 7. Unit Tests
- [ ] Test `inputDataHandler.py` - add sample data
- [ ] Test `categorySearchPipeline.py` - verify it discovers templates
- [ ] Test `productExtractionPipeline.py` - verify it extracts products
- [ ] Test `universalProductExtractor.py` - verify extraction works

### 8. Integration Tests
- [ ] Run `main.py` for 5-10 minutes
- [ ] Verify both pipelines start correctly
- [ ] Verify templates are saved to database
- [ ] Verify products are extracted and saved
- [ ] Verify `extracted_urls` table is populated
- [ ] Verify duplicate URLs are skipped

## Deployment

### 9. Production Environment
- [ ] Server has Python 3.8+
- [ ] Server has Chrome browser installed
- [ ] Server has stable internet connection
- [ ] Server can access Supabase
- [ ] Environment variables are set

### 10. Run Production
- [ ] Start with: `python main.py`
- [ ] Monitor logs for first 10 minutes
- [ ] Verify no critical errors
- [ ] Verify data is being saved

### 11. Monitoring
- [ ] Set up log monitoring (optional)
- [ ] Verify pipelines continue running
- [ ] Check database periodically for new data

## Post-Deployment

### 12. Verification
- [ ] Check `search_url_templates` table has entries
- [ ] Check `product_data` table has entries
- [ ] Check `extracted_urls` table is being populated
- [ ] Verify duplicate URLs are not being re-extracted

### 13. Maintenance
- [ ] Add new products/categories as needed using `inputDataHandler.py`
- [ ] Monitor for errors in logs
- [ ] Check Google API quota usage
- [ ] Monitor database size

## Common Issues

- **"No products found"** → Add products using `inputDataHandler.py`
- **"No templates found"** → Wait for Category Pipeline to discover sites
- **"ChromeDriver error"** → Install Chrome browser
- **"Supabase connection failed"** → Check credentials
- **"All URLs already extracted"** → Normal - pipelines will wait for new data

## Success Criteria

✅ Both pipelines run without crashing
✅ Templates are discovered and saved
✅ Products are extracted and saved
✅ Duplicate URLs are skipped
✅ New data added via `inputDataHandler.py` is processed automatically

