def get_condition_advice(condition: str, health_analysis: dict) -> str:
    """Get specific advice based on health condition"""
    condition = condition.lower()
    
    if 'diabetes' in condition:
        sugar_content = health_analysis.get('nutritional_breakdown', {}).get('sugar_content', {})
        if sugar_content.get('assessment') == 'High':
            return "High sugar content - consider alternatives with lower sugar"
        return "Sugar content is within acceptable range"
        
    if 'hypertension' in condition or 'blood pressure' in condition:
        sodium_content = health_analysis.get('nutritional_breakdown', {}).get('sodium_content', {})
        if sodium_content.get('assessment') == 'High':
            return "High sodium content - look for low-sodium alternatives"
        return "Sodium content is within acceptable range"
        
    if 'heart' in condition:
        fat_content = health_analysis.get('nutritional_breakdown', {}).get('fat_content', {})
        if fat_content and fat_content.get('assessment') == 'High':
            return "High fat content - consider heart-healthy alternatives"
        return "Fat content is within acceptable range"
        
    if 'celiac' in condition or 'gluten' in condition:
        if 'gluten' in str(health_analysis.get('ingredients_text', '')).lower():
            return "Contains gluten - avoid this product"
        return "No obvious gluten content detected"
        
    return "No specific concerns for this condition"