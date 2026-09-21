import json
import os
from typing import List, Dict, Any

def search_vendors(product_name: str) -> List[Dict[str, Any]]:
    """
    Simulates searching a database for vendors offering a specific product.
    Returns a list of vendor raw dictionaries.
    """
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "vendors.json")
    if not os.path.exists(data_path):
        raise FileNotFoundError("Vendors database not found.")
        
    with open(data_path, "r") as f:
        vendors = json.load(f)
        
    matching_vendors = []
    # Simple keyword match
    search_term = product_name.lower()
    
    # Simple pluralization handling (e.g. laptop vs laptops)
    if search_term.endswith('s'):
        search_term = search_term[:-1]
        
    for vendor in vendors:
        # Check if they offer the product and are available
        offered_products = [p.lower() for p in vendor.get("products_offered", [])]
        
        # Check if search term is in any of the offered products
        if any(search_term in p or p in search_term for p in offered_products):
            if vendor.get("availability", False):
                matching_vendors.append(vendor)
                
    return matching_vendors
