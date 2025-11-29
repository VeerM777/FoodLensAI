"""
Enhanced Product Categorizer using multiple ML approaches
Combines pattern matching, semantic similarity, and zero-shot classification
"""
import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Try to import ML libraries with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

@dataclass
class CategoryResult:
    """Result from categorization with confidence and method used"""
    category: str
    confidence: float
    method: str
    subcategory: Optional[str] = None
    matched_keywords: List[str] = None

class EnhancedProductCategorizer:
    """
    Advanced product categorizer using multiple ML techniques:
    1. Rule-based pattern matching (fast fallback)
    2. Semantic similarity with sentence transformers
    3. Zero-shot classification with transformers
    4. Ensemble voting for final decision
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Comprehensive Indian food/beverage categories
        self.categories = {
            # Beverages
            "fruit_juices": ["mango juice", "orange juice", "apple juice", "mixed fruit", "fruit drink", "juice"],
            "carbonated_drinks": ["cola", "pepsi", "coca cola", "sprite", "fanta", "soda", "carbonated", "soft drink"],
            "dairy_beverages": ["milk", "lassi", "buttermilk", "flavored milk", "dairy drink"],
            "tea_coffee": ["tea", "coffee", "chai", "green tea", "black tea", "instant coffee"],
            "energy_drinks": ["energy drink", "sports drink", "glucose", "electrolyte"],
            "water": ["water", "mineral water", "packaged water"],
            
            # Snacks
            "chips_crisps": ["chips", "potato chips", "banana chips", "crisps", "wafers"],
            "namkeen": ["namkeen", "bhujia", "sev", "mixture", "chivda", "mathri"],
            "biscuits_cookies": ["biscuit", "cookie", "cracker", "rusk", "toast"],
            "nuts_dried_fruits": ["almonds", "cashew", "peanuts", "dry fruits", "nuts", "raisins"],
            
            # Confectionery
            "chocolates": ["chocolate", "cocoa", "dark chocolate", "milk chocolate"],
            "candies_sweets": ["candy", "sweet", "toffee", "lollipop", "gum", "mint"],
            "traditional_sweets": ["laddu", "barfi", "halwa", "gulab jamun", "rasgulla"],
            
            # Spreads & Condiments
            "spreads": ["jam", "jelly", "honey", "peanut butter", "chocolate spread", "nutella"],
            "pickles_chutneys": ["pickle", "chutney", "sauce", "ketchup", "mayonnaise"],
            
            # Instant Foods
            "instant_noodles": ["noodles", "maggi", "pasta", "vermicelli", "instant noodles"],
            "ready_to_eat": ["ready to eat", "instant", "popcorn", "instant food"],
            
            # Dairy Products
            "dairy_products": ["cheese", "butter", "ghee", "yogurt", "curd", "paneer"],
            
            # Cereals & Grains
            "breakfast_cereals": ["cereal", "cornflakes", "oats", "muesli", "granola"],
            "rice_grains": ["rice", "wheat", "flour", "grain", "quinoa"],
            
            # Cooking Ingredients
            "spices_seasonings": ["spice", "masala", "turmeric", "pepper", "salt", "seasoning"],
            "oils_ghee": ["oil", "ghee", "cooking oil", "coconut oil", "mustard oil"],
            
            # Health Foods
            "health_supplements": ["protein", "vitamin", "supplement", "health drink", "nutrition"],
            "organic_natural": ["organic", "natural", "fresh", "pure"],
        }
        
        # Brand to category mapping (Indian brands)
        self.brand_category_map = {
            # Beverages
            "frooti": "fruit_juices", "maaza": "fruit_juices", "slice": "fruit_juices",
            "real": "fruit_juices", "tropicana": "fruit_juices", "minute maid": "fruit_juices",
            "coca cola": "carbonated_drinks", "pepsi": "carbonated_drinks", "thums up": "carbonated_drinks",
            "sprite": "carbonated_drinks", "fanta": "carbonated_drinks", "limca": "carbonated_drinks",
            "amul": "dairy_beverages", "mother dairy": "dairy_beverages",
            "tata tea": "tea_coffee", "red label": "tea_coffee", "taj mahal": "tea_coffee",
            "nescafe": "tea_coffee", "bru": "tea_coffee",
            
            # Snacks
            "lays": "chips_crisps", "kurkure": "chips_crisps", "bingo": "chips_crisps",
            "haldiram": "namkeen", "bikaji": "namkeen", "sagar": "namkeen",
            "parle g": "biscuits_cookies", "britannia": "biscuits_cookies", "sunfeast": "biscuits_cookies",
            "oreo": "biscuits_cookies", "monaco": "biscuits_cookies",
            
            # Confectionery
            "dairy milk": "chocolates", "kit kat": "chocolates", "5 star": "chocolates",
            "snickers": "chocolates", "toblerone": "chocolates", "ferrero rocher": "chocolates",
            "cadbury": "chocolates", "nestle": "chocolates",
            
            # Instant Foods
            "maggi": "instant_noodles", "yippee": "instant_noodles", "top ramen": "instant_noodles",
            "knorr": "instant_noodles", "ching's": "instant_noodles",
            
            # Others
            "kissan": "spreads", "mapro": "spreads", "nutella": "spreads",
            "mtr": "ready_to_eat", "gits": "ready_to_eat", "ashirvaad": "rice_grains",
            "fortune": "oils_ghee", "sundrop": "oils_ghee", "saffola": "oils_ghee",
        }
        
        # Initialize ML models
        self._init_ml_models()
        
    def _init_ml_models(self):
        """Initialize machine learning models with fallbacks"""
        self.sentence_model = None
        self.zero_shot_classifier = None
        
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                # Use a lightweight, multilingual model for semantic similarity
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("✅ Sentence Transformer model loaded")
                
                # Precompute category embeddings for fast similarity search
                self._precompute_category_embeddings()
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load Sentence Transformer: {e}")
        
        try:
            if TRANSFORMERS_AVAILABLE:
                # Use DistilBERT for zero-shot classification
                self.zero_shot_classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",  # Good for zero-shot
                    device=-1  # Use CPU
                )
                self.logger.info("✅ Zero-shot classifier loaded")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load zero-shot classifier: {e}")
    
    def _precompute_category_embeddings(self):
        """Precompute embeddings for all categories for fast similarity search"""
        if not self.sentence_model:
            return
        
        try:
            category_texts = []
            self.category_names = []
            
            for category, keywords in self.categories.items():
                # Create category description
                category_text = f"{category.replace('_', ' ')}: {', '.join(keywords[:5])}"
                category_texts.append(category_text)
                self.category_names.append(category)
            
            # Compute embeddings
            self.category_embeddings = self.sentence_model.encode(category_texts)
            self.logger.info(f"✅ Precomputed embeddings for {len(category_texts)} categories")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not precompute category embeddings: {e}")
            self.category_embeddings = None
    
    def categorize_product(self, product_name: str, brand: str = "") -> CategoryResult:
        """
        Categorize product using ensemble of methods
        Returns the best category with confidence score
        """
        if not product_name:
            return CategoryResult("unknown", 0.0, "empty_input")
        
        product_text = f"{brand} {product_name}".strip().lower()
        
        # Method 1: Brand-based categorization (highest confidence)
        brand_result = self._categorize_by_brand(brand.lower())
        
        # Method 2: Rule-based pattern matching
        rule_result = self._categorize_by_rules(product_text)
        
        # Method 3: Semantic similarity (if available)
        semantic_result = self._categorize_by_similarity(product_text)
        
        # Method 4: Zero-shot classification (if available)
        zero_shot_result = self._categorize_by_zero_shot(product_text)
        
        # Ensemble voting
        final_result = self._ensemble_vote([
            brand_result, rule_result, semantic_result, zero_shot_result
        ])
        
        return final_result
    
    def _categorize_by_brand(self, brand: str) -> Optional[CategoryResult]:
        """Categorize based on known brand mappings"""
        if not brand:
            return None
            
        # Direct brand match
        if brand in self.brand_category_map:
            return CategoryResult(
                category=self.brand_category_map[brand],
                confidence=0.95,
                method="brand_mapping",
                matched_keywords=[brand]
            )
        
        # Partial brand match
        for known_brand, category in self.brand_category_map.items():
            if known_brand in brand or brand in known_brand:
                return CategoryResult(
                    category=category,
                    confidence=0.85,
                    method="brand_partial",
                    matched_keywords=[known_brand]
                )
        
        return None
    
    def _categorize_by_rules(self, product_text: str) -> Optional[CategoryResult]:
        """Rule-based categorization with scoring"""
        best_category = None
        best_score = 0
        matched_keywords = []
        
        for category, keywords in self.categories.items():
            score = 0
            current_matches = []
            
            for keyword in keywords:
                if keyword in product_text:
                    # Weight longer keywords more
                    weight = len(keyword.split())
                    score += weight
                    current_matches.append(keyword)
            
            if score > best_score:
                best_score = score
                best_category = category
                matched_keywords = current_matches
        
        if best_category and best_score > 0:
            # Normalize confidence (rule-based is less reliable)
            confidence = min(0.8, 0.3 + (best_score * 0.1))
            return CategoryResult(
                category=best_category,
                confidence=confidence,
                method="rule_based",
                matched_keywords=matched_keywords
            )
        
        return None
    
    def _categorize_by_similarity(self, product_text: str) -> Optional[CategoryResult]:
        """Semantic similarity using sentence transformers"""
        if not self.sentence_model or not hasattr(self, 'category_embeddings'):
            return None
        
        try:
            # Get product embedding
            product_embedding = self.sentence_model.encode([product_text])
            
            # Calculate similarities
            similarities = np.dot(product_embedding, self.category_embeddings.T)[0]
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]
            
            if best_similarity > 0.3:  # Threshold for semantic similarity
                return CategoryResult(
                    category=self.category_names[best_idx],
                    confidence=min(0.9, best_similarity),
                    method="semantic_similarity"
                )
        except Exception as e:
            self.logger.warning(f"⚠️ Semantic similarity failed: {e}")
        
        return None
    
    def _categorize_by_zero_shot(self, product_text: str) -> Optional[CategoryResult]:
        """Zero-shot classification using transformers"""
        if not self.zero_shot_classifier:
            return None
        
        try:
            # Convert categories to human-readable labels
            candidate_labels = [cat.replace('_', ' ') for cat in self.categories.keys()]
            
            # Classify
            result = self.zero_shot_classifier(product_text, candidate_labels)
            
            if result['scores'][0] > 0.5:  # Confidence threshold
                # Convert back to category key
                predicted_label = result['labels'][0]
                predicted_category = predicted_label.replace(' ', '_')
                
                return CategoryResult(
                    category=predicted_category,
                    confidence=result['scores'][0],
                    method="zero_shot_classification"
                )
        except Exception as e:
            self.logger.warning(f"⚠️ Zero-shot classification failed: {e}")
        
        return None
    
    def _ensemble_vote(self, results: List[Optional[CategoryResult]]) -> CategoryResult:
        """Ensemble voting to combine results from multiple methods"""
        # Filter out None results
        valid_results = [r for r in results if r is not None]
        
        if not valid_results:
            return CategoryResult("unknown", 0.0, "no_classification")
        
        # Weight by confidence and method reliability
        method_weights = {
            "brand_mapping": 1.0,
            "brand_partial": 0.9,
            "zero_shot_classification": 0.8,
            "semantic_similarity": 0.7,
            "rule_based": 0.6
        }
        
        # Calculate weighted scores for each category
        category_scores = {}
        
        for result in valid_results:
            weight = method_weights.get(result.method, 0.5)
            weighted_score = result.confidence * weight
            
            if result.category not in category_scores:
                category_scores[result.category] = []
            category_scores[result.category].append((weighted_score, result))
        
        # Find best category
        best_category = None
        best_total_score = 0
        best_result = None
        
        for category, score_list in category_scores.items():
            # Take the maximum score for this category
            total_score = max(score[0] for score in score_list)
            
            if total_score > best_total_score:
                best_total_score = total_score
                best_category = category
                best_result = max(score_list, key=lambda x: x[0])[1]
        
        # Boost confidence if multiple methods agree
        if len([r for r in valid_results if r.category == best_category]) > 1:
            best_result.confidence = min(0.95, best_result.confidence + 0.1)
            best_result.method += "_ensemble"
        
        return best_result or CategoryResult("unknown", 0.0, "ensemble_failed")
    
    def get_category_alternatives_mapping(self) -> Dict[str, List[str]]:
        """Return mapping for alternative suggestion"""
        return {
            # Beverages - suggest healthier alternatives within same category
            "fruit_juices": ["fresh_fruits", "coconut_water", "fresh_lime_water"],
            "carbonated_drinks": ["fruit_juices", "coconut_water", "herbal_tea"],
            "dairy_beverages": ["plant_milk", "coconut_milk", "fresh_juice"],
            
            # Snacks - suggest healthier alternatives
            "chips_crisps": ["nuts_dried_fruits", "roasted_chana", "fresh_fruits"],
            "namkeen": ["nuts_dried_fruits", "roasted_seeds", "homemade_snacks"],
            "biscuits_cookies": ["nuts_dried_fruits", "fresh_fruits", "oats_cookies"],
            
            # Confectionery - suggest healthier sweets
            "chocolates": ["dark_chocolate", "nuts_dried_fruits", "fresh_fruits"],
            "candies_sweets": ["fresh_fruits", "dates", "nuts_dried_fruits"],
            "traditional_sweets": ["fresh_fruits", "dates", "homemade_sweets"],
            
            # Default alternatives
            "default": ["fresh_fruits", "nuts_dried_fruits", "herbal_tea", "coconut_water"]
        }

# Global instance for backward compatibility
enhanced_categorizer = EnhancedProductCategorizer()