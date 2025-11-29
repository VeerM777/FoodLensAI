"""
Lightweight Enhanced Product Categorizer
No external dependencies - uses advanced pattern matching and heuristics
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CategoryResult:
    category: str
    confidence: float
    method: str
    subcategory: Optional[str] = None
    matched_keywords: List[str] = None

class LightweightProductCategorizer:
    """
    Advanced product categorizer using sophisticated pattern matching
    Designed specifically for Indian food/beverage products
    """
    
    def __init__(self):
        # Hierarchical category structure for better alternatives matching
        self.categories = {
            # Beverages (Level 1 category for alternatives)
            "mango_drinks": {
                "keywords": ["mango", "frooti", "maaza", "slice", "aam", "mango drink", "mango juice"],
                "brands": ["frooti", "maaza", "slice", "aam panna"],
                "parent": "fruit_drinks",
                "alternatives_category": "fruit_drinks"
            },
            "fruit_drinks": {
                "keywords": ["fruit drink", "fruit juice", "mixed fruit", "real", "tropicana"],
                "brands": ["real", "tropicana", "minute maid", "paper boat"],
                "parent": "beverages",
                "alternatives_category": "fruit_drinks"
            },
            "carbonated_beverages": {
                "keywords": ["cola", "pepsi", "coca cola", "sprite", "fanta", "soda", "carbonated", "soft drink", "cold drink"],
                "brands": ["coca cola", "pepsi", "sprite", "fanta", "thums up", "limca"],
                "parent": "beverages",
                "alternatives_category": "beverages"
            },
            "dairy_beverages": {
                "keywords": ["milk", "lassi", "buttermilk", "flavored milk", "dairy drink", "milkshake"],
                "brands": ["amul", "mother dairy", "nestle", "britannia"],
                "parent": "beverages",
                "alternatives_category": "beverages",
                "exclude_keywords": ["ice cream", "icecream", "chocobar", "frozen", "kulfi", "cone", "scoop"]
            },
            "health_drinks": {
                "keywords": ["bournvita", "horlicks", "complan", "boost", "health drink", "protein"],
                "brands": ["bournvita", "horlicks", "complan", "boost", "protinex"],
                "parent": "beverages", 
                "alternatives_category": "beverages"
            },
            
            # Frozen Desserts
            "ice_cream": {
                "keywords": ["ice cream", "icecream", "chocobar", "choco bar", "kulfi", "frozen dessert", 
                            "cone", "scoop", "popsicle", "bar", "frozen", "gelato", "sorbet"],
                "brands": ["amul", "kwality walls", "vadilal", "mother dairy", "baskin robbins", 
                          "havmor", "noto", "gelato", "magnum"],
                "parent": "frozen_desserts",
                "alternatives_category": "healthy_desserts"
            },
            
            # Snacks
            "potato_chips": {
                "keywords": ["potato chips", "chips", "wafers", "crisps", "aloo", "potato", "lays"],
                "brands": ["lays", "lay's", "bingo", "uncle chipps", "pringles"],
                "parent": "snacks",
                "alternatives_category": "healthy_snacks"
            },
            "corn_snacks": {
                "keywords": ["kurkure", "corn", "cheetos", "corn snack", "corn chips"],
                "brands": ["kurkure", "cheetos", "doritos"],
                "parent": "snacks",
                "alternatives_category": "healthy_snacks"
            },
            "namkeen": {
                "keywords": ["namkeen", "bhujia", "sev", "mixture", "chivda", "mathri", "farsan"],
                "brands": ["haldiram", "haldirams", "bikano", "balaji"],
                "parent": "snacks",
                "alternatives_category": "healthy_snacks"
            },
            
            # Biscuits & Confectionery
            "biscuits": {
                "keywords": ["biscuit", "cookie", "cracker", "rusk", "toast", "wafer"],
                "brands": ["parle", "britannia", "sunfeast", "mcvities", "oreo"],
                "parent": "confectionery",
                "alternatives_category": "healthy_snacks"
            },
            "chocolates": {
                "keywords": ["chocolate", "cocoa", "dark chocolate", "milk chocolate", "bar"],
                "brands": ["cadbury", "dairy milk", "nestle", "kitkat", "ferrero", "snickers"],
                "parent": "confectionery",
                "alternatives_category": "healthy_sweets"
            },
            
            # Instant Foods
            "instant_noodles": {
                "keywords": ["noodles", "maggi", "pasta", "vermicelli", "instant noodles", "ramen"],
                "brands": ["maggi", "yippee", "top ramen", "knorr", "sunfeast"],
                "parent": "instant_foods",
                "alternatives_category": "healthy_meals"
            }
        }
        
        # Alternative mappings based on category hierarchy with specific Indian brands
        self.alternatives_mapping = {
            # Snacks alternatives - used for potato_chips, corn_snacks, namkeen
            "healthy_snacks": [
                {"name": "Cornitos Roasted Puffs", "brand": "Cornitos", "type": "Healthy Snacks", "score": 88,
                 "benefits": "Baked not fried, quinoa & oats based, high protein",
                 "availability": "Modern Trade, Nykaa, Amazon", "price": "₹150-200 per 150g"},
                {"name": "4700BC Gourmet Popcorn", "brand": "4700BC", "type": "Healthy Snacks", "score": 85,
                 "benefits": "Air-popped, whole grain, multiple flavors available",
                 "availability": "Supermarkets, online stores", "price": "₹180-250 per 100g"},
                {"name": "Happilo Premium Nuts", "brand": "Happilo", "type": "Nuts & Seeds", "score": 92,
                 "benefits": "Raw almonds, walnuts, cashews - protein rich",
                 "availability": "Modern Trade, Amazon, Flipkart", "price": "₹500-800 per kg"}
            ],
            # Individual category specific alternatives
            "potato_chips": [
                {"name": "Cornitos Nacho Crisps", "brand": "Cornitos", "type": "Baked Snacks", "score": 88,
                 "benefits": "Baked not fried, made from corn, lower fat content",
                 "availability": "Modern Trade, Amazon, Nykaa", "price": "₹150-200 per 150g"},
                {"name": "Too Yumm Veggie Chips", "brand": "Too Yumm", "type": "Vegetable Chips", "score": 85,
                 "benefits": "Real vegetables, baked, no trans fat",
                 "availability": "Supermarkets, BigBasket", "price": "₹130-180 per 100g"},
                {"name": "Happilo Roasted Almonds", "brand": "Happilo", "type": "Nuts", "score": 92,
                 "benefits": "High protein, healthy fats, no artificial flavors",
                 "availability": "Modern Trade, online stores", "price": "₹600-800 per kg"}
            ],
            "corn_snacks": [
                {"name": "Cornitos Roasted Puffs", "brand": "Cornitos", "type": "Healthy Puffs", "score": 88,
                 "benefits": "Quinoa & oats based, high protein, baked",
                 "availability": "Modern Trade, Nykaa, Amazon", "price": "₹150-200 per 150g"},
                {"name": "Yoga Bar Millet Cookies", "brand": "Yoga Bar", "type": "Healthy Cookies", "score": 90,
                 "benefits": "Millet-based, high fiber, no refined sugar",
                 "availability": "Health stores, online", "price": "₹200-300 per pack"},
                {"name": "Nourish Organics Roasted Seeds", "brand": "Nourish Organics", "type": "Seeds Mix", "score": 94,
                 "benefits": "Pumpkin & sunflower seeds, omega-3, organic",
                 "availability": "Organic stores, Amazon", "price": "₹300-400 per pack"}
            ],
            "namkeen": [
                {"name": "Haldiram's Baked Sev", "brand": "Haldiram's", "type": "Baked Traditional", "score": 82,
                 "benefits": "Traditional taste, baked version, lower oil",
                 "availability": "All retail stores", "price": "₹120-150 per 200g"},
                {"name": "Bikaji Roasted Chana Dal", "brand": "Bikaji", "type": "Protein Snack", "score": 88,
                 "benefits": "High protein, roasted not fried, traditional spices",
                 "availability": "Traditional stores, modern trade", "price": "₹80-120 per 200g"},
                {"name": "True Elements Roasted Fox Nuts", "brand": "True Elements", "type": "Healthy Puffs", "score": 92,
                 "benefits": "Makhana - low calorie, high protein, calcium rich",
                 "availability": "Health stores, Amazon, Flipkart", "price": "₹300-450 per pack"}
            ],
            # Mango drinks alternatives
            "mango_drinks": [
                {"name": "Paper Boat Aam Ras", "brand": "Paper Boat", "type": "Natural Fruit Drink", "score": 90,
                 "benefits": "Real mango pulp, no artificial colors, traditional taste",
                 "availability": "Modern Trade, BigBasket, Swiggy Instamart", "price": "₹25-35 per 250ml"},
                {"name": "Real Activ Mango", "brand": "Dabur Real", "type": "Fruit Juice", "score": 85,
                 "benefits": "100% fruit juice, vitamin C, no added sugar variant available",
                 "availability": "Supermarkets, local stores", "price": "₹120-150 per 1L"},
                {"name": "Raw Pressery Cold Pressed", "brand": "Raw Pressery", "type": "Premium Juice", "score": 92,
                 "benefits": "Cold-pressed, no preservatives, high nutritional value",
                 "availability": "Premium stores, Zomato, online", "price": "₹180-250 per 250ml"}
            ],
            # Instant noodles alternatives  
            "instant_noodles": [
                {"name": "Saffola Masala Oats", "brand": "Saffola", "type": "Healthy Instant", "score": 88,
                 "benefits": "High fiber, protein, low sodium, ready in 3 minutes",
                 "availability": "All supermarkets, online stores", "price": "₹150-200 per 500g"},
                {"name": "Slurrp Farm Ragi Noodles", "brand": "Slurrp Farm", "type": "Healthy Noodles", "score": 92,
                 "benefits": "Millet-based, no preservatives, high calcium & iron",
                 "availability": "FirstCry, Amazon, modern trade", "price": "₹180-250 per pack"},
                {"name": "MTR Ready to Eat Poha", "brand": "MTR", "type": "Traditional Ready Meal", "score": 85,
                 "benefits": "Authentic taste, preservative-free, convenient",
                 "availability": "Supermarkets, online groceries", "price": "₹40-60 per pack"}
            ],
            "fruit_drinks": [
                {"name": "Paper Boat Aam Ras", "brand": "Paper Boat", "type": "Natural Fruit Drink", "score": 90,
                 "benefits": "Real mango pulp, no artificial colors, traditional taste",
                 "availability": "Modern Trade, BigBasket, Swiggy Instamart", "price": "₹25-35 per 250ml"},
                {"name": "Real Activ Mango", "brand": "Dabur Real", "type": "Fruit Juice", "score": 85,
                 "benefits": "100% fruit juice, vitamin C, no added sugar variant available",
                 "availability": "Supermarkets, local stores", "price": "₹120-150 per 1L"},
                {"name": "Raw Pressery Cold Pressed", "brand": "Raw Pressery", "type": "Premium Juice", "score": 92,
                 "benefits": "Cold-pressed, no preservatives, high nutritional value",
                 "availability": "Premium stores, Zomato, online", "price": "₹180-250 per 250ml"}
            ],
            "beverages": [
                {"name": "Amul Buttermilk Masala Chaas", "brand": "Amul", "type": "Traditional Drink", "score": 88,
                 "benefits": "Probiotics, cooling effect, aids digestion, ready to drink",
                 "availability": "All retail stores, modern trade", "price": "₹15-20 per 200ml"},
                {"name": "Paper Boat Jaljeera", "brand": "Paper Boat", "type": "Traditional Drink", "score": 85,
                 "benefits": "Natural spices, mint, cumin - digestive and refreshing",
                 "availability": "Modern Trade, online stores", "price": "₹25-35 per 250ml"},
                {"name": "Organic India Tulsi Green Tea", "brand": "Organic India", "type": "Herbal Tea", "score": 90,
                 "benefits": "Antioxidants, immunity booster, organic certified",
                 "availability": "Health stores, Amazon, pharmacies", "price": "₹150-250 per pack"}
            ],
            "ice_cream": [
                {"name": "NOTO Low-Cal Ice Cream", "brand": "NOTO", "type": "Healthy Ice Cream", "score": 88,
                 "benefits": "50% less calories, high protein, no artificial sweeteners",
                 "availability": "Swiggy Instamart, Blinkit, BigBasket, select supermarkets", "price": "₹95-120 per 125ml"},
                {"name": "Amul Sugar-Free Lite Ice Cream", "brand": "Amul", "type": "Low-Calorie Dessert", "score": 82,
                 "benefits": "Sugar-free option, lower calories, calcium-rich",
                 "availability": "All supermarkets, local dairies, online platforms", "price": "₹40-60 per 90g"},
                {"name": "Vadilal Frozen Yogurt", "brand": "Vadilal", "type": "Frozen Yogurt", "score": 85,
                 "benefits": "Probiotic cultures, lower fat, natural ingredients",
                 "availability": "BigBasket, local stores, online groceries", "price": "₹60-90 per 100g"}
            ],
            "healthy_desserts": [
                {"name": "NOTO Low-Cal Ice Cream", "brand": "NOTO", "type": "Healthy Ice Cream", "score": 88,
                 "benefits": "50% less calories, high protein, no artificial sweeteners",
                 "availability": "Swiggy Instamart, Blinkit, BigBasket, select supermarkets", "price": "₹95-120 per 125ml"},
                {"name": "Amul Sugar-Free Lite Ice Cream", "brand": "Amul", "type": "Low-Calorie Dessert", "score": 82,
                 "benefits": "Sugar-free option, lower calories, calcium-rich",
                 "availability": "All supermarkets, local dairies, online platforms", "price": "₹40-60 per 90g"},
                {"name": "Yoga Bar Dark Chocolate", "brand": "Yoga Bar", "type": "Healthy Chocolate", "score": 85,
                 "benefits": "70% cocoa, no refined sugar, antioxidant-rich",
                 "availability": "Health stores, Amazon, modern trade", "price": "₹150-200 per bar"}
            ],
            "healthy_snacks": [
                {"name": "Cornitos Roasted Puffs", "brand": "Cornitos", "type": "Healthy Snacks", "score": 88,
                 "benefits": "Baked not fried, quinoa & oats based, high protein",
                 "availability": "Modern Trade, Nykaa, Amazon", "price": "₹150-200 per 150g"},
                {"name": "4700BC Gourmet Popcorn", "brand": "4700BC", "type": "Healthy Snacks", "score": 85,
                 "benefits": "Air-popped, whole grain, multiple flavors available",
                 "availability": "Supermarkets, online stores", "price": "₹180-250 per 100g"},
                {"name": "Happilo Premium Nuts", "brand": "Happilo", "type": "Nuts & Seeds", "score": 92,
                 "benefits": "Raw almonds, walnuts, cashews - protein rich",
                 "availability": "Modern Trade, Amazon, Flipkart", "price": "₹500-800 per kg"}
            ],
            "chocolates": [
                {"name": "Amul Dark Chocolate", "brand": "Amul", "type": "Dark Chocolate", "score": 85,
                 "benefits": "70% cocoa, antioxidants, less sugar than milk chocolate",
                 "availability": "All supermarkets, local stores", "price": "₹100-150 per 150g"},
                {"name": "Cadbury Bournville", "brand": "Cadbury", "type": "Dark Chocolate", "score": 82,
                 "benefits": "Rich cocoa, no added milk, premium taste",
                 "availability": "Widespread retail availability", "price": "₹120-180 per 80g"},
                {"name": "Raw Pressery Dates", "brand": "Raw Pressery", "type": "Natural Sweet", "score": 92,
                 "benefits": "Organic dates, natural sweetness, high fiber & minerals",
                 "availability": "Premium stores, online", "price": "₹250-350 per 250g"}
            ],
            "biscuits": [
                {"name": "Britannia NutriChoice Oats", "brand": "Britannia", "type": "Healthy Biscuits", "score": 78,
                 "benefits": "High fiber, multigrain, diabetes friendly",
                 "availability": "All supermarkets, local stores", "price": "₹40-60 per pack"},
                {"name": "Sunfeast Farmlite Digestive", "brand": "Sunfeast", "type": "Digestive Biscuits", "score": 75,
                 "benefits": "Wholemeal flour, digestive properties, fiber rich",
                 "availability": "Supermarkets, convenience stores", "price": "₹35-50 per pack"},
                {"name": "Yoga Bar Protein Cookies", "brand": "Yoga Bar", "type": "Protein Cookies", "score": 88,
                 "benefits": "12g protein, no refined sugar, almond flour based",
                 "availability": "Health stores, Amazon, gyms", "price": "₹150-200 per pack"}
            ],
            "healthy_sweets": [
                {"name": "Organic India Jaggery", "brand": "Organic India", "type": "Natural Sweetener", "score": 88,
                 "benefits": "Organic jaggery, iron rich, unrefined sugar alternative",
                 "availability": "Organic stores, Amazon", "price": "₹120-180 per kg"},
                {"name": "24 Mantra Organic Dates", "brand": "24 Mantra", "type": "Organic Dates", "score": 92,
                 "benefits": "Organic certification, natural sweetness, high fiber",
                 "availability": "Organic stores, modern trade", "price": "₹200-300 per 250g"},
                {"name": "Conscious Food Dry Fruits Laddu", "brand": "Conscious Food", "type": "Healthy Traditional", "score": 85,
                 "benefits": "No refined sugar, nuts & dates based, traditional recipe",
                 "availability": "Health stores, online organic stores", "price": "₹300-450 per pack"}
            ],
            "healthy_meals": [
                {"name": "Saffola Masala Oats", "brand": "Saffola", "type": "Healthy Instant", "score": 88,
                 "benefits": "High fiber, protein, low sodium, ready in 3 minutes",
                 "availability": "All supermarkets, online stores", "price": "₹150-200 per 500g"},
                {"name": "Slurrp Farm Ragi Noodles", "brand": "Slurrp Farm", "type": "Healthy Noodles", "score": 92,
                 "benefits": "Millet-based, no preservatives, high calcium & iron",
                 "availability": "FirstCry, Amazon, modern trade", "price": "₹180-250 per pack"},
                {"name": "MTR Ready to Eat Poha", "brand": "MTR", "type": "Traditional Ready Meal", "score": 85,
                 "benefits": "Authentic taste, preservative-free, convenient",
                 "availability": "Supermarkets, online groceries", "price": "₹40-60 per pack"}
            ]
        }
    
    def categorize_product(self, product_name: str, brand: str = "") -> CategoryResult:
        """Enhanced product categorization with better accuracy"""
        if not product_name:
            return CategoryResult("unknown", 0.0, "empty_input")
        
        full_text = f"{brand} {product_name}".strip().lower()
        
        # Step 1: Exact brand matching (highest accuracy)
        exact_result = self._match_exact_brand(full_text)
        if exact_result and exact_result.confidence > 0.8:
            return exact_result
        
        # Step 2: Category-specific keyword matching
        category_result = self._match_category_keywords(full_text, product_name)
        if category_result and category_result.confidence > 0.6:
            return category_result
        
        # Step 3: Fuzzy/partial matching
        fuzzy_result = self._fuzzy_match(full_text)
        if fuzzy_result:
            return fuzzy_result
        
        # Fallback
        return CategoryResult("processed_food", 0.3, "fallback")
    
    def _match_exact_brand(self, text: str) -> Optional[CategoryResult]:
        """Match against known brand patterns with better context validation"""
        best_match = None
        best_score = 0
        
        for category, data in self.categories.items():
            for brand in data["brands"]:
                if brand in text:
                    # Calculate match score based on brand + keyword context
                    score = len(brand)  # Longer brand names get higher base score
                    
                    # Boost score if category keywords also match
                    keyword_matches = [kw for kw in data["keywords"] if kw in text]
                    score += len(keyword_matches) * 3  # Keywords are important for disambiguation
                    
                    # Specific product validation for ambiguous brands
                    if brand == "amul":
                        # Amul disambiguation - ice cream vs milk/dairy
                        if any(w in text for w in ["ice cream", "icecream", "chocobar", "choco bar", "kulfi", "cone", "scoop", "frozen"]):
                            if category == "ice_cream":
                                score += 15  # Strong boost for ice cream
                            elif category == "dairy_beverages":
                                score -= 10  # Strong penalty for dairy_beverages
                        elif any(w in text for w in ["milk", "lassi", "buttermilk", "chaas", "dairy drink"]):
                            if category == "dairy_beverages":
                                score += 10
                            elif category == "ice_cream":
                                score -= 10
                        # Default slight preference for dairy if no clear context
                        elif category == "dairy_beverages":
                            score -= 3
                    
                    elif brand == "nestle":
                        # Nestle disambiguation
                        if any(w in text for w in ["maggi", "noodles", "instant"]):
                            if category == "instant_noodles":
                                score += 10  # Big boost for correct context
                        elif any(w in text for w in ["kitkat", "chocolate", "bar"]):
                            if category == "chocolates":
                                score += 10
                        elif any(w in text for w in ["milk", "dairy"]):
                            if category == "dairy_beverages":
                                score += 10
                        else:
                            score -= 5  # Penalty for no context
                    
                    elif brand == "pepsi" and "chips" in text:
                        # PepsiCo owns Lay's, but chips should go to snacks, not beverages
                        if category == "potato_chips":
                            score += 10
                        elif category == "carbonated_beverages":
                            score -= 5
                    
                    if score > best_score:
                        best_score = score
                        confidence = min(0.98, 0.8 + (score * 0.02))
                        
                        best_match = CategoryResult(
                            category=category,
                            confidence=confidence,
                            method="context_aware_brand_match",
                            matched_keywords=[brand] + keyword_matches,
                            subcategory=data.get("parent")
                        )
        
        return best_match
    
    def _match_category_keywords(self, text: str, original_name: str) -> Optional[CategoryResult]:
        """Enhanced keyword matching with scoring and exclusion support"""
        best_category = None
        best_score = 0
        best_matches = []
        
        for category, data in self.categories.items():
            score = 0
            matches = []
            
            # Check exclusion keywords first
            exclude_keywords = data.get("exclude_keywords", [])
            if any(excl in text for excl in exclude_keywords):
                continue  # Skip this category entirely
            
            # Score based on keyword presence and importance
            for keyword in data["keywords"]:
                if keyword in text:
                    # Longer keywords get higher scores
                    word_weight = len(keyword.split())
                    
                    # Exact match in original name gets bonus
                    if keyword in original_name.lower():
                        word_weight *= 2
                    
                    score += word_weight
                    matches.append(keyword)
            
            # Bonus for multiple matches
            if len(matches) > 1:
                score += len(matches) * 0.5
            
            if score > best_score:
                best_score = score
                best_category = category
                best_matches = matches
        
        if best_category and best_score > 1:
            confidence = min(0.9, 0.5 + (best_score * 0.1))
            
            return CategoryResult(
                category=best_category,
                confidence=confidence,
                method="enhanced_keyword_match",
                matched_keywords=best_matches,
                subcategory=self.categories[best_category].get("parent")
            )
        
        return None
    
    def _fuzzy_match(self, text: str) -> Optional[CategoryResult]:
        """Fuzzy matching for partial brand/keyword matches"""
        for category, data in self.categories.items():
            # Check for partial brand matches
            for brand in data["brands"]:
                brand_words = brand.split()
                if len(brand_words) > 1:
                    # Check if any part of multi-word brand matches
                    for word in brand_words:
                        if len(word) > 3 and word in text:
                            return CategoryResult(
                                category=category,
                                confidence=0.7,
                                method="fuzzy_brand_match",
                                matched_keywords=[word],
                                subcategory=data.get("parent")
                            )
        
        return None
    
    def get_alternatives_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Get healthy alternatives for a given product category"""
        if category not in self.categories:
            return []
        
        # Get the alternatives category mapping
        alt_category = self.categories[category].get("alternatives_category", "healthy_snacks")
        
        # Return alternatives from the mapping
        return self.alternatives_mapping.get(alt_category, [])

# Global instance
lightweight_categorizer = LightweightProductCategorizer()