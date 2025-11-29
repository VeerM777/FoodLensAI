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
    def __init__(self):
        """
        Initialize the SearchUtils class with minimal static data
        Designed to prioritize real-time searches for a market-ready system
        """
        # No predefined category database
        # Will rely on real-time search for product categorization
        self.category_db = {}
        
        # Just a minimal set of very common items to handle basic cases
        # when real-time search fails or for quick response
        self.common_categories = {
            # Core items that are unmistakable in their category
            'coca-cola': {'category': 'Carbonated beverages', 'type': 'beverage'},
            'pepsi': {'category': 'Carbonated beverages', 'type': 'beverage'},
            'nutella': {'category': 'Chocolate spreads', 'type': 'spread'}
        }
        
        # Very minimal brand mapping only for most recognized brands
        # Real-time search will be the primary way to determine product categories
        self.brand_categories = {
            'coca-cola': {'category': 'Carbonated beverages', 'type': 'beverage'},
            'pepsi': {'category': 'Carbonated beverages', 'type': 'beverage'},
            'ferrero': {'category': 'Chocolate spreads', 'type': 'spread'}
        }

        # Minimal alternatives database with just a few core healthy alternatives
        # Most alternatives will be generated through real-time search
        self.alternatives_db = {
            'beverage': [
                {
                    "name": "Coconut Water",
                    "brand": "Natural",
                    "health_score": 92,
                    "health_benefits": "Natural electrolytes, low sugar, good hydration",
                    "key_benefits": "Natural hydration, no added sugar"
                },
                {
                    "name": "Green Tea",
                    "brand": "Organic",
                    "health_score": 90,
                    "health_benefits": "Rich in antioxidants, improves metabolism",
                    "key_benefits": "Antioxidants, zero sugar, metabolic benefits"
                }
            ],
            'spread': [
                {
                    "name": "Natural Peanut Butter",
                    "brand": "Organic",
                    "health_score": 85,
                    "health_benefits": "High protein, healthy fats, no added sugar",
                    "key_benefits": "Protein source, natural ingredients"
                }
            ]
        }
                {
                    "name": "Pintola Organic Peanut Butter",
                    "brand": "Pintola",
                    "health_score": 86,
                    "price": "₹300-350 per jar",
                    "where_to_buy": "Health food stores, online marketplaces",
                    "health_benefits": "High protein, healthy fats, no added sugar or preservatives, organic ingredients",
                    "key_benefits": "High protein, natural ingredients, no added sugar"
                },
                {
                    "name": "True Elements Almond Butter",
                    "brand": "True Elements",
                    "health_score": 88,
                    "price": "₹500-600 per jar",
                    "where_to_buy": "Health stores, e-commerce platforms",
                    "health_benefits": "High in vitamin E, good fats, no added sugar, pure almond goodness",
                    "key_benefits": "Healthy fats, vitamin E, no additives" 
                },
                {
                    "name": "St. Dalfour Fruit Spread",
                    "brand": "St. Dalfour",
                    "health_score": 82,
                    "price": "₹350-450 per jar",
                    "where_to_buy": "Premium supermarkets, imported food sections",
                    "health_benefits": "100% fruit, no added sugar, no preservatives or artificial flavors",
                    "key_benefits": "No added sugar, pure fruit, no additives"
                },
                {
                    "name": "Asitis Nutrition Dark Chocolate Protein Spread",
                    "brand": "Asitis Nutrition",
                    "health_score": 78,
                    "price": "₹500-600 per jar",
                    "where_to_buy": "Fitness stores, online sports nutrition sites",
                    "health_benefits": "High protein content, reduced sugar, added whey protein for fitness enthusiasts",
                    "key_benefits": "High protein, lower sugar than regular spreads"
                },
                {
                    "name": "Alpino Natural Peanut Butter",
                    "brand": "Alpino",
                    "health_score": 85,
                    "price": "₹280-350 per jar",
                    "where_to_buy": "Major retail stores, online platforms",
                    "health_benefits": "High protein, healthy fats, zero trans fat, natural ingredients",
                    "key_benefits": "High protein, natural ingredients, no hydrogenated oils"
                }
            ],
            'beverage': [
                {
                    "name": "Coconut Water",
                    "brand": "Tender Fresh",
                    "health_score": 92,
                    "price": "₹40-60 per bottle",
                    "where_to_buy": "Supermarkets, local stores, online retailers",
                    "health_benefits": "Natural electrolytes, rich in potassium, zero added sugar, hydrating, low calorie",
                    "key_benefits": "Natural electrolytes, zero added sugar"
                },
                {
                    "name": "Fresh Lime Water",
                    "brand": "Homemade",
                    "health_score": 90,
                    "price": "₹10-20 per glass",
                    "where_to_buy": "Restaurants, food stalls, make at home",
                    "health_benefits": "Vitamin C rich, aids digestion, detoxifying, natural hydration, minimal calories",
                    "key_benefits": "Natural vitamin C, aids digestion"
                },
                {
                    "name": "Raw Pressery Mixed Fruit Juice",
                    "brand": "Raw Pressery",
                    "health_score": 85,
                    "price": "₹80-100 per bottle",
                    "where_to_buy": "Premium supermarkets, online grocers",
                    "health_benefits": "Cold pressed, no preservatives, no added sugar, rich in vitamins, antioxidants",
                    "key_benefits": "Cold pressed, no preservatives or added sugar"
                },
                {
                    "name": "Paper Boat Coconut Water",
                    "brand": "Paper Boat",
                    "health_score": 88,
                    "price": "₹50-70 per tetra pack",
                    "where_to_buy": "Supermarkets, convenience stores, online",
                    "health_benefits": "Natural electrolytes, no preservatives, low calorie, no added flavors",
                    "key_benefits": "Natural hydration, no preservatives"
                },
                {
                    "name": "B-Natural Mixed Fruit No Sugar",
                    "brand": "B-Natural",
                    "health_score": 82,
                    "price": "₹75-90 per carton",
                    "where_to_buy": "Major retail stores, online platforms",
                    "health_benefits": "No added sugar, preservative-free, good source of vitamins, lower calories than sodas",
                    "key_benefits": "No added sugar, preservative-free"
                }
            ],
            'ice_cream': [
                {
                    "name": "Amul Sugar Free Ice Cream",
                    "brand": "Amul",
                    "health_score": 82,
                    "price": "₹220-250 per pack",
                    "where_to_buy": "Amul outlets, supermarkets",
                    "health_benefits": "No added sugar, diabetic friendly, lower calories",
                    "key_benefits": "Zero added sugar, suitable for diabetics"
                },
                {
                    "name": "NIC Natural Ice Cream",
                    "brand": "NIC",
                    "health_score": 78,
                    "price": "₹80-100 per scoop",
                    "where_to_buy": "NIC outlets, food delivery apps",
                    "health_benefits": "Made with natural ingredients, real fruit flavors, no artificial additives",
                    "key_benefits": "Natural ingredients, no artificial colors or flavors"
                },
                {
                    "name": "Haagen-Dazs Low Fat Frozen Yogurt",
                    "brand": "Haagen-Dazs",
                    "health_score": 85,
                    "price": "₹250-300 per cup",
                    "where_to_buy": "Premium stores, Haagen-Dazs outlets",
                    "health_benefits": "Lower fat content, probiotic benefits, premium quality",
                    "key_benefits": "Probiotics for gut health, lower fat content"
                },
                {
                    "name": "Mother Dairy Fruit Yogurt",
                    "brand": "Mother Dairy",
                    "health_score": 88,
                    "price": "₹30-40 per cup",
                    "where_to_buy": "Mother Dairy outlets, local stores",
                    "health_benefits": "High protein, probiotics, natural fruit, low fat",
                    "key_benefits": "High protein, probiotic enriched"
                },
                {
                    "name": "Epigamia Greek Yogurt",
                    "brand": "Epigamia",
                    "health_score": 90,
                    "price": "₹40-50 per cup",
                    "where_to_buy": "Premium stores, online grocers",
                    "health_benefits": "High protein, zero added sugar, gut-friendly probiotics",
                    "key_benefits": "High protein, zero added sugar"
                }
            ],
            'dairy': [
                {
                    "name": "Amul Sugar Free Ice Cream",
                    "brand": "Amul",
                    "health_score": 82,
                    "price": "₹220-250 per pack",
                    "where_to_buy": "Amul outlets, supermarkets",
                    "health_benefits": "No added sugar, diabetic friendly, lower calories",
                    "key_benefits": "Zero added sugar, suitable for diabetics"
                },
                {
                    "name": "NIC Natural Ice Cream",
                    "brand": "NIC",
                    "health_score": 78,
                    "price": "₹80-100 per scoop",
                    "where_to_buy": "NIC outlets, food delivery apps",
                    "health_benefits": "Made with natural ingredients, real fruit flavors, no artificial additives",
                    "key_benefits": "Natural ingredients, no artificial colors or flavors"
                },
                {
                    "name": "Epigamia Greek Yogurt",
                    "brand": "Epigamia",
                    "health_score": 90,
                    "price": "₹40-50 per cup",
                    "where_to_buy": "Premium stores, online grocers",
                    "health_benefits": "High protein, zero added sugar, gut-friendly probiotics",
                    "key_benefits": "High protein, zero added sugar"
                },
                {
                    "name": "Go Protein Power Milk",
                    "brand": "Go",
                    "health_score": 85,
                    "price": "₹80-100 per liter",
                    "where_to_buy": "Supermarkets, local stores",
                    "health_benefits": "High protein content, good for muscle growth and recovery",
                    "key_benefits": "30% more protein than regular milk" 
                },
                {
                    "name": "Amul Slim Trim Milk",
                    "brand": "Amul",
                    "health_score": 83,
                    "price": "₹60-70 per liter",
                    "where_to_buy": "Local stores, supermarkets",
                    "health_benefits": "Low fat milk with all essential nutrients preserved",
                    "key_benefits": "Low fat with full calcium benefits"
                }
            ],
            'noodles': [
                {
                    "name": "Saffola Masala Oats",
                    "brand": "Saffola",
                    "health_score": 85,
                    "key_benefits": "High fiber, protein rich, whole grain oats base",
                    "price": "₹15-25 per serving",
                    "where_to_buy": "All supermarkets, online stores",
                    "health_benefits": "High fiber content, protein rich, whole grain based",
                    "fssai_status": "FSSAI compliant with A grade"
                },
                {
                    "name": "Slurrp Farm Millet Noodles",
                    "brand": "Slurrp Farm",
                    "health_score": 88,
                    "key_benefits": "Made with millets, high fiber, natural ingredients",
                    "price": "₹45-50 per pack",
                    "where_to_buy": "Health food stores, online",
                    "health_benefits": "High in fiber and protein, made with healthy millets",
                    "fssai_status": "FSSAI certified health food"
                },
                {
                    "name": "Patanjali Atta Noodles",
                    "brand": "Patanjali",
                    "health_score": 75,
                    "key_benefits": "Made with whole wheat, lower sodium content",
                    "price": "₹15-20 per pack",
                    "where_to_buy": "Patanjali stores, general stores",
                    "health_benefits": "Made with whole wheat flour, no artificial colors",
                    "fssai_status": "FSSAI compliant"
                },
                {
                    "name": "Top Ramen Whole Grain Noodles",
                    "brand": "Nissin",
                    "health_score": 78,
                    "key_benefits": "Made with whole wheat, lower sodium content",
                    "price": "₹25-30 per pack",
                    "where_to_buy": "Supermarkets, online retailers",
                    "health_benefits": "Whole wheat base, reduced sodium",
                    "fssai_status": "FSSAI certified"
                },
                {
                    "name": "Sunfeast Yippee Quik Meals Atta Noodles",
                    "brand": "Sunfeast",
                    "health_score": 72,
                    "key_benefits": "Whole wheat base, no added MSG",
                    "price": "₹20-25 per pack",
                    "where_to_buy": "Local stores, online platforms",
                    "health_benefits": "Made with whole wheat flour, no MSG",
                    "fssai_status": "FSSAI compliant"
                }
            ],
            'bread': [
                {
                    "name": "Theobroma Multigrain Bread",
                    "brand": "Theobroma",
                    "health_score": 88,
                    "price": "₹120-150 per loaf",
                    "where_to_buy": "Theobroma outlets, food delivery apps",
                    "health_benefits": "High fiber, multiple whole grains, no preservatives",
                    "fssai_status": "FSSAI certified premium bakery"
                },
                {
                    "name": "Modern Whole Wheat Bread",
                    "brand": "Modern",
                    "health_score": 85,
                    "price": "₹45-55 per pack",
                    "where_to_buy": "Local stores, supermarkets",
                    "health_benefits": "100% whole wheat, good source of fiber, no artificial preservatives",
                    "fssai_status": "FSSAI compliant with A grade"
                },
                {
                    "name": "Britannia Brown Bread",
                    "brand": "Britannia",
                    "health_score": 82,
                    "price": "₹40-50 per pack",
                    "where_to_buy": "All major stores",
                    "health_benefits": "Whole wheat flour, high fiber, fortified with vitamins",
                    "fssai_status": "FSSAI certified, meets all standards"
                },
                {
                    "name": "English Oven Protein Bread",
                    "brand": "English Oven",
                    "health_score": 86,
                    "price": "₹65-75 per pack",
                    "where_to_buy": "Premium stores, online delivery",
                    "health_benefits": "High protein, added seeds, omega-3 rich",
                    "fssai_status": "FSSAI compliant premium product"
                },
                {
                    "name": "Nature's Own Multigrain Sourdough",
                    "brand": "Nature's Own",
                    "health_score": 90,
                    "price": "₹180-200 per loaf",
                    "where_to_buy": "Specialty bakeries, organic stores",
                    "health_benefits": "Natural fermentation, probiotic properties, high fiber, low gluten",
                    "fssai_status": "FSSAI certified artisanal product"
                }
            ],
            'cereal': [
                {
                    "name": "Soulfull Ragi Bites",
                    "brand": "Soulfull",
                    "health_score": 88,
                    "price": "₹180-220",
                    "where_to_buy": "Major supermarkets",
                    "health_benefits": "Made with millets, high protein",
                    "fssai_status": "FSSAI certified health food"
                }
            ],
            'biscuits': [
                {
                    "name": "Britannia NutriChoice Hi-Fiber Digestive",
                    "brand": "Britannia",
                    "health_score": 78,
                    "price": "₹30-50 per pack",
                    "where_to_buy": "All major supermarkets",
                    "health_benefits": "High fiber content (4.5g/100g), whole wheat, low sugar",
                    "fssai_status": "FSSAI compliant with A grade"
                }
            ]
        }

    def search_product_category(self, product_name: str) -> Dict[str, str]:
        """
        Search and determine accurate product category and type using multiple methods:
        1. Static database matching
        2. Keyword detection
        3. Real-time search and analysis (if the above fail)
        """
        print(f"🔍 Determining category for: {product_name}")
        
        # Clean and lowercase product name
        clean_name = product_name.lower().strip()
        
        # Direct match
        for key, value in self.category_db.items():
            if key in clean_name:
                print(f"✅ Found direct match in category_db: {value['type']}")
                return value
                
        # Try to match by brand names
        for brand, category in self.brand_categories.items():
            if brand in clean_name:
                print(f"✅ Found brand match: {brand} → {category['type']}")
                return category
                
        # Try to detect bread products by keywords
        bread_keywords = ['bread', 'pain', 'loaf', 'baguette', 'roti', 'pav']
        for keyword in bread_keywords:
            if keyword in clean_name:
                print(f"✅ Found bread keyword match: {keyword}")
                return {'category': 'Breads and Bakery', 'type': 'bread'}
        
        # Try to detect beverage products by keywords
        beverage_keywords = ['cola', 'soda', 'drink', 'juice', 'water', 'pet', 'bottle', 'can', 'ltr', 'litre', 'ml']
        for keyword in beverage_keywords:
            if keyword in clean_name:
                print(f"✅ Found beverage keyword match: {keyword}")
                return {'category': 'Carbonated beverages', 'type': 'beverage'}
                
        # Special case for common brands/products
        common_beverages = ['coca', 'coke', 'pepsi', 'sprite', 'fanta', 'limca', 'maaza', 'frooti', 'slice']
        for beverage in common_beverages:
            if beverage in clean_name:
                print(f"✅ Found beverage brand match: {beverage}")
                return {'category': 'Carbonated beverages', 'type': 'beverage'}
                
        # If no match found, try real-time category determination
        print("⚠️ No static matches found, trying real-time category search")
        real_time_category = self.search_real_time_category(product_name)
        if real_time_category:
            print(f"✅ Found category via real-time search: {real_time_category['type']}")
            return real_time_category
                
        # Default category if no match found
        print("⚠️ No category found, using default: processed_food")
        return {'category': 'Processed foods', 'type': 'processed_food'}
        
    def search_real_time_category(self, product_name: str) -> Dict[str, str]:
        """
        Perform real-time search to determine product category
        """
        try:
            print(f"🌐 Performing real-time category search for: {product_name}")
            
            # Handle known products directly for more accurate categorization
            known_products_map = {
                "nutella": {"category": "Spreads", "type": "spread"},
                "ferrero": {"category": "Spreads", "type": "spread"},
                "coca-cola": {"category": "Carbonated beverages", "type": "beverage"},
                "coke": {"category": "Carbonated beverages", "type": "beverage"},
                "pepsi": {"category": "Carbonated beverages", "type": "beverage"},
                "sprite": {"category": "Carbonated beverages", "type": "beverage"},
                "fanta": {"category": "Carbonated beverages", "type": "beverage"},
                "skippy": {"category": "Spreads", "type": "spread"},
                "jif": {"category": "Spreads", "type": "spread"},
                "smuckers": {"category": "Spreads", "type": "spread"},
                "nutella": {"category": "Spreads", "type": "spread"},
                "jam": {"category": "Spreads", "type": "spread"},
                "jelly": {"category": "Spreads", "type": "spread"},
                "peanut butter": {"category": "Spreads", "type": "spread"},
                "almond butter": {"category": "Spreads", "type": "spread"},
                "honey": {"category": "Spreads", "type": "spread"}
            }
            
            # Check if this is a known product
            product_lower = product_name.lower()
            for known_term, category_info in known_products_map.items():
                if known_term in product_lower:
                    print(f"✅ Direct match found for {product_name}: {category_info['category']}")
                    return category_info
            
            # Run two different search queries for more comprehensive results
            search_queries = [
                f"what type of food is {product_name}",
                f"what category of food product is {product_name}"
            ]
            
            all_content = ""
            for search_query in search_queries:
                search_results = self.run_search(search_query, "product_category")
                if search_results:
                    all_content += " ".join([result.get('content', '') for result in search_results])
            
            if not all_content:
                print("❌ No search results found")
                return None
                
            # Define category keywords to look for
            category_mappings = {
                'beverage': ['beverage', 'drink', 'soda', 'cola', 'soft drink', 'juice', 'water'],
                'bread': ['bread', 'bakery', 'loaf', 'bun', 'baguette', 'roll', 'toast'],
                'cereal': ['cereal', 'breakfast', 'granola', 'muesli', 'oats', 'flakes'],
                'chocolate': ['chocolate', 'candy', 'sweet', 'confectionery', 'cocoa'],
                'dairy': ['dairy', 'milk', 'cheese', 'yogurt', 'curd', 'butter'],
                'biscuits': ['biscuit', 'cookie', 'cracker', 'wafer'],
                'ice_cream': ['ice cream', 'frozen dessert', 'frozen yogurt', 'gelato'],
                'noodles': ['noodle', 'pasta', 'ramen', 'instant noodle'],
                'snack': ['snack', 'chips', 'crisps', 'nachos', 'popcorn'],
                'spread': ['spread', 'nutella', 'jam', 'jelly', 'peanut butter', 'hazelnut', 'chocolate spread', 
                          'nut butter', 'margarine', 'breakfast spread', 'toast spread', 'sandwich spread']
            }
            
            # Look for clear category indicators first
            for category, keywords in category_mappings.items():
                for keyword in keywords:
                    indicator_patterns = [
                        f"{product_name} is a(n)? {keyword}",
                        f"{product_name} is a type of {keyword}",
                        f"{product_name}, a(n)? {keyword}",
                        f"{product_name} falls under the category of {keyword}",
                        f"{product_name} belongs to the {keyword} category"
                    ]
                    
                    for pattern in indicator_patterns:
                        if re.search(pattern, all_content, re.IGNORECASE):
                            print(f"✅ Found direct category indicator: {category} from pattern '{pattern}'")
                            
                            # Map category to proper format
                            if category == 'beverage':
                                return {'category': 'Carbonated beverages', 'type': 'beverage'}
                            elif category == 'bread':
                                return {'category': 'Breads and Bakery', 'type': 'bread'}
                            elif category == 'chocolate':
                                return {'category': 'Chocolate confectionery', 'type': 'chocolate'}
                            elif category == 'dairy':
                                return {'category': 'Dairy products', 'type': 'dairy'}
                            elif category == 'spread':
                                return {'category': 'Spreads', 'type': 'spread'}
                            else:
                                return {'category': category.capitalize(), 'type': category}
            
            # If no direct indicators, count occurrences of category keywords
            category_counts = {}
            for category, keywords in category_mappings.items():
                count = 0
                for keyword in keywords:
                    count += len(re.findall(r'\b' + keyword + r'\b', all_content.lower()))
                category_counts[category] = count
                
            # Additional check specifically for spreads
            if "spread" in product_name.lower() or "nutella" in product_name.lower() or "butter" in product_name.lower() or "jam" in product_name.lower():
                category_counts['spread'] = category_counts.get('spread', 0) + 10  # Give extra weight
                
            # Get the category with the highest count
            if category_counts:
                best_category = max(category_counts.items(), key=lambda x: x[1])
                if best_category[1] > 0:  # If we found at least one match
                    print(f"✅ Found category through keyword count: {best_category[0]} with {best_category[1]} mentions")
                    
                    # Map category to proper format
                    if best_category[0] == 'beverage':
                        return {'category': 'Carbonated beverages', 'type': 'beverage'}
                    elif best_category[0] == 'bread':
                        return {'category': 'Breads and Bakery', 'type': 'bread'}
                    elif best_category[0] == 'chocolate':
                        return {'category': 'Chocolate confectionery', 'type': 'chocolate'}
                    elif best_category[0] == 'dairy':
                        return {'category': 'Dairy products', 'type': 'dairy'}
                    elif best_category[0] == 'spread':
                        return {'category': 'Spreads', 'type': 'spread'}
                    else:
                        return {'category': best_category[0].capitalize(), 'type': best_category[0]}
            
            return None
            
        except Exception as e:
            print(f"❌ Error in real-time category search: {e}")
            return None

    def get_alternatives(self, product_type: str, product_name: str = "") -> List[Dict[str, Any]]:
        """
        Get alternatives for a product - prioritizing real-time search for better results
        Returns appropriate alternatives based on product type and name
        """
        print(f"🔍 Finding alternatives for: {product_name} (type: {product_type})")
        
        # Check if product name is empty
        if not product_name:
            print("⚠️ Product name is empty, using only product type")
        
        # Special handling for spreads like Nutella
        if product_type == "spread" or (product_name and any(spread in product_name.lower() for spread in ["nutella", "jam", "jelly", "butter", "spread"])):
            print(f"🥜 Handling spread-specific alternatives for {product_name}")
            
            # Always try real-time search first for spreads
            spread_search_results = self.search_real_time_alternatives(product_name, "spread")
            if spread_search_results and len(spread_search_results) >= 2:
                print(f"✅ Found {len(spread_search_results)} spread alternatives via real-time search")
                return spread_search_results
                
            # If real-time search didn't return enough results, use database
            spread_alternatives = self.alternatives_db.get("spread", [])
            if len(spread_alternatives) >= 2:
                print(f"✅ Found {len(spread_alternatives)} spread alternatives in database")
                return spread_alternatives
        
        # Special handling for beverages to ensure they get beverage alternatives
        if product_type == "beverage" or (product_name and any(beverage in product_name.lower() for beverage in ["coca", "coke", "pepsi", "sprite", "fanta"])):
            print(f"🥤 Handling beverage-specific alternatives for {product_name}")
            
            # Always try real-time search first for beverages
            beverage_search_results = self.search_real_time_alternatives(product_name, "beverage")
            if beverage_search_results and len(beverage_search_results) >= 2:
                print(f"✅ Found {len(beverage_search_results)} beverage alternatives via real-time search")
                return beverage_search_results
                
            # If real-time search didn't return enough results, use database
            beverage_alternatives = self.alternatives_db.get("beverage", [])
            if len(beverage_alternatives) >= 2:
                print(f"✅ Found {len(beverage_alternatives)} beverage alternatives in database")
                return beverage_alternatives
        
        # For other products, prioritize real-time search if we have a product name
        search_alternatives = []
        if product_name:
            print(f"🔎 Trying real-time search for alternatives to {product_name}")
            search_alternatives = self.search_real_time_alternatives(product_name, product_type)
            
            # If we found good alternatives through search, return them
            if search_alternatives and len(search_alternatives) >= 3:
                print(f"🌐 Found {len(search_alternatives)} alternatives via real-time search")
                return search_alternatives
        
        # Then try to get from database if real-time search didn't provide enough alternatives
        db_alternatives = self.alternatives_db.get(product_type, [])
        
        # If we have enough alternatives in DB, return them
        if len(db_alternatives) >= 3:
            print(f"📚 Found {len(db_alternatives)} alternatives in database for {product_type}")
            return db_alternatives
            
        # If we don't have enough from database but have some from search, use those
        if search_alternatives and len(search_alternatives) > 0:
            print(f"🌐 Using {len(search_alternatives)} alternatives from search (not enough in DB)")
            return search_alternatives
            
        # If specific product type didn't yield results, try using a more generic category
        if product_type not in ["beverage", "spread", "dairy", "snack", "cereal"]:
            generic_alternatives = self.alternatives_db.get("healthy_foods", [])
            if generic_alternatives:
                print(f"📚 Using generic healthy food alternatives as fallback")
                return generic_alternatives
            
        # If nothing found, return what we have in DB or empty list
        print("⚠️ No good alternatives found, returning what's available")
        return db_alternatives if db_alternatives else []
        
    def search_real_time_alternatives(self, product_name: str, product_type: str) -> List[Dict[str, Any]]:
        """
        Perform real-time search for alternatives based on product name and type
        Enhanced with more robust alternative detection and extraction
        """
        print(f"🔍 Real-time search for alternatives to {product_name} ({product_type})")
        
        # Prepare multiple search queries for better results
        search_queries = []
        
        # Build type-specific search queries
        if product_type == "spread":
            # Special handling for spread products like Nutella
            if "nutella" in product_name.lower():
                search_queries.append(f"healthy alternatives to nutella chocolate spread")
                search_queries.append(f"nutritious chocolate spread alternatives")
                search_queries.append(f"healthy nut butters instead of nutella")
                search_queries.append(f"low sugar spreads alternatives to nutella")
                search_queries.append(f"natural spread alternatives to nutella")
            elif "jam" in product_name.lower() or "jelly" in product_name.lower():
                search_queries.append(f"healthy alternatives to {product_name}")
                search_queries.append(f"nutritious jam alternatives")
                search_queries.append(f"low sugar jam spreads")
                search_queries.append(f"natural fruit spread alternatives")
            elif "butter" in product_name.lower():
                search_queries.append(f"healthy alternatives to {product_name}")
                search_queries.append(f"natural nut butter options")
                search_queries.append(f"nutritious butter alternatives")
                search_queries.append(f"organic spread alternatives to {product_name}")
            else:
                search_queries.append(f"healthy alternatives to {product_name}")
                search_queries.append(f"nutritious spread options")
                search_queries.append(f"low sugar spread alternatives")
        elif product_type == "beverage":
            if "coca" in product_name.lower() or "coke" in product_name.lower() or "pepsi" in product_name.lower():
                search_queries.append(f"healthy alternatives to {product_name} drink beverage")
                search_queries.append(f"healthy drink alternatives to soda")
                search_queries.append(f"alternatives to soft drinks healthy options")
                search_queries.append(f"best healthy drinks instead of soda")
            else:
                search_queries.append(f"healthy alternatives to {product_name} drink")
                search_queries.append(f"healthy {product_type} alternatives to {product_name}")
        elif product_type == "bread":
            search_queries.append(f"healthy bread alternatives to {product_name}")
            search_queries.append(f"whole grain bread alternatives")
        elif product_type == "cereal":
            search_queries.append(f"healthy cereal alternatives to {product_name}")
            search_queries.append(f"nutritious breakfast options instead of {product_type}")
        elif product_type == "chocolate":
            search_queries.append(f"healthy chocolate alternatives to {product_name}")
            search_queries.append(f"low sugar chocolate options")
        elif product_type == "biscuits":
            search_queries.append(f"healthy biscuit alternatives to {product_name}")
            search_queries.append(f"nutritious cookies low sugar")
        else:
            # Generic search queries
            search_queries.append(f"healthy alternative to {product_name} {product_type}")
            search_queries.append(f"healthy {product_type} options india")
            
        # Add location context for India
        search_queries.append(f"healthy {product_type} alternatives india")
        
        # Run multiple searches and combine results
        all_results = []
        for query in search_queries:
            search_results = self.run_search(query, product_type)
            all_results.extend(search_results)
            
        # Deduplicate by URL
        unique_urls = set()
        unique_results = []
        for result in all_results:
            if result.get('url') not in unique_urls:
                unique_urls.add(result.get('url'))
                unique_results.append(result)
        
        # Parse results into alternatives
        alternatives = []
        
        for result in unique_results:
            content = result.get('content', '').lower()
            title = result.get('title', '').lower()
            
            # Try to extract product names and details using multiple methods
            product_names = self._extract_product_names(content, title)
            
            # Add names from title if they match pattern
            title_matches = re.findall(r'(\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3}\b)', result.get('title', ''))
            if title_matches:
                for match in title_matches:
                    if len(match) > 3 and match.lower() not in [p.lower() for p in product_names]:
                        if product_type.lower() in match.lower() or "healthy" in match.lower():
                            continue  # Skip general terms
                        product_names.append(match)
            
                # Process each found product
                for product in product_names:
                    # Skip if too short or matches original product
                    if len(product) <= 3:
                        continue
                        
                    if product_name.lower() in product.lower():
                        continue
                    
                    # Skip if product name is too generic or common
                    if not self._is_valid_product_name(product):
                        print(f"⚠️ Skipping invalid product name: {product}")
                        continue
                        
                    # Skip if already in alternatives
                    if any(alt.get('name', '').lower() == product.lower() for alt in alternatives):
                        continue
                    
                    # Calculate a health score based on content
                    health_score = self._calculate_health_score(content, product)
                    
                    # Only include products that have a good health score
                    if health_score >= 70:
                        # Extract product details
                        brand = self._extract_brand(product, content)
                        
                        # Ensure we have a proper brand name
                        if not brand or brand.lower() in ["health", "healthy", "alternative", "nutritious", "natural"]:
                            # Try to get brand from first word of product if it's capitalized
                            if " " in product and product.split()[0][0].isupper():
                                brand = product.split()[0]
                            else:
                                brand = "Premium Choice"  # Better default than "Health Alternative"
                                
                        price = self._extract_price(content, product)
                        availability = self._extract_availability(content)
                        health_benefits = self._extract_health_benefits(content, product)
                        key_benefits = self._extract_key_benefits(content, product)
                        
                        # Create alternative object
                        alternative = {
                            "name": product,
                            "brand": brand,
                            "health_score": health_score,
                            "price": price,
                            "where_to_buy": availability,
                            "health_benefits": health_benefits,
                            "key_benefits": key_benefits
                        }
                        
                        print(f"✅ Found valid alternative: {product} (brand: {brand})")
                        alternatives.append(alternative)        # Add type-specific alternatives for beverages
        if product_type == "beverage" or (product_name and any(beverage in product_name.lower() for beverage in ["coca", "coke", "pepsi", "sprite", "fanta", "soda", "soft drink"])):
            print(f"🥤 Adding reliable beverage alternatives for {product_name}")
            common_beverage_alternatives = [
                {
                    "name": "Coconut Water",
                    "brand": "Tender Fresh",
                    "health_score": 92,
                    "price": "₹40-60 per bottle",
                    "where_to_buy": "Supermarkets, local stores",
                    "health_benefits": "Natural electrolytes, rich in potassium, zero added sugar, hydrating, low calorie",
                    "key_benefits": "Natural electrolytes, zero added sugar"
                },
                {
                    "name": "Fresh Lime Soda",
                    "brand": "Homemade",
                    "health_score": 90,
                    "price": "₹20-30 per glass",
                    "where_to_buy": "Restaurants, make at home",
                    "health_benefits": "Vitamin C rich, aids digestion, detoxifying, natural hydration with minimal calories",
                    "key_benefits": "Natural vitamin C, aids digestion"
                },
                {
                    "name": "Raw Pressery Mixed Fruit Juice",
                    "brand": "Raw Pressery",
                    "health_score": 85,
                    "price": "₹80-100 per bottle",
                    "where_to_buy": "Premium supermarkets, online grocers",
                    "health_benefits": "Cold pressed, no preservatives, no added sugar, rich in vitamins and antioxidants",
                    "key_benefits": "Cold pressed, no preservatives or added sugar"
                },
                {
                    "name": "Paper Boat Coconut Water",
                    "brand": "Paper Boat",
                    "health_score": 88,
                    "price": "₹50-70 per tetra pack",
                    "where_to_buy": "Supermarkets, convenience stores, online",
                    "health_benefits": "Natural electrolytes, no preservatives, low calorie, no added flavors",
                    "key_benefits": "Natural hydration, no preservatives"
                },
                {
                    "name": "Sparkling Water",
                    "brand": "Schweppes",
                    "health_score": 88,
                    "price": "₹70-90 per bottle",
                    "where_to_buy": "Premium stores, online",
                    "health_benefits": "Zero calories, zero sugar, natural alternative to soda",
                    "key_benefits": "Zero calories, natural carbonated refreshment"
                }
            ]
            
            # Add these only if alternatives list is empty or has few items
            if len(alternatives) < 3:
                print(f"🥤 Using reliable beverage alternatives since search found only {len(alternatives)} options")
                alternatives = common_beverage_alternatives
            # Or if we already have some alternatives, add these if they're not duplicates
            else:
                for alt in common_beverage_alternatives:
                    if not any(existing.get('name', '').lower() == alt['name'].lower() for existing in alternatives):
                        alternatives.append(alt)
                    
        # If we found more than 5 alternatives, just return the top 5 by health score
        if len(alternatives) > 5:
            alternatives.sort(key=lambda x: x.get('health_score', 0), reverse=True)
            return alternatives[:5]
            
        return alternatives
        
    def _extract_product_names(self, content: str, title: str) -> List[str]:
        """
        Extract potential product names from content with improved filtering
        to avoid generic terms being extracted as product names
        """
        products = []
        
        # First look for products mentioned in comparison context
        comparison_patterns = [
            r'([A-Z][a-zA-Z\s\-\']+) instead of ([A-Z][a-zA-Z\s\-\']+)',
            r'([A-Z][a-zA-Z\s\-\']+) as an alternative to ([A-Z][a-zA-Z\s\-\']+)',
            r'replace ([A-Z][a-zA-Z\s\-\']+) with ([A-Z][a-zA-Z\s\-\']+)',
            r'substitute ([A-Z][a-zA-Z\s\-\']+) with ([A-Z][a-zA-Z\s\-\']+)',
            r'([A-Z][a-zA-Z\s\-\']+) is similar to ([A-Z][a-zA-Z\s\-\']+)'
        ]
        
        for pattern in comparison_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    for product in match:
                        if self._is_valid_product_name(product.strip()):
                            products.append(product.strip())
                else:
                    if self._is_valid_product_name(match.strip()):
                        products.append(match.strip())
        
        # Look for products in recommendation contexts
        recommendation_patterns = [
            r'([A-Z][a-zA-Z\s\-\']+) is a healthy alternative',
            r'try ([A-Z][a-zA-Z\s\-\']+) instead',
            r'([A-Z][a-zA-Z\s\-\']+) offers a healthier option',
            r'([A-Z][a-zA-Z\s\-\']+) is recommended',
            r'([A-Z][a-zA-Z\s\-\']+) is a better choice',
            r'switch to ([A-Z][a-zA-Z\s\-\']+)',
            r'choose ([A-Z][a-zA-Z\s\-\']+) instead',
            r'([A-Z][a-zA-Z\s\-\']+) contains less sugar',
            r'([A-Z][a-zA-Z\s\-\']+) has better nutritional value',
            r'healthier alternatives? like ([A-Z][a-zA-Z\s\-\']+)',
            r'consider ([A-Z][a-zA-Z\s\-\']+) as a substitute'
        ]
        
        for pattern in recommendation_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                product_name = match.strip()
                if self._is_valid_product_name(product_name):
                    products.append(product_name)
            
        # Extract branded product names (typically have Brand followed by Product)
        branded_patterns = [
            r'([A-Z][a-zA-Z]+\'s [A-Za-z\s\-]+)',  # Brand's Product
            r'([A-Z][a-zA-Z]+ [A-Za-z\s\-]+ [A-Za-z]+)',  # Brand Product Type
            r'([A-Z][a-zA-Z\-]+\s+[A-Za-z\-]+)',  # Brand Product
            r'([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)'  # Two capitalized words (likely a brand name)
        ]
        
        for pattern in branded_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                product_name = match.strip()
                if self._is_valid_product_name(product_name):
                    products.append(product_name)
        
        # Extract products from lists (often found in recommendation articles)
        # Look for bulleted list items
        bullet_points = re.findall(r'[•\-*]\s+([A-Z][a-zA-Z\s\-\']+)', content)
        for point in bullet_points:
            if self._is_valid_product_name(point.strip()):
                products.append(point.strip())
                
        # Look for numbered list items
        numbered_points = re.findall(r'\d+\.\s+([A-Z][a-zA-Z\s\-\']+)', content)
        for point in numbered_points:
            if self._is_valid_product_name(point.strip()):
                products.append(point.strip())
        
        # Look for products in headers and subheadings (often indicating a section about that product)
        header_pattern = r'<h[2-4]>([A-Z][a-zA-Z\s\-\']+)</h[2-4]>'
        header_matches = re.findall(header_pattern, content)
        for match in header_matches:
            if self._is_valid_product_name(match.strip()):
                products.append(match.strip())
                
        # If we have a title about alternatives, extract more aggressively
        if title and ("alternative" in title.lower() or "substitute" in title.lower() or 
                     "instead of" in title.lower() or "replacement" in title.lower()):
            # Extract names from content with more relaxed patterns
            product_candidates = re.findall(r'([A-Z][a-zA-Z\-\']{1,20}(?:\s+[A-Za-z\-\']{1,20}){0,3})', content)
            for candidate in product_candidates:
                if self._is_valid_product_name(candidate.strip()):
                    products.append(candidate.strip())
            
        # Add specific brand products if they appear in content
        known_brands = {
            "Nutella": ["Nutella"],
            "Coca-Cola": ["Coca-Cola", "Coke"],
            "Pepsi": ["Pepsi"],
            "Skippy": ["Skippy"],
            "Jif": ["Jif"],
            "Smucker": ["Smucker's"],
            "Heinz": ["Heinz"],
            "Ferrero": ["Ferrero"]
        }
        
        for brand, variants in known_brands.items():
            for variant in variants:
                if variant in content:
                    products.append(brand)
                    break
            
        # Filter out duplicates and ensure we have valid product names
        unique_products = []
        seen_products_lower = set()
        
        for product in products:
            product = product.strip()
            product_lower = product.lower()
            
            if (product and self._is_valid_product_name(product) and 
                product_lower not in seen_products_lower):
                unique_products.append(product)
                seen_products_lower.add(product_lower)
                
        return unique_products
        
    def _is_valid_product_name(self, name: str) -> bool:
        """
        Determine if a string is likely to be a valid product name
        This helps filter out generic terms that aren't actual products
        """
        # Must have minimum length
        if len(name) < 4:
            return False
            
        # Skip very long names
        if len(name) > 40:
            return False
            
        # Must start with capital letter (most product names do)
        if not name[0].isupper():
            return False
            
        # Skip if it's just a single word that's generic
        common_words = [
            "breakfast", "nutritious", "options", "search", "google", "healthy", 
            "alternative", "nutritional", "benefits", "food", "diet", "dietary", 
            "drinks", "beverage", "product", "natural", "organic", "brand",
            "protein", "nutrition", "instead", "website", "article", "india",
            "indian", "healthy", "health", "good", "better", "best", "top",
            "recommend", "recommended", "popular", "choice", "spread", "option",
            "complete", "guide", "list", "review", "reviews", "buying", "buy",
            "purchase", "store", "online", "check", "information", "content",
            "help", "advice", "tips", "tricks", "how", "what", "where", "when",
            "lifestyle", "market", "shopping", "shop", "super", "super", "mega",
            "ultra", "premium", "deluxe", "quality", "perfect", "ideal", "amazon"
        ]
        
        # Check if it's a single word generic term
        if len(name.split()) == 1 and name.lower() in common_words:
            return False
            
        # Skip if it contains only generic words
        words = name.lower().split()
        if all(word in common_words for word in words):
            return False
            
        # Skip if it's too generic
        generic_phrases = [
            "this product", "these products", "other brands", "other options",
            "find out", "read more", "click here", "visit website", "learn more",
            "more information", "check out", "website", "blog post", "article",
            "healthy alternative", "better option", "top choice"
        ]
        
        for phrase in generic_phrases:
            if phrase in name.lower():
                return False
            
        # Must not be just a type descriptor
        generic_types = ["juice", "water", "drink", "beverage", "soda", "food", "spread", "product"]
        if name.lower() in generic_types:
            return False
            
        # Check if name is just a single word that's a common food type
        if len(name.split()) == 1 and name.lower() in ["chocolate", "milk", "butter", "jam", "cream", "yogurt"]:
            return False
            
        # Check for names that are just verbs or actions
        action_words = ["using", "eating", "drinking", "making", "cooking", "preparing", "buying", "ordering"]
        if name.lower() in action_words:
            return False
            
        # Must contain at least one non-common word
        has_non_common = False
        for word in words:
            if word not in common_words and word not in generic_types:
                has_non_common = True
                break
                
        if not has_non_common:
            return False
            
        return True
        
    def _extract_brand(self, product: str, content: str) -> str:
        """Extract brand from product name or content"""
        # Try to get first word of product as brand
        words = product.split()
        if len(words) > 1:
            return words[0]
            
        # Look for brand mentions near product name
        brand_patterns = [
            rf'by ([A-Za-z]+)\s+{re.escape(product)}',
            rf'{re.escape(product)}\s+by ([A-Za-z]+)',
            rf'from ([A-Za-z]+)'
        ]
        
        for pattern in brand_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                return matches[0].strip()
                
        return "Health Alternative"  # Default brand
        
    def _calculate_health_score(self, content: str, product: str) -> int:
        """Calculate health score based on content"""
        base_score = 75  # Start with a decent score
        
        # Positive factors
        positive_factors = [
            'organic', 'natural', 'no preservatives', 'no artificial', 
            'whole grain', 'high fiber', 'protein', 'vitamin', 
            'mineral', 'antioxidant', 'probiotic', 'low sugar',
            'sugar free', 'low fat', 'fat free', 'nutritious'
        ]
        
        # Negative factors
        negative_factors = [
            'sugar', 'high sugar', 'artificial', 'preservative',
            'coloring', 'flavoring', 'additive', 'processed',
            'hydrogenated', 'trans fat', 'high sodium'
        ]
        
        # Look for positive factors
        for factor in positive_factors:
            pattern = rf'{re.escape(factor)}|{re.escape(product)}.*{re.escape(factor)}|{re.escape(factor)}.*{re.escape(product)}'
            matches = re.findall(pattern, content, re.IGNORECASE)
            base_score += len(matches) * 3
            
        # Look for negative factors
        for factor in negative_factors:
            pattern = rf'{re.escape(factor)}|{re.escape(product)}.*{re.escape(factor)}|{re.escape(factor)}.*{re.escape(product)}'
            matches = re.findall(pattern, content, re.IGNORECASE)
            base_score -= len(matches) * 2
            
        # Ensure score is between 60-95
        return min(95, max(60, base_score))
        
    def _extract_price(self, content: str, product: str) -> str:
        """Extract price information from content"""
        price_patterns = [
            r'₹\s*(\d+(?:[-,]\d+)?)',
            r'Rs\.?\s*(\d+(?:[-,]\d+)?)',
            r'costs?\s*(?:around|about)?\s*₹\s*(\d+(?:[-,]\d+)?)',
            r'price(?:d)?\s*(?:at|around)?\s*₹\s*(\d+(?:[-,]\d+)?)',
            r'(\d+(?:[-,]\d+)?)\s*rupees'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                price = matches[0]
                # Determine unit
                if 'kg' in content[content.find(matches[0])-20:content.find(matches[0])+20]:
                    return f"₹{price} per kg"
                elif 'gram' in content[content.find(matches[0])-20:content.find(matches[0])+20]:
                    return f"₹{price} per pack"
                else:
                    return f"₹{price}"
                    
        # Default price range based on product type
        product_lower = product.lower()
        if any(word in product_lower for word in ['water', 'juice', 'milk']):
            return "₹50-80 per bottle"
        elif any(word in product_lower for word in ['yogurt', 'curd']):
            return "₹30-50 per cup"
        else:
            return "₹100-150 per pack"
        
    def _extract_availability(self, content: str) -> str:
        """Extract availability information"""
        locations = [
            'supermarket', 'grocery store', 'health food store', 'online',
            'amazon', 'flipkart', 'big basket', 'grofers', 'nature\'s basket',
            'retail store', 'shop', 'market', 'outlet'
        ]
        
        found_locations = []
        for location in locations:
            if location in content.lower():
                found_locations.append(location)
                
        if found_locations:
            return ", ".join(found_locations).title()
        else:
            return "Supermarkets and online stores"
            
    def _extract_health_benefits(self, content: str, product: str) -> str:
        """Extract health benefits from content"""
        benefits = []
        
        # Look for benefits
        benefit_patterns = [
            rf'{re.escape(product)}.*?(?:has|contains|is rich in|is high in|provides)\s+([^.]+)',
            r'(?:rich in|high in|source of|provides)\s+([^.]+)',
            r'(?:benefits|advantages).*?include\s+([^.]+)'
        ]
        
        for pattern in benefit_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) > 5 and len(match) < 100:  # Reasonable length for a benefit
                    benefits.append(match.strip())
                    
        # If we found benefits, join them
        if benefits:
            # Take just the first 2 benefits to avoid too much text
            return "; ".join(benefits[:2]).capitalize()
            
        # Otherwise, look for specific nutritional keywords
        nutrition_keywords = [
            'protein', 'fiber', 'vitamin', 'mineral', 'calcium', 'iron',
            'antioxidant', 'omega', 'nutrient', 'probiotic', 'prebiotic',
            'low sugar', 'no preservatives', 'natural', 'organic'
        ]
        
        found_keywords = []
        for keyword in nutrition_keywords:
            if keyword in content.lower():
                found_keywords.append(keyword)
                
        if found_keywords:
            return ", ".join(found_keywords).title() + " content"
        else:
            return "Natural and nutritious alternative"
            
    def _extract_key_benefits(self, content: str, product: str) -> str:
        """Extract key benefits - shorter version of health benefits"""
        health_benefits = self._extract_health_benefits(content, product)
        
        # If benefits are already short enough, use them
        if len(health_benefits) <= 50:
            return health_benefits
            
        # Otherwise, shorten them
        words = health_benefits.split()
        if len(words) > 7:
            return " ".join(words[:7]) + "..."
        else:
            return health_benefits

    def run_search(self, query: str, category: str) -> List[Dict[str, Any]]:
        """
        Run web search for product information or alternatives
        Enhanced with more sophisticated search and results processing
        """
        try:
            print(f"🔍 Running real-time search for: {query} in category {category}")
            
            # Define targeted search URLs based on category
            search_urls = {
                "product_category": [
                    "https://www.healthline.com/nutrition/",
                    "https://www.medicalnewstoday.com/nutrition/",
                    "https://food.ndtv.com/",
                    "https://www.tarladalal.com/recipes-for-indian/",
                    "https://www.bbcgoodfood.com/recipes/"
                ],
                "beverage": [
                    "https://www.healthline.com/nutrition/healthy-beverages/",
                    "https://food.ndtv.com/food-drinks/",
                    "https://www.medicalnewstoday.com/articles/healthy-drinks/",
                    "https://www.drinkpreneur.com/healthy-drinks/",
                    "https://www.bbcgoodfood.com/recipes/collection/healthy-drinks-recipes/"
                ],
                "bread": [
                    "https://www.healthline.com/nutrition/healthiest-bread/",
                    "https://www.medicalnewstoday.com/articles/healthy-bread/",
                    "https://food.ndtv.com/food-drinks/multigrain-atta-roti-bread-healthy-options/"
                ],
                "cereal": [
                    "https://www.healthline.com/nutrition/healthiest-breakfast-cereals/",
                    "https://food.ndtv.com/food-drinks/breakfast-cereals/"
                ],
                "chocolate": [
                    "https://www.healthline.com/nutrition/dark-chocolate-benefits/",
                    "https://food.ndtv.com/food-drinks/dark-chocolate-benefits/"
                ],
                "snack": [
                    "https://www.healthline.com/nutrition/healthy-snacks-for-adults/",
                    "https://food.ndtv.com/food-drinks/healthy-snacks/"
                ],
                "default": [
                    "https://www.healthline.com/nutrition/",
                    "https://www.medicalnewstoday.com/nutrition/",
                    "https://food.ndtv.com/",
                    "https://www.netmeds.com/health-library/category/healthy-alternatives/"
                ]
            }
            
            # Select appropriate URLs based on category
            if category in search_urls:
                urls = search_urls[category]
            else:
                urls = search_urls["default"]
            
            # Enhanced query with category-specific terms
            if category == "product_category":
                enhanced_query = f"what type of food is {query} classification"
            elif category == "product_alternatives":
                enhanced_query = f"healthy alternatives to {query} nutrition benefits"
            else:
                enhanced_query = f"healthy alternative {category} india nutrition {query}"
                
            print(f"🔎 Enhanced search query: {enhanced_query}")
                
            # Add general search engines to supplement specialized sites
            general_search_urls = [
                "https://www.google.com/search?q=",
                "https://duckduckgo.com/?q="
            ]
            
            # Combine specialized and general search URLs
            all_search_urls = urls + general_search_urls
            
            # Perform the searches
            search_results = []
            for site in all_search_urls:
                try:
                    print(f"📡 Searching: {site}")
                    encoded_query = requests.utils.quote(enhanced_query)
                    search_url = f"{site}{encoded_query}"
                    
                    # Add user agent to avoid being blocked
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    response = requests.get(search_url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract the title
                        title = soup.title.string if soup.title else site
                        
                        # Extract content more intelligently based on common content patterns
                        content = ""
                        
                        # Look for main content containers
                        content_selectors = [
                            "article", "main", ".content", "#content", 
                            ".main-content", "#main-content", ".post-content",
                            ".entry-content", ".article-content"
                        ]
                        
                        for selector in content_selectors:
                            content_section = soup.select_one(selector)
                            if content_section:
                                content += content_section.get_text(strip=True, separator=" ") + " "
                                
                        # If no content found via selectors, use the whole page
                        if not content:
                            content = soup.get_text(strip=True, separator=" ")
                        
                        # Clean up content
                        content = re.sub(r'\s+', ' ', content).strip()
                        
                        # Extract search results from Google/DuckDuckGo if applicable
                        if "google.com/search" in site or "duckduckgo.com" in site:
                            # Try to extract search result snippets
                            results = []
                            
                            # Google search results
                            if "google.com" in site:
                                snippets = soup.select(".g .VwiC3b")
                                for snippet in snippets[:5]:  # Take first 5 snippets
                                    results.append(snippet.get_text(strip=True))
                                    
                            # DuckDuckGo results
                            if "duckduckgo.com" in site:
                                snippets = soup.select(".result__snippet")
                                for snippet in snippets[:5]:
                                    results.append(snippet.get_text(strip=True))
                                    
                            # If we found search results, use them instead
                            if results:
                                content = " ".join(results)
                        
                        search_results.append({
                            'title': title,
                            'content': content[:10000],  # Take more content for better analysis
                            'url': search_url
                        })
                        print(f"✅ Got content from {site} - {len(content)} chars")
                        
                except Exception as e:
                    print(f"❌ Error fetching {site}: {e}")
                    continue
            
            return search_results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []

# Create instance
search_utils = SearchUtils()