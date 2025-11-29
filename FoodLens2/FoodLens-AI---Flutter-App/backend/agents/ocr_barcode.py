"""
OCR and Barcode processing agents
"""
import re
import os
from typing import Dict, Any, List
from PIL import Image
import google.generativeai as genai
from config.settings import config
from utils.search import search_utils

# Configure Gemini
if config.GOOGLE_API_KEY:
    genai.configure(api_key=config.GOOGLE_API_KEY)

class OCRAgent:
    """Handles OCR text processing and product name extraction"""
    
    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """
        Extract text from image using Gemini Vision API
        Note: This method is a fallback when barcode reader doesn't find product text.
        """
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return ""
        
        try:
            print(f"🔍 Using Gemini 1.5 Flash for advanced OCR...")
            img = Image.open(image_path)
            
            # Use Gemini 2.0 Flash (latest stable model)
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config={
                    'temperature': 0.1,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            prompt = """You are an expert OCR system. Extract ALL visible text from this food product package image.

Focus on identifying:
1. BRAND NAME (in large letters - e.g., Balaji, Haldiram, Parle)
2. PRODUCT NAME (main product - e.g., Crunchex, Wafers, Biscuits)
3. FLAVOR/VARIANT (e.g., Chilli Tadka, Masala, Plain)
4. WEIGHT/QUANTITY (e.g., 85g, 100g)

Return in this EXACT format:
[BRAND]: <brand name>
[PRODUCT]: <product name>
[VARIANT]: <flavor or variant>
[WEIGHT]: <weight if visible>

IMPORTANT: Extract text EXACTLY as it appears on the package. Be accurate."""
            
            response = model.generate_content([prompt, img])
            
            if response and response.text:
                extracted_text = response.text
                print(f"✅ Gemini Vision extracted {len(extracted_text)} characters")
                print(f"📄 Extracted: {extracted_text[:300]}...")
                return extracted_text
            else:
                print(f"⚠️ Gemini returned empty response")
                return ""
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini Vision error: {error_msg}")
            
            if "quota" in error_msg.lower() or "429" in error_msg:
                print(f"⚠️ API quota exceeded. Please wait a minute and try again.")
            elif "404" in error_msg:
                print(f"⚠️ Model not found. Using fallback.")
            
            return ""
        #     print(f"❌ Gemini Vision OCR failed: {e}")
        #     return ""
    
    @staticmethod
    def process_ocr_text(ocr_text: str) -> Dict[str, Any]:
        """
        Process OCR text to extract product information
        """
        if not ocr_text:
            return {"product_name": "", "brand": "", "weight": "", "ingredients": []}
        
        print(f"📄 Raw OCR text:\n{ocr_text[:300]}...")  # Debug
        
        # Try to parse structured format first (from improved prompt)
        brand = ""
        product_name = ""
        variant = ""
        weight = ""
        
        # Parse structured format
        for line in ocr_text.split('\n'):
            line = line.strip()
            if line.startswith('[BRAND]:'):
                brand = line.replace('[BRAND]:', '').strip()
            elif line.startswith('[PRODUCT]:'):
                product_name = line.replace('[PRODUCT]:', '').strip()
            elif line.startswith('[VARIANT]:'):
                variant = line.replace('[VARIANT]:', '').strip()
            elif line.startswith('[WEIGHT]:'):
                weight = line.replace('[WEIGHT]:', '').strip()
        
        # If structured parsing worked, use it
        full_product = ""
        if brand or product_name:
            # Combine product name with variant if both exist
            full_product = product_name
            if variant and variant.lower() not in product_name.lower():
                full_product = f"{product_name} {variant}".strip()
            
            print(f"✅ Structured parsing: Brand='{brand}', Product='{full_product}'")
        else:
            # Fallback to old parsing logic
            print("📝 Using fallback OCR parsing...")
            
            # Clean OCR text but preserve important characters
            cleaned_text = re.sub(r'[^\w\s\.\,\-\(\)\%\']', ' ', ocr_text)
            lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
            
            print(f"📄 Processing OCR lines ({len(lines)} total): {lines[:10]}...")  # Debug first 10 lines
            
            # Common Indian food brands (expanded list)
            known_brands = [
                'balaji', 'haldiram', 'bikano', 'britannia', 'parle', 'itch',
                'lays', 'kurkure', 'bingo', 'act ii', 'maggi', 'yippee',
                'nestle', 'amul', 'cadbury', 'kellogs', 'sunfeast', 'too yumm',
                'priya', 'mtr', 'tops', 'aashirvaad', 'pillsbury', 'kissan'
            ]
            
            # Product type keywords that help identify product lines
            product_keywords = [
                'wafers', 'chips', 'biscuit', 'cookie', 'chocolate', 'candy',
                'namkeen', 'mixture', 'chivda', 'sev', 'bhujia', 'chana',
                'crunchex', 'crunchey', 'crunchy', 'masala', 'tadka', 'spicy'
            ]
            
            # Collect all potential brand and product words
            brand_candidates = []
            product_words = []
            
            # First, try to identify brand from known brands
            for line in lines[:10]:  # Check more lines
                line_lower = line.lower()
                for known_brand in known_brands:
                    if known_brand in line_lower:
                        brand_candidates.append(line.title())
                        print(f"✅ Brand candidate: {line.title()}")
                        break
            
            # Select the first brand candidate
            if brand_candidates:
                brand = brand_candidates[0]
                print(f"✅ Selected brand: {brand}")
            
            # Extract product name - collect product-related words
            for i, line in enumerate(lines[:15]):  # Check more lines
                line_lower = line.lower()
                line_words = line.split()
                
                # Skip very short lines (likely not product names)
                if len(line) < 2:
                    continue
                    
                # Skip lines that are just brand (already found)
                if brand and line.lower().strip() == brand.lower().strip():
                    continue
                
                # Check if line contains product keywords
                for keyword in product_keywords:
                    if keyword in line_lower:
                        product_words.append(line.title())
                        print(f"✅ Product keyword found: {line.title()}")
                        break
                
                # Also collect words that look like product names (2-5 words, mostly caps)
                if 2 <= len(line_words) <= 5 and not full_product:
                    # Check if it looks like a product name
                    if any(char.isupper() for char in line):
                        product_words.append(line.title())
                        print(f"📝 Product candidate: {line.title()}")
            
            # Combine product words intelligently
            if product_words:
                # Remove duplicates while preserving order
                seen = set()
                unique_product_words = []
                for word in product_words:
                    word_lower = word.lower()
                    if word_lower not in seen:
                        seen.add(word_lower)
                        unique_product_words.append(word)
                
                # Combine up to 3 product words
                full_product = ' '.join(unique_product_words[:3])
                print(f"✅ Combined product name: {full_product}")
            
            # If still no product name, use the longest meaningful line
            if not full_product:
                meaningful_lines = [line for line in lines[:10] if 3 <= len(line.split()) <= 8]
                if meaningful_lines:
                    full_product = meaningful_lines[0].title()
                    print(f"📝 Using fallback product name: {full_product}")
                elif lines:
                    # Last resort: combine first few non-empty lines
                    full_product = ' '.join(lines[:2]).title()
                    print(f"📝 Using emergency fallback: {full_product}")
        
        # Extract weight information if not already found
        if not weight:
            weight_pattern = r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|oz|gm)\b'
            weight_match = re.search(weight_pattern, ocr_text, re.IGNORECASE)
            if weight_match:
                weight = weight_match.group(0)
        
        # Extract ingredients (look for ingredient list)
        ingredients = []
        for line in ocr_text.split('\n'):
            if 'ingredient' in line.lower():
                # Extract ingredients from this line and following lines
                ingredients_text = line.lower().replace('ingredients:', '').strip()
                if ingredients_text:
                    ingredients = [ing.strip() for ing in ingredients_text.split(',')]
                break
        
        # Combine brand and product for better identification
        final_product_name = ""
        if full_product and brand:
            # If we have both, combine them
            if brand.lower() not in full_product.lower():
                final_product_name = f"{brand} {full_product}"
            else:
                final_product_name = full_product
        elif full_product:
            final_product_name = full_product
        elif brand:
            final_product_name = brand
        
        print(f"🎯 Final extraction - Product: '{final_product_name}', Brand: '{brand}'")
        
        return {
            "product_name": final_product_name,
            "brand": brand,
            "weight": weight,
            "ingredients": ingredients,
            "full_text": ocr_text
        }

class BarcodeAgent:
    """Handles barcode processing and product database lookup"""
    
    @staticmethod
    def process_barcode(barcode: str) -> Dict[str, Any]:
        """
        Process barcode and fetch product data
        """
        if not barcode:
            return {"status": 0, "product": None}
        
        # Clean barcode: remove spaces, dashes, and other non-numeric characters
        original_barcode = barcode
        barcode = ''.join(c for c in barcode if c.isdigit())
        
        print(f"🔍 Processing barcode: {original_barcode} -> cleaned: {barcode}")
        
        # Fetch from product database
        result = search_utils.search_product_databases("", barcode)
        
        print(f"📦 OpenFoodFacts API Response Status: {result.get('status')}")
        
        if result.get("status") == 1 and result.get("product"):
            product = result["product"]
            product_name = product.get("product_name", "")
            print(f"✅ Product found: {product_name}")
            return {
                "status": 1,
                "product_name": product_name,
                "brand": product.get("brands", ""),
                "ingredients_text": product.get("ingredients_text", ""),
                "nutriments": product.get("nutriments", {}),
                "categories": product.get("categories", ""),
                "labels": product.get("labels", ""),
                "full_product_data": product
            }
        else:
            print(f"❌ Barcode {barcode} not found in OpenFoodFacts database")
            print(f"💡 Tip: This product may not be in the OpenFoodFacts database yet")
            print(f"   The app will continue with OCR-based analysis")
            return {"status": 0, "product": None, "barcode": barcode}
    
    @staticmethod
    def classify_product_type(product_name: str, categories: str = "", ingredients: List[str] = None) -> Dict[str, Any]:
        """
        Enhanced product classification using ML and pattern matching
        Returns: Dict with 'type', 'confidence', 'method', and additional metadata
        """
        # Try lightweight enhanced categorization first  
        try:
            from utils.lightweight_categorizer import lightweight_categorizer
            
            # Extract brand from product name (usually first part)
            product_parts = product_name.split()
            brand = product_parts[0] if product_parts else ""
            
            # Use lightweight categorizer
            result = lightweight_categorizer.categorize_product(product_name, brand)
            
            print(f"🎯 Enhanced Classification: {product_name}")
            print(f"   Category: {result.category}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Method: {result.method}")
            print(f"   Matches: {result.matched_keywords}")
            
            return {
                "type": result.category,
                "confidence": result.confidence,
                "method": f"lightweight_{result.method}",
                "matched_keywords": result.matched_keywords or [],
                "subcategory": result.subcategory,
                "match_score": int(result.confidence * 10)  # For backward compatibility
            }
            
        except ImportError as e:
            print(f"⚠️ Lightweight categorizer not available, falling back to pattern matching: {e}")
        except Exception as e:
            print(f"⚠️ Lightweight categorizer failed, falling back to pattern matching: {e}")
        
        # Fallback to original pattern matching
        text_to_analyze = f"{product_name} {categories}".lower()
        if ingredients:
            # Ensure ingredients is a list of strings
            if isinstance(ingredients, list):
                # Filter out non-string elements and convert to strings
                string_ingredients = [str(ing) for ing in ingredients if ing]
                text_to_analyze += " " + " ".join(string_ingredients).lower()
            elif isinstance(ingredients, str):
                text_to_analyze += " " + ingredients.lower()
        
        confidence = 0.5  # Base confidence
        matched_keywords = []
        classification_method = "pattern_matching_fallback"
        
        # Comprehensive brand-product mappings for Indian market
        brand_product_map = {
            # Noodles & Pasta
            "maggi": "instant_noodles",
            "yippee": "instant_noodles",
            "top ramen": "instant_noodles",
            "sunfeast": "instant_noodles" if "yippee" in text_to_analyze else None,
            "knorr": "instant_noodles" if "noodles" in text_to_analyze else None,
            
            # Dairy Products
            "amul": "dairy",
            "mother dairy": "dairy",
            "nestle": "dairy" if any(w in text_to_analyze for w in ["milk", "cream", "yogurt", "curd"]) else None,
            "britannia": "dairy" if any(w in text_to_analyze for w in ["milk", "cream", "cheese"]) else None,
            
            # Breakfast Cereals
            "kellogs": "breakfast_cereal",
            "kellogg": "breakfast_cereal",
            "quaker": "breakfast_cereal",
            "saffola": "breakfast_cereal" if "oats" in text_to_analyze else None,
            "bagrry": "breakfast_cereal",
            
            # Biscuits & Cookies
            "parle": "biscuits",
            "britannia": "biscuits" if not any(w in text_to_analyze for w in ["milk", "bread", "cake"]) else None,
            "sunfeast": "biscuits" if not "yippee" in text_to_analyze else None,
            "mcvities": "biscuits",
            "oreo": "biscuits",
            "hide & seek": "biscuits",
            
            # Chocolates & Confectionery
            "cadbury": "chocolate",
            "dairy milk": "chocolate",
            "bournville": "chocolate",
            "kitkat": "chocolate",
            "nestle": "chocolate" if any(w in text_to_analyze for w in ["kitkat", "munch", "bar one"]) else None,
            "ferrero": "chocolate",
            "hershey": "chocolate",
            "snickers": "chocolate",
            "milkybar": "chocolate",
            "5 star": "chocolate",
            
            # Beverages
            "coca cola": "carbonated_beverage",
            "coca-cola": "carbonated_beverage",
            "pepsi": "carbonated_beverage",
            "sprite": "carbonated_beverage",
            "fanta": "carbonated_beverage",
            "limca": "carbonated_beverage",
            "thums up": "carbonated_beverage",
            "maaza": "fruit_drink",
            "frooti": "fruit_drink",
            "slice": "fruit_drink",
            "appy fizz": "fruit_drink",
            "tropicana": "juice",
            "real": "juice",
            "paper boat": "traditional_beverage",
            "bournvita": "health_drink",
            "horlicks": "health_drink",
            "complan": "health_drink",
            "boost": "health_drink",
            
            # Snacks
            "lays": "potato_chips",
            "kurkure": "corn_snack",
            "bingo": "potato_chips",
            "haldiram": "namkeen",
            "haldirams": "namkeen",
            "bikano": "namkeen",
            "uncle chipps": "potato_chips",
            "pringles": "potato_chips",
            "doritos": "corn_chips",
            
            # Traditional/Ayurvedic
            "dabur": "ayurvedic",
            "patanjali": "ayurvedic",
            "himalaya": "ayurvedic",
            
            # Condiments
            "kissan": "condiments",
            "maggi": "condiments" if "sauce" in text_to_analyze or "ketchup" in text_to_analyze else None,
            "ching": "condiments",
            
            # Spices
            "mdh": "spices",
            "everest": "spices",
            "catch": "spices",
            
            # Bread & Bakery
            "britannia": "bread" if "bread" in text_to_analyze else None,
            "harvest gold": "bread",
            "modern": "bread",
            "kitty": "bread",
        }
        
        # Check for brand-specific categorization with confidence boost
        for brand, category in brand_product_map.items():
            if brand in text_to_analyze and category:
                confidence += 0.3
                matched_keywords.append(f"brand:{brand}")
                classification_method = "brand_mapping"
                
                # Further refinement for multi-product brands
                if brand in ["kellogs", "kellogg"]:
                    if any(cereal in text_to_analyze for cereal in ["chocos", "coco pops", "chocolate"]):
                        return {"type": "chocolate_cereal", "confidence": min(confidence + 0.2, 1.0), "method": classification_method, "matched_keywords": matched_keywords}
                    elif "corn flakes" in text_to_analyze:
                        return {"type": "corn_flakes", "confidence": min(confidence + 0.2, 1.0), "method": classification_method, "matched_keywords": matched_keywords}
                    else:
                        return {"type": "breakfast_cereal", "confidence": confidence, "method": classification_method, "matched_keywords": matched_keywords}
                
                elif brand == "amul":
                    if "ice cream" in text_to_analyze or "kulfi" in text_to_analyze:
                        return {"type": "ice_cream", "confidence": min(confidence + 0.2, 1.0), "method": classification_method, "matched_keywords": matched_keywords}
                    elif "milk" in text_to_analyze:
                        return {"type": "packaged_milk", "confidence": min(confidence + 0.2, 1.0), "method": classification_method, "matched_keywords": matched_keywords}
                    elif "butter" in text_to_analyze:
                        return {"type": "butter", "confidence": min(confidence + 0.2, 1.0), "method": classification_method, "matched_keywords": matched_keywords}
                    elif "cheese" in text_to_analyze:
                        return {"type": "cheese", "confidence": min(confidence + 0.2, 1.0), "method": classification_method, "matched_keywords": matched_keywords}
                    else:
                        return {"type": category, "confidence": confidence, "method": classification_method, "matched_keywords": matched_keywords}
                
                else:
                    return {"type": category, "confidence": confidence, "method": classification_method, "matched_keywords": matched_keywords}
        
        # Priority-based keyword classification with multi-level matching
        classification_rules = {
            # Frozen Desserts
            "ice_cream": {
                "high_priority": ["ice cream", "kulfi", "gelato"],
                "medium_priority": ["frozen dessert", "sundae", "cone"],
                "low_priority": ["frozen", "dessert"]
            },
            
            # Baked Goods
            "biscuits": {
                "high_priority": ["biscuit", "cookie", "marie", "glucose biscuit"],
                "medium_priority": ["cracker", "digestive", "cream biscuit"],
                "low_priority": ["wafer", "rusk"]
            },
            
            # Chocolates
            "chocolate": {
                "high_priority": ["chocolate bar", "cocoa", "dark chocolate", "milk chocolate"],
                "medium_priority": ["chocolate", "choco", "cacao"],
                "low_priority": ["cocoa powder"]
            },
            
            "chocolate_drink": {
                "high_priority": ["chocolate drink", "cocoa drink", "drinking chocolate"],
                "medium_priority": ["choco drink"],
                "low_priority": []
            },
            
            # Health Drinks
            "health_drink": {
                "high_priority": ["health drink", "malt drink", "energy drink"],
                "medium_priority": ["health food drink", "nutritional drink"],
                "low_priority": ["protein drink"]
            },
            
            # Noodles & Pasta
            "instant_noodles": {
                "high_priority": ["instant noodles", "2 minute noodles", "cup noodles"],
                "medium_priority": ["noodles", "ramen", "hakka noodles"],
                "low_priority": ["pasta", "vermicelli"]
            },
            
            # Breakfast Cereals
            "breakfast_cereal": {
                "high_priority": ["breakfast cereal", "corn flakes", "wheat flakes"],
                "medium_priority": ["cereal", "flakes", "muesli", "granola"],
                "low_priority": ["oats", "porridge", "breakfast"]
            },
            
            # Snacks
            "potato_chips": {
                "high_priority": ["potato chips", "potato crisps", "aloo chips"],
                "medium_priority": ["chips", "crisps"],
                "low_priority": []
            },
            
            "namkeen": {
                "high_priority": ["namkeen", "bhujia", "mixture", "sev"],
                "medium_priority": ["savory snack", "indian snack"],
                "low_priority": ["snack mix"]
            },
            
            "corn_snack": {
                "high_priority": ["corn puffs", "cheese puffs", "masala puffs"],
                "medium_priority": ["corn snack", "puffs"],
                "low_priority": []
            },
            
            # Beverages
            "carbonated_beverage": {
                "high_priority": ["cola", "soda", "carbonated drink", "soft drink"],
                "medium_priority": ["fizzy drink", "carbonated"],
                "low_priority": ["aerated"]
            },
            
            "fruit_drink": {
                "high_priority": ["fruit drink", "mango drink", "orange drink"],
                "medium_priority": ["fruit beverage", "flavored drink"],
                "low_priority": []
            },
            
            "juice": {
                "high_priority": ["100% juice", "fruit juice", "vegetable juice"],
                "medium_priority": ["juice", "fresh juice"],
                "low_priority": []
            },
            
            # Dairy
            "packaged_milk": {
                "high_priority": ["toned milk", "full cream milk", "skimmed milk", "cow milk", "buffalo milk"],
                "medium_priority": ["milk", "dairy milk"],
                "low_priority": []
            },
            
            "yogurt": {
                "high_priority": ["yogurt", "curd", "dahi", "greek yogurt"],
                "medium_priority": ["yoghurt", "probiotic drink"],
                "low_priority": []
            },
            
            # Bread & Bakery
            "bread": {
                "high_priority": ["bread", "sandwich bread", "whole wheat bread", "multigrain bread"],
                "medium_priority": ["loaf", "pav", "bun"],
                "low_priority": ["bakery"]
            },
            
            # Condiments
            "ketchup": {
                "high_priority": ["tomato ketchup", "ketchup"],
                "medium_priority": ["tomato sauce"],
                "low_priority": []
            },
            
            "sauce": {
                "high_priority": ["chili sauce", "soy sauce", "hot sauce"],
                "medium_priority": ["sauce"],
                "low_priority": []
            },
        }
        
        # Match against classification rules with priority scoring
        best_match = None
        best_score = 0
        
        for category, rules in classification_rules.items():
            score = 0
            matches = []
            
            # Check high priority keywords (3 points each)
            for keyword in rules["high_priority"]:
                if keyword in text_to_analyze:
                    score += 3
                    matches.append(f"high:{keyword}")
            
            # Check medium priority keywords (2 points each)
            for keyword in rules["medium_priority"]:
                if keyword in text_to_analyze:
                    score += 2
                    matches.append(f"med:{keyword}")
            
            # Check low priority keywords (1 point each)
            for keyword in rules["low_priority"]:
                if keyword in text_to_analyze:
                    score += 1
                    matches.append(f"low:{keyword}")
            
            # Update best match if this category scores higher
            if score > best_score:
                best_score = score
                best_match = category
                matched_keywords = matches
        
        # Calculate final confidence based on match score
        if best_match:
            # Score-based confidence (max 0.95 for pattern matching)
            if best_score >= 5:
                confidence = 0.9
            elif best_score >= 3:
                confidence = 0.75
            elif best_score >= 2:
                confidence = 0.6
            else:
                confidence = 0.5
            
            return {
                "type": best_match,
                "confidence": confidence,
                "method": "keyword_matching",
                "matched_keywords": matched_keywords,
                "match_score": best_score
            }
        
        # Fallback to generic processed food
        return {
            "type": "processed_food",
            "confidence": 0.3,
            "method": "fallback",
            "matched_keywords": [],
            "match_score": 0
        }

# Global instances
ocr_agent = OCRAgent()
barcode_agent = BarcodeAgent()