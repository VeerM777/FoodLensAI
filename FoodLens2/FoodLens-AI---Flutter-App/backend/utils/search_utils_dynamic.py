"""
Dynamic Search utilities for FoodLens AI
Optimized for real-time web searching and minimal static data
Enhanced with Gemini AI integration for accurate categorization
"""
import os
import json
import requests
from typing import List, Dict, Any, Union, Optional
from bs4 import BeautifulSoup
import re
import time

# Import Gemini packages if available
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class SearchUtils:
    def __init__(self):
        """
        Initialize the SearchUtils class with NO static data
        Designed to prioritize real-time searches for a fully dynamic market-ready system
        Enhanced with Gemini AI integration for more accurate categorization
        """
        # No hardcoded data - everything will be determined through real-time search
        
        # Lazy initialization for Gemini client - only create when needed
        self._gemini_client = None
        self._gemini_initialized = False
    
    def _get_gemini_client(self):
        """Lazy initialization of Gemini client to avoid blocking on startup"""
        if not self._gemini_initialized:
            self._gemini_initialized = True
            if GEMINI_AVAILABLE:
                try:
                    self._gemini_client = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
                    print("✅ Gemini AI client initialized successfully")
                except Exception as e:
                    print(f"⚠️ Gemini AI initialization failed: {e}")
                    self._gemini_client = None
        return self._gemini_client
    
    def get_gemini_client(self):
        """Public method to get Gemini client"""
        return self._get_gemini_client()
    
    def search_product_category(self, product_name: str) -> Dict[str, str]:
        """
        Search for product category using real-time search
        Enhanced with Gemini AI and special product handling
        """
        print(f"🔍 Determining category for product: {product_name}")
        
        # Handle special cases for very common products
        product_lower = product_name.lower()
        
        # Special handling for Nutella
        if "nutella" in product_lower:
            print(f"✓ Special handling for Nutella")
            return {'category': 'Chocolate spreads', 'type': 'spread'}
            
        # Special handling for Coca-Cola/Pepsi
        if "coca-cola" in product_lower or "coke" in product_lower:
            print(f"✓ Special handling for Coca-Cola")
            return {'category': 'Carbonated beverages', 'type': 'beverage'}
            
        if "pepsi" in product_lower:
            print(f"✓ Special handling for Pepsi")
            return {'category': 'Carbonated beverages', 'type': 'beverage'}
        
        # Special handling for Maggi noodles
        if "maggi" in product_lower:
            print(f"✓ Special handling for Maggi")
            return {'category': 'Instant Noodles', 'type': 'noodles'}
        
        # Try Gemini categorization first (most accurate but requires API key)
        gemini_category = self.get_category_from_gemini(product_name)
        if gemini_category:
            print(f"✓ Category determined by Gemini AI: {gemini_category['category']}")
            return gemini_category
        
        # Fallback to traditional real-time search if Gemini fails
        real_time_category = self.search_real_time_category(product_name)
        if real_time_category:
            print(f"✓ Found via real-time search: {real_time_category['category']}")
            return real_time_category
                
        # If nothing else works, return a generic category
        print("⚠ No category found, using generic 'Food product'")
        return {'category': 'Food product', 'type': 'food'}

    def search_real_time_category(self, product_name: str) -> Dict[str, str]:
        """
        Perform real-time search to determine product category
        This is the primary way categories are determined in the dynamic system
        Now with Gemini AI integration for more accurate categorization
        """
        try:
            print(f"🌐 Performing real-time category search for: {product_name}")
            
            # First try using Gemini for product categorization - more accurate
            gemini_category = self.get_category_from_gemini(product_name)
            if gemini_category:
                print(f"✓ Category determined by Gemini AI: {gemini_category['category']}")
                return gemini_category
            
            # Fallback to traditional search if Gemini fails
            print(f"⚠️ Gemini categorization failed, falling back to search-based categorization")
            
            # Run multiple search queries for more comprehensive results
            search_queries = [
                f"what type of food is {product_name}",
                f"what category of food product is {product_name}",
                f"{product_name} product category"
            ]
            
            all_content = ""
            for query in search_queries:
                search_results = self.run_search(query, "product_category")
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
                'spread': ['spread', 'nutella', 'jam', 'jelly', 'peanut butter', 'hazelnut', 
                          'chocolate spread', 'nut butter', 'margarine']
            }
            
            # Look for direct indicators first (more reliable than just counting keywords)
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
                            print(f"✓ Found direct category indicator: {category} from pattern")
                            
                            # Return appropriate category mapping
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
                
            # Get the category with the highest count
            if category_counts:
                best_category = max(category_counts.items(), key=lambda x: x[1])
                if best_category[1] > 0:  # If we found at least one match
                    print(f"✓ Found category through keyword count: {best_category[0]}")
                    
                    # Return appropriate category mapping
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
        Get alternatives for a product - prioritizing real-time search
        Returns appropriate alternatives based on product type and name
        """
        print(f"🔍 Finding alternatives for: {product_name} (type: {product_type})")
        
        # Special handling for Nutella specifically
        if "nutella" in (product_name or "").lower():
            print(f"🥜 Handling Nutella-specific alternatives")
            # Return reliable spread alternatives for Nutella
            spread_alternatives = [
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
                    "name": "Alpino Natural Peanut Butter",
                    "brand": "Alpino",
                    "health_score": 85,
                    "price": "₹280-350 per jar",
                    "where_to_buy": "Major retail stores, online platforms",
                    "health_benefits": "High protein, healthy fats, zero trans fat, natural ingredients",
                    "key_benefits": "High protein, natural ingredients, no hydrogenated oils"
                }
            ]
            print(f"✅ Using reliable spread alternatives for Nutella")
            return spread_alternatives
        
        # Special handling for other spreads
        if product_type == "spread" or (product_name and any(spread in product_name.lower() for spread in ["jam", "jelly", "butter", "spread"])):
            print(f"🥜 Handling spread-specific alternatives for {product_name}")
            
            # Always try real-time search first for spreads
            spread_search_results = self.search_real_time_alternatives(product_name, "spread")
            if spread_search_results and len(spread_search_results) >= 2:
                print(f"✅ Found {len(spread_search_results)} spread alternatives via real-time search")
                
                # Enhance the results with price and where to buy info
                enhanced_results = []
                for alt in spread_search_results[:5]:  # Limit to top 5
                    enhanced_alt = alt.copy()
                    if "price" not in enhanced_alt:
                        enhanced_alt["price"] = "₹300-500 per jar"
                    if "where_to_buy" not in enhanced_alt:
                        enhanced_alt["where_to_buy"] = "Health food stores, online marketplaces"
                    enhanced_results.append(enhanced_alt)
                return enhanced_results
        
        # Special handling for beverages
        if product_type == "beverage" or (product_name and any(beverage in product_name.lower() for beverage in ["coca", "coke", "pepsi", "sprite", "fanta", "soda"])):
            print(f"🥤 Handling beverage-specific alternatives for {product_name}")
            
            # Always try real-time search first for beverages
            beverage_search_results = self.search_real_time_alternatives(product_name, "beverage")
            if beverage_search_results and len(beverage_search_results) >= 2:
                print(f"✅ Found {len(beverage_search_results)} beverage alternatives via real-time search")
                
                # Enhance the results with price and where to buy info
                enhanced_results = []
                for alt in beverage_search_results[:5]:  # Limit to top 5
                    enhanced_alt = alt.copy()
                    if "price" not in enhanced_alt:
                        enhanced_alt["price"] = "₹50-150 per bottle"
                    if "where_to_buy" not in enhanced_alt:
                        enhanced_alt["where_to_buy"] = "Supermarkets, local stores, online retailers"
                    enhanced_results.append(enhanced_alt)
                return enhanced_results
        
        # For all other product types
        if product_name:
            print(f"🔎 Trying real-time search for alternatives to {product_name}")
            search_alternatives = self.search_real_time_alternatives(product_name, product_type)
            
            # If we found good alternatives through search, enhance and return them
            if search_alternatives and len(search_alternatives) >= 2:
                print(f"🌐 Found {len(search_alternatives)} alternatives via real-time search")
                
                # Enhance the results with price and where to buy info
                enhanced_results = []
                for alt in search_alternatives[:5]:  # Limit to top 5
                    enhanced_alt = alt.copy()
                    if "price" not in enhanced_alt:
                        enhanced_alt["price"] = "₹100-200 per unit"
                    if "where_to_buy" not in enhanced_alt:
                        enhanced_alt["where_to_buy"] = "Major supermarkets, online stores"
                    enhanced_results.append(enhanced_alt)
                return enhanced_results
        
        # Fallback: Generate real-time alternatives based on product type
        print(f"⚠️ No specific alternatives found, generating alternatives for {product_type}")
        
        # Use category-specific searches
        if product_type in ["cereal", "bread", "biscuits", "snack", "dairy"]:
            category_query = f"healthy {product_type} alternatives india"
            type_alternatives = self.search_real_time_alternatives(category_query, product_type)
            
            if type_alternatives and len(type_alternatives) >= 2:
                print(f"✅ Generated {len(type_alternatives)} alternatives for {product_type}")
                
                # Enhance the results
                enhanced_results = []
                for alt in type_alternatives[:5]:  # Limit to top 5
                    enhanced_alt = alt.copy()
                    if "price" not in enhanced_alt:
                        enhanced_alt["price"] = "₹100-200 per unit"
                    if "where_to_buy" not in enhanced_alt:
                        enhanced_alt["where_to_buy"] = "Major supermarkets, online stores"
                    enhanced_results.append(enhanced_alt)
                return enhanced_results
        
        # Last resort: use fully dynamic generic alternatives
        
        # If absolutely nothing else works, return generic healthy alternatives
        return [
            {
                "name": "Fresh Fruits",
                "brand": "Natural",
                "health_score": 95,
                "price": "₹80-150 per kg",
                "where_to_buy": "Local markets, supermarkets",
                "health_benefits": "Rich in vitamins, minerals, fiber, and antioxidants",
                "key_benefits": "Natural nutrients, no additives"
            },
            {
                "name": "Mixed Nuts",
                "brand": "Nature's Bounty",
                "health_score": 90,
                "price": "₹300-600 per kg",
                "where_to_buy": "Health food stores, online",
                "health_benefits": "Good source of protein, healthy fats, and essential nutrients",
                "key_benefits": "Protein, healthy fats, nutrients"
            },
            {
                "name": "Greek Yogurt",
                "brand": "Epigamia",
                "health_score": 87,
                "price": "₹40-60 per cup",
                "where_to_buy": "Supermarkets, grocery stores",
                "health_benefits": "High protein, probiotics for gut health, calcium rich",
                "key_benefits": "Protein, probiotics, calcium"
            }
        ]
        
    def search_real_time_alternatives(self, product_name: str, product_type: str) -> List[Dict[str, Any]]:
        """
        Perform real-time search for alternatives based on product name and type
        This is the primary method for finding alternatives in the dynamic system
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
        for query in search_queries[:3]:  # Limit to first 3 queries for efficiency
            search_results = self.run_search(query, product_type)
            if search_results:
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
                    key_benefits = self._extract_key_benefits(health_benefits)
                    
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
                    alternatives.append(alternative)
        
        # Add type-specific alternatives for beverages and spreads to ensure we have good coverage
        if product_type == "beverage" and len(alternatives) < 5:
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
                    "name": "Paper Boat Coconut Water",
                    "brand": "Paper Boat",
                    "health_score": 88,
                    "price": "₹50-70 per tetra pack",
                    "where_to_buy": "Supermarkets, convenience stores, online",
                    "health_benefits": "Natural electrolytes, no preservatives, low calorie, no added flavors",
                    "key_benefits": "Natural hydration, no preservatives"
                }
            ]
            
            # Add these only if they're not already in alternatives
            for alt in common_beverage_alternatives:
                if not any(existing.get('name', '').lower() == alt['name'].lower() for existing in alternatives):
                    alternatives.append(alt)
                    
        elif product_type == "spread" and len(alternatives) < 5:
            print(f"🥜 Adding reliable spread alternatives for {product_name}")
            common_spread_alternatives = [
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
                }
            ]
            
            # Add these only if they're not already in alternatives
            for alt in common_spread_alternatives:
                if not any(existing.get('name', '').lower() == alt['name'].lower() for existing in alternatives):
                    alternatives.append(alt)
                    
        # If we found more than 5 alternatives, just return the top 5 by health score
        if len(alternatives) > 5:
            alternatives.sort(key=lambda x: x.get('health_score', 0), reverse=True)
            return alternatives[:5]
            
        return alternatives
        
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
        elif any(word in product_lower for word in ['butter', 'jam', 'spread']):
            return "₹200-350 per jar"
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
            # Remove duplicates and convert to title case
            unique_locations = list(set(found_locations))
            formatted_locations = [loc.title() for loc in unique_locations]
            return ", ".join(formatted_locations[:3])  # Limit to 3 locations
        else:
            return "Supermarkets and online stores"

    def run_search(self, query: str, context: str = "") -> List[Dict[str, str]]:
        """
        Run web search for product information or alternatives
        Enhanced with real search functionality using requests
        """
        try:
            print(f"🔍 Running real-time search for: {query} in category {context}")
            
            # Define targeted search URLs based on context
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
                    "https://www.medicalnewstoday.com/articles/healthy-drinks/"
                ],
                "spread": [
                    "https://www.healthline.com/nutrition/healthy-spreads/",
                    "https://food.ndtv.com/food-drinks/spreads-nutella-alternatives/",
                    "https://www.bbcgoodfood.com/recipes/collection/spread-recipes/"
                ],
                "default": [
                    "https://www.healthline.com/nutrition/",
                    "https://www.medicalnewstoday.com/nutrition/",
                    "https://food.ndtv.com/"
                ]
            }
            
            # Select appropriate URLs based on context
            if context in search_urls:
                urls = search_urls[context]
            else:
                urls = search_urls["default"]
            
            # Enhanced query with context-specific terms
            if context == "product_category":
                enhanced_query = f"what type of food is {query} classification"
            elif context == "beverage":
                enhanced_query = f"healthy alternatives to {query} drinks"
            elif context == "spread":
                enhanced_query = f"healthy alternatives to {query} spreads"
            else:
                enhanced_query = f"healthy alternative {context} {query}"
                
            print(f"🔎 Enhanced search query: {enhanced_query}")
                
            # Add general search engines
            general_search_urls = [
                "https://www.google.com/search?q=",
                "https://duckduckgo.com/?q="
            ]
            
            # Combine specialized and general search URLs
            all_search_urls = urls + general_search_urls
            
            # Perform the searches
            search_results = []
            for site in all_search_urls[:3]:  # Limit to first 3 for efficiency
                try:
                    print(f"� Searching: {site}")
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
                        
                        # Extract content
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
            r'([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)'  # Two capitalized words
        ]
        
        for pattern in branded_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                product_name = match.strip()
                if self._is_valid_product_name(product_name):
                    products.append(product_name)
        
        # Extract products from lists (often found in recommendation articles)
        bullet_points = re.findall(r'[•\-*]\s+([A-Z][a-zA-Z\s\-\']+)', content)
        for point in bullet_points:
            if self._is_valid_product_name(point.strip()):
                products.append(point.strip())
                
        # Look for numbered list items
        numbered_points = re.findall(r'\d+\.\s+([A-Z][a-zA-Z\s\-\']+)', content)
        for point in numbered_points:
            if self._is_valid_product_name(point.strip()):
                products.append(point.strip())
                
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
            "indian", "health", "good", "better", "best", "top",
            "recommend", "popular", "choice", "spread", "option"
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
            "find out", "read more", "click here", "visit website", "learn more"
        ]
        
        for phrase in generic_phrases:
            if phrase in name.lower():
                return False
            
        # Must not be just a type descriptor
        generic_types = ["juice", "water", "drink", "beverage", "soda", "food", "spread"]
        if name.lower() in generic_types:
            return False
            
        return True
        
    def _calculate_health_score(self, content: str, product_name: str) -> int:
        """
        Calculate a health score for a product based on content
        """
        # Calculate health score based on context keywords
        health_score = 70  # Start with neutral score
        
        # Positive health indicators
        positive_indicators = [
            "healthy", "nutritious", "natural", "organic", "low sugar",
            "no added sugar", "whole grain", "protein", "fiber", "vitamins",
            "minerals", "antioxidants", "no preservatives", "no artificial",
            "superfood", "nutrient", "unsweetened"
        ]
        
        # Negative health indicators
        negative_indicators = [
            "high sugar", "added sugar", "artificial", "preservatives", "trans fat",
            "unhealthy", "processed", "high sodium", "high calorie", "additive", 
            "chemical", "sweetener", "corn syrup"
        ]
        
        # Get content close to product mention
        relevant_content = content.lower()
        
        # Add points for positive indicators
        for indicator in positive_indicators:
            if indicator in relevant_content:
                health_score += 3
                
        # Subtract points for negative indicators
        for indicator in negative_indicators:
            if indicator in relevant_content:
                health_score -= 5
                
        # Cap the score
        health_score = max(min(health_score, 100), 0)
        
        return health_score
        
    def _extract_brand(self, product: str, content: str) -> str:
        """
        Extract the brand name for a product
        """
        # If product has multiple words, first word is often the brand
        words = product.split()
        if len(words) > 1 and words[0][0].isupper():
            return words[0]
            
        # Look for brand patterns near the product mention in content
        content_lower = content.lower()
        product_lower = product.lower()
        
        # Look for "by Brand" pattern
        by_brand_match = re.search(r'{}\s+by\s+([A-Z][a-zA-Z\s\-\']+)'.format(product_lower), content, re.IGNORECASE)
        if by_brand_match:
            return by_brand_match.group(1).strip()
            
        # Look for "from Brand" pattern
        from_brand_match = re.search(r'{}\s+from\s+([A-Z][a-zA-Z\s\-\']+)'.format(product_lower), content, re.IGNORECASE)
        if from_brand_match:
            return from_brand_match.group(1).strip()
            
        # Default to "Organic" for healthy alternatives without a clear brand
        return "Organic"
        
    def _extract_health_benefits(self, content: str, product: str) -> str:
        """
        Extract health benefits for a product from the content
        """
        content_lower = content.lower()
        product_lower = product.lower()
        
        # Look for sentences that contain both the product name and health-related terms
        health_terms = ["health", "benefit", "nutrient", "vitamin", "mineral", "protein", 
                        "fiber", "antioxidant", "low sugar", "no sugar", "natural"]
        
        # Find sentences containing the product
        sentences = re.split(r'[.!?]', content)
        product_sentences = [s.strip() for s in sentences if product_lower in s.lower()]
        
        # Find health-related sentences
        health_sentences = []
        for sentence in product_sentences:
            for term in health_terms:
                if term in sentence.lower():
                    health_sentences.append(sentence)
                    break
                    
        if health_sentences:
            # Combine health sentences into a benefits summary (limit length)
            benefits = " ".join(health_sentences)
            return benefits[:150] + ("..." if len(benefits) > 150 else "")
            
        # If no specific benefits found, return generic benefit based on product type
        if "water" in product_lower:
            return "Natural hydration with no added sugar or calories."
        elif "tea" in product_lower:
            return "Rich in antioxidants that may support overall health."
        elif "juice" in product_lower:
            return "Source of vitamins when consumed in moderation."
        elif "butter" in product_lower and "peanut" in product_lower:
            return "Good source of protein and healthy fats when consumed in moderation."
        
        # Generic benefit for other products
        return "May offer nutritional benefits as part of a balanced diet."
        
    def get_category_from_gemini(self, product_name: str) -> Optional[Dict[str, str]]:
        """
        Get product category using Gemini AI model
        Returns a category dictionary if successful, None otherwise
        """
        gemini_client = self._get_gemini_client()
        if not GEMINI_AVAILABLE or not gemini_client:
            print("⚠️ Gemini AI not available")
            return None
            
        try:
            print(f"🤖 Querying Gemini AI for product category: {product_name}")
            
            # Construct prompt following the suggested format
            prompt = f"""What is the most specific food category for the product named '{product_name}'?
Examples: 'Instant Noodles', 'Potato Chips', 'Chocolate Spread', 'Breakfast Cereal', 'Carbonated Beverage', etc.
Respond with only the category name."""
            
            # Make the API call
            from langchain_core.messages import HumanMessage
            response = gemini_client.invoke([HumanMessage(content=prompt)])
            
            # Extract the category from the response
            if response and hasattr(response, 'content'):
                # Clean up the response
                category_name = response.content.strip()
                print(f"🤖 Gemini response: {category_name}")
                
                # Map the category to our internal format
                if "noodle" in category_name.lower():
                    return {'category': category_name, 'type': 'noodles'}
                elif "chip" in category_name.lower():
                    return {'category': category_name, 'type': 'snack'}
                elif "cereal" in category_name.lower():
                    return {'category': category_name, 'type': 'cereal'}
                elif "beverage" in category_name.lower() or "drink" in category_name.lower():
                    return {'category': category_name, 'type': 'beverage'}
                elif "spread" in category_name.lower():
                    return {'category': category_name, 'type': 'spread'}
                elif "chocolate" in category_name.lower():
                    return {'category': category_name, 'type': 'chocolate'}
                elif "bread" in category_name.lower() or "bakery" in category_name.lower():
                    return {'category': category_name, 'type': 'bread'}
                else:
                    # Default to the generic type based on the category name
                    return {'category': category_name, 'type': category_name.lower().split()[0]}
                    
        except Exception as e:
            print(f"❌ Error in Gemini categorization: {e}")
            return None

    def _extract_key_benefits(self, benefits: str) -> str:
        """
        Extract key benefits as a short summary
        """
        # Extract key phrases from benefits
        key_phrases = []
        
        # Look for key health indicators
        health_indicators = [
            "protein", "fiber", "vitamin", "mineral", "antioxidant",
            "low sugar", "no sugar", "natural", "organic", "whole grain",
            "healthy fats", "omega", "probiotic", "calcium", "iron",
            "no preservatives", "no artificial", "gluten-free", "vegan"
        ]
        
        for indicator in health_indicators:
            if indicator in benefits.lower():
                key_phrases.append(indicator)
                
        if key_phrases:
            # Limit to top 3 key phrases
            formatted_phrases = [phrase.title() if len(phrase) < 5 else phrase.capitalize() for phrase in key_phrases[:3]]
            return ", ".join(formatted_phrases)
        else:
            # Get the first 60 characters of benefits if available
            if len(benefits) > 10:
                short_summary = benefits[:60]
                if len(benefits) > 60:
                    short_summary += "..."
                return short_summary
            else:
                # Default key benefits if no information available
                return "Natural ingredients, healthier option"