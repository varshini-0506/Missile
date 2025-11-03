"""
Product Extraction Pipeline

For each product in the products table:
1. Get product name and category_id
2. Get all search_url_templates for that category_id
3. Replace placeholder ({query} or {your_query}) with product name
4. Pass constructed URL to universalProductExtractor.extract_products()
5. Extractor automatically saves products to product_data table
"""

import sys
import os
from typing import Dict, List, Any, Optional
import time
from urllib.parse import quote_plus

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, "..", "Missile"))

# Import product extractor
from universalProductExtractor import UniversalProductExtractor

# Supabase imports
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("[!] Warning: supabase-py not installed. Install with: pip install supabase")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://whfjofihihlhctizchmj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndoZmpvZmloaWhsaGN0aXpjaG1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzNzQzNDMsImV4cCI6MjA3Njk1MDM0M30.OsJnOqeJgT5REPg7uxkGmmVcHIcs5QO4vdyDi66qpR0")

if not SUPABASE_KEY:
    print("[!] Warning: SUPABASE_KEY not set. Database operations will be skipped.")


class ProductExtractionPipeline:
    """
    Pipeline for extracting products using search URL templates
    """
    
    def __init__(self):
        """Initialize all components"""
        print(f"\n{'='*80}")
        print("INITIALIZING PRODUCT EXTRACTION PIPELINE")
        print(f"{'='*80}\n")
        
        # Initialize product extractor
        print("[*] Initializing Universal Product Extractor...")
        self.extractor = UniversalProductExtractor()
        print("[✓] Product Extractor initialized\n")
        
        # Initialize Supabase client
        self.supabase: Optional[Client] = None
        if SUPABASE_AVAILABLE and SUPABASE_KEY:
            try:
                print("[*] Connecting to Supabase...")
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("[✓] Connected to Supabase\n")
            except Exception as e:
                print(f"[✗] Failed to connect to Supabase: {e}\n")
                self.supabase = None
        else:
            print("[!] Supabase not configured - database operations disabled\n")
    
    def get_all_products(self, order_by_oldest: bool = True) -> List[Dict[str, Any]]:
        """
        Get all products from the products table with their category_id
        Optionally order by last_extracted timestamp (oldest first for continuous processing)
        
        Args:
            order_by_oldest: If True, returns products ordered by last_extracted (oldest first)
                           If False, returns products in any order
        
        Returns:
            List of products with product_id, name, and category_id
        """
        if not self.supabase:
            print("[!] Supabase not available - cannot get products")
            return []
        
        try:
            # Try to select with last_extracted if column exists
            # If column doesn't exist, we'll fall back to simple select
            try:
                response = self.supabase.table("products").select(
                    "product_id, name, category_id, last_extracted"
                ).execute()
            except:
                # If last_extracted column doesn't exist, select without it
                response = self.supabase.table("products").select(
                    "product_id, name, category_id"
                ).execute()
            
            if response.data:
                products = response.data
                
                # Sort by last_extracted if column exists and order_by_oldest is True
                if order_by_oldest and any('last_extracted' in p for p in products):
                    # Sort: NULLs first (never extracted), then by timestamp ASC
                    products.sort(key=lambda x: (
                        0 if x.get('last_extracted') is None else 1,  # NULLs come first
                        x.get('last_extracted') or ''  # Then by timestamp
                    ))
                
                print(f"[✓] Found {len(products)} products in database")
                if order_by_oldest:
                    never_extracted = sum(1 for p in products if p.get('last_extracted') is None)
                    if never_extracted > 0:
                        print(f"    {never_extracted} products never extracted")
                
                return products
            
            print("[!] No products found in database")
            return []
            
        except Exception as e:
            print(f"[✗] Error getting products: {e}")
            return []
    
    def update_product_last_extracted(self, product_id: int) -> bool:
        """
        Update product's last_extracted timestamp after processing
        
        Args:
            product_id: ID of the product
            
        Returns:
            True if updated successfully, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            from datetime import datetime
            current_time = datetime.now().isoformat()
            
            # Try to update last_extracted column
            # If column doesn't exist, this will fail silently (column can be added later)
            response = self.supabase.table("products").update({
                "last_extracted": current_time
            }).eq("product_id", product_id).execute()
            
            return response.data is not None
        except Exception as e:
            # Column might not exist yet - that's okay
            # We'll just track in memory/logs
            return False
    
    def get_search_templates_for_category(self, category_id: int) -> List[Dict[str, Any]]:
        """
        Get all search URL templates for a given category_id
        
        Args:
            category_id: ID of the category
            
        Returns:
            List of search URL templates
        """
        if not self.supabase:
            print("[!] Supabase not available - cannot get templates")
            return []
        
        try:
            response = self.supabase.table("search_url_templates").select(
                "id, search_url"
            ).eq("category_id", category_id).execute()
            
            if response.data:
                return response.data
            
            return []
            
        except Exception as e:
            print(f"[✗] Error getting search templates for category {category_id}: {e}")
            return []
    
    def is_url_already_extracted(self, product_id: int, template_id: int) -> bool:
        """
        Check if a URL has already been sent to extractor for this product+template combination
        
        Args:
            product_id: ID of the product
            template_id: ID of the template
            
        Returns:
            True if URL already extracted, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            response = self.supabase.table("extracted_urls").select(
                "id"
            ).eq("product_id", product_id).eq("template_id", template_id).limit(1).execute()
            
            return response.data and len(response.data) > 0
            
        except Exception as e:
            # Table might not exist yet - treat as not extracted
            return False
    
    def save_extracted_url(self, product_id: int, template_id: int, constructed_url: str, 
                          num_products: int, saved_count: int, success: bool) -> bool:
        """
        Save URL that was sent to extractor to the extracted_urls table
        
        Args:
            product_id: ID of the product
            template_id: ID of the template
            constructed_url: The actual URL sent to extractor
            num_products: Number of products found
            saved_count: Number of products saved to DB
            success: Whether extraction was successful
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            data = {
                "product_id": product_id,
                "template_id": template_id,
                "constructed_url": constructed_url,
                "products_found": num_products,
                "products_saved": saved_count,
                "success": success
            }
            
            # Use upsert to handle duplicates gracefully
            response = self.supabase.table("extracted_urls").upsert(
                data,
                on_conflict="product_id,template_id"
            ).execute()
            
            return response.data is not None
            
        except Exception as e:
            # Table might not exist - that's okay
            return False
    
    def replace_placeholder_in_url(self, url_template: str, product_name: str) -> str:
        """
        Replace placeholder in URL template with product name
        
        Handles different placeholder formats:
        - {query}
        - {your_query}
        - {q}
        
        Args:
            url_template: URL template with placeholder
            product_name: Product name to replace placeholder
            
        Returns:
            Complete URL with product name
        """
        # URL encode the product name
        encoded_name = quote_plus(product_name)
        
        # Try different placeholder formats
        if "{query}" in url_template:
            return url_template.replace("{query}", encoded_name)
        elif "{your_query}" in url_template:
            return url_template.replace("{your_query}", encoded_name)
        elif "{q}" in url_template:
            return url_template.replace("{q}", encoded_name)
        else:
            # No placeholder found, append as query parameter
            # This handles templates without placeholders
            separator = "&" if "?" in url_template else "?"
            return f"{url_template}{separator}q={encoded_name}"
    
    def process_product(self, product: Dict[str, Any], product_index: int = None, total_products: int = None) -> Dict[str, Any]:
        """
        Process a single product: get templates, build URLs, extract products
        
        Args:
            product: Product dictionary with product_id, name, category_id
            product_index: Current product index (for progress tracking)
            total_products: Total number of products (for progress tracking)
            
        Returns:
            Summary of processing results
        """
        product_id = product["product_id"]
        product_name = product["name"]
        category_id = product["category_id"]
        last_extracted = product.get("last_extracted")
        
        print(f"\n{'='*80}")
        if product_index is not None and total_products is not None:
            print(f"PROCESSING PRODUCT [{product_index}/{total_products}]: {product_name}")
        else:
            print(f"PROCESSING PRODUCT: {product_name}")
        print(f"Product ID: {product_id} | Category ID: {category_id}")
        if last_extracted:
            print(f"Last extracted: {last_extracted}")
        else:
            print(f"Last extracted: Never (first time)")
        print(f"{'='*80}\n")
        
        # Get search templates for this category
        templates = self.get_search_templates_for_category(category_id)
        
        if not templates:
            print(f"[!] No search URL templates found for category {category_id}")
            return {
                "product_id": product_id,
                "product_name": product_name,
                "templates_found": 0,
                "urls_processed": 0,
                "total_products_extracted": 0,
                "success": False
            }
        
        print(f"[✓] Found {len(templates)} search URL templates for this category\n")
        
        total_products_extracted = 0
        urls_processed = 0
        
        # Process each template
        for i, template in enumerate(templates, 1):
            template_id = template["id"]
            url_template = template["search_url"]
            
            print(f"\n[{i}/{len(templates)}] Processing template {template_id}")
            print(f"    Template: {url_template[:80]}...")
            
            # Check if this URL has already been extracted
            if self.is_url_already_extracted(product_id, template_id):
                print(f"    [⊘] URL already extracted - skipping")
                continue
            
            # Replace placeholder with product name
            search_url = self.replace_placeholder_in_url(url_template, product_name)
            print(f"    Constructed URL: {search_url[:100]}...")
            
            num_products = 0
            saved_count = 0
            extraction_success = False
            
            try:
                # Extract products from the search URL
                # Pass category_id and searched product_id so extracted products are linked correctly
                print(f"    [*] Extracting products...")
                result = self.extractor.extract_products(
                    search_url, 
                    max_items=50, 
                    wait_seconds=12,
                    category_id=category_id,
                    searched_product_id=product_id
                )
                
                if result.get("success"):
                    num_products = result.get("num_products", 0)
                    saved_count = result.get("saved_to_db", 0)
                    extraction_success = True
                    total_products_extracted += num_products
                    urls_processed += 1
                    
                    print(f"    [✓] Extracted {num_products} products (saved {saved_count} to DB)")
                else:
                    error = result.get("error", "Unknown error")
                    print(f"    [✗] Extraction failed: {error}")
                    extraction_success = False
                
            except Exception as e:
                print(f"    [✗] Exception during extraction: {e}")
                extraction_success = False
            
            # Save URL to extracted_urls table
            self.save_extracted_url(
                product_id=product_id,
                template_id=template_id,
                constructed_url=search_url,
                num_products=num_products,
                saved_count=saved_count,
                success=extraction_success
            )
            
            # Small delay between URLs to avoid rate limiting
            if i < len(templates):
                time.sleep(2)
        
        print(f"\n[✓] Finished processing product '{product_name}'")
        print(f"    Templates used: {len(templates)}")
        print(f"    URLs processed: {urls_processed}")
        print(f"    Total products extracted: {total_products_extracted}")
        
        # Update last_extracted timestamp
        self.update_product_last_extracted(product_id)
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "templates_found": len(templates),
            "urls_processed": urls_processed,
            "total_products_extracted": total_products_extracted,
            "success": True
        }
    
    def run_continuous(self, delay_between_products: int = 5):
        """
        Run pipeline continuously, processing products one by one
        Processes oldest products first (never extracted > oldest timestamp)
        Tracks progress and resumes from where it left off
        
        Args:
            delay_between_products: Delay in seconds between processing products
        """
        print(f"\n{'='*80}")
        print("STARTING CONTINUOUS PRODUCT EXTRACTION")
        print("Processing oldest/never-extracted products first")
        print(f"{'='*80}\n")
        print(f"[*] Delay between products: {delay_between_products} seconds\n")
        
        processed_count = 0
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                print(f"\n{'='*80}")
                print(f"CYCLE #{cycle_count} - Getting products (oldest first)...")
                print(f"{'='*80}\n")
                
                # Get all products ordered by oldest first
                products = self.get_all_products(order_by_oldest=True)
                
                if not products:
                    print("[!] No products found. Waiting 30 seconds before retry...")
                    time.sleep(30)
                    continue
                
                print(f"[*] Processing {len(products)} products in this cycle\n")
                
                # Process each product
                for i, product in enumerate(products, 1):
                    result = self.process_product(
                        product, 
                        product_index=i, 
                        total_products=len(products)
                    )
                    processed_count += 1
                    
                    if result.get("success"):
                        print(f"\n[✓] Successfully processed product #{processed_count} ({i}/{len(products)} in cycle)")
                        print(f"    Product: {result.get('product_name')}")
                        print(f"    Extracted: {result.get('total_products_extracted')} products from {result.get('urls_processed')} URLs")
                    else:
                        print(f"\n[✗] Failed to process product #{processed_count} ({i}/{len(products)} in cycle)")
                    
                    # Delay before next product
                    if i < len(products):
                        print(f"\n[*] Waiting {delay_between_products} seconds before next product...\n")
                        time.sleep(delay_between_products)
                
                print(f"\n{'='*80}")
                print(f"CYCLE #{cycle_count} COMPLETE")
                print(f"Total products processed this cycle: {len(products)}")
                print(f"Total products processed overall: {processed_count}")
                
                # Check if any URLs were actually processed (not all skipped)
                # If all URLs were skipped, products are already fully processed
                print(f"[*] Checking for new URLs to extract...")
                print(f"[*] Next cycle will process products from oldest (never extracted first)")
                print(f"[*] Restarting cycle...")
                print(f"{'='*80}\n")
                
                # Longer delay before starting next cycle to avoid busy-waiting
                # when all products are already processed
                time.sleep(10)
                
            except KeyboardInterrupt:
                print(f"\n\n[!] Pipeline interrupted by user")
                print(f"[✓] Processed {processed_count} products before stopping")
                print(f"[✓] Completed {cycle_count} cycle(s)")
                print(f"[*] Next run will continue from oldest unprocessed products\n")
                break
            except Exception as e:
                print(f"\n[✗] Error in continuous loop: {e}")
                print(f"[*] Waiting 10 seconds before retry...\n")
                time.sleep(10)
    
    def run_once(self, max_products: Optional[int] = None):
        """
        Run pipeline once, processing all products (or up to max_products)
        
        Args:
            max_products: Maximum number of products to process (None for all)
        """
        print(f"\n{'='*80}")
        print("STARTING SINGLE-RUN PRODUCT EXTRACTION")
        print(f"{'='*80}\n")
        
        # Get all products
        products = self.get_all_products()
        
        if not products:
            print("[!] No products found in database")
            return
        
        if max_products:
            products = products[:max_products]
            print(f"[*] Processing first {max_products} products\n")
        
        processed_count = 0
        
        for i, product in enumerate(products, 1):
            result = self.process_product(
                product, 
                product_index=i, 
                total_products=len(products)
            )
            processed_count += 1
            
            if result.get("success"):
                print(f"\n[✓] Successfully processed product #{processed_count}/{len(products)}")
                print(f"    Extracted: {result.get('total_products_extracted')} products")
            else:
                print(f"\n[✗] Failed to process product #{processed_count}/{len(products)}")
            
            # Small delay between products
            if processed_count < len(products):
                time.sleep(2)
        
        print(f"\n{'='*80}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'='*80}")
        print(f"Total products processed: {processed_count}")
        print(f"{'='*80}\n")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print(f"\n{'='*80}")
    print("PRODUCT EXTRACTION PIPELINE")
    print(f"{'='*80}\n")
    
    # Initialize pipeline
    pipeline = ProductExtractionPipeline()
    
    # Run once (process all products)
    # Or use run_continuous() for endless processing
    pipeline.run_once()

