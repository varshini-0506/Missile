# Universal E-Commerce Search URL Discovery Agent
# Enhanced with extensive selector patterns for any e-commerce website

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, parse_qs, urlencode
import time
import concurrent.futures


class UniversalSearchURLAgent:
    """
    Universal agent for discovering search URLs across any e-commerce platform.
    Uses extensive selector patterns to identify search inputs and extract URL patterns.
    """
    
    def __init__(self):
        """Initialize with comprehensive selector patterns"""
        self.comprehensive_selectors = self._build_comprehensive_selectors()
    
    def _build_comprehensive_selectors(self):
        """
        Build an extensive collection of CSS and XPath selectors
        Returns dictionary organized by selector type
        """
        return {
            # ==================== INPUT TYPE SELECTORS ====================
            'by_input_type': [
                # Search input types
                'input[type="search"]',
                'input[type="text"]',
                'input[type="tel"]',
                'input[type="email"]',
                'input[type="url"]',
            ],
            
            # ==================== NAME ATTRIBUTE SELECTORS ====================
            'by_name_attribute': [
                # Common search field names
                'input[name="q"]',
                'input[name="query"]',
                'input[name="search"]',
                'input[name="keyword"]',
                'input[name="keywords"]',
                'input[name="s"]',
                'input[name="search_query"]',
                'input[name="searchTerm"]',
                'input[name="searchQuery"]',
                'input[name="searchBox"]',
                'input[name="search-field"]',
                'input[name="search_field"]',
                'input[name="searchInput"]',
                'input[name="searchVal"]',
                'input[name="searchValue"]',
                'input[name="searchProduct"]',
                'input[name="product_search"]',
                'input[name="productSearch"]',
                'input[name="field-keywords"]',
                'input[name="k"]',
                'input[name="find"]',
                'input[name="filter"]',
                'input[name="searchstring"]',
                'input[name="search_string"]',
                'input[name="search-query"]',
                'input[name="search-term"]',
                'input[name="term"]',
                'input[name="terms"]',
                'input[name="siteSearch"]',
                'input[name="site-search"]',
                'input[name="site_search"]',
            ],
            
            # ==================== ID ATTRIBUTE SELECTORS ====================
            'by_id_attribute': [
                # Common search field IDs
                'input#search',
                'input#searchbox',
                'input#search-box',
                'input#search_box',
                'input#searchBar',
                'input#search-bar',
                'input#search_bar',
                'input#searchInput',
                'input#search-input',
                'input#search_input',
                'input#searchField',
                'input#search-field',
                'input#search_field',
                'input#query',
                'input#q',
                'input#s',
                'input#search_query',
                'input#searchQuery',
                'input#keyword',
                'input#keywords',
                'input#site-search',
                'input#site_search',
                'input#siteSearch',
                'input#inputValEnter',
                'input#twotabsearchtextbox',  # Amazon
                'input#gh-ac',  # eBay
                'input#searchVal',
                'input#search-product',
                'input#product-search',
                'input#productSearch',
                'input#global-search',
                'input#globalSearch',
                'input#main-search',
                'input#mainSearch',
                'input#header-search',
                'input#headerSearch',
                'input#top-search',
                'input#topSearch',
            ],
            
            # ==================== CLASS ATTRIBUTE SELECTORS ====================
            'by_class_attribute': [
                # Common search field classes
                'input.search',
                'input.searchbox',
                'input.search-box',
                'input.search_box',
                'input.searchBar',
                'input.search-bar',
                'input.search_bar',
                'input.searchInput',
                'input.search-input',
                'input.search_input',
                'input.searchField',
                'input.search-field',
                'input.search_field',
                'input.search-query',
                'input.search_query',
                'input.searchQuery',
                'input.site-search',
                'input.siteSearch',
                'input.global-search',
                'input.globalSearch',
                'input.header-search',
                'input.headerSearch',
                'input.desktop-searchBar',
                'input.mobile-searchBar',
                'input.Pke_EE',  # Flipkart
                'input._3704LK',  # Flipkart alternative
                'input.nav-input',
                'input.nav-search-input',
                'input.form-control',
                'input.form-input',
                'input.react-autosuggest__input',
                'input.autosuggest-input',
                'input.autocomplete-input',
            ],
            
            # ==================== PLACEHOLDER ATTRIBUTE SELECTORS ====================
            'by_placeholder': [
                # English
                'input[placeholder*="Search" i]',
                'input[placeholder*="search" i]',
                'input[placeholder*="Find" i]',
                'input[placeholder*="find" i]',
                'input[placeholder*="Look for" i]',
                'input[placeholder*="looking for" i]',
                'input[placeholder*="What are you" i]',
                'input[placeholder*="Product" i]',
                'input[placeholder*="product" i]',
                'input[placeholder*="Item" i]',
                'input[placeholder*="item" i]',
                'input[placeholder*="Brand" i]',
                'input[placeholder*="Enter" i]',
                'input[placeholder*="Type" i]',
                'input[placeholder*="Query" i]',
                'input[placeholder*="Keyword" i]',
                # Common phrases
                'input[placeholder*="Search for products" i]',
                'input[placeholder*="Search products" i]',
                'input[placeholder*="Search for items" i]',
                'input[placeholder*="Find products" i]',
                'input[placeholder*="What are you looking for" i]',
                'input[placeholder*="I\'m shopping for" i]',
                'input[placeholder*="Try searching" i]',
            ],
            
            # ==================== TITLE ATTRIBUTE SELECTORS ====================
            'by_title': [
                'input[title*="Search" i]',
                'input[title*="Find" i]',
                'input[title*="Query" i]',
                'input[title*="Product" i]',
            ],
            
            # ==================== ARIA ATTRIBUTE SELECTORS ====================
            'by_aria': [
                'input[aria-label*="Search" i]',
                'input[aria-label*="search" i]',
                'input[aria-label*="Find" i]',
                'input[aria-label*="Query" i]',
                'input[aria-label*="Product" i]',
                'input[role="searchbox"]',
                'input[role="search"]',
                '[role="searchbox"]',
                '[role="search"] input',
            ],
            
            # ==================== DATA ATTRIBUTE SELECTORS ====================
            'by_data_attributes': [
                'input[data-search]',
                'input[data-searchbox]',
                'input[data-search-input]',
                'input[data-type="search"]',
                'input[data-role="search"]',
                'input[data-component="search"]',
                'input[data-testid*="search" i]',
                'input[data-test*="search" i]',
                'input[data-cy*="search" i]',
            ],
            
            # ==================== FORM ACTION SELECTORS ====================
            'by_form_action': [
                'form[action*="search"] input[type="text"]',
                'form[action*="search"] input[type="search"]',
                'form[action*="/search"] input',
                'form[action*="query"] input',
                'form[action*="find"] input',
                'form[class*="search" i] input',
                'form[id*="search" i] input',
                'form[role="search"] input',
            ],
            
            # ==================== CONTAINER-BASED SELECTORS ====================
            'by_container': [
                'div[class*="search" i] input',
                'div[id*="search" i] input',
                'div[role="search"] input',
                'header input[type="text"]',
                'header input[type="search"]',
                'nav input[type="text"]',
                'nav input[type="search"]',
                '.header input',
                '.navbar input',
                '.nav-bar input',
                '.top-bar input',
                '.search-container input',
                '.search-wrapper input',
                '.search-box input',
                '.searchbox input',
                '.search-form input',
                '.search-area input',
            ],
            
            # ==================== AUTOCOMPLETE ATTRIBUTE SELECTORS ====================
            'by_autocomplete': [
                'input[autocomplete="search"]',
                'input[autocomplete*="search" i]',
            ],
            
            # ==================== XPATH SELECTORS ====================
            'xpath_selectors': [
                # By placeholder
                "//input[contains(@placeholder, 'Search')]",
                "//input[contains(@placeholder, 'search')]",
                "//input[contains(@placeholder, 'Find')]",
                "//input[contains(@placeholder, 'find')]",
                "//input[contains(@placeholder, 'Product')]",
                "//input[contains(@placeholder, 'product')]",
                "//input[contains(@placeholder, 'What are you')]",
                
                # By aria-label
                "//input[contains(@aria-label, 'Search')]",
                "//input[contains(@aria-label, 'search')]",
                "//input[contains(@aria-label, 'Find')]",
                
                # By title
                "//input[contains(@title, 'Search')]",
                "//input[contains(@title, 'search')]",
                
                # By name
                "//input[@name='q']",
                "//input[@name='query']",
                "//input[@name='search']",
                "//input[@name='keyword']",
                "//input[@name='s']",
                
                # By class
                "//input[contains(@class, 'search')]",
                "//input[contains(@class, 'Search')]",
                
                # By id
                "//input[contains(@id, 'search')]",
                "//input[contains(@id, 'Search')]",
                
                # By type
                "//input[@type='search']",
                
                # Form-based
                "//form[contains(@action, 'search')]//input[@type='text']",
                "//form[contains(@action, 'search')]//input[@type='search']",
                "//form[contains(@class, 'search')]//input",
                "//form[@role='search']//input",
                
                # Role-based
                "//*[@role='searchbox']",
                "//*[@role='search']//input",
                
                # Container-based
                "//div[contains(@class, 'search')]//input[@type='text']",
                "//div[contains(@class, 'search')]//input[@type='search']",
                "//header//input[@type='text']",
                "//header//input[@type='search']",
                "//nav//input[@type='text']",
                "//nav//input[@type='search']",
                
                # Visible text inputs (generic fallback)
                "//input[@type='text' and not(@hidden)]",
                "//input[@type='search' and not(@hidden)]",
            ],
        }
    
    def discover_search_url(self, site_url, test_query="iphone"):
        """
        Discover search URL for any e-commerce website
        
        Args:
            site_url: The website URL to analyze
            test_query: Test search term (default: "iphone")
        
        Returns:
            dict: Search URL pattern and metadata
        """
        driver = None
        try:
            driver = self._setup_fast_driver()
            
            print(f"[Universal Agent] Starting discovery for: {site_url}")
            
            # Navigate to site
            driver.get(site_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Try to handle common popups/overlays
            self._handle_popups(driver)
            
            # Enhanced page load wait
            self._wait_for_dynamic_content(driver)
            
            # Find search input using comprehensive selectors
            search_input = self._find_search_input_universal(driver, site_url)
            
            if not search_input:
                return {
                    "error": "Search input not found after trying all selector patterns",
                    "site_url": site_url
                }
            
            # Store initial URL
            initial_url = driver.current_url
            
            # Perform search
            search_input.clear()
            search_input.send_keys(test_query)
            time.sleep(0.5)
            
            # Submit search
            try:
                search_button = self._find_search_button_universal(driver)
                if search_button:
                    search_button.click()
                else:
                    search_input.send_keys(Keys.RETURN)
            except:
                search_input.send_keys(Keys.RETURN)
            
            # Wait for URL change or results
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.current_url != initial_url
                )
            except TimeoutException:
                pass
            
            time.sleep(2)
            
            # Get and parse search URL
            search_url = driver.current_url
            result = self._parse_url_structure(search_url, test_query)
            result["site_url"] = site_url
            result["site_name"] = urlparse(site_url).netloc
            
            return result
            
        except Exception as e:
            return {
                "error": f"{str(e)}",
                "site_url": site_url
            }
        finally:
            if driver:
                driver.quit()
    
    def _find_search_input_universal(self, driver, site_url):
        """
        Universal search input finder using comprehensive selector patterns
        Tries selectors in order of specificity
        """
        print(f"[Universal Agent] Attempting to find search input...")
        
        # Counter for debugging
        attempt = 0
        
        # 1. Try specific name attributes (most reliable)
        print(f"[Universal Agent] Trying name attribute selectors...")
        for selector in self.comprehensive_selectors['by_name_attribute']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with name selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 2. Try specific ID attributes
        print(f"[Universal Agent] Trying ID attribute selectors...")
        for selector in self.comprehensive_selectors['by_id_attribute']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with ID selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 3. Try class attributes
        print(f"[Universal Agent] Trying class attribute selectors...")
        for selector in self.comprehensive_selectors['by_class_attribute']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with class selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 4. Try placeholder attributes
        print(f"[Universal Agent] Trying placeholder attribute selectors...")
        for selector in self.comprehensive_selectors['by_placeholder']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with placeholder selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 5. Try ARIA attributes
        print(f"[Universal Agent] Trying ARIA attribute selectors...")
        for selector in self.comprehensive_selectors['by_aria']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with ARIA selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 6. Try title attributes
        print(f"[Universal Agent] Trying title attribute selectors...")
        for selector in self.comprehensive_selectors['by_title']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with title selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 7. Try data attributes
        print(f"[Universal Agent] Trying data attribute selectors...")
        for selector in self.comprehensive_selectors['by_data_attributes']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with data attribute selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 8. Try form action-based selectors
        print(f"[Universal Agent] Trying form action selectors...")
        for selector in self.comprehensive_selectors['by_form_action']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with form action selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 9. Try container-based selectors
        print(f"[Universal Agent] Trying container-based selectors...")
        for selector in self.comprehensive_selectors['by_container']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with container selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 10. Try input type selectors (more generic)
        print(f"[Universal Agent] Trying input type selectors...")
        for selector in self.comprehensive_selectors['by_input_type']:
            try:
                attempt += 1
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with input type selector (attempt {attempt}): {selector}")
                        return element
            except:
                continue
        
        # 11. Try XPath selectors
        print(f"[Universal Agent] Trying XPath selectors...")
        for xpath in self.comprehensive_selectors['xpath_selectors']:
            try:
                attempt += 1
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found with XPath selector (attempt {attempt}): {xpath}")
                        return element
            except:
                continue
        
        # 12. Last resort: try clicking search icons/buttons to reveal input
        print(f"[Universal Agent] Trying to trigger search UI...")
        search_trigger_result = self._try_search_triggers(driver)
        if search_trigger_result:
            return search_trigger_result
        
        print(f"[Universal Agent] ✗ Could not find search input after {attempt} attempts")
        return None
    
    def _try_search_triggers(self, driver):
        """
        Try clicking elements that might reveal a search input
        (e.g., search icons, mobile menu buttons)
        """
        trigger_selectors = [
            # Search icon/button selectors
            'button[class*="search" i]',
            'button[aria-label*="search" i]',
            'button[title*="search" i]',
            'a[class*="search" i]',
            'a[aria-label*="search" i]',
            'div[class*="search" i][role="button"]',
            'span[class*="search" i]',
            'i[class*="search" i]',
            '[data-testid*="search" i]',
            # Icon classes
            '.fa-search',
            '.icon-search',
            '.search-icon',
            # SVG icons
            'svg[class*="search" i]',
            'svg[aria-label*="search" i]',
            # Mobile menu
            'button[class*="menu" i]',
            'button[class*="hamburger" i]',
            'button[aria-label*="menu" i]',
            '[aria-label*="navigation" i]',
        ]
        
        for selector in trigger_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements[:3]:  # Try first 3 matches
                    if element.is_displayed():
                        print(f"[Universal Agent] Clicking search trigger: {selector}")
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(2)
                        
                        # Check if input appeared
                        for input_selector in ['input[type="search"]', 'input[type="text"]']:
                            try:
                                new_inputs = driver.find_elements(By.CSS_SELECTOR, input_selector)
                                for inp in new_inputs:
                                    if inp.is_displayed() and inp.is_enabled():
                                        print(f"[Universal Agent] ✓ Found input after trigger")
                                        return inp
                            except:
                                continue
            except:
                continue
        
        return None
    
    def _find_search_button_universal(self, driver):
        """Universal search button finder"""
        button_selectors = [
            # Specific buttons
            'button[type="submit"]',
            'input[type="submit"]',
            'button[aria-label*="search" i]',
            'button[title*="search" i]',
            'button[class*="search" i]',
            'button#nav-search-submit-button',  # Amazon
            # Form submit buttons
            'form[action*="search"] button[type="submit"]',
            'form[role="search"] button[type="submit"]',
            # Icon buttons
            'button .fa-search',
            'button .icon-search',
            'button svg[class*="search" i]',
        ]
        
        for selector in button_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
        
        return None
    
    def _wait_for_dynamic_content(self, driver):
        """Wait for dynamic content and try to trigger it"""
        try:
            # Wait for any input to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input, button, a'))
            )
            
            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, 100);")
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Hover over header to trigger dropdowns
            try:
                header_selectors = ['header', 'nav', '.header', '.navbar', '.top-bar']
                for selector in header_selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element.is_displayed():
                            driver.execute_script(
                                "arguments[0].dispatchEvent(new Event('mouseover'));", 
                                element
                            )
                            time.sleep(0.5)
                            break
                    except:
                        continue
            except:
                pass
            
            time.sleep(2)
            
        except Exception as e:
            print(f"[Universal Agent] Dynamic content wait: {e}")
    
    def _handle_popups(self, driver):
        """Try to close common popups/overlays"""
        popup_close_selectors = [
            'button[aria-label*="close" i]',
            'button[class*="close" i]',
            'button[class*="dismiss" i]',
            '[class*="modal"] button',
            '[class*="popup"] button',
            '[class*="overlay"] button',
            '.close-button',
            '.dismiss-button',
            'button[title*="close" i]',
        ]
        
        for selector in popup_close_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements[:1]:  # Try first match only
                    if element.is_displayed():
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.5)
                        return
            except:
                continue
    
    def _parse_url_structure(self, url, test_query):
        """Parse URL structure and extract search pattern"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Find search parameter
        search_param = None
        for key, values in query_params.items():
            if test_query.lower() in str(values).lower():
                search_param = key
                break
        
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Create URL template
        if search_param:
            # Build template with essential params
            url_template = f"{base_url}?{search_param}={{query}}"
            
            # Add other params as optional
            other_params = {k: v for k, v in query_params.items() if k != search_param}
            if other_params:
                optional_params = "&".join([f"{k}={v[0]}" for k, v in other_params.items()])
                url_template_full = f"{url_template}&{optional_params}"
            else:
                url_template_full = url_template
        else:
            url_template = base_url
            url_template_full = url
        
        return {
            "success": True,
            "platform": parsed.netloc,
            "full_url": url,
            "base_url": base_url,
            "search_parameter": search_param,
            "url_template": url_template,
            "url_template_full": url_template_full,
            "query_params": query_params,
            "example": f"{base_url}?{search_param}={{your_query}}" if search_param else base_url,
            "test_query": test_query,
        }
    
    def _setup_fast_driver(self):
        """Setup Chrome with optimizations"""
        chrome_options = Options()
        
        # Headless mode
        chrome_options.add_argument('--headless=new')
        
        # Performance optimizations
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Anti-detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Use webdriver-manager if available, otherwise try system Chrome
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                print(f"[!] WebDriver Manager failed, trying system Chrome: {e}")
                driver = webdriver.Chrome(options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.set_page_load_timeout(30)
        
        return driver
    
    def discover_multiple_sites(self, sites, test_query="iphone", max_workers=2):
        """
        Discover search URLs from multiple sites in parallel
        
        Args:
            sites: Dictionary of {"name": "url"} or list of URLs
            test_query: Search term to use
            max_workers: Number of parallel browsers
        
        Returns:
            dict: Results for each site
        """
        # Handle both dict and list inputs
        if isinstance(sites, list):
            sites_dict = {url: url for url in sites}
        else:
            sites_dict = sites
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_site = {
                executor.submit(self.discover_search_url, url, test_query): name 
                for name, url in sites_dict.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_site):
                site_name = future_to_site[future]
                try:
                    result = future.result()
                    results[site_name] = result
                    if "error" not in result:
                        print(f"✓ {site_name} completed successfully")
                    else:
                        print(f"✗ {site_name} failed: {result.get('error')}")
                except Exception as e:
                    results[site_name] = {"error": str(e)}
                    print(f"✗ {site_name} failed with exception: {e}")
        
        return results


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UNIVERSAL E-COMMERCE SEARCH URL DISCOVERY AGENT")
    print("=" * 80)
    print("Enhanced with 200+ selector patterns to work with ANY e-commerce site")
    print("=" * 80)
    
    # Example 1: Single site discovery
    print("\n### EXAMPLE 1: Single Site Discovery ###\n")
    
    agent = UniversalSearchURLAgent()
    
    # Test with any e-commerce URL
    test_url = "https://www.amazon.in/"
    print(f"Testing with: {test_url}")
    
    result = agent.discover_search_url(test_url, test_query="fashion")
    
    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)
    
    if "error" not in result:
        print(f"\n✓ SUCCESS!")
        print(f"  Platform: {result.get('platform')}")
        print(f"  Search Parameter: {result.get('search_parameter')}")
        print(f"  Base URL: {result.get('base_url')}")
        print(f"  Simple Template: {result.get('url_template')}")
        print(f"  Full Template: {result.get('url_template_full')}")
        print(f"  Example Usage: {result.get('example')}")
        print(f"  All Query Params: {result.get('query_params')}")
    else:
        print(f"\n✗ FAILED")
        print(f"  Error: {result.get('error')}")
    

    