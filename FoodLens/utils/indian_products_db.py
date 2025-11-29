"""
Hardcoded database of common Indian food products for barcode lookup fallback
This helps when OpenFoodFacts doesn't have the product
"""

INDIAN_PRODUCTS = {
    # Balaji Products
    "8906010501570": {
        "product_name": "Balaji Crunchex Chilli Tadka",
        "brand": "Balaji",
        "category": "chips",
        "weight": "85g"
    },
    "8906010501587": {
        "product_name": "Balaji Crunchex Masala Masti",
        "brand": "Balaji",
        "category": "chips",
        "weight": "85g"
    },
    "8906010501594": {
        "product_name": "Balaji Crunchex Simply Salted",
        "brand": "Balaji",
        "category": "chips",
        "weight": "85g"
    },
}

def lookup_indian_product(barcode: str):
    """
    Lookup product in Indian products database
    Returns product info dict or None if not found
    """
    return INDIAN_PRODUCTS.get(barcode)
