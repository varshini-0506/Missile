
import requests
from urllib.parse import urlparse, urlencode
import json
import time
from typing import List, Dict, Set
import csv
from datetime import datetime
import os

# Google Custom Search API credentials - use environment variables or defaults
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyDvWUeUaMF7otiD1EYs5OzyJ1dQFfxgHu8")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "858497242c8c04abc")


class GoogleCustomSearchAPI:
    """
    Extract e-commerce website links using Google Custom Search API
    Stores ALL results with complete details
    """
    
    def __init__(self, api_key: str, search_engine_id: str, country_code: str = 'in'):
        """
        Initialize Google Custom Search API
        
        Args:
            api_key: Google Custom Search API key
            search_engine_id: Google Custom Search Engine ID
            country_code: Country code for search location (default: 'in' for India)
                         Examples: 'in' (India), 'us' (United States), 'uk' (United Kingdom)
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.country_code = country_code.lower()
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        print(f"[*] Google Custom Search initialized for country: {country_code.upper()}")
        
        # E-commerce domain patterns (generic only - no brand names)
        # Pure pattern-based detection - accepts ANY e-commerce site
        self.ecommerce_keywords = [
            'shop', 'store', 'buy', 'cart', 'checkout', 'ecommerce',
            'marketplace', 'retail', 'purchase', 'merchant', 'seller',
            'selling', 'vendor', 'trade', 'commerce', 'mall', 'boutique',
            'bazaar', 'mart', 'sale', 'deals', 'offer', 'discount',
            'outlet', 'warehouse', 'market'
        ]

        # Additional heuristics to widen detection to newer platforms
        self.ecommerce_path_keywords = [
            '/product', '/products', '/shop', '/store', '/item', '/items',
            '/buy', '/purchase', '/order', '/orders', '/cart', '/checkout',
            '/basket', '/bag', '/wishlist', '/compare', '/listing', '/listings',
            '/catalog', '/category', '/categories', '/deal', '/deals',
            '/sale', '/sales', '/collections'
        ]

        self.ecommerce_text_signals = [
            'shop', 'store', 'buy', 'sell', 'selling', 'purchase',
            'shop now', 'shop online', 'buy now', 'buy online', 'add to cart',
            'add-to-cart', 'in stock', 'free shipping', 'price', 'prices',
            'order', 'order now', 'checkout', 'cart', 'best price', 'sale', 'deal',
            'discount', 'ships', 'available now', 'secure checkout', '$', '₹',
            'rs.', 'usd', 'eur', 'gbp', 'aed'
        ]

        self.ecommerce_tld_suffixes = (
            '.store', '.shop', '.shopping', '.boutique', '.market', '.mall', '.sale'
        )

        self.queries_used = 0
    
    def search(self, query: str, start_index: int = 1, num_results: int = 10) -> Dict:
        """
        Perform a Google Custom Search
        
        Args:
            query: Search query string
            start_index: Starting index for pagination (default: 1)
            num_results: Number of results per page (default: 10, max: 10)
        """
        
        params = {
            'q': query,
            'key': self.api_key,
            'cx': self.search_engine_id,
            'start': start_index,
            'num': min(num_results, 10),
            'gl': self.country_code  # Geo location: search results for specific country
        }
        
        try:
            print(f"[*] Searching Google API: '{query}' (start: {start_index})")
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            self.queries_used += 1
            data = response.json()
            
            if 'error' in data:
                error_info = data['error']
                print(f"[✗] API Error: {error_info.get('message')}")
                return {}
            
            if 'queries' in data and 'request' in data['queries']:
                total_results = data['queries']['request'][0].get('totalResults', '0')
                print(
                    f"[✓] Google estimates ~{total_results} results "
                    f"(returning top {params['num']} in this call)"
                )
            
            return data
        
        except requests.exceptions.Timeout:
            print("[✗] Request timeout - Google API took too long")
            return {}
        except requests.exceptions.HTTPError as e:
            print(f"[✗] HTTP Error: {e.response.status_code}")
            if e.response.status_code == 403:
                print("    Quota exceeded! You've used all free queries for today.")
                print("    Free tier: 100 queries/day")
            return {}
        except Exception as e:
            print(f"[✗] Error: {e}")
            return {}
    
    def is_ecommerce_site(self, url: str, domain: str, title: str = "", snippet: str = "") -> bool:
        """
        Determine if the result points to an e-commerce site using heuristic signals.
        """

        url_lower = url.lower()
        domain_lower = domain.lower()
        text_blob = f"{title} {snippet}".lower()

        # TLD-based heuristic (e.g., example.store, example.shop)
        if domain_lower.endswith(self.ecommerce_tld_suffixes):
            return True

        # Domain keyword heuristic
        for keyword in self.ecommerce_keywords:
            if keyword in domain_lower:
                return True

        # URL path keyword heuristic
        for path_keyword in self.ecommerce_path_keywords:
            if path_keyword in url_lower:
                return True

        # Text-based heuristic (title + snippet)
        for signal in self.ecommerce_text_signals:
            if signal in text_blob:
                return True

        return False
    
    def extract_domain(self, url: str) -> str:
        """Extract clean domain from URL"""
        try:
            clean_url = url.split('?')[0].split('#')[0]
            parsed = urlparse(clean_url)
            netloc = parsed.netloc
            
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            return netloc
        except:
            return url
    
    def extract_links_from_response(self, response: Dict) -> List[Dict]:
        """Extract search results from API response"""
        
        results = []
        
        if 'items' not in response:
            return results
        
        for item in response['items']:
            try:
                result = {
                    'title': item.get('title', 'N/A'),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', ''),
                    'domain': self.extract_domain(item.get('link', ''))
                }
                results.append(result)
            except:
                continue
        
        return results
    
    def search_all_pages(self, product_name: str, max_results: int = 10, max_pages: int = 1) -> List[Dict]:
        """
        Search paginated Google Custom Search results for a product.
        Returns ALL collected results (no deduplication).

        Args:
            product_name: Product name to search for.
            max_results: Maximum number of results to collect (10 results per API call).
            max_pages: Upper bound on the number of pages (API requests) to fetch.
        """

        print(f"\n{'='*80}")
        print(f"SEARCHING GOOGLE API FOR: {product_name}")
        print(f"{'='*80}\n")

        query = f"{product_name} online shopping"
        all_results = []

        # Calculate pages while respecting API caps (10 results per request)
        num_pages = max(1, min((max_results + 9) // 10, max_pages, 10))
        estimated_results = min(max_results, num_pages * 10)

        print(f"[*] Fetching up to {num_pages} page(s) (targeting up to {estimated_results} results)...\n")

        for page in range(num_pages):
            results_remaining = max_results - len(all_results)
            if results_remaining <= 0:
                break

            start_index = page * 10 + 1
            response = self.search(query, start_index=start_index, num_results=results_remaining)

            if not response or 'items' not in response:
                print(f"[!] No more results or API error on page {page + 1}")
                break

            page_results = self.extract_links_from_response(response)
            all_results.extend(page_results)

            print(f"[✓] Page {page + 1}: Got {len(page_results)} results\n")

            # Respectful pacing when multiple requests are necessary
            if page < num_pages - 1 and results_remaining > len(page_results):
                time.sleep(0.5)

        print(f"[✓] Total results retrieved: {len(all_results)}\n")

        return all_results
    
    def extract_all_ecommerce_results(self, product_name: str, max_results: int = 10, max_pages: int = 1) -> List[Dict]:
        """
        Extract ALL e-commerce results (with all details)
        Returns list of all e-commerce results WITHOUT deduplication

        Args:
            product_name: Product name to search for.
            max_results: Maximum number of results to analyse.
            max_pages: Upper bound on API calls (pagination pages).

        Each result contains:
        - title: Page title
        - link: Full URL
        - snippet: Search snippet/description
        - display_link: Formatted domain
        - domain: Extracted domain
        """

        # Get all search results
        all_results = self.search_all_pages(
            product_name,
            max_results=max_results,
            max_pages=max_pages,
        )
        
        # Filter for e-commerce sites ONLY
        ecommerce_results = []
        
        print(f"{'='*80}")
        print(f"FILTERING E-COMMERCE WEBSITES")
        print(f"{'='*80}\n")
        
        for i, result in enumerate(all_results, 1):
            link = result['link']
            domain = result['domain']
            title = result['title']
            snippet = result['snippet']

            # Check if it's an e-commerce site
            if self.is_ecommerce_site(link, domain, title, snippet):
                ecommerce_results.append(result)
                print(f"{len(ecommerce_results)}. {domain}")
                print(f"   Title: {result['title'][:70]}...")
                print(f"   URL: {link[:70]}...\n")
        
        print(f"{'='*80}")
        print(f"RESULTS")
        print(f"{'='*80}")
        print(f"\n📊 Total E-Commerce Results Found: {len(ecommerce_results)}")
        print(f"📊 Total Search Results Scanned: {len(all_results)}")
        print(f"📊 API Queries Used: {self.queries_used}\n")
        
        return ecommerce_results
    
    def extract_unique_ecommerce_domains(self, product_name: str, max_results: int = 10, max_pages: int = 1) -> List[str]:
        """
        Extract unique e-commerce domains (old method)
        Returns only unique domain names
        """

        all_results = self.search_all_pages(
            product_name,
            max_results=max_results,
            max_pages=max_pages,
        )
        ecommerce_links = set()
        
        print(f"{'='*80}")
        print(f"FILTERING E-COMMERCE WEBSITES")
        print(f"{'='*80}\n")
        
        for i, result in enumerate(all_results, 1):
            link = result['link']
            domain = result['domain']
            title = result['title']
            snippet = result['snippet']

            if self.is_ecommerce_site(link, domain, title, snippet):
                ecommerce_links.add(domain)
                print(f"{len(ecommerce_links)}. {domain}")
                print(f"   Title: {result['title'][:70]}...\n")
        
        result_list = sorted(list(ecommerce_links))
        
        print(f"{'='*80}")
        print(f"RESULTS")
        print(f"{'='*80}")
        print(f"\n📊 Total Unique E-Commerce Sites Found: {len(result_list)}")
        print(f"📊 Total Search Results Scanned: {len(all_results)}")
        print(f"📊 API Queries Used: {self.queries_used}\n")
        
        return result_list


# ==============================================================================
# STORAGE & EXPORT FUNCTIONS
# ==============================================================================

def save_all_results_json(results: List[Dict], product_name: str, filename: str = None) -> str:
    """
    Save ALL results to JSON file
    
    Args:
        results: List of all e-commerce results
        product_name: Product name for reference
        filename: Custom filename (optional)
    
    Returns:
        str: Filename where data was saved
    """
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ecommerce_ALL_RESULTS_{product_name.replace(' ', '_')}_{timestamp}.json"
    
    data = {
        "product": product_name,
        "search_time": datetime.now().isoformat(),
        "total_results": len(results),
        "results": results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved ALL {len(results)} results to: {filename}\n")
    return filename


def save_all_results_csv(results: List[Dict], product_name: str, filename: str = None) -> str:
    """
    Save ALL results to CSV file
    
    Args:
        results: List of all e-commerce results
        product_name: Product name for reference
        filename: Custom filename (optional)
    
    Returns:
        str: Filename where data was saved
    """
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ecommerce_ALL_RESULTS_{product_name.replace(' ', '_')}_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Rank', 'Domain', 'Title', 'URL', 'Display Link', 'Snippet'])
        
        # All results
        for rank, result in enumerate(results, 1):
            writer.writerow([
                rank,
                result['domain'],
                result['title'],
                result['link'],
                result['display_link'],
                result['snippet']
            ])
    
    print(f"✓ Saved ALL {len(results)} results to: {filename}\n")
    return filename


def save_all_results_txt(results: List[Dict], product_name: str, filename: str = None) -> str:
    """
    Save ALL results to TXT file (human readable)
    
    Args:
        results: List of all e-commerce results
        product_name: Product name for reference
        filename: Custom filename (optional)
    
    Returns:
        str: Filename where data was saved
    """
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ecommerce_ALL_RESULTS_{product_name.replace(' ', '_')}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"E-Commerce Search Results\n")
        f.write(f"Product: {product_name}\n")
        f.write(f"Search Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Results: {len(results)}\n")
        f.write("="*80 + "\n\n")
        
        for rank, result in enumerate(results, 1):
            f.write(f"{rank}. {result['domain']}\n")
            f.write(f"   Title: {result['title']}\n")
            f.write(f"   URL: {result['link']}\n")
            f.write(f"   Snippet: {result['snippet']}\n")
            f.write(f"\n")
    
    print(f"✓ Saved ALL {len(results)} results to: {filename}\n")
    return filename


def save_all_results_html(results: List[Dict], product_name: str, filename: str = None) -> str:
    """
    Save ALL results to HTML file (viewable in browser)
    
    Args:
        results: List of all e-commerce results
        product_name: Product name for reference
        filename: Custom filename (optional)
    
    Returns:
        str: Filename where data was saved
    """
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ecommerce_ALL_RESULTS_{product_name.replace(' ', '_')}_{timestamp}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>E-Commerce Search Results - {product_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
            .result {{ background-color: white; margin: 10px 0; padding: 15px; border-left: 4px solid #3498db; }}
            .domain {{ font-weight: bold; color: #3498db; font-size: 16px; }}
            .title {{ margin: 5px 0; color: #2c3e50; }}
            .url {{ margin: 5px 0; color: #7f8c8d; font-size: 12px; word-break: break-all; }}
            .snippet {{ margin: 5px 0; color: #555; font-size: 13px; font-style: italic; }}
            .rank {{ background-color: #3498db; color: white; padding: 2px 6px; border-radius: 3px; margin-right: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>E-Commerce Search Results</h1>
            <p><strong>Product:</strong> {product_name}</p>
            <p><strong>Search Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total Results:</strong> {len(results)}</p>
        </div>
    """
    
    for rank, result in enumerate(results, 1):
        html_content += f"""
        <div class="result">
            <div><span class="rank">{rank}</span><span class="domain">{result['domain']}</span></div>
            <div class="title"><strong>Title:</strong> {result['title']}</div>
            <div class="url"><strong>URL:</strong> <a href="{result['link']}" target="_blank">{result['link']}</a></div>
            <div class="snippet"><strong>Snippet:</strong> {result['snippet']}</div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Saved ALL {len(results)} results to: {filename}\n")
    return filename


# ==============================================================================
# MAIN - SAVE ALL RESULTS
# ==============================================================================

if __name__ == "__main__":
    
    print(f"\n{'='*80}")
    print("E-COMMERCE LINK EXTRACTOR - SAVE ALL RESULTS")
    print(f"{'='*80}\n")
    
    if not API_KEY or not SEARCH_ENGINE_ID:
        print("[!] Please set API_KEY and SEARCH_ENGINE_ID at top of file!")
        exit()
    
    # Initialize searcher
    searcher = GoogleCustomSearchAPI(API_KEY, SEARCH_ENGINE_ID)
    
    # Get input
    product = input("Enter product name: ").strip()
    
    if not product:
        print("Please enter a product name!")
        exit()
    
    print()
    
    # Extract ALL results (not deduplicated)
    # Default to a single API request (10 results) to stay within quota per product
    all_results = searcher.extract_all_ecommerce_results(
        product,
        max_results=10,
        max_pages=1,
    )
    
    if not all_results:
        print("\n❌ No e-commerce results found!")
        exit()
    
    print(f"\n{'='*80}")
    print("SAVING RESULTS (JSON ONLY)")
    print(f"{'='*80}\n")
    
    # Save JSON only
    json_file = save_all_results_json(all_results, product)
    
    print(f"{'='*80}")
    print("DONE")
    print(f"{'='*80}\n")
    print(f"✅ Saved {len(all_results)} results to:")
    print(f"   {json_file}\n")