"""
Search utilities for FoodLens AI
Optimized for web searching and product database queries
"""
import os
import json
import requests
from typing import List, Dict, Any, Union
from bs4 import BeautifulSoup
import re
import time

class SearchUtils:
    """Centralized search utilities class"""
    
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour
    
    def semantic_search(self, query: str) -> List[Union[str, Dict[str, Any]]]:
        """
        Wrapper for semantic search functionality
        """
        try:
            # Check cache first
            if query in self.cache:
                cached_result, timestamp = self.cache[query]
                if time.time() - timestamp < self.cache_timeout:
                    return cached_result
            
            # Perform search (placeholder for actual implementation)
            results = []
            
            # Cache results
            self.cache[query] = (results, time.time())
            return results
            
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []
    
    def search_product_databases(self, product_name: str, barcode: str = None) -> Dict[str, Any]:
        """
        Search OpenFoodFacts and other product databases
        """
        try:
            if barcode:
                url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            else:
                # Search by name
                search_url = "https://world.openfoodfacts.org/cgi/search.pl"
                params = {
                    "search_terms": product_name,
                    "search_simple": 1,
                    "action": "process",
                    "json": 1
                }
                response = requests.get(search_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("products"):
                        # Get the first product
                        barcode = data["products"][0]["code"]
                        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
                    else:
                        return {"status": 0, "product": None}
                else:
                    return {"status": 0, "product": None}
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    print(f"✅ Found product in OpenFoodFacts: {data.get('product', {}).get('product_name', 'Unknown')}")
                else:
                    print(f"❌ Barcode {barcode} exists but has no product data in OpenFoodFacts")
                return data
            else:
                print(f"❌ OpenFoodFacts API returned status code: {response.status_code}")
                return {"status": 0, "product": None}
                
        except Exception as e:
            print(f"❌ Product database search error: {e}")
            print(f"   URL attempted: {url if 'url' in locals() else 'N/A'}")
            return {"status": 0, "product": None}
    
    def get_curated_indian_alternatives(self, product_type: str, health_conditions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get curated alternatives from Indian market database
        """
        alternatives_db = {
            'biscuits': [
                {
                    "name": "Britannia NutriChoice Hi-Fiber Digestive",
                    "brand": "Britannia",
                    "health_score": 78,
                    "price": "₹30-50 per pack",
                    "where_to_buy": "All major supermarkets and online stores",
                    "health_benefits": "High fiber content, whole wheat, digestive health"
                },
                {
                    "name": "Parle Hide & Seek Fab Orange",
                    "brand": "Parle",
                    "health_score": 65,
                    "price": "₹20-35 per pack",
                    "where_to_buy": "Widely available in all stores",
                    "health_benefits": "Real orange flavor, no artificial colors"
                }
            ],
            'chocolate': [
                {
                    "name": "Amul Dark Chocolate 55%",
                    "brand": "Amul",
                    "health_score": 82,
                    "price": "₹80-120 per bar",
                    "where_to_buy": "Amul outlets, supermarkets",
                    "health_benefits": "Higher cocoa content, antioxidants, heart healthy"
                }
            ],
            'noodles': [
                {
                    "name": "Saffola Masala Oats",
                    "brand": "Saffola",
                    "health_score": 85,
                    "price": "₹15-25 per serving",
                    "where_to_buy": "All supermarkets, BigBasket, Amazon",
                    "health_benefits": "High fiber, protein rich, heart healthy oats"
                }
            ],
            'breakfast_cereal': [
                {
                    "name": "Soulfull Ragi Bites",
                    "brand": "Soulfull",
                    "health_score": 88,
                    "price": "₹180-220 per pack",
                    "where_to_buy": "Major supermarkets, online stores",
                    "health_benefits": "Made with millets, high protein, no artificial colors"
                },
                {
                    "name": "Kellogg's All-Bran Original",
                    "brand": "Kellogg's",
                    "health_score": 85,
                    "price": "₹350-400 per pack", 
                    "where_to_buy": "All major supermarkets",
                    "health_benefits": "Very high fiber content, helps digestion, fortified vitamins"
                }
            ],
            'ice_cream': [
                {
                    "name": "Amul Sugar Free Ice Cream",
                    "brand": "Amul",
                    "health_score": 72,
                    "price": "₹150-200 per pack",
                    "where_to_buy": "Amul outlets, major supermarkets",
                    "health_benefits": "No added sugar, diabetic friendly, lower calories"
                },
                {
                    "name": "NIC Natural Ice Cream",
                    "brand": "NIC",
                    "health_score": 68,
                    "price": "₹80-150 per serving",
                    "where_to_buy": "NIC outlets across India",
                    "health_benefits": "Made with natural ingredients, real fruit flavors"
                },
                {
                    "name": "Haagen-Dazs Low Fat Frozen Yogurt",
                    "brand": "Haagen-Dazs",
                    "health_score": 75,
                    "price": "₹350-450 per pack",
                    "where_to_buy": "Premium supermarkets, online delivery",
                    "health_benefits": "Lower fat content, probiotic benefits, premium quality"
                }
            ]
        }
        
        return alternatives_db.get(product_type, [])
    
    def get_health_consumption_advice(self, product_type: str, health_conditions: List[str]) -> str:
        """
        Get consumption advice based on product type and health conditions
        """
        advice_db = {
            'ice_cream': {
                'diabetes': 'Very small portion (25ml) maximum once per week',
                'hypertension': 'Small portion (50ml) maximum 2 times per week',
                'default': '1 small serving (50ml) 2-3 times per week'
            },
            'biscuits': {
                'diabetes': '1-2 biscuits maximum once per day',
                'default': '2-3 biscuits with tea/coffee'
            },
            'chocolate': {
                'diabetes': 'Very small piece (5-10g) occasionally',
                'default': '1 small piece (15-20g) daily is acceptable'
            }
        }
        
        product_advice = advice_db.get(product_type, {})
        
        # Check for specific health conditions
        for condition in health_conditions:
            if condition.lower() in product_advice:
                return product_advice[condition.lower()]
        
        return product_advice.get('default', 'Consume in moderation')

# Global instance
search_utils = SearchUtils()