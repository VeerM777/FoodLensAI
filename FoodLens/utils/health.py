"""
Health scoring and analysis utilities
"""
from typing import Dict, Any, List, Tuple
from config.settings import config
import re

class HealthAnalyzer:
    """Health analysis and scoring utilities"""
    
    # Ingredient quality penalties (higher = worse for health)
    HARMFUL_INGREDIENTS = {
        # Processed fats (very harmful)
        r'palm oil|palmolein|palm kernel': -30,
        r'hydrogenated|partially hydrogenated': -35,
        r'trans fat|transfat': -40,
        r'vegetable fat|vanaspati': -25,
        
        # Artificial additives (harmful)
        r'artificial flavor|artificial colour|artificial color': -15,
        r'sodium benzoate|potassium sorbate': -10,
        r'monosodium glutamate|msg|e621': -20,
        r'aspartame|sucralose|acesulfame': -12,
        r'high fructose corn syrup|hfcs': -25,
        r'tbhq|bha|bht': -15,
        
        # Processed sugars
        r'corn syrup|glucose syrup|invert sugar': -15,
        r'maltodextrin': -10,
    }
    
    # Natural/quality ingredient bonuses (lower penalties or bonuses)
    QUALITY_INGREDIENTS = {
        r'butter|milk fat|cream': 0,  # No penalty for natural dairy
        r'whole grain|whole wheat|oats': +10,
        r'olive oil|coconut oil|mustard oil': +5,
        r'natural flavor|natural colour': 0,
    }
    
    # Category-specific quality standards
    CATEGORY_STANDARDS = {
        'butter': {
            'name_patterns': [r'butter', r'makhan'],
            'required_ingredients': [r'butter', r'milk', r'cream', r'milk fat'],
            'forbidden_ingredients': [r'palm', r'vegetable', r'vanaspati'],
            'base_score_penalty': 0  # Natural butter has no base penalty
        },
        'spread': {
            'name_patterns': [r'spread', r'margarine'],
            'forbidden_ingredients': [],  # Spreads expected to have vegetable oils
            'base_score_penalty': -20  # Spreads are processed, lower base
        },
        'processed_food': {
            'base_score_penalty': -5
        },
        'natural_dairy': {
            'name_patterns': [r'milk', r'dahi', r'curd', r'paneer', r'cheese'],
            'base_score_penalty': 0
        }
    }
    
    @staticmethod
    def analyze_ingredient_quality(ingredients_text: str, product_name: str, category: str = None) -> Tuple[int, List[str], str]:
        """
        Analyze ingredient quality and return quality penalty score and list of concerns.
        Returns: (quality_penalty, concerns_list, quality_grade)
        
        Negative penalty = harmful, Positive = beneficial
        """
        if not ingredients_text or ingredients_text == "Ingredients not available - AI estimated nutrition":
            return 0, ["Ingredients not available for analysis"], "UNKNOWN"
        
        ingredients_lower = ingredients_text.lower()
        product_lower = product_name.lower()
        quality_penalty = 0
        concerns = []
        
        # Detect product category from name if not provided
        detected_category = category
        if not detected_category or detected_category == "unknown":
            if any(re.search(pattern, product_lower) for pattern in [r'butter', r'makhan']):
                if 'spread' not in product_lower and 'margarine' not in product_lower:
                    detected_category = 'butter'
                else:
                    detected_category = 'spread'
            elif any(re.search(pattern, product_lower) for pattern in [r'spread', r'margarine']):
                detected_category = 'spread'
        
        # Apply category-specific validation
        if detected_category == 'butter':
            # Real butter MUST have dairy ingredients
            has_dairy = any(re.search(pattern, ingredients_lower) 
                          for pattern in HealthAnalyzer.CATEGORY_STANDARDS['butter']['required_ingredients'])
            
            # Check for forbidden ingredients in butter
            has_forbidden = any(re.search(pattern, ingredients_lower) 
                              for pattern in HealthAnalyzer.CATEGORY_STANDARDS['butter']['forbidden_ingredients'])
            
            if has_forbidden:
                quality_penalty -= 40  # Severe penalty for fake "butter"
                concerns.append("⚠️ Product labeled as butter contains palm/vegetable oil - NOT REAL BUTTER")
                detected_category = 'spread'  # Reclassify as spread
            elif not has_dairy:
                quality_penalty -= 30
                concerns.append("⚠️ No dairy ingredients found - may not be real butter")
            else:
                quality_penalty += 10  # Bonus for real butter
                concerns.append("✓ Natural dairy butter - good fat source")
        
        # Check for harmful ingredients
        for pattern, penalty in HealthAnalyzer.HARMFUL_INGREDIENTS.items():
            if re.search(pattern, ingredients_lower):
                quality_penalty += penalty
                ingredient_match = re.search(pattern, ingredients_lower).group()
                concerns.append(f"⚠️ Contains {ingredient_match.title()} (harmful ingredient)")
        
        # Check for quality ingredients
        for pattern, bonus in HealthAnalyzer.QUALITY_INGREDIENTS.items():
            if re.search(pattern, ingredients_lower):
                quality_penalty += bonus
                if bonus > 0:
                    ingredient_match = re.search(pattern, ingredients_lower).group()
                    concerns.append(f"✓ Contains {ingredient_match.title()} (quality ingredient)")
        
        # Determine quality grade
        if quality_penalty >= 10:
            quality_grade = "EXCELLENT"
        elif quality_penalty >= 0:
            quality_grade = "GOOD"
        elif quality_penalty >= -20:
            quality_grade = "AVERAGE"
        elif quality_penalty >= -40:
            quality_grade = "POOR"
        else:
            quality_grade = "VERY_POOR"
        
        return quality_penalty, concerns, quality_grade
    
    @staticmethod
    def calculate_health_score(nutrition_data: Dict[str, Any], health_conditions: List[str] = None, 
                              ingredients_text: str = None, product_name: str = "", category: str = None) -> Dict[str, Any]:
        """
        Calculate health score based on nutritional data, ingredient quality, and health conditions
        Returns dict with score, breakdown, and quality analysis
        """
        if not nutrition_data:
            return {
                "score": 50,
                "breakdown": {"base": 50},
                "quality_grade": "UNKNOWN",
                "ingredient_concerns": []
            }
        
        # Correct category if product name suggests different category
        detected_category = category
        product_lower = product_name.lower()
        
        # Fix wrong categories from OpenFoodFacts
        if 'butter' in product_lower and 'peanut' not in product_lower and 'almond' not in product_lower:
            if 'spread' not in product_lower and 'margarine' not in product_lower:
                detected_category = 'butter'
                print(f"🔧 Category corrected: {category} → butter (product name contains 'butter')")
        elif 'ghee' in product_lower:
            detected_category = 'ghee'
            print(f"🔧 Category corrected: {category} → ghee")
        elif any(word in product_lower for word in ['spread', 'margarine', 'fat spread']):
            detected_category = 'spread'
            print(f"🔧 Category corrected: {category} → spread")
        
        # Step 1: Analyze ingredient quality FIRST (most important)
        ingredient_quality_penalty = 0
        ingredient_concerns = []
        quality_grade = "UNKNOWN"
        
        if ingredients_text:
            ingredient_quality_penalty, ingredient_concerns, quality_grade = HealthAnalyzer.analyze_ingredient_quality(
                ingredients_text, product_name, detected_category
            )
        
        # Step 2: Start with base score adjusted by ingredient quality
        score = 60 + ingredient_quality_penalty  # Ingredient quality is PRIMARY factor
        
        # Get nutritional values per 100g
        sugar = nutrition_data.get('sugars_100g', 0) or 0
        sodium = nutrition_data.get('sodium_100g', 0) or 0
        fiber = nutrition_data.get('fiber_100g', 0) or 0
        protein = nutrition_data.get('proteins_100g', 0) or 0
        saturated_fat = nutrition_data.get('saturated-fat_100g', 0) or 0
        
        # Sugar scoring (lower is better) - stricter for beverages
        if sugar <= 2:
            score += 10
        elif sugar <= 5:
            score += 5
        elif sugar <= 8:
            score -= 5
        elif sugar <= 12:
            score -= 15
        elif sugar <= 20:
            score -= 25
        else:
            score -= 35  # Very high sugar penalty
        
        # Sodium scoring (lower is better)
        sodium_mg = sodium * 1000 if sodium < 10 else sodium  # Convert to mg if needed
        if sodium_mg <= 140:
            score += 10
        elif sodium_mg <= 300:
            score += 5
        elif sodium_mg <= 600:
            score += 0
        else:
            score -= 10
        
        # Fiber scoring (higher is better)
        if fiber >= 6:
            score += 10
        elif fiber >= 3:
            score += 5
        elif fiber >= 1:
            score += 2
        
        # Protein scoring (higher is better)
        if protein >= 10:
            score += 8
        elif protein >= 5:
            score += 4
        elif protein >= 2:
            score += 2
        
        # Saturated fat scoring (CONTEXT-AWARE: natural dairy vs processed)
        is_natural_dairy = detected_category in ['butter', 'ghee', 'dairy', 'cheese', 'milk']
        has_palm_oil = ingredients_text and ('palm' in ingredients_text.lower())
        
        if is_natural_dairy and not has_palm_oil:
            # Natural dairy: Saturated fat is less harmful (contains beneficial nutrients)
            print(f"🥛 Natural dairy detected - applying reduced saturated fat penalty")
            if saturated_fat > 60:
                score -= 5  # Minimal penalty for natural dairy
            elif saturated_fat > 50:
                score -= 3
            # No penalty below 50g for natural dairy butter/ghee
        else:
            # Processed products or palm oil: Standard penalties
            if saturated_fat <= 1.5:
                score += 5
            elif saturated_fat <= 5:
                score += 2
            elif saturated_fat > 20:
                score -= 15
            elif saturated_fat > 10:
                score -= 10
        
        # Apply health condition penalties (personalized scoring)
        health_condition_penalties = []
        if health_conditions:
            print(f"👤 Applying health condition adjustments for: {health_conditions}")
            for condition in health_conditions:
                condition_lower = condition.lower()
                if 'diabetes' in condition_lower or 'prediabetes' in condition_lower:
                    if sugar > 15:
                        score -= 25
                        health_condition_penalties.append("High sugar - dangerous for diabetes")
                    elif sugar > 5:
                        score -= 10
                        health_condition_penalties.append("Moderate sugar - monitor blood glucose")
                elif 'hypertension' in condition_lower or 'blood pressure' in condition_lower:
                    if sodium_mg > 600:
                        score -= 25
                        health_condition_penalties.append("High sodium - may raise blood pressure")
                    elif sodium_mg > 300:
                        score -= 15
                        health_condition_penalties.append("Moderate sodium - monitor blood pressure")
                elif 'heart' in condition_lower or 'cholesterol' in condition_lower:
                    if saturated_fat > 15 and not is_natural_dairy:
                        score -= 20
                        health_condition_penalties.append("High saturated fat - may affect cholesterol")
                    elif saturated_fat > 10:
                        score -= 10
                elif 'kidney' in condition_lower:
                    if protein > 15:
                        score -= 15
                        health_condition_penalties.append("High protein - may stress kidneys")
        
        # Ensure score is within bounds
        final_score = max(0, min(100, score))
        
        # Return comprehensive result
        return {
            "score": final_score,
            "breakdown": {
                "ingredient_quality": ingredient_quality_penalty,
                "base": 60,
                "sugar": sugar,
                "sodium": sodium_mg,
                "fiber": fiber,
                "protein": protein,
                "saturated_fat": saturated_fat
            },
            "quality_grade": quality_grade,
            "ingredient_concerns": ingredient_concerns
        }
    
    @staticmethod
    def calculate_beverage_health_score(nutrition_data: Dict[str, Any], beverage_type: str = "carbonated", 
                                       health_conditions: List[str] = None, ingredients_text: str = None, 
                                       product_name: str = "") -> Dict[str, Any]:
        """
        Special health scoring for beverages with stricter sugar penalties
        """
        if not nutrition_data:
            return {
                "score": 30,
                "breakdown": {"base": 30},
                "quality_grade": "POOR",
                "ingredient_concerns": ["Beverage - typically high sugar"]
            }
            
        score = 40  # Lower base score for beverages
        
        # Get nutritional values per 100ml
        sugar = nutrition_data.get('sugars_100g', 0) or 0
        sodium = nutrition_data.get('sodium_100g', 0) or 0
        
        # Very strict sugar scoring for beverages
        if sugar <= 1:
            score += 15
        elif sugar <= 3:
            score += 5  
        elif sugar <= 6:
            score -= 10
        elif sugar <= 10:
            score -= 20
        else:
            score -= 30  # Coca Cola falls here (10.6g)
        
        # Carbonated beverages get additional penalty
        if beverage_type == "carbonated":
            score -= 15  # Additional penalty for carbonation
            
        # Sodium scoring
        sodium_mg = sodium * 1000 if sodium < 10 else sodium
        if sodium_mg <= 50:
            score += 5
        elif sodium_mg <= 140:
            score += 2
        
        # Health condition penalties (stricter for beverages)
        if health_conditions:
            for condition in health_conditions:
                condition_lower = condition.lower()
                if 'diabetes' in condition_lower and sugar > 5:
                    score -= 25
        
        # Analyze ingredients for beverages too
        ingredient_concerns = []
        quality_grade = "AVERAGE"
        if ingredients_text:
            _, ingredient_concerns, quality_grade = HealthAnalyzer.analyze_ingredient_quality(
                ingredients_text, product_name, "beverage"
            )
        
        final_score = max(0, min(100, score))
        return {
            "score": final_score,
            "breakdown": {
                "base": 40,
                "sugar": sugar,
                "sodium": sodium_mg,
                "beverage_type": beverage_type
            },
            "quality_grade": quality_grade,
            "ingredient_concerns": ingredient_concerns
        }
    
    @staticmethod
    def get_verdict(health_score: int, health_conditions: List[str] = None) -> Dict[str, str]:
        """
        Get consumption verdict based on health score (STRICTER STANDARDS)
        80+ = Good, 70-79 = Moderate, <70 = Avoid/Not Recommended
        """
        if health_score >= config.HEALTH_SCORE_THRESHOLDS["excellent"]:
            return {
                "title": "Good Choice",
                "subtitle": "This product meets high nutritional standards and is safe for regular consumption. Great for your health!",
                "action": "CONSUME"
            }
        elif health_score >= config.HEALTH_SCORE_THRESHOLDS["good"]:
            return {
                "title": "Moderate Choice",
                "subtitle": "Acceptable for occasional consumption. Limit portion size and frequency. Balance with healthier options.",
                "action": "MODERATE"
            }
        elif health_score >= config.HEALTH_SCORE_THRESHOLDS["average"]:
            return {
                "title": "Not Recommended",
                "subtitle": "Below optimal nutritional standards. Consume rarely in minimal portions. Consider healthier alternatives.",
                "action": "AVOID"
            }
        elif health_score >= config.HEALTH_SCORE_THRESHOLDS["poor"]:
            return {
                "title": "Avoid",
                "subtitle": "Poor nutritional profile with potential health concerns. Strongly recommend choosing healthier alternatives.",
                "action": "AVOID"
            }
        else:
            return {
                "title": "Strongly Avoid",
                "subtitle": "Very poor nutritional value with significant health risks. Do not consume regularly.",
                "action": "AVOID"
            }
    
    @staticmethod
    def get_consumption_advice(product_type: str, health_score: int, health_conditions: List[str] = None) -> str:
        """
        Get specific consumption advice based on product type and health profile (STRICTER STANDARDS)
        """
        # Special advice for beverages
        if product_type in ["carbonated_beverage", "beverage"] or "beverage" in product_type:
            if health_score >= 80:
                return "Good beverage choice - safe for regular consumption in moderate amounts"
            elif health_score >= 70:
                return "Acceptable for occasional consumption only - limit portions and frequency"
            elif health_score >= 50:
                return "Not recommended for regular consumption. High sugar/additives present. Choose water or natural alternatives."
            else:
                return "Avoid this beverage. Very high sugar and harmful additives. Opt for water, coconut water, or fresh juice instead."
        
        # Regular food advice
        if health_score >= 80:
            return "Excellent choice - enjoy as part of your regular balanced diet"
        elif health_score >= 70:
            return "Acceptable for occasional consumption - limit portion size and frequency"
        elif health_score >= 50:
            return "Not recommended - consume rarely in small portions. Consider healthier alternatives."
        else:
            return "Avoid regular consumption - poor nutritional profile. Choose healthier alternatives for better health."

# Global instance
health_analyzer = HealthAnalyzer()