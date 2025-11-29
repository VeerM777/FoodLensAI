"""
Health scoring and analysis utilities
"""
from typing import Dict, Any, List
from config.settings import config

class HealthAnalyzer:
    """Health analysis and scoring utilities"""
    
    @staticmethod
    def calculate_health_score(nutrition_data: Dict[str, Any], health_conditions: List[str] = None) -> int:
        """
        Calculate health score based on nutritional data and health conditions
        Returns score from 0-100
        """
        if not nutrition_data:
            return 50  # Default middle score
            
        score = 60  # Base score
        
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
        
        # Saturated fat scoring (lower is better)
        if saturated_fat <= 1.5:
            score += 5
        elif saturated_fat <= 5:
            score += 2
        elif saturated_fat > 10:
            score -= 10
        
        # Apply health condition penalties
        if health_conditions:
            for condition in health_conditions:
                condition_lower = condition.lower()
                if 'diabetes' in condition_lower:
                    if sugar > 15:
                        score -= 20
                    if sodium_mg > 400:
                        score -= 10
                elif 'hypertension' in condition_lower or 'blood pressure' in condition_lower:
                    if sodium_mg > 300:
                        score -= 20
                elif 'heart' in condition_lower:
                    if saturated_fat > 5:
                        score -= 15
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_beverage_health_score(nutrition_data: Dict[str, Any], beverage_type: str = "carbonated", health_conditions: List[str] = None) -> int:
        """
        Special health scoring for beverages with stricter sugar penalties
        """
        if not nutrition_data:
            return 30  # Lower default for beverages
            
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
        
        return max(0, min(100, score))
    
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