from .health_advice import get_condition_advice

def format_analysis_response(product_data, health_analysis, alternatives_result, fssai_compliance, user_profile):
    """
    Format the analysis response into clear, separate sections
    """
    product_name = product_data.get("product_name", "Unknown Product")
    
    # 1. Main Analysis Section
    main_analysis = f"""
==================================
🍽️ **Product Analysis Report**
==================================

📋 **Basic Information**
Product: {product_name}
Brand: {product_data.get('brand', 'Not specified')}
Category: {product_data.get('categories', '').split(',')[0].strip().title() or product_data.get('product_type', '').title()}

📊 **Health Assessment**
• Health Score: {health_analysis['health_score']}/100
• Verdict: {health_analysis['verdict']['title']}
• Recommendation: {health_analysis['consumption_advice']}

❗ **Key Health Insights**
{chr(10).join(health_analysis.get('health_warnings', ['No major health concerns identified']))}

💪 **Nutritional Profile**
{chr(10).join([f"• {aspect}" for aspect in product_data.get('nutritional_highlights', {}).get('positive_aspects', ['No significant nutritional benefits identified'])])}

🏥 **FSSAI Compliance**
• Status: {fssai_compliance['regulatory_status']}
• Safety Rating: {fssai_compliance['food_safety_rating']}
• Key Requirements:
{chr(10).join([f"  - {rec}" for rec in fssai_compliance['fssai_recommendations']])}
"""

    # 2. Alternatives Analysis Section (completely separate)
    alternatives_section = """
==================================
🔄 **Healthier Alternatives**
==================================
"""
    
    better_alternatives = [alt for alt in alternatives_result.get('alternatives', []) 
                         if alt['health_score'] > health_analysis['health_score']]
    better_alternatives.sort(key=lambda x: x['health_score'], reverse=True)

    if better_alternatives:
        alternatives_section += "\nScientifically Verified Better Options:\n"
        for i, alt in enumerate(better_alternatives[:5], 1):
            improvement = alt['health_score'] - health_analysis['health_score']
            alternatives_section += f"""
----------------------------------------------
{i}. {alt['name']} ({alt['brand']})
----------------------------------------------
▸ Health Score: {alt['health_score']}/100 ({improvement:+.0f} points better)
▸ Key Benefits: {alt['health_benefits']}
▸ Price Range: {alt['price']}
▸ Where to Buy: {alt['where_to_buy']}

Why This is Healthier:
• {improvement} points higher health score
• Better nutritional profile
• {alt.get('fssai_status', 'FSSAI compliant')}
• {', '.join(alt.get('key_advantages', ['Healthier ingredients']))}
"""
    else:
        alternatives_section += "\nℹ️ No significantly healthier alternatives found in this category.\nConsider exploring different food categories for healthier options.\n"

    # 3. Personal Health Notes Section
    health_notes_section = """
==================================
💡 **Personal Health Notes**
==================================
"""
    
    if user_profile.get('health_conditions'):
        health_notes_section += "\nBased on your health conditions:\n"
        for condition in user_profile['health_conditions']:
            health_notes_section += f"• {condition}: {get_condition_advice(condition, health_analysis)}\n"
    else:
        health_notes_section += "\nNo specific health conditions noted. For personalized advice, update your health profile.\n"

    # Combine all sections with clear separation
    complete_analysis = f"""
{main_analysis}

{alternatives_section}

{health_notes_section}
"""

    return complete_analysis