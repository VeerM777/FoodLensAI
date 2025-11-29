"""
Enhanced health score calculator considering user profile and conditions
"""
from typing import Dict, Any, List, Optional

class HealthScoreCalculator:
    """Calculates personalized health scores"""
    
    def __init__(self):
        # Risk factors for different health conditions
        self.risk_factors = {
            "diabetes": {
                "high_risk": ["sugar", "carbohydrates", "glucose syrup"],
                "moderate_risk": ["starch", "honey", "corn syrup"]
            },
            "hypertension": {
                "high_risk": ["sodium", "salt", "msg"],
                "moderate_risk": ["preservatives", "nitrates"]
            },
            "celiac": {
                "high_risk": ["wheat", "barley", "rye"],
                "moderate_risk": ["oats", "malt"]
            },
            "lactose_intolerance": {
                "high_risk": ["milk", "cream", "whey"],
                "moderate_risk": ["lactose", "casein"]
            }
        }
        
        # BMI categories and their impact
        self.bmi_categories = {
            "underweight": {"range": (0, 18.5), "impact": -10},
            "normal": {"range": (18.5, 24.9), "impact": 0},
            "overweight": {"range": (25, 29.9), "impact": -15},
            "obese": {"range": (30, float('inf')), "impact": -25}
        }
    
    def calculate_score(
        self,
        nutritional_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        health_conditions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate personalized health score
        """
        base_score = 100
        adjustments = []
        
        # 1. Calculate BMI and its impact
        bmi_impact = self._calculate_bmi_impact(user_profile)
        if bmi_impact != 0:
            base_score += bmi_impact
            adjustments.append({
                "factor": "BMI",
                "impact": bmi_impact,
                "details": "BMI indicates need for weight management"
            })
        
        # 2. Analyze nutritional content
        nutrients = nutritional_data.get("nutrients", {})
        nutrient_impact = self._analyze_nutrients(nutrients, user_profile)
        base_score += nutrient_impact["score_impact"]
        adjustments.extend(nutrient_impact["adjustments"])
        
        # 3. Check health conditions
        if health_conditions:
            health_impact = self._analyze_health_conditions(
                health_conditions, 
                nutritional_data
            )
            base_score += health_impact["score_impact"]
            adjustments.extend(health_impact["adjustments"])
        
        # 4. Age-based adjustments
        age_impact = self._calculate_age_impact(user_profile.get("age", 30))
        if age_impact != 0:
            base_score += age_impact
            adjustments.append({
                "factor": "Age",
                "impact": age_impact,
                "details": "Age-specific nutritional needs considered"
            })
        
        # Ensure score stays within bounds
        final_score = max(0, min(100, base_score))
        
        return {
            "score": final_score,
            "adjustments": adjustments,
            "recommendation": self._get_recommendation(final_score)
        }
    
    def _calculate_bmi_impact(self, user_profile: Dict[str, Any]) -> int:
        """Calculate BMI impact on health score"""
        try:
            height_m = user_profile.get("height", 170) / 100
            weight_kg = user_profile.get("weight", 70)
            bmi = weight_kg / (height_m * height_m)
            
            for category, data in self.bmi_categories.items():
                if data["range"][0] <= bmi < data["range"][1]:
                    return data["impact"]
        except Exception:
            return 0
        return 0
    
    def _analyze_nutrients(
        self, 
        nutrients: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze nutritional content"""
        score_impact = 0
        adjustments = []
        
        # Sugar analysis
        sugar = nutrients.get("sugar", {}).get("value", 0)
        if sugar > 25:
            score_impact -= 20
            adjustments.append({
                "factor": "Sugar",
                "impact": -20,
                "details": "High sugar content"
            })
        
        # Sodium analysis
        sodium = nutrients.get("sodium", {}).get("value", 0)
        if sodium > 500:
            score_impact -= 15
            adjustments.append({
                "factor": "Sodium",
                "impact": -15,
                "details": "High sodium content"
            })
        
        # Protein analysis
        protein = nutrients.get("protein", {}).get("value", 0)
        if protein > 15:
            score_impact += 10
            adjustments.append({
                "factor": "Protein",
                "impact": 10,
                "details": "Good protein content"
            })
        
        # Fiber analysis
        fiber = nutrients.get("fiber", {}).get("value", 0)
        if fiber > 5:
            score_impact += 10
            adjustments.append({
                "factor": "Fiber",
                "impact": 10,
                "details": "Good fiber content"
            })
        
        return {
            "score_impact": score_impact,
            "adjustments": adjustments
        }
    
    def _analyze_health_conditions(
        self,
        conditions: List[str],
        nutritional_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze impact based on health conditions"""
        score_impact = 0
        adjustments = []
        
        ingredients_text = nutritional_data.get("ingredients_text", "").lower()
        nutrients = nutritional_data.get("nutrients", {})
        
        for condition in conditions:
            condition = condition.lower()
            if condition in self.risk_factors:
                # Check high risk ingredients
                for ingredient in self.risk_factors[condition]["high_risk"]:
                    if ingredient in ingredients_text:
                        score_impact -= 30
                        adjustments.append({
                            "factor": f"{condition.title()} Risk",
                            "impact": -30,
                            "details": f"Contains {ingredient} (high risk for {condition})"
                        })
                        break
                
                # Check moderate risk ingredients
                for ingredient in self.risk_factors[condition]["moderate_risk"]:
                    if ingredient in ingredients_text:
                        score_impact -= 15
                        adjustments.append({
                            "factor": f"{condition.title()} Risk",
                            "impact": -15,
                            "details": f"Contains {ingredient} (moderate risk for {condition})"
                        })
                        break
        
        return {
            "score_impact": score_impact,
            "adjustments": adjustments
        }
    
    def _calculate_age_impact(self, age: int) -> int:
        """Calculate age-based impact"""
        if age < 12:
            return -10  # Children need special consideration
        elif age > 60:
            return -5  # Elderly need special consideration
        return 0
    
    def _get_recommendation(self, score: float) -> Dict[str, str]:
        """Generate consumption recommendation based on score"""
        if score >= 80:
            return {
                "verdict": "RECOMMENDED",
                "frequency": "Can be consumed regularly",
                "portion_size": "Normal portion",
                "warning_level": "low"
            }
        elif score >= 60:
            return {
                "verdict": "MODERATE",
                "frequency": "2-3 times per week",
                "portion_size": "Moderate portion",
                "warning_level": "medium"
            }
        elif score >= 40:
            return {
                "verdict": "CAUTION",
                "frequency": "Once per week",
                "portion_size": "Small portion",
                "warning_level": "high"
            }
        else:
            return {
                "verdict": "NOT RECOMMENDED",
                "frequency": "Avoid or limit severely",
                "portion_size": "Minimal if consumed",
                "warning_level": "severe"
            }

# Global instance
health_calculator = HealthScoreCalculator()