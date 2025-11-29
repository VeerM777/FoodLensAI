"""
Health analysis and alternatives recommendation agents
"""
from typing import Dict, Any, List
from utils.health import health_analyzer
from utils.search import search_utils

class HealthScoreAgent:
    """Calculates health scores and provides consumption recommendations"""
    
    @staticmethod
    def analyze_health_impact(product_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze health impact and generate score with recommendations
        """
        print("--- 🏥 Health Score Agent ---")
        
        # Extract data
        nutriments = product_data.get("nutriments", {})
        product_name = product_data.get("product_name", "Unknown Product")
        health_conditions = user_profile.get("health_conditions", [])
        
        print(f"📊 Analyzing health impact for: {product_name}")
        print(f"🏥 Health conditions: {health_conditions}")
        
        # Calculate health score - use special scoring for beverages
        product_type = product_data.get("product_type", "processed_food")
        if product_type in ["carbonated_beverage", "beverage"] or "beverage" in product_type:
            health_score = health_analyzer.calculate_beverage_health_score(
                nutriments, "carbonated" if "carbonated" in product_type else "beverage", health_conditions
            )
            print(f"🥤 Using beverage-specific scoring for {product_type}")
        else:
            health_score = health_analyzer.calculate_health_score(nutriments, health_conditions)
        
        # Get verdict
        verdict = health_analyzer.get_verdict(health_score, health_conditions)
        
        # Get consumption advice
        product_type = product_data.get("product_type", "processed_food")
        consumption_advice = health_analyzer.get_consumption_advice(
            product_type, health_score, health_conditions
        )
        
        # Determine if should consume
        should_consume = health_score >= 50
        
        print(f"📊 Health Score: {health_score}/100")
        print(f"📋 Verdict: {verdict['title']}")
        print(f"💡 Advice: {consumption_advice}")
        
        return {
            "health_score": health_score,
            "verdict": verdict,
            "should_consume": should_consume,
            "consumption_advice": consumption_advice,
            "analysis_summary": f"Health Score: {health_score}/100 - {verdict['title']}"
        }

class AlternativesAgent:
    """Provides AI-powered healthier product alternatives using category-specific prompts"""
    
    @staticmethod
    def find_alternatives(product_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find healthier alternatives using AI model with category-specific prompts
        """
        print("--- 🔍 AI-Powered Alternatives Recommendation Agent ---")
        
        product_name = product_data.get("product_name", "")
        product_type = product_data.get("product_type", "processed_food")
        health_conditions = user_profile.get("health_conditions", [])
        user_tier = user_profile.get("tier", "free")
        nutriments = product_data.get("nutriments", {})
        
        print(f"🛒 Finding alternatives for: {product_name}")
        print(f"📂 Product type: {product_type}")
        print(f"👤 User tier: {user_tier}")
        
        alternatives = []
        
        # Only provide alternatives for premium users
        if user_tier == "premium":
            try:
                # Get enhanced categorization result
                from utils.lightweight_categorizer import lightweight_categorizer
                
                # Get detailed category info - try to extract brand from product name or use brand from product_data
                brand = product_data.get("brand", "")
                if not brand:
                    # Try to detect brand from product name
                    if "parle" in product_name.lower() or "hide" in product_name.lower():
                        brand = "Parle"
                    elif "britannia" in product_name.lower():
                        brand = "Britannia"
                    elif "cadbury" in product_name.lower():
                        brand = "Cadbury"
                    elif "nestle" in product_name.lower() or "maggi" in product_name.lower():
                        brand = "Nestle"
                    elif "lay" in product_name.lower():
                        brand = "Lay's"
                
                category_result = lightweight_categorizer.categorize_product(product_name, brand)
                detailed_category = category_result.category if category_result else product_type
                confidence = category_result.confidence if category_result else 0.5
                
                print(f"🎯 Enhanced category: {detailed_category} (confidence: {confidence:.2f}) [brand: {brand}]")
                
                # Generate AI prompt based on category and product details
                ai_prompt = AlternativesAgent._generate_category_specific_prompt(
                    product_name, detailed_category, nutriments, health_conditions
                )
                
                print(f"🤖 Generated AI prompt for category: {detailed_category}")
                
                # Get AI-generated alternatives
                alternatives = AlternativesAgent._get_ai_alternatives(ai_prompt)
                
                if alternatives:
                    print(f"✅ AI generated {len(alternatives)} alternatives")
                else:
                    print("🔄 AI alternatives failed, using fallback")
                    alternatives = AlternativesAgent._get_generic_alternatives(detailed_category)
                    
            except Exception as e:
                print(f"⚠️ AI alternatives failed: {e}")
                alternatives = AlternativesAgent._get_generic_alternatives(product_type)
        else:
            print("🔒 AI-powered alternatives available for premium users only")
        
        return {
            "alternatives": alternatives,
            "alternatives_source": "AI Model with Category-Specific Prompting" if alternatives else "None",
            "total_found": len(alternatives),
            "enhanced_category": detailed_category if 'detailed_category' in locals() else product_type
        }
    
    @staticmethod
    def _generate_category_specific_prompt(product_name: str, category: str, nutriments: Dict[str, Any], health_conditions: List[str]) -> str:
        """Generate detailed category-specific prompt for AI model"""
        
        # Extract key nutritional info
        calories = nutriments.get("energy-kcal_100g", "Unknown")
        sugar = nutriments.get("sugars_100g", "Unknown") 
        fat = nutriments.get("fat_100g", "Unknown")
        protein = nutriments.get("proteins_100g", "Unknown")
        sodium = nutriments.get("sodium_100g", "Unknown")
        
        # Category-specific context and requirements
        category_contexts = {
            "mango_drinks": {
                "context": "fruit drinks and beverages in the Indian market",
                "focus": "natural fruit content, sugar levels, artificial additives",
                "alternatives_type": "natural fruit juices, fresh fruits, healthier beverages"
            },
            "potato_chips": {
                "context": "savory snacks and chips in the Indian market", 
                "focus": "oil content, sodium levels, processing method (fried vs baked)",
                "alternatives_type": "baked snacks, roasted nuts, healthier crunchy options"
            },
            "instant_noodles": {
                "context": "instant and convenience foods in the Indian market",
                "focus": "sodium content, preservatives, nutritional value, MSG",
                "alternatives_type": "healthier instant foods, oats, traditional quick meals"
            },
            "chocolates": {
                "context": "confectionery and sweet treats in the Indian market",
                "focus": "sugar content, cocoa percentage, artificial ingredients",
                "alternatives_type": "dark chocolate, natural sweets, traditional Indian sweets"
            },
            "biscuits": {
                "context": "biscuits and cookies in the Indian market",
                "focus": "refined flour, sugar content, trans fats, preservatives", 
                "alternatives_type": "whole grain biscuits, oat cookies, healthier snack options"
            },
            "carbonated_beverages": {
                "context": "soft drinks and carbonated beverages in the Indian market",
                "focus": "sugar content, artificial sweeteners, caffeine, preservatives",
                "alternatives_type": "natural drinks, coconut water, fresh lime water, herbal drinks"
            }
        }
        
        # Get category-specific context or use default
        cat_info = category_contexts.get(category, {
            "context": f"{category} products in the Indian market",
            "focus": "nutritional content, artificial additives, processing methods",
            "alternatives_type": "healthier versions of similar products"
        })
        
        # Health conditions context
        health_context = ""
        if health_conditions:
            health_context = f"\nIMPORTANT: The user has these health conditions: {', '.join(health_conditions)}. Prioritize alternatives that are suitable for these conditions."
        
        # Generate the detailed prompt
        prompt = f"""
You are a nutrition expert specializing in {cat_info['context']}. 

PRODUCT TO ANALYZE: {product_name}
CATEGORY: {category}
NUTRITIONAL INFO: Calories: {calories}/100g, Sugar: {sugar}g/100g, Fat: {fat}g/100g, Protein: {protein}g/100g, Sodium: {sodium}mg/100g
{health_context}

Please provide 3-5 healthier alternatives available in the Indian market. Focus on {cat_info['focus']}.

For each alternative, provide:
1. **Product Name** with specific brand if available
2. **Type/Category** (e.g., Baked Snack, Natural Juice, etc.)
3. **Health Score** (0-100 based on nutritional value)
4. **Key Benefits** (why it's healthier than {product_name})
5. **Price Range** in Indian Rupees (₹)
6. **Availability** (where to buy in India - online/offline)

Focus on {cat_info['alternatives_type']} that are:
- Actually available in Indian market
- Have better nutritional profile than {product_name}
- Suitable for the user's health conditions if any
- Reasonably priced and accessible

Format as JSON array with keys: name, brand, type, score, benefits, price, availability
"""
        
        return prompt.strip()
    
    @staticmethod
    def _get_ai_alternatives(prompt: str) -> List[Dict[str, Any]]:
        """Get alternatives from AI model using the detailed prompt"""
        try:
            # Get AI response from Gemini
            ai_response = AlternativesAgent._query_ai_model(prompt)
            
            if ai_response:
                print(f"🤖 Received AI response ({len(ai_response)} chars)")
                
                # Try to parse JSON response first
                try:
                    import json
                    if isinstance(ai_response, str):
                        # Extract JSON from markdown code blocks if present
                        if "```json" in ai_response:
                            json_start = ai_response.find("```json") + 7
                            json_end = ai_response.find("```", json_start)
                            ai_response = ai_response[json_start:json_end].strip()
                        
                        alternatives = json.loads(ai_response)
                        
                        # Validate structure
                        if isinstance(alternatives, list) and len(alternatives) > 0:
                            print(f"✅ Successfully parsed JSON with {len(alternatives)} alternatives")
                            return alternatives[:5]  # Max 5 alternatives
                    
                except json.JSONDecodeError as e:
                    print(f"🔄 JSON parsing failed, using text parser: {e}")
                
                # Fallback to text parsing since Gemini gives structured text, not JSON
                return AlternativesAgent._parse_text_response(ai_response)
            else:
                print("❌ No AI response received")
            
        except Exception as e:
            print(f"⚠️ AI query failed: {e}")
        
        return []
    
    @staticmethod
    def _query_ai_model(prompt: str) -> str:
        """Query the AI model (Gemini) with the detailed prompt"""
        try:
            # Use the existing search utils Gemini client
            from utils.search_utils_dynamic import SearchUtils
            
            # Create SearchUtils instance
            search_utils = SearchUtils()
            
            # Get Gemini client
            gemini_client = search_utils._get_gemini_client()
            
            if gemini_client:
                print("🤖 Querying Gemini model for alternatives...")
                
                # Generate response using langchain format
                from langchain_core.messages import HumanMessage
                response = gemini_client.invoke([HumanMessage(content=prompt)])
                
                if response and hasattr(response, 'content'):
                    return response.content
                
        except Exception as e:
            print(f"⚠️ Gemini query failed: {e}")
        
        return ""
    
    @staticmethod
    def _parse_text_response(text_response: str) -> List[Dict[str, Any]]:
        """Parse Gemini's text response into structured alternatives"""
        alternatives = []
        
        try:
            import re
            
            # Find all numbered alternatives using a simple approach
            # Look for lines starting with numbers followed by period
            lines = text_response.split('\n')
            current_alternative = None
            
            for line in lines:
                line = line.strip()
                
                # Check if this line starts a new alternative (e.g., "1. Product Name")
                number_match = re.match(r'^(\d+)\.\s+(.+)', line)
                if number_match:
                    # Save previous alternative if exists
                    if current_alternative and current_alternative.get('name'):
                        alternatives.append(current_alternative)
                    
                    # Start new alternative
                    product_line = number_match.group(2)
                    
                    # Extract product name and brand
                    if '(' in product_line and ')' in product_line:
                        product_name = product_line.split('(')[0].strip()
                        brand_part = product_line.split('(')[1].split(')')[0]
                        # Clean brand - take first brand if multiple mentioned
                        brand = brand_part.split(',')[0].strip() if ',' in brand_part else brand_part.strip()
                        if any(word in brand.lower() for word in ['various', 'homemade', 'local']):
                            brand = "Various Brands"
                    else:
                        product_name = product_line.strip()
                        brand = "Various Brands"
                    
                    current_alternative = {
                        "name": product_name,
                        "brand": brand,
                        "type": "Healthy Alternative",
                        "score": 85,
                        "benefits": "",
                        "price": "",
                        "availability": "Supermarkets, online stores"
                    }
                    
                elif current_alternative:
                    # Process property lines for current alternative
                    if line.startswith('Type:'):
                        current_alternative["type"] = line.replace('Type:', '').strip()
                    elif line.startswith('Score:'):
                        score_match = re.search(r'(\d+)', line)
                        if score_match:
                            current_alternative["score"] = int(score_match.group(1))
                    elif line.startswith('Benefits:'):
                        current_alternative["benefits"] = line.replace('Benefits:', '').strip()
                    elif line.startswith('Price:'):
                        current_alternative["price"] = line.replace('Price:', '').strip()
                    elif '₹' in line and not current_alternative["price"]:
                        # Extract price from any line containing ₹
                        price_match = re.search(r'₹[^\n.]*', line)
                        if price_match:
                            current_alternative["price"] = price_match.group(0).strip()
                    elif not current_alternative["benefits"] and any(word in line.lower() for word in ['benefits', 'healthy', 'rich', 'contains', 'made with', 'high']):
                        # Likely a benefits line
                        current_alternative["benefits"] = line.strip()
            
            # Don't forget the last alternative
            if current_alternative and current_alternative.get('name'):
                alternatives.append(current_alternative)
            
            # Ensure all alternatives have required fields
            for alt in alternatives:
                if not alt.get("benefits"):
                    alt["benefits"] = "Healthier alternative with better nutritional profile"
                if not alt.get("price"):
                    alt["price"] = "₹100-200"
                if not alt.get("availability"):
                    alt["availability"] = "Supermarkets, online stores"
            
            print(f"✅ Parsed {len(alternatives)} alternatives from AI text response")
            return alternatives[:5]  # Max 5 alternatives
            
        except Exception as e:
            print(f"⚠️ Text parsing failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a minimal fallback
            return [{
                "name": "Healthy Alternative Available",
                "brand": "Various Brands", 
                "type": "Healthy Option",
                "score": 85,
                "benefits": "Better nutritional profile than original product",
                "price": "₹100-200",
                "availability": "Local stores, online"
            }]
    
    @staticmethod
    def _get_generic_alternatives(product_type: str) -> List[Dict[str, Any]]:
        """Fallback generic alternatives"""
        generic_alternatives = {
            "fruit_drinks": [
                {"name": "Fresh Fruits", "type": "Natural", "score": 95, 
                 "benefits": "Rich in vitamins, minerals, fiber", 
                 "availability": "Local markets", "price": "₹80-150 per kg"}
            ],
            "mango_drinks": [
                {"name": "Fresh Mango", "type": "Natural", "score": 95,
                 "benefits": "Rich in vitamins A & C, fiber",
                 "availability": "Fruit vendors", "price": "₹100-150 per kg"}
            ],
            "default": [
                {"name": "Fresh Fruits", "type": "Natural", "score": 90,
                 "benefits": "Natural vitamins and minerals",
                 "availability": "Everywhere", "price": "₹50-200 per kg"}
            ]
        }
        
        return generic_alternatives.get(product_type, generic_alternatives["default"])

class ClaimVerificationAgent:
    """Verifies marketing claims on product packaging"""
    
    @staticmethod
    def verify_claims(product_data: Dict[str, Any], ocr_text: str = "") -> Dict[str, Any]:
        """
        Analyze and verify marketing claims
        """
        print("--- 🔬 Claim Verification Agent ---")
        
        # Common marketing claims to look for
        claims_to_check = [
            "sugar free", "no added sugar", "natural", "organic", 
            "healthy", "low fat", "high protein", "whole grain"
        ]
        
        text_to_analyze = f"{ocr_text} {product_data.get('product_name', '')}".lower()
        nutriments = product_data.get("nutriments", {})
        
        verified_claims = 0
        unverified_claims = 0
        misleading_claims = 0
        claim_results = []
        
        for claim in claims_to_check:
            if claim in text_to_analyze:
                # Verify claim against nutritional data
                is_valid = ClaimVerificationAgent._verify_specific_claim(claim, nutriments)
                
                claim_results.append({
                    "claim": claim.title(),
                    "found": True,
                    "verified": is_valid,
                    "explanation": ClaimVerificationAgent._get_claim_explanation(claim, is_valid, nutriments)
                })
                
                if is_valid:
                    verified_claims += 1
                else:
                    misleading_claims += 1
                    unverified_claims += 1
        
        # Calculate credibility score
        total_claims = len(claim_results)
        credibility_score = (verified_claims / total_claims * 100) if total_claims > 0 else 0
        
        print(f"📋 Found {total_claims} claims, {verified_claims} verified, {misleading_claims} misleading")
        
        return {
            "total_claims_investigated": total_claims,
            "verified_claims": verified_claims,
            "unverified_claims": unverified_claims,
            "claims_with_conflicts": misleading_claims,
            "overall_credibility_score": int(credibility_score),
            "misleading_claims_count": misleading_claims,
            "false_claims_count": misleading_claims,
            "individual_claim_results": claim_results,
            "misleading_analysis": "✅ **NO OBVIOUS MISLEADING CLAIMS DETECTED** based on available nutritional data." if misleading_claims == 0 else f"⚠️ **{misleading_claims} POTENTIALLY MISLEADING CLAIMS DETECTED**",
            "recommendation": "Focus on nutritional facts rather than marketing claims" if total_claims == 0 else "Verify claims against actual nutritional data"
        }
    
    @staticmethod
    def _verify_specific_claim(claim: str, nutriments: Dict[str, Any]) -> bool:
        """Verify a specific claim against nutritional data"""
        
        if "sugar free" in claim or "no added sugar" in claim:
            sugar = nutriments.get("sugars_100g", 0) or 0
            return sugar <= 0.5  # EU regulation for sugar-free claim
        
        elif "low fat" in claim:
            fat = nutriments.get("fat_100g", 0) or 0
            return fat <= 3  # EU regulation for low-fat claim
        
        elif "high protein" in claim:
            protein = nutriments.get("proteins_100g", 0) or 0
            return protein >= 12  # EU regulation for high-protein claim
        
        # For claims we can't verify nutritionally, assume valid
        return True
    
    @staticmethod
    def _get_claim_explanation(claim: str, is_valid: bool, nutriments: Dict[str, Any]) -> str:
        """Get explanation for claim verification"""
        
        if "sugar" in claim:
            sugar = nutriments.get("sugars_100g", 0) or 0
            if is_valid:
                return f"✅ Verified: Sugar content is {sugar}g per 100g"
            else:
                return f"❌ Misleading: Contains {sugar}g sugar per 100g"
        
        elif "fat" in claim:
            fat = nutriments.get("fat_100g", 0) or 0
            if is_valid:
                return f"✅ Verified: Fat content is {fat}g per 100g"
            else:
                return f"❌ Misleading: Contains {fat}g fat per 100g"
        
        elif "protein" in claim:
            protein = nutriments.get("proteins_100g", 0) or 0
            if is_valid:
                return f"✅ Verified: Protein content is {protein}g per 100g"
            else:
                return f"❌ Misleading: Contains only {protein}g protein per 100g"
        
        return "✅ Claim appears valid based on available information"

# Global instances
health_score_agent = HealthScoreAgent()
alternatives_agent = AlternativesAgent()
claim_verification_agent = ClaimVerificationAgent()