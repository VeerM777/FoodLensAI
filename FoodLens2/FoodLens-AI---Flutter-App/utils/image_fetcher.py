"""
Product Image Fetcher
Fetches real product images from multiple sources
"""
import requests
import json
from typing import Optional
import time

class ProductImageFetcher:
    """Fetch product images from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FoodLens/1.0 (Nutrition App)'
        })
    
    def get_product_image(self, product_name: str, brand: str = "") -> str:
        """
        Get product image URL from multiple sources
        Returns the best available image URL or placeholder
        """
        # Try multiple sources in order of preference
        image_url = None
        
        # 1. Try OpenFoodFacts API (best for food products)
        image_url = self._fetch_from_openfoodfacts(product_name, brand)
        if image_url:
            return image_url
        
        # 2. Try Unsplash (high quality food images)
        image_url = self._fetch_from_unsplash(product_name, brand)
        if image_url:
            return image_url
        
        # 3. Fallback to a better placeholder with product name
        return self._generate_placeholder(product_name)
    
    def _fetch_from_openfoodfacts(self, product_name: str, brand: str = "") -> Optional[str]:
        """Fetch image from OpenFoodFacts database"""
        try:
            # Search for product in OpenFoodFacts
            search_term = f"{brand} {product_name}".strip()
            url = f"https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': search_term,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': 3
            }
            
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                for product in products:
                    # Get the first product with an image
                    if product.get('image_url'):
                        print(f"✅ Found image from OpenFoodFacts: {product.get('product_name')}")
                        return product['image_url']
                    elif product.get('image_front_url'):
                        return product['image_front_url']
                    elif product.get('image_small_url'):
                        return product['image_small_url']
        except Exception as e:
            print(f"⚠️ OpenFoodFacts image fetch failed: {e}")
        
        return None
    
    def _fetch_from_unsplash(self, product_name: str, brand: str = "") -> Optional[str]:
        """Fetch image from Unsplash (requires API key for production)"""
        try:
            # For demo purposes, use Unsplash Source (no API key required)
            # This provides random food images
            # In production, you'd use the full Unsplash API with your key
            
            # Clean product name for search
            search_term = product_name.lower().replace('&', 'and')
            
            # Common food categories for better image matching
            food_keywords = {
                'makhana': 'fox nuts',
                'khakhra': 'crackers',
                'chana': 'chickpeas',
                'namkeen': 'indian snacks',
                'oats': 'oatmeal',
                'muesli': 'granola'
            }
            
            for keyword, replacement in food_keywords.items():
                if keyword in search_term:
                    search_term = replacement
                    break
            
            # Use Unsplash Source for random images
            # Format: https://source.unsplash.com/200x200/?food,{search_term}
            image_url = f"https://source.unsplash.com/200x200/?food,{search_term.replace(' ', ',')}"
            
            # Verify the URL is accessible
            response = self.session.head(image_url, timeout=3, allow_redirects=True)
            if response.status_code == 200:
                print(f"✅ Using Unsplash image for: {product_name}")
                return image_url
        except Exception as e:
            print(f"⚠️ Unsplash image fetch failed: {e}")
        
        return None
    
    def _generate_placeholder(self, product_name: str) -> str:
        """Generate a descriptive placeholder image URL"""
        # Clean product name for URL
        clean_name = product_name.replace(' ', '+').replace('&', 'and')
        
        # Use a better placeholder service with Indian food context
        return f"https://ui-avatars.com/api/?name={clean_name}&size=200&background=4CAF50&color=fff&bold=true"

# Global instance
image_fetcher = ProductImageFetcher()
