"""
Category Search URL Discovery Pipeline

Continuously processes categories starting from oldest (least recently updated):
1. Gets oldest category by latest_input timestamp
2. Gets first product from that category
3. Discovers e-commerce sites for category using ecomFinding.py
4. Converts domains to search URL templates using universalSearch.py
5. Saves search templates to database with category_id
6. Updates category's latest_updated timestamp
7. Moves to next category (endless loop)
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import time

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from ecomFinding import GoogleCustomSearchAPI, API_KEY, SEARCH_ENGINE_ID
from universalSearch import UniversalSearchURLAgent

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


class CategorySearchPipeline:
    """
    Pipeline for discovering and saving search URL templates for categories
    """
    
    def __init__(self):
        """Initialize all components"""
        print(f"\n{'='*80}")
        print("INITIALIZING CATEGORY SEARCH URL DISCOVERY PIPELINE")
        print(f"{'='*80}\n")
        
        # Initialize e-commerce finder
        print("[*] Initializing Google Custom Search API...")
        self.ecom_finder = GoogleCustomSearchAPI(API_KEY, SEARCH_ENGINE_ID)
        
        # Initialize search URL discoverer
        print("[*] Initializing Universal Search URL Agent...")
        self.search_agent = UniversalSearchURLAgent()
        
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
    
    def get_oldest_category(self) -> Optional[Dict[str, Any]]:
        """
        Get the category with oldest latest_updated timestamp (least recently processed)
        Returns None if no categories found
        
        Returns:
            Dictionary with category_id and name, or None
        """
        if not self.supabase:
            print("[!] Supabase not available - cannot get category")
            return None
        
        try:
            # Fetch all categories and sort in Python (Supabase client doesn't support nulls_first)
            response = self.supabase.table("categories").select(
                "category_id, name, latest_input, latest_updated"
            ).execute()
            
            if response.data and len(response.data) > 0:
                # Sort in Python: NULLs first (oldest/never processed), then by timestamp ASC
                categories = response.data
                categories.sort(key=lambda x: (
                    0 if x.get('latest_updated') is None else 1,  # NULLs come first (0 < 1)
                    x.get('latest_updated') or ''  # Then by timestamp (empty string for NULLs)
                ))
                
                category = categories[0]
                print(f"[✓] Found oldest category: {category['name']} (ID: {category['category_id']})")
                print(f"    Latest updated: {category.get('latest_updated', 'Never')}")
                return category
            
            return None
            
        except Exception as e:
            print(f"[✗] Error getting oldest category: {e}")
            return None
    
    def get_nth_product(self, category_id: int, product_index: int) -> Optional[str]:
        """
        Get the Nth product name for a given category_id (1st, 2nd, 3rd, etc.)
        
        Args:
            category_id: ID of the category
            product_index: Product index (1 for 1st product, 2 for 2nd, etc.)
            
        Returns:
            Product name or None if category has fewer products than index
        """
        if not self.supabase:
            print("[!] Supabase not available - cannot get product")
            return None
        
        try:
            # Get all products for this category and select the Nth one
            # Fetch all and select Nth item (more reliable than range/offset)
            response = self.supabase.table("products").select("name").eq(
                "category_id", category_id
            ).order("product_id").execute()  # Order by product_id for consistency
            
            if response.data and len(response.data) >= product_index:
                product_name = response.data[product_index - 1]["name"]  # 0-based index
                print(f"[✓] Found {product_index}{self._ordinal_suffix(product_index)} product: {product_name}")
                return product_name
            
            print(f"[!] Category {category_id} doesn't have {product_index}{self._ordinal_suffix(product_index)} product")
            return None
            
        except Exception as e:
            print(f"[✗] Error getting {product_index}{self._ordinal_suffix(product_index)} product: {e}")
            return None
    
    def _ordinal_suffix(self, n: int) -> str:
        """Get ordinal suffix (st, nd, rd, th)"""
        if 10 <= n % 100 <= 20:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    
    def discover_ecommerce_sites(self, category_name: str, product_name: str) -> List[Dict[str, Any]]:
        """
        Discover e-commerce sites for a category + product using ecomFinding.py
        
        Args:
            category_name: Name of the category
            product_name: Name of the product
            
        Returns:
            List of e-commerce site results with domain, link, etc.
        """
        search_term = f"{category_name} {product_name}"
        print(f"\n[*] Discovering e-commerce sites for: {search_term}")
        
        results = self.ecom_finder.extract_all_ecommerce_results(
            search_term,
            max_results=10,
            max_pages=1
        )
        
        if not results:
            print(f"[!] No e-commerce sites found for '{search_term}'")
            return []
        
        print(f"[✓] Found {len(results)} e-commerce sites\n")
        return results
    
    def convert_domains_to_urls(self, ecommerce_results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract unique domain URLs from e-commerce results and convert to base URLs
        
        Args:
            ecommerce_results: List of e-commerce site results
            
        Returns:
            List of unique base URLs (https://domain.com)
        """
        domains_seen = set()
        urls = []
        
        for result in ecommerce_results:
            domain = result.get('domain', '')
            link = result.get('link', '')
            
            if not domain or not link:
                continue
            
            # Convert to base URL (https://domain.com) using proper URL parsing
            if link.startswith('http'):
                try:
                    parsed = urlparse(link)
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                    
                    if domain not in domains_seen:
                        domains_seen.add(domain)
                        urls.append(base_url)
                        print(f"  [→] {base_url}")
                except Exception as e:
                    print(f"  [✗] Error parsing URL {link}: {e}")
                    continue
        
        print(f"\n[✓] Extracted {len(urls)} unique domain URLs\n")
        return urls
    
    def discover_search_templates(self, domain_urls: List[str], test_query: str) -> List[Dict[str, Any]]:
        """
        Discover search URL templates for each domain using universalSearch.py
        
        Args:
            domain_urls: List of base domain URLs
            test_query: Product name to use as test query
            
        Returns:
            List of search URL template results
        """
        print(f"\n[*] Discovering search URL templates...")
        print(f"    Test query: {test_query}")
        print(f"    Domains: {len(domain_urls)}\n")
        
        templates = []
        
        for i, url in enumerate(domain_urls, 1):
            print(f"\n[{i}/{len(domain_urls)}] Discovering template for: {url}")
            
            try:
                result = self.search_agent.discover_search_url(url, test_query=test_query)
                
                if "error" not in result:
                    # Extract the url_template from result
                    url_template = result.get("url_template") or result.get("url_template_full", "")
                    
                    if url_template:
                        templates.append({
                            "platform": result.get("platform", ""),
                            "search_url": url_template,
                            "base_url": result.get("base_url", ""),
                            "site_url": result.get("site_url", "")
                        })
                        print(f"[✓] Successfully discovered template for {result.get('platform')}")
                        print(f"    Template: {url_template[:80]}...")
                    else:
                        print(f"[!] No template found for {result.get('platform')}")
                else:
                    print(f"[✗] Failed: {result.get('error')}")
            
            except Exception as e:
                print(f"[✗] Exception: {str(e)}")
            
            # Small delay between sites
            if i < len(domain_urls):
                time.sleep(1)
        
        print(f"\n[✓] Discovered {len(templates)} search URL templates\n")
        return templates
    
    def save_search_template(self, category_id: int, search_url: str, platform: str = "") -> bool:
        """
        Save search URL template to database with category_id
        
        Args:
            category_id: ID of the category
            search_url: Search URL template (with {query} or {your_query} placeholder)
            platform: Platform/domain name
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.supabase:
            print("[!] Supabase not available - cannot save template")
            return False
        
        try:
            # Prepare data for insertion
            data = {
                "category_id": category_id,
                "search_url": search_url,
                # Note: search_url_templates table only has: id, search_url, category_id
                # Platform info can be stored in notes if needed
            }
            
            # Insert (upsert on unique constraint: search_url, category_id)
            response = self.supabase.table("search_url_templates").upsert(
                data,
                on_conflict="search_url,category_id"
            ).execute()
            
            if response.data:
                print(f"[✓] Saved search template for category_id: {category_id}")
                print(f"    Platform: {platform}")
                print(f"    URL: {search_url[:80]}...")
                return True
            else:
                print(f"[✗] Failed to save template")
                return False
                
        except Exception as e:
            print(f"[✗] Error saving search template: {e}")
            return False
    
    def update_category_timestamp(self, category_id: int) -> bool:
        """
        Update category's latest_updated timestamp in categories table
        
        Args:
            category_id: ID of the category
            
        Returns:
            True if updated successfully
        """
        if not self.supabase:
            print("[!] Supabase not available - cannot update timestamp")
            return False
        
        try:
            current_time = datetime.now().isoformat()
            response = self.supabase.table("categories").update({
                "latest_updated": current_time
            }).eq("category_id", category_id).execute()
            
            if response.data:
                print(f"[✓] Updated latest_updated timestamp for category_id: {category_id}")
                return True
            else:
                print(f"[✗] Failed to update timestamp")
                return False
                
        except Exception as e:
            print(f"[✗] Error updating timestamp: {e}")
            return False
    
    def process_category(self, category: Dict[str, Any], product_index: int) -> bool:
        """
        Process a single category with Nth product: discover sites, templates, and save to DB
        
        Args:
            category: Dictionary with category_id and name
            product_index: Index of product to use (1st, 2nd, 3rd, etc.)
            
        Returns:
            True if processed successfully, False if category doesn't have Nth product
        """
        category_id = category["category_id"]
        category_name = category["name"]
        
        print(f"\n{'='*80}")
        print(f"PROCESSING CATEGORY: {category_name} (ID: {category_id})")
        print(f"Using {product_index}{self._ordinal_suffix(product_index)} product")
        print(f"{'='*80}\n")
        
        # Step 1: Get Nth product from category
        product = self.get_nth_product(category_id, product_index)
        if not product:
            print(f"[!] Skipping category '{category_name}' - no {product_index}{self._ordinal_suffix(product_index)} product found")
            return False
        
        # Step 2: Discover e-commerce sites using category + product
        ecommerce_sites = self.discover_ecommerce_sites(category_name, product)
        if not ecommerce_sites:
            print(f"[!] No e-commerce sites found for '{category_name} {product}'")
            return False
        
        # Step 3: Convert domains to URLs
        domain_urls = self.convert_domains_to_urls(ecommerce_sites)
        if not domain_urls:
            print(f"[!] No valid domain URLs extracted")
            return False
        
        # Step 4: Discover search templates
        templates = self.discover_search_templates(domain_urls, test_query=product)
        if not templates:
            print(f"[!] No search templates discovered")
            return False
        
        # Step 5: Save templates to database
        saved_count = 0
        for template in templates:
            if self.save_search_template(
                category_id=category_id,
                search_url=template["search_url"],
                platform=template.get("platform", "")
            ):
                saved_count += 1
        
        print(f"\n[✓] Saved {saved_count}/{len(templates)} templates for category '{category_name}'")
        
        # Step 6: Update category timestamp
        self.update_category_timestamp(category_id)
        
        return True
    
    def run_continuous(self, delay_between_categories: int = 5):
        """
        Run pipeline continuously, processing categories with Nth product in cycles
        Cycle 1: All categories with 1st product
        Cycle 2: All categories with 2nd product
        Cycle 3: All categories with 3rd product
        And so on...
        
        Args:
            delay_between_categories: Delay in seconds between processing categories
        """
        print(f"\n{'='*80}")
        print("STARTING CONTINUOUS CATEGORY PROCESSING")
        print("Processing by product cycles: 1st product for all, then 2nd, then 3rd, etc.")
        print(f"{'='*80}\n")
        print(f"[*] Delay between categories: {delay_between_categories} seconds\n")
        
        product_index = 1  # Start with 1st product
        processed_count = 0
        categories_without_nth_product = 0
        max_skip_threshold = 5  # If 5 consecutive categories don't have Nth product, move to next product
        
        while True:
            try:
                # Get oldest category
                category = self.get_oldest_category()
                
                if not category:
                    print("[!] No categories found. Waiting 30 seconds before retry...")
                    time.sleep(30)
                    continue
                
                # Process category with current product_index
                success = self.process_category(category, product_index)
                
                if success:
                    processed_count += 1
                    categories_without_nth_product = 0  # Reset counter on success
                    print(f"\n[✓] Successfully processed category #{processed_count} with {product_index}{self._ordinal_suffix(product_index)} product")
                else:
                    categories_without_nth_product += 1
                    print(f"\n[!] Category doesn't have {product_index}{self._ordinal_suffix(product_index)} product (skipped)")
                    
                    # Update timestamp even when skipped so category moves forward in queue
                    # This prevents getting stuck on the same category forever
                    category_id = category.get("category_id")
                    if category_id:
                        print(f"[*] Updating category timestamp to allow other categories to be processed...")
                        self.update_category_timestamp(category_id)
                    
                    # If too many categories don't have this product_index, move to next product
                    if categories_without_nth_product >= max_skip_threshold:
                        print(f"\n[*] {max_skip_threshold} consecutive categories don't have {product_index}{self._ordinal_suffix(product_index)} product")
                        print(f"[*] Moving to next product index: {product_index + 1}\n")
                        product_index += 1
                        categories_without_nth_product = 0  # Reset counter
                        continue
                
                # Delay before next category
                print(f"\n[*] Waiting {delay_between_categories} seconds before next category...\n")
                time.sleep(delay_between_categories)
                
            except KeyboardInterrupt:
                print(f"\n\n[!] Pipeline interrupted by user")
                print(f"[✓] Processed {processed_count} categories before stopping")
                print(f"[✓] Current product index: {product_index}\n")
                break
            except Exception as e:
                print(f"\n[✗] Error in continuous loop: {e}")
                print(f"[*] Waiting 10 seconds before retry...\n")
                time.sleep(10)


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print(f"\n{'='*80}")
    print("CATEGORY SEARCH URL DISCOVERY PIPELINE")
    print(f"{'='*80}\n")
    
    # Initialize pipeline
    pipeline = CategorySearchPipeline()
    
    # Run continuously
    # Process categories one by one in endless loop
    pipeline.run_continuous(delay_between_categories=5)

