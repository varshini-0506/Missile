"""
Input Data Handler for Product Pipeline

Handles dictionary input format:
{
    "category_name": ["product1", "product2", ...],
    "another_category": ["prod1", "prod2", ...]
}

Processes and saves:
1. Categories (if not exist, create them)
2. Products with category_id references
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Supabase imports
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("[!] Warning: supabase-py not installed. Install with: pip install supabase")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://whfjofihihlhctizchmj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_KEY:
    print("[!] Warning: SUPABASE_KEY not set. Database operations will be skipped.")


class InputDataHandler:
    """
    Handles input data in format: {"category": ["product1", "product2", ...]}
    Saves categories and products to database with proper relationships
    """
    
    def __init__(self):
        """Initialize Supabase connection"""
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
    
    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """
        Get category_id if exists, otherwise create category and return id
        
        Args:
            category_name: Name of the category
            
        Returns:
            category_id or None if failed
        """
        if not self.supabase:
            print(f"[!] Supabase not available - cannot process category: {category_name}")
            return None
        
        try:
            # Check if category exists
            response = self.supabase.table("categories").select("category_id").eq(
                "name", category_name
            ).execute()
            
            if response.data and len(response.data) > 0:
                category_id = response.data[0]["category_id"]
                print(f"[✓] Category '{category_name}' already exists (ID: {category_id})")
                return category_id
            
            # Create new category with latest_input timestamp
            current_time = datetime.now().isoformat()
            response = self.supabase.table("categories").insert({
                "name": category_name,
                "latest_input": current_time,
                "latest_updated": current_time
            }).execute()
            
            if response.data and len(response.data) > 0:
                category_id = response.data[0]["category_id"]
                print(f"[✓] Created new category '{category_name}' (ID: {category_id})")
                return category_id
            else:
                print(f"[✗] Failed to create category '{category_name}'")
                return None
                
        except Exception as e:
            print(f"[✗] Error processing category '{category_name}': {str(e)}")
            return None
    
    def save_product(self, product_name: str, category_id: int) -> bool:
        """
        Save product to database with category_id
        
        Args:
            product_name: Name of the product
            category_id: ID of the category
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            # Check if product already exists for this category
            response = self.supabase.table("products").select("product_id").eq(
                "name", product_name
            ).eq("category_id", category_id).execute()
            
            if response.data and len(response.data) > 0:
                print(f"  [→] Product '{product_name}' already exists in this category")
                return True
            
            # Insert new product
            response = self.supabase.table("products").insert({
                "name": product_name,
                "category_id": category_id
            }).execute()
            
            if response.data:
                # Update category's latest_input timestamp when product is added
                self.update_category_latest_input(category_id)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"  [✗] Error saving product '{product_name}': {str(e)}")
            return False
    
    def process_input_data(self, data: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Process input dictionary and save to database
        
        Args:
            data: Dictionary in format {"category": ["product1", "product2", ...]}
            
        Returns:
            Dictionary with processing results
        """
        if not self.supabase:
            return {
                "success": False,
                "error": "Supabase not available"
            }
        
        print(f"\n{'='*80}")
        print("PROCESSING INPUT DATA")
        print(f"{'='*80}\n")
        
        results = {
            "success": True,
            "categories_processed": 0,
            "categories_created": 0,
            "categories_existing": 0,
            "products_saved": 0,
            "products_failed": 0,
            "category_details": {}
        }
        
        for category_name, products in data.items():
            print(f"\n📁 Processing Category: {category_name}")
            print(f"   Products: {len(products)}")
            
            # Get or create category
            category_id = self.get_or_create_category(category_name)
            
            if not category_id:
                print(f"[✗] Skipping category '{category_name}' - failed to get/create")
                results["products_failed"] += len(products)
                continue
            
            results["categories_processed"] += 1
            
            # Update latest_input timestamp when category receives products
            self.update_category_latest_input(category_id)
            
            if category_id:
                # Track if this was a new category
                response = self.supabase.table("categories").select("category_id").eq(
                    "name", category_name
                ).limit(1).execute()
                
                # This is a simple check - if we just created it, it's new
                # In practice, we'd track this better, but for now we'll count existing vs new
                results["categories_existing"] += 1  # Will adjust after
        
            # Process products for this category
            category_products_saved = 0
            category_products_failed = 0
            
            for product_name in products:
                if not product_name or not product_name.strip():
                    continue
                
                product_name_clean = product_name.strip()
                
                if self.save_product(product_name_clean, category_id):
                    category_products_saved += 1
                    results["products_saved"] += 1
                else:
                    category_products_failed += 1
                    results["products_failed"] += 1
            
            # Store category details
            results["category_details"][category_name] = {
                "category_id": category_id,
                "products_count": len(products),
                "products_saved": category_products_saved,
                "products_failed": category_products_failed
            }
            
            print(f"   [✓] Saved {category_products_saved}/{len(products)} products")
        
        # Summary
        print(f"\n{'='*80}")
        print("PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Categories processed: {results['categories_processed']}")
        print(f"Products saved: {results['products_saved']}")
        print(f"Products failed: {results['products_failed']}")
        print(f"{'='*80}\n")
        
        return results
    
    def load_from_json_file(self, file_path: str) -> Dict[str, List[str]]:
        """
        Load input data from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with category-product mapping
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate format
            if not isinstance(data, dict):
                raise ValueError("JSON must contain a dictionary/object")
            
            # Validate each entry is a list
            for category, products in data.items():
                if not isinstance(products, list):
                    raise ValueError(f"Category '{category}' must have a list of products")
            
            return data
            
        except FileNotFoundError:
            print(f"[✗] File not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"[✗] Invalid JSON in file: {e}")
            return {}
        except Exception as e:
            print(f"[✗] Error loading file: {e}")
            return {}
    
    def save_from_dict(self, data: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Convenience method to process and save data
        
        Args:
            data: Dictionary in format {"category": ["product1", "product2", ...]}
            
        Returns:
            Processing results
        """
        return self.process_input_data(data)
    
    def get_category_id(self, category_name: str) -> Optional[int]:
        """
        Get category_id for a given category name
        
        Args:
            category_name: Name of the category
            
        Returns:
            category_id or None if not found
        """
        if not self.supabase:
            return None
        
        try:
            response = self.supabase.table("categories").select("category_id").eq(
                "name", category_name
            ).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]["category_id"]
            return None
            
        except Exception as e:
            print(f"[✗] Error getting category_id: {e}")
            return None
    
    def update_category_latest_input(self, category_id: int) -> bool:
        """
        Update category's latest_input timestamp when products are added
        
        Args:
            category_id: ID of the category
            
        Returns:
            True if updated successfully
        """
        if not self.supabase:
            return False
        
        try:
            current_time = datetime.now().isoformat()
            response = self.supabase.table("categories").update({
                "latest_input": current_time
            }).eq("category_id", category_id).execute()
            
            return response.data is not None
        except Exception as e:
            print(f"[✗] Error updating category latest_input: {e}")
            return False
    
    def update_category_latest_updated(self, category_id: int) -> bool:
        """
        Update category's latest_updated timestamp (for category modifications)
        
        Args:
            category_id: ID of the category
            
        Returns:
            True if updated successfully
        """
        if not self.supabase:
            return False
        
        try:
            current_time = datetime.now().isoformat()
            response = self.supabase.table("categories").update({
                "latest_updated": current_time
            }).eq("category_id", category_id).execute()
            
            return response.data is not None
        except Exception as e:
            print(f"[✗] Error updating category latest_updated: {e}")
            return False
    
    def get_products_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """
        Get all products for a given category_id
        
        Args:
            category_id: ID of the category
            
        Returns:
            List of products
        """
        if not self.supabase:
            return []
        
        try:
            response = self.supabase.table("products").select("*").eq(
                "category_id", category_id
            ).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"[✗] Error getting products: {e}")
            return []


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print(f"\n{'='*80}")
    print("INPUT DATA HANDLER")
    print(f"{'='*80}\n")
    
    # Example input data
    example_data = {
        "Electronics": ["laptop", "smartphone", "headphones", "tablet"],
        "Fashion": ["shirt", "jeans", "shoes", "watch"],
        "Home & Kitchen": ["microwave", "blender", "kettle"]
    }
    
    # Initialize handler
    handler = InputDataHandler()
    
    # Option 1: Load from JSON file
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"[*] Loading data from file: {file_path}\n")
        data = handler.load_from_json_file(file_path)
        
        if data:
            handler.process_input_data(data)
        else:
            print("[✗] Failed to load data from file")
    
    # Option 2: Use example data
    else:
        print("[*] Using example data (provide JSON file path as argument to use file)")
        print("\nExample format:")
        print(json.dumps(example_data, indent=2))
        print("\nPress Enter to process example data, or Ctrl+C to cancel...")
        
        try:
            input()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)
        
        handler.process_input_data(example_data)

