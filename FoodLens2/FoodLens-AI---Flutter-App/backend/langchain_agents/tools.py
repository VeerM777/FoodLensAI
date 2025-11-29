"""
LangChain tools for FoodLens AI
Wraps existing functionality in LangChain-compatible tools
"""
from typing import Dict, Any, List, Optional, Type, Union
from langchain_core.tools import BaseTool, tool
# Use pydantic directly without langchain's compatibility layer
from pydantic import BaseModel, Field
import sys
import os
import re
import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.ai.generativelanguage import Part

# Add parent directory to path to import the modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Import existing functionality
try:
    from search_utils import (
        search_product_category,
        get_category_from_gemini, 
        get_alternatives,
        search_fssai_compliance,
        verify_health_claims
    )
    # Initialize utilities
    from search_utils import SearchUtils
    search_utils = SearchUtils()
except ImportError:
    print("Warning: Could not import all functions from search_utils. Some functionality may be limited.")
    search_utils = None

# Import new dynamic search utilities - completely non-hardcoded
try:
    from dynamic_search import dynamic_search
    dynamic_search_available = True
    print("✅ Dynamic search utilities loaded successfully")
except ImportError:
    print("Warning: Could not import dynamic search utilities. Falling back to standard search.")
    dynamic_search_available = False

# Configure Gemini AI if available
try:
    import google.generativeai as genai
    # Configure Gemini AI
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
except ImportError:
    print("Warning: Google Generative AI not available")

# Tool input schemas
class ProductCategoryInput(BaseModel):
    product_name: str = Field(description="Name of the product to categorize")
    ingredients: Optional[List[str]] = Field(default=None, description="List of ingredients in the product")

class HealthScoreInput(BaseModel):
    product_name: str = Field(description="Name of the food product")
    nutrition_data: Dict[str, Any] = Field(description="Nutritional data for the product")
    ingredients: Optional[List[str]] = Field(default=None, description="List of ingredients in the product")
    health_conditions: Optional[List[str]] = Field(default=None, description="User health conditions")

class AlternativesInput(BaseModel):
    product_name: str = Field(description="Name of the product")
    product_type: str = Field(description="Type/category of product")

class OCRInput(BaseModel):
    text: str = Field(description="OCR text extracted from image")

class BarcodeInput(BaseModel):
    barcode: str = Field(description="Barcode number extracted from image")

class ClaimVerificationInput(BaseModel):
    product_data: Dict[str, Any] = Field(description="Product data including name, brand, etc.")
    ocr_text: str = Field(description="OCR text from product packaging")

class FSSAIVerificationInput(BaseModel):
    product_data: Dict[str, Any] = Field(description="Product data including name, brand, etc.")
    ocr_text: str = Field(description="OCR text from product packaging")

# Implement custom versions of tools
def get_category_from_gemini_impl(product_name: str, ingredients: str = None) -> Dict[str, str]:
    """
    Get product category using Gemini AI
    """
    try:
        if GOOGLE_API_KEY and 'genai' in globals():
            # Prepare the prompt with more detailed categorization
            prompt = f"""
            Analyze this food product carefully:
            Product name: {product_name}
            Ingredients: {ingredients if ingredients else 'Unknown'}

            Be very specific about categorization. For example:
            - If it's a biscuit like Parle-G, categorize it as "biscuits" not general "snack"
            - If it's chips like Lay's, categorize it as "chips" not general "snack" 
            - If it's noodles like Maggi, categorize it as "instant noodles" not general "food"

            Return the product category in JSON format with the following fields:
            {{
                "category": [very specific food category like "biscuits", "chips", "chocolate", "instant noodles", "breakfast cereal", etc.],
                "type": [general type: "food", "beverage", "snack", "dessert", etc],
                "sub_category": [even more specific like "glucose biscuits", "potato chips", "dark chocolate", etc.],
                "health_classification": [one of "healthy", "moderately_healthy", "unhealthy"]
            }}

            Only return valid JSON, nothing else.
            """

            # Generate response from Gemini
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.2},
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            response_text = response.text
            # Extract JSON if wrapped in code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            import json
            try:
                result = json.loads(response_text)
                
                # Ensure all required fields are present
                if "category" not in result:
                    result["category"] = "processed food"
                if "type" not in result:
                    result["type"] = "food"
                if "health_classification" not in result:
                    result["health_classification"] = "moderately_healthy"
                # Handle new sub_category field
                if "sub_category" not in result:
                    result["sub_category"] = result["category"]
                
                return result
            except json.JSONDecodeError:
                print(f"Error decoding JSON from Gemini response: {response_text}")
                return {"category": "processed food", "type": "food", "health_classification": "moderately_healthy", "sub_category": "processed food"}
    except Exception as e:
        print(f"Error in get_category_from_gemini: {str(e)}")
    
    # Fallback to simple categorization
    return {"category": "processed food", "type": "food", "health_classification": "moderately_healthy"}

def search_product_category_impl(product_name: str) -> Dict[str, str]:
    """
    Search for product category using web search
    """
    try:
        # Try to use existing function if available
        if search_utils:
            return search_utils.search_product_category(product_name)
        
        # Fallback implementation
        search_query = f"{product_name} food category nutrition facts"
        url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract potential category from search results
        text_content = soup.get_text().lower()
        
        # Define category mappings
        categories = {
            "dairy": ["dairy", "milk", "cheese", "yogurt", "butter", "cream"],
            "fruits": ["fruit", "apple", "banana", "orange", "grape", "berry"],
            "vegetables": ["vegetable", "carrot", "broccoli", "spinach", "tomato"],
            "grains": ["grain", "bread", "rice", "pasta", "cereal", "wheat"],
            "proteins": ["protein", "meat", "chicken", "beef", "fish", "seafood", "egg", "legume"],
            "snacks": ["snack", "chip", "crisp", "cookie", "cracker", "popcorn"],
            "beverages": ["beverage", "drink", "soda", "juice", "water", "coffee", "tea"],
            "sweets": ["sweet", "dessert", "chocolate", "candy", "cake", "ice cream"],
            "processed": ["processed", "canned", "frozen", "ready-to-eat", "fast food"]
        }
        
        # Find matches
        best_category = "processed food"
        max_matches = 0
        
        for category, keywords in categories.items():
            matches = sum(keyword in text_content for keyword in keywords)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return {
            "category": best_category,
            "type": "beverage" if best_category == "beverages" else "food"
        }
    except Exception as e:
        print(f"Error in search_product_category: {str(e)}")
        return {"category": "processed food", "type": "food"}

# Import enhanced classification from ocr_barcode agent
try:
    from agents.ocr_barcode import barcode_agent
    pattern_matching_available = True
except ImportError:
    pattern_matching_available = False

# Define LangChain tools
@tool("categorize_product", args_schema=ProductCategoryInput)
def categorize_product(product_name: str, ingredients: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Categorizes a food product based on its name and ingredients.
    Uses a multi-layered approach with confidence scoring:
    1. Dynamic AI classification (Gemini with web search)
    2. Enhanced pattern matching with brand recognition
    3. Fallback generic categorization
    
    Returns category information including type, category name, and confidence score.
    """
    ingredients_str = ", ".join(ingredients) if ingredients else ""
    
    # Priority 1: Try dynamic search for completely non-hardcoded results (MOST RELIABLE)
    if dynamic_search_available:
        try:
            print(f"🤖 Attempting AI-based categorization for: {product_name}")
            category = dynamic_search.categorize_product(product_name, ingredients_str)
            
            # Add confidence and method info if not present
            if isinstance(category, dict):
                category.setdefault("confidence", 0.95)
                category.setdefault("method", "ai_dynamic")
                print(f"✅ AI categorization successful: {category.get('category')} (confidence: {category.get('confidence')})")
                return category
        except Exception as e:
            print(f"⚠️ Dynamic categorization failed: {str(e)}, falling back to pattern matching")
    
    # Priority 2: Try enhanced pattern matching (RELIABLE FALLBACK)
    if pattern_matching_available:
        try:
            print(f"🔍 Attempting pattern matching for: {product_name}")
            pattern_result = barcode_agent.classify_product_type(
                product_name, 
                "", 
                ingredients if ingredients else []
            )
            
            # If pattern matching has good confidence, use it
            if isinstance(pattern_result, dict):
                confidence = pattern_result.get("confidence", 0.5)
                product_type = pattern_result.get("type", "processed_food")
                
                print(f"✅ Pattern matching result: {product_type} (confidence: {confidence})")
                
                # If confidence is good enough, return the result
                if confidence >= 0.6:
                    return {
                        "category": product_type,
                        "type": "food" if product_type not in ["beverage", "juice", "drink"] else "beverage",
                        "sub_category": product_type,
                        "confidence": confidence,
                        "method": pattern_result.get("method", "pattern_matching")
                    }
        except Exception as e:
            print(f"⚠️ Pattern matching failed: {str(e)}")
    
    # Priority 3: Try Gemini AI directly (GOOD FALLBACK)
    try:
        print(f"🔄 Attempting direct Gemini categorization for: {product_name}")
        category = get_category_from_gemini_impl(product_name, ingredients_str)
        if category:
            category.setdefault("confidence", 0.85)
            category.setdefault("method", "ai_gemini")
            print(f"✅ Gemini categorization successful: {category.get('category')}")
            return category
    except Exception as e:
        print(f"⚠️ Gemini categorization failed: {str(e)}")
    
    # Priority 4: Last resort - search-based categorization
    print(f"⚠️ Using fallback categorization for: {product_name}")
    fallback = search_product_category_impl(product_name)
    fallback.setdefault("confidence", 0.3)
    fallback.setdefault("method", "fallback")
    return fallback

@tool("calculate_health_score", args_schema=HealthScoreInput)
def calculate_health_score(
    product_name: str, 
    nutrition_data: Dict[str, Any], 
    ingredients: Optional[List[str]] = None,
    health_conditions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate health score for a food product based on nutritional data.
    Returns a score from 0-100 where higher is healthier.
    """
    # Define base scoring system
    base_score = 50  # Start with neutral score
    
    # Check for problematic ingredients
    problematic_ingredients = [
        "high fructose corn syrup", "hydrogenated", "msg", "artificial color",
        "sodium nitrite", "sodium nitrate", "artificial sweetener", "aspartame",
        "saccharin", "sucralose", "potassium benzoate", "sodium benzoate"
    ]
    
    # Lower score for each problematic ingredient
    if ingredients:
        for ing in problematic_ingredients:
            if any(ing in i.lower() for i in ingredients):
                base_score -= 5
    
    # Evaluate nutrition values
    # Higher protein is good
    protein = nutrition_data.get("protein", 0)
    if protein > 15:
        base_score += 10
    elif protein > 8:
        base_score += 5
    
    # Lower sugar is good
    sugar = nutrition_data.get("sugar", 0)
    if sugar > 15:
        base_score -= 10
    elif sugar > 8:
        base_score -= 5
    
    # Lower sodium is good
    sodium = nutrition_data.get("sodium", 0)
    if sodium > 500:
        base_score -= 10
    elif sodium > 300:
        base_score -= 5
    
    # Higher fiber is good
    fiber = nutrition_data.get("fiber", 0)
    if fiber > 5:
        base_score += 10
    elif fiber > 3:
        base_score += 5
    
    # Account for health conditions
    if health_conditions:
        # Adjust score based on health conditions
        if "diabetes" in health_conditions and sugar > 5:
            base_score -= 15
        if "hypertension" in health_conditions and sodium > 200:
            base_score -= 15
        if "heart disease" in health_conditions and nutrition_data.get("saturated_fat", 0) > 3:
            base_score -= 15
    
    # Ensure score is within 0-100 range
    final_score = max(0, min(100, base_score))
    
    # Generate verdict
    verdict = ""
    if final_score >= 80:
        verdict = {
            "title": "Excellent choice!",
            "description": "This product is highly nutritious and provides excellent health benefits."
        }
    elif final_score >= 60:
        verdict = {
            "title": "Good option",
            "description": "This product has decent nutritional value and is generally a good choice."
        }
    elif final_score >= 40:
        verdict = {
            "title": "Moderate nutritional value",
            "description": "This product has moderate nutritional value. Consider healthier alternatives."
        }
    elif final_score >= 20:
        verdict = {
            "title": "Poor nutritional profile",
            "description": "This product has poor nutritional value. Consume occasionally."
        }
    else:
        verdict = {
            "title": "Very unhealthy choice",
            "description": "This product has very poor nutritional value. Avoid regular consumption."
        }
    
    # Generate positives and negatives
    positives = []
    negatives = []
    
    if nutrition_data.get("protein", 0) > 8:
        positives.append("Good source of protein")
    
    if nutrition_data.get("fiber", 0) > 3:
        positives.append("Good source of fiber")
    
    if nutrition_data.get("sugar", 0) < 5:
        positives.append("Low in sugar")
    
    if nutrition_data.get("sodium", 0) < 200:
        positives.append("Low in sodium")
    
    if nutrition_data.get("sugar", 0) > 15:
        negatives.append("High in sugar")
    
    if nutrition_data.get("sodium", 0) > 400:
        negatives.append("High in sodium")
    
    if nutrition_data.get("saturated_fat", 0) > 5:
        negatives.append("High in saturated fat")
    
    return {
        "score": final_score,
        "verdict": verdict,
        "positives": positives,
        "negatives": negatives
    }

@tool("find_alternatives", args_schema=AlternativesInput)
def find_alternatives(product_name: str, product_type: str) -> List[Dict[str, Any]]:
    """
    Find healthier alternative products for a given food product.
    Returns a list of alternative products with health scores and details.
    """
    try:
        # First try using dynamic search for completely non-hardcoded alternatives
        if dynamic_search_available:
            try:
                # Get detailed category information
                category_info = dynamic_search.categorize_product(product_name)
                
                # Get alternatives using dynamic search
                dynamic_alternatives = dynamic_search.get_alternatives(product_name, category_info)
                
                # If we found alternatives, return them
                if dynamic_alternatives and len(dynamic_alternatives) > 0:
                    print(f"Found {len(dynamic_alternatives)} alternatives using dynamic search")
                    return dynamic_alternatives
            except Exception as e:
                print(f"Dynamic alternatives search failed: {str(e)}, falling back to other methods")
        
        # Next try using search_utils if available
        if search_utils:
            alternatives = search_utils.get_alternatives(product_type, product_name)
            if alternatives and len(alternatives) > 0:
                return alternatives
        
        # Get category from product name as a last resort
        category_result = get_category_from_gemini_impl(product_name)
        specific_category = category_result.get("category", "").lower()
        sub_category = category_result.get("sub_category", "").lower()
        
        # Start with an empty list - we'll query Gemini directly instead of using hardcoded values
        alternatives = []
        
        # Use Gemini AI directly to get alternatives without hardcoding
        if GOOGLE_API_KEY and 'genai' in globals():
            prompt = f"""
            I need to find healthier alternatives to this food product:
            
            Product: {product_name}
            Category: {specific_category}
            Type: {product_type}
            
            Please provide 5 specific healthier alternatives that are in the same category but with better nutritional profiles.
            Focus on products available in India.
            
            Return the alternatives in this JSON format:
            {{
                "alternatives": [
                    {{
                        "name": "Alternative Product Name",
                        "brand": "Brand Name",
                        "health_score": [health score out of 100],
                        "health_benefits": "Brief description of health benefits compared to original product"
                    }},
                    ...more alternatives...
                ]
            }}
            
            Only return valid JSON, nothing else.
            """
            
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.3},
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                response_text = response.text
                # Extract JSON if wrapped in code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(response_text)
                alternatives = result.get("alternatives", [])
                
                if alternatives and len(alternatives) > 0:
                    return alternatives
            except Exception as e:
                print(f"Error getting alternatives from Gemini: {str(e)}")
                
        # If all else fails, provide a minimal set of generic alternatives as a last resort
        if not alternatives:
            alternatives = [
                {
                    "name": f"Healthier {specific_category} alternative",
                    "brand": "Various brands",
                    "health_score": 75,
                    "health_benefits": "Better nutritional profile than original product"
                },
                {
                    "name": f"Homemade {specific_category}",
                    "brand": "Homemade",
                    "health_score": 85,
                    "health_benefits": "Control over ingredients and preparation methods"
                }
            ]
            alternatives = [
                {
                    "name": "Britannia NutriChoice Digestive",
                    "brand": "Britannia",
                    "health_score": 75,
                    "health_benefits": "High in fiber, whole grain, less sugar than regular biscuits"
                },
                {
                    "name": "Unibic Oatmeal Cookies",
                    "brand": "Unibic",
                    "health_score": 72,
                    "health_benefits": "Contains oats, high in fiber, moderate sugar"
                },
                {
                    "name": "McVities Digestive",
                    "brand": "McVities",
                    "health_score": 68,
                    "health_benefits": "Whole wheat, less sweet, good fiber content"
                },
                {
                    "name": "Threptin Lite",
                    "brand": "Raptakos",
                    "health_score": 82,
                    "health_benefits": "High protein, sugar-controlled, good for balanced nutrition"
                },
                {
                    "name": "RiteBite Max Protein",
                    "brand": "RiteBite",
                    "health_score": 80,
                    "health_benefits": "High protein, lower sugar, added fiber"
                }
            ]
        elif "chips" in specific_category or "crisps" in specific_category:
            alternatives = [
                {
                    "name": "Baked Chips",
                    "brand": "Lay's Baked",
                    "health_score": 65,
                    "health_benefits": "40% less fat than regular chips, baked not fried"
                },
                {
                    "name": "Too Yumm! Multigrain Chips",
                    "brand": "Too Yumm!",
                    "health_score": 70,
                    "health_benefits": "Baked, contains multigrain, low in fat"
                },
                {
                    "name": "Popcorn (Lightly Salted)",
                    "brand": "Act II",
                    "health_score": 75,
                    "health_benefits": "Low calorie, whole grain, high fiber"
                },
                {
                    "name": "Khakhra",
                    "brand": "Lijjat",
                    "health_score": 78,
                    "health_benefits": "Baked, not fried, made with whole wheat"
                },
                {
                    "name": "Fox Nuts/Makhana",
                    "brand": "Gourmet's",
                    "health_score": 85,
                    "health_benefits": "Low in sodium, good source of protein and fiber"
                }
            ]
        elif "chocolate" in specific_category or "candy" in specific_category:
            alternatives = [
                {
                    "name": "Dark Chocolate (70%+)",
                    "brand": "Amul",
                    "health_score": 68,
                    "health_benefits": "Antioxidants, less sugar than milk chocolate"
                },
                {
                    "name": "Date & Nut Bar",
                    "brand": "Eatopia",
                    "health_score": 82,
                    "health_benefits": "Natural sweetness, fiber, healthy fats"
                },
                {
                    "name": "Organic Jaggery Chikki",
                    "brand": "24 Mantra",
                    "health_score": 75,
                    "health_benefits": "Natural sweetener, nuts provide protein and healthy fats"
                },
                {
                    "name": "Sugar-Free Dark Chocolate",
                    "brand": "Zevic",
                    "health_score": 72,
                    "health_benefits": "No added sugar, sweetened with stevia"
                },
                {
                    "name": "Cacao Nibs",
                    "brand": "Urban Platter",
                    "health_score": 85,
                    "health_benefits": "Pure cacao, high antioxidants, no added sugar"
                }
            ]
        elif "beverage" in product_type.lower() or "drink" in specific_category:
            alternatives = [
                {
                    "name": "Green Tea",
                    "brand": "Organic India",
                    "health_score": 90,
                    "health_benefits": "Antioxidants, zero calories, metabolism support"
                },
                {
                    "name": "Coconut Water",
                    "brand": "RAW Pressery",
                    "health_score": 85,
                    "health_benefits": "Natural electrolytes, no added sugar"
                },
                {
                    "name": "Buttermilk",
                    "brand": "Amul",
                    "health_score": 75,
                    "health_benefits": "Probiotics, low fat, good for digestion"
                },
                {
                    "name": "Smoothie",
                    "brand": "Raw Pressery",
                    "health_score": 80,
                    "health_benefits": "Real fruit, fiber, no added sugar"
                },
                {
                    "name": "Lemon Water with Honey",
                    "brand": "Homemade",
                    "health_score": 88,
                    "health_benefits": "Vitamin C, hydrating, natural ingredients"
                }
            ]
        elif "noodle" in specific_category or "pasta" in specific_category:
            alternatives = [
                {
                    "name": "Saffola Masala Oats",
                    "brand": "Saffola",
                    "health_score": 80,
                    "health_benefits": "High fiber from oats, lower sodium than instant noodles"
                },
                {
                    "name": "Whole Wheat Pasta",
                    "brand": "Disano",
                    "health_score": 75,
                    "health_benefits": "Higher fiber, complex carbs, more nutrients"
                },
                {
                    "name": "Multi-grain Noodles",
                    "brand": "Top Ramen Atta Noodles",
                    "health_score": 70,
                    "health_benefits": "Made with wheat flour, lower refined flour content"
                },
                {
                    "name": "Quinoa Pasta",
                    "brand": "Naturally Yours",
                    "health_score": 85,
                    "health_benefits": "Complete protein, gluten-free, higher nutrition"
                },
                {
                    "name": "Brown Rice Noodles",
                    "brand": "24 Mantra",
                    "health_score": 78,
                    "health_benefits": "Whole grain, higher fiber than white rice noodles"
                }
            ]
        # General fallback if no specific category matched
        else:
            alternatives = [
                {
                    "name": "Multigrain Bread",
                    "brand": "Britannia",
                    "health_score": 75,
                    "health_benefits": "Multiple grains, higher fiber content"
                },
                {
                    "name": "Roasted Chana",
                    "brand": "Haldiram's",
                    "health_score": 80,
                    "health_benefits": "High protein, low fat, good fiber content"
                },
                {
                    "name": "Sprouted Moong",
                    "brand": "Homemade",
                    "health_score": 90,
                    "health_benefits": "High protein, enzyme-rich, excellent nutrition"
                },
                {
                    "name": "Vegetable Idli",
                    "brand": "MTR",
                    "health_score": 85,
                    "health_benefits": "Fermented, low fat, added vegetables"
                },
                {
                    "name": "Ragi Cookies",
                    "brand": "Early Foods",
                    "health_score": 78,
                    "health_benefits": "Whole grain millet, iron-rich, less sugar"
                }
            ]
        
        return alternatives
        
    except Exception as e:
        print(f"Error finding alternatives: {str(e)}")
        return []

@tool("process_ocr", args_schema=OCRInput)
def process_ocr(text: str) -> Dict[str, Any]:
    """
    Process OCR text from a food product image.
    Extracts product name, brand, ingredients, etc.
    """
    # Initialize result
    result = {
        "product_name": "",
        "brand": "",
        "ingredients": [],
        "nutrition": {},
        "manufacturing_date": "",
        "expiry_date": "",
        "fssai_license": "",
        "net_weight": "",
        "claims": []
    }
    
    # Extract product name (assume it's often at the beginning, in larger text)
    lines = text.strip().split('\n')
    if lines and lines[0]:
        result["product_name"] = lines[0].strip()
    
    # Try to extract brand name (typically near product name)
    if len(lines) > 1:
        potential_brand = lines[1].strip()
        if len(potential_brand.split()) <= 3:  # Brand names are typically short
            result["brand"] = potential_brand
    
    # Extract ingredients
    ingredients_match = re.search(r'ingredients?:?(.*?)(?:\.|nutritional|nutrition|expiry|$)', 
                                  text, re.IGNORECASE | re.DOTALL)
    if ingredients_match:
        ingredients_text = ingredients_match.group(1).strip()
        ingredients = [ing.strip() for ing in re.split(r',|\.', ingredients_text) if ing.strip()]
        result["ingredients"] = ingredients
    
    # Extract FSSAI license number
    fssai_match = re.search(r'fssai(?:\s+license)?\s+(?:no\.?|number)?[:.\s]*(\d+)', 
                            text, re.IGNORECASE)
    if fssai_match:
        result["fssai_license"] = fssai_match.group(1).strip()
    
    # Extract manufacturing and expiry dates
    mfg_match = re.search(r'(?:mfg|manufacturing|packed on)[.\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+[a-zA-Z]+\s+\d{2,4})', 
                          text, re.IGNORECASE)
    if mfg_match:
        result["manufacturing_date"] = mfg_match.group(1).strip()
    
    exp_match = re.search(r'(?:exp|expiry|best before)[.\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+[a-zA-Z]+\s+\d{2,4})', 
                          text, re.IGNORECASE)
    if exp_match:
        result["expiry_date"] = exp_match.group(1).strip()
    
    # Extract net weight
    weight_match = re.search(r'(?:net\s+(?:weight|wt)|net contents)[.\s:]*(\d+\.?\d*\s*[a-zA-Z]+)', 
                             text, re.IGNORECASE)
    if weight_match:
        result["net_weight"] = weight_match.group(1).strip()
    
    # Extract health claims
    common_claims = [
        "low fat", "high protein", "sugar free", "no sugar", "no added sugar",
        "high fiber", "low calorie", "fat free", "gluten free", "organic",
        "natural", "no preservatives", "no artificial", "healthy", "nutritious"
    ]
    
    claims = []
    for claim in common_claims:
        if re.search(r'\b' + re.escape(claim) + r'\b', text, re.IGNORECASE):
            claims.append(claim)
    
    result["claims"] = claims
    
    return result

@tool("process_barcode", args_schema=BarcodeInput)
def process_barcode(barcode: str) -> Dict[str, Any]:
    """
    Process barcode information from a food product.
    Returns detailed product information if available.
    """
    # Try to query the Open Food Facts database
    try:
        if barcode and barcode.isdigit():
            # Use Open Food Facts API to get product info
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == 1:
                    product = data.get("product", {})
                    
                    result = {
                        "product_name": product.get("product_name", ""),
                        "brand": product.get("brands", ""),
                        "ingredients": product.get("ingredients_text", "").split(", "),
                        "nutrition": {
                            "energy": product.get("nutriments", {}).get("energy", 0),
                            "fat": product.get("nutriments", {}).get("fat", 0),
                            "saturated_fat": product.get("nutriments", {}).get("saturated-fat", 0),
                            "carbohydrates": product.get("nutriments", {}).get("carbohydrates", 0),
                            "sugar": product.get("nutriments", {}).get("sugars", 0),
                            "protein": product.get("nutriments", {}).get("proteins", 0),
                            "salt": product.get("nutriments", {}).get("salt", 0),
                            "sodium": product.get("nutriments", {}).get("sodium", 0),
                            "fiber": product.get("nutriments", {}).get("fiber", 0),
                        },
                        "net_weight": product.get("quantity", ""),
                        "countries": product.get("countries", ""),
                        "image_url": product.get("image_url", "")
                    }
                    
                    return result
    except Exception as e:
        print(f"Error processing barcode: {str(e)}")
    
    # If barcode lookup fails or barcode is invalid, return empty dict
    return {}

@tool("verify_claims", args_schema=ClaimVerificationInput)
def verify_claims(product_data: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
    """
    Verify health and nutrition claims on food product packaging.
    Returns analysis of claim accuracy and credibility.
    """
    try:
        # Extract claims from product data
        claims = product_data.get("claims", [])
        
        # If no claims are explicitly listed, try to extract them from OCR
        if not claims:
            common_claims = [
                "low fat", "high protein", "sugar free", "no sugar", "no added sugar",
                "high fiber", "low calorie", "fat free", "gluten free", "organic",
                "natural", "no preservatives", "no artificial", "healthy", "nutritious"
            ]
            
            for claim in common_claims:
                if re.search(r'\b' + re.escape(claim) + r'\b', ocr_text, re.IGNORECASE):
                    claims.append(claim)
        
        # Check if claims are supported by nutrition data
        nutrition = product_data.get("nutrition", {})
        misleading_claims = []
        
        for claim in claims:
            claim_lower = claim.lower()
            
            if "low fat" in claim_lower and nutrition.get("fat", 0) > 3:
                misleading_claims.append({
                    "claim": claim,
                    "reason": f"Claims 'low fat' but contains {nutrition.get('fat')}g fat per serving"
                })
            
            elif "high protein" in claim_lower and nutrition.get("protein", 0) < 6:
                misleading_claims.append({
                    "claim": claim,
                    "reason": f"Claims 'high protein' but only contains {nutrition.get('protein')}g protein per serving"
                })
            
            elif any(sugar_claim in claim_lower for sugar_claim in ["sugar free", "no sugar"]) and nutrition.get("sugar", 0) > 0.5:
                misleading_claims.append({
                    "claim": claim,
                    "reason": f"Claims 'sugar free'/'no sugar' but contains {nutrition.get('sugar')}g sugar per serving"
                })
            
            elif "high fiber" in claim_lower and nutrition.get("fiber", 0) < 3:
                misleading_claims.append({
                    "claim": claim,
                    "reason": f"Claims 'high fiber' but only contains {nutrition.get('fiber')}g fiber per serving"
                })
            
            elif "low calorie" in claim_lower and nutrition.get("calories", 0) > 40:
                misleading_claims.append({
                    "claim": claim,
                    "reason": f"Claims 'low calorie' but contains {nutrition.get('calories')} calories per serving"
                })
        
        return {
            "claims": claims,
            "misleading_claims": misleading_claims,
            "has_misleading_claims": len(misleading_claims) > 0
        }
    except Exception as e:
        print(f"Error verifying claims: {str(e)}")
        return {"claims": [], "misleading_claims": [], "has_misleading_claims": False}

@tool("verify_fssai", args_schema=FSSAIVerificationInput)
def verify_fssai(product_data: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
    """
    Verify FSSAI compliance and regulatory information.
    Returns compliance status and regulatory details.
    """
    try:
        # Extract FSSAI license number
        fssai_license = product_data.get("fssai_license", "")
        
        # If not in product info, try to extract from OCR text
        if not fssai_license:
            fssai_match = re.search(r'fssai(?:\s+license)?\s+(?:no\.?|number)?[:.\s]*(\d+)', 
                                    ocr_text, re.IGNORECASE)
            if fssai_match:
                fssai_license = fssai_match.group(1).strip()
        
        # Check if FSSAI license number is valid (simplified)
        is_valid_format = False
        if fssai_license:
            # Valid FSSAI numbers are typically 14 digits
            is_valid_format = len(fssai_license) == 14 and fssai_license.isdigit()
        
        # Check for mandatory label requirements
        required_labels = [
            "ingredients", "nutrition", "manufacturer", "best before", "net weight"
        ]
        
        missing_labels = []
        for label in required_labels:
            if not re.search(r'\b' + re.escape(label) + r'\b', ocr_text, re.IGNORECASE):
                missing_labels.append(label)
        
        return {
            "fssai_license": fssai_license,
            "is_valid_format": is_valid_format,
            "missing_labels": missing_labels,
            "is_compliant": bool(fssai_license and is_valid_format and not missing_labels)
        }
    except Exception as e:
        print(f"Error verifying FSSAI compliance: {str(e)}")
        return {
            "fssai_license": "",
            "is_valid_format": False,
            "missing_labels": [],
            "is_compliant": False
        }

# Create the tools list for the agent
tools = [
    categorize_product,
    calculate_health_score,
    find_alternatives,
    process_ocr,
    process_barcode,
    verify_claims,
    verify_fssai
]