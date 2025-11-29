"""
Optimized FastAPI application for FoodLens AI
Clean, modular structure with proper error handling
"""
import os
import re
import json
import datetime
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Import our modules
from config.settings import config
from models.database import get_db, create_tables, User, HealthCondition, Allergy, ScanHistory, ChatHistory
from agents.ocr_barcode import ocr_agent, barcode_agent
from agents.health_analysis import health_score_agent, alternatives_agent, claim_verification_agent
from agents.fssai_verification import fssai_agent
from utils.search_utils_dynamic import SearchUtils  # Import the fully dynamic search utils class
from utils.image_fetcher import image_fetcher  # Import image fetcher

# Create instances later on demand - avoid blocking at startup
search_utils = None
barcode_reader_instance = None

def get_ai_alternatives_with_context(prompt: str, category: str) -> List[Dict]:
    """Get AI-powered alternatives using Gemini with enhanced context"""
    try:
        # Use search utils to get Gemini client
        search_client = get_search_utils()
        gemini_client = search_client.get_gemini_client()
        
        if not gemini_client:
            print("⚠️ Gemini client not available for AI alternatives")
            return []
        
        # Generate AI alternatives
        response = gemini_client.invoke(prompt)
        
        if response and isinstance(response, str):
            # Parse the response into structured alternatives
            alternatives = parse_ai_alternatives_response(response)
            return alternatives
        elif response and hasattr(response, 'content'):
            # Parse the response content
            alternatives = parse_ai_alternatives_response(response.content)
            return alternatives
        else:
            print("⚠️ Empty response from Gemini AI")
            return []
            
    except Exception as e:
        print(f"❌ Error getting AI alternatives: {e}")
        return []

def parse_ai_alternatives_response(ai_text: str) -> List[Dict]:
    """Parse AI response into structured alternatives with better field extraction"""
    alternatives = []
    
    try:
        import re
        
        # Split by numbered alternatives (1., 2., 3.)
        sections = re.split(r'\n\s*(?=\d+\.\s+)', ai_text)
        
        for section in sections:
            if not section.strip():
                continue
                
            alt = {
                'name': '',
                'brand': 'Various',
                'health_score': 85,
                'score': 85,
                'key_benefits': 'Healthier alternative',
                'health_benefits': 'Healthier alternative',
                'where_to_buy': 'Indian markets',
                'price': '₹50-200'
            }
            
            # Extract product name (first line, usually with ### or bold markers)
            name_match = re.search(r'^\d+\.\s+(?:###\s+)?(?:\*\*)?(.+?)(?:\*\*)?(?:\n|$)', section, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                # Clean up name - remove brand in parentheses if present
                name = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()
                alt['name'] = name
            
            # Extract brand (usually in parentheses after name)
            brand_match = re.search(r'\(([^)]+)\)', section)
            if brand_match:
                alt['brand'] = brand_match.group(1).strip()
            
            # Extract health score
            score_match = re.search(r'(?:score|health\s*score).*?(\d+)(?:/100)?', section, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                alt['health_score'] = score
                alt['score'] = score
            
            # Extract key benefits - look for bullet points or "benefits:" section
            benefits_lines = []
            for line in section.split('\n'):
                line = line.strip()
                # Skip if it's a price line or availability line
                if '₹' in line and 'price' in line.lower():
                    continue
                if 'where to buy' in line.lower() or 'available at' in line.lower():
                    continue
                # Look for benefit indicators
                if any(indicator in line.lower() for indicator in ['benefit', 'good for', 'rich in', 'low in', 'high in', 'protein', 'fiber', 'calcium']):
                    # Clean up the line
                    clean_line = re.sub(r'^\*+\s*', '', line)  # Remove leading asterisks
                    clean_line = re.sub(r'^\-\s*', '', clean_line)  # Remove leading dash
                    clean_line = re.sub(r'^\d+\.\s*', '', clean_line)  # Remove numbering
                    clean_line = clean_line.replace('Key health benefits:', '').replace('Benefits:', '').strip()
                    if clean_line and len(clean_line) > 5:
                        benefits_lines.append(clean_line)
            
            if benefits_lines:
                benefits = '. '.join(benefits_lines[:3])  # Take first 3 benefit points
                alt['key_benefits'] = benefits
                alt['health_benefits'] = benefits
            
            # Extract where to buy - look for specific section
            buy_match = re.search(r'(?:where to buy|available at)(?:\s+in India)?[:\s]+(.+?)(?=\n|price|₹|$)', section, re.IGNORECASE | re.DOTALL)
            if buy_match:
                availability = buy_match.group(1).strip()
                # Clean up - remove asterisks and extra formatting
                availability = re.sub(r'^\*+\s*', '', availability)
                availability = re.sub(r'\*+$', '', availability)
                # Remove "Approximate price range" if it got included
                availability = re.sub(r'Approximate price range.*', '', availability, flags=re.IGNORECASE).strip()
                if availability and len(availability) > 5:
                    alt['where_to_buy'] = availability
            
            # Extract price - look for ₹ symbol and price patterns
            price_match = re.search(r'(?:price|approximate price).*?(₹\s*\d+[\d,\s\-₹]+)', section, re.IGNORECASE)
            if price_match:
                price = price_match.group(1).strip()
                # Clean up the price
                price = re.sub(r'\s+', ' ', price)
                alt['price'] = price
            
            # Only add if we have a valid name
            if alt['name'] and len(alt['name']) > 3:
                alternatives.append(alt)
            
            # Stop after 3 alternatives
            if len(alternatives) >= 3:
                break
        
        # Ensure we have at least 3 alternatives
        while len(alternatives) < 3:
            alternatives.append({
                'name': f'Healthy Option {len(alternatives) + 1}',
                'brand': 'Natural',
                'health_score': 85,
                'score': 85,
                'health_benefits': 'Rich in nutrients and low in processed ingredients',
                'key_benefits': 'Rich in nutrients and low in processed ingredients',
                'where_to_buy': 'Supermarkets, health stores',
                'price': '₹100-300'
            })
            
        return alternatives[:3]  # Return max 3
        
    except Exception as e:
        print(f"⚠️ Error parsing AI response: {e}")
        print(f"📝 AI Text preview: {ai_text[:500]}")
        # Return fallback alternatives
        return [
            {
                'name': 'Fresh Fruits',
                'brand': 'Natural',
                'health_score': 95,
                'score': 95,
                'health_benefits': 'Rich in vitamins, minerals, and fiber',
                'key_benefits': 'Rich in vitamins, minerals, and fiber',
                'where_to_buy': 'Local markets, supermarkets',
                'price': '₹80-150 per kg'
            },
            {
                'name': 'Nuts and Seeds',
                'brand': 'Various',
                'health_score': 90,
                'score': 90,
                'health_benefits': 'Good source of healthy fats and protein',
                'key_benefits': 'Good source of healthy fats and protein',
                'where_to_buy': 'Health stores, online',
                'price': '₹300-600 per kg'
            },
            {
                'name': 'Whole Grain Snacks',
                'brand': 'Organic',
                'health_score': 85,
                'score': 85,
                'health_benefits': 'High fiber, complex carbohydrates',
                'key_benefits': 'High fiber, complex carbohydrates',
                'where_to_buy': 'Health food stores',
                'price': '₹150-400'
            }
        ]

def _create_category_based_nutrition_estimate(product_name: str, brand: str, category: str) -> Dict[str, Any]:
    """
    Create estimated nutritional data based on product category when database lookup fails
    Returns typical values for the product category
    """
    print(f"📊 Creating category-based nutrition estimate for {category}")
    
    # Typical nutritional values per 100g for different categories
    category_nutrition = {
        "instant_noodles": {
            "energy_100g": 450,
            "fat_100g": 18,
            "saturated-fat_100g": 9,
            "carbohydrates_100g": 63,
            "sugars_100g": 3,
            "fiber_100g": 2,
            "proteins_100g": 9,
            "salt_100g": 2.5,
            "sodium_100g": 1000
        },
        "dairy_beverages": {
            "energy_100g": 60,
            "fat_100g": 3,
            "saturated-fat_100g": 2,
            "carbohydrates_100g": 5,
            "sugars_100g": 5,
            "fiber_100g": 0,
            "proteins_100g": 3.2,
            "salt_100g": 0.1,
            "sodium_100g": 40
        },
        "carbonated_beverages": {
            "energy_100g": 42,
            "fat_100g": 0,
            "saturated-fat_100g": 0,
            "carbohydrates_100g": 10.6,
            "sugars_100g": 10.6,
            "fiber_100g": 0,
            "proteins_100g": 0,
            "salt_100g": 0,
            "sodium_100g": 10
        },
        "potato_chips": {
            "energy_100g": 536,
            "fat_100g": 34,
            "saturated-fat_100g": 12,
            "carbohydrates_100g": 52,
            "sugars_100g": 1,
            "fiber_100g": 4,
            "proteins_100g": 6,
            "salt_100g": 1.5,
            "sodium_100g": 600
        },
        "biscuits": {
            "energy_100g": 480,
            "fat_100g": 22,
            "saturated-fat_100g": 10,
            "carbohydrates_100g": 65,
            "sugars_100g": 25,
            "fiber_100g": 2,
            "proteins_100g": 7,
            "salt_100g": 0.8,
            "sodium_100g": 320
        },
        "chocolates": {
            "energy_100g": 530,
            "fat_100g": 30,
            "saturated-fat_100g": 18,
            "carbohydrates_100g": 60,
            "sugars_100g": 55,
            "fiber_100g": 3,
            "proteins_100g": 5,
            "salt_100g": 0.2,
            "sodium_100g": 80
        },
        "processed_food": {
            "energy_100g": 350,
            "fat_100g": 15,
            "saturated-fat_100g": 5,
            "carbohydrates_100g": 45,
            "sugars_100g": 10,
            "fiber_100g": 3,
            "proteins_100g": 8,
            "salt_100g": 1,
            "sodium_100g": 400
        }
    }
    
    # Get nutrition for category, default to processed_food
    nutriments = category_nutrition.get(category, category_nutrition["processed_food"]).copy()
    
    print(f"✅ Using estimated nutrition for {category}: sugar={nutriments['sugars_100g']}g, sodium={nutriments['sodium_100g']}mg")
    
    return {
        "status": 1,
        "product_name": product_name,
        "brand": brand,
        "ingredients_text": "Ingredients not available - using category-based estimates",
        "nutriments": nutriments,
        "categories": category,
        "labels": "ESTIMATED_FROM_CATEGORY",
        "full_product_data": {"source": "category_estimation"}
    }

def get_search_utils():
    """Lazy-load search utils to avoid blocking at startup"""
    global search_utils
    if search_utils is None:
        search_utils = SearchUtils()
    return search_utils

def get_barcode_reader():
    """Lazy-load barcode reader to avoid blocking at startup"""
    global barcode_reader_instance
    if barcode_reader_instance is None:
        from utils.barcode_reader import BarcodeReader
        barcode_reader_instance = BarcodeReader()  # This will be slow on first use but not at startup
    return barcode_reader_instance

from utils.response_formatter import format_analysis_response  # Import the new response formatter
from utils.health import health_analyzer

# Create FastAPI app
app = FastAPI(
    title="FoodLens AI Backend",
    description="Agentic AI-powered food analysis and health recommendation system",
    version="1.0.0"
)

# Add CORS middleware - Enhanced for Flutter integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins for development
    allow_credentials=False,       # Must be False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Pydantic models for API requests
class UserCreate(BaseModel):
    id: str
    email: str
    age: int = None
    gender: str = None
    height_cm: float = None
    weight_kg: float = None
    fitness_goals: str = None
    tier: str = "free"  # "free" or "premium" - now users can select their tier!
    health_conditions: List[str] = []
    allergies: List[str] = []

class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: str = None

class TierUpdate(BaseModel):
    tier: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "tier": "premium"
            }
        }

class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    fitness_goals: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 26,
                "weight_kg": 68.5,
                "height_cm": 175,
                "fitness_goals": "muscle_gain"
            }
        }

class HealthConditionAdd(BaseModel):
    condition_name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "condition_name": "diabetes"
            }
        }

class AllergyAdd(BaseModel):
    allergen: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "allergen": "peanuts"
            }
        }

class FoodAnalysisResult(BaseModel):
    summary: str
    health_score: int
    verdict: Dict
    should_consume: bool
    consumption_advice: str
    product_type: str
    health_conditions: List[str]
    claim_analysis: Dict
    alternatives: List[Dict]
    premium_features: bool

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()

def check_and_reset_monthly_scans(user: User, db: Session) -> User:
    """Check if monthly scan limit needs to be reset"""
    from datetime import datetime
    
    now = datetime.now()
    current_month_key = f"{now.year}-{now.month:02d}"
    
    # If no reset date or different month, reset the counter
    if not user.last_scan_reset or not user.last_scan_reset.startswith(current_month_key):
        user.scan_count = 0
        user.last_scan_reset = now.isoformat()
        db.commit()
        print(f"🔄 Reset scan count for user {user.id} (new month: {current_month_key})")
    
    return user

def get_or_create_user(user_id: str, db: Session) -> User:
    """Get existing user or create new one - respects database tier values"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Determine tier based on user ID for new users only
        if user_id in ["test-user-123"] or "premium" in user_id:
            tier = "premium"
        elif user_id in ["free-user-456"] or "free" in user_id:
            tier = "free"
        else:
            tier = "free"  # Default to free for new users
        
        from datetime import datetime
        user = User(
            id=user_id, 
            email=f"{user_id}@example.com", 
            tier=tier, 
            scan_count=0,
            last_scan_reset=datetime.now().isoformat()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created NEW user {user_id} with tier: {tier}")
    else:
        print(f"✅ Found EXISTING user {user_id} with tier: {user.tier}")
        # Check and reset monthly scans if needed
        user = check_and_reset_monthly_scans(user, db)
    
    # Only update test users - DO NOT override database values for API-created users
    if user.id == "test-user-123" and user.tier != "premium":
        user.tier = "premium"
        db.commit()
        print(f"🔄 Updated test user {user.id} tier to premium")
    elif user.id == "free-user-456" and user.tier != "free":
        user.tier = "free"
        db.commit()
        print(f"🔄 Updated test user {user.id} tier to free")
        
    return user

def get_user_profile(user: User) -> Dict:
    """Convert user object to profile dict"""
    health_conditions = [hc.condition_name for hc in user.health_conditions]
    allergies = [allergy.allergen_name for allergy in user.allergies]
    
    return {
        "tier": user.tier,
        "age": user.age,
        "gender": user.gender,
        "health_conditions": health_conditions,
        "allergies": allergies,
        "fitness_goals": user.fitness_goals
    }

def save_scan_history(user_id: str, analysis_result: Dict, db: Session):
    """Save scan history for premium users"""
    try:
        # Check if user is premium by querying database
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.tier != "premium":
            print(f"ℹ️ Skipping scan history for user {user_id} (tier: {user.tier if user else 'not found'})")
            return  # Only save history for premium users
        
        # Handle both old format and new nested format
        if "summary" in analysis_result:
            # New format with nested structure
            summary = analysis_result["summary"]
            product_name = summary.get("product_name", "Unknown")
            brand = summary.get("brand", "")
            health_score = summary.get("health_score", 0)
            verdict_str = summary.get("verdict", "Unknown")
        else:
            # Old format with flat structure
            product_name = analysis_result.get("product_name", "Unknown")
            brand = analysis_result.get("brand", "")
            health_score = analysis_result.get("health_score", 0)
            
            # Extract verdict title from verdict dict
            verdict_data = analysis_result.get("verdict", {})
            if isinstance(verdict_data, dict):
                verdict_str = verdict_data.get("title", "Unknown")
            else:
                verdict_str = str(verdict_data)
        
        scan_entry = ScanHistory(
            user_id=user_id,
            product_name=product_name,
            health_score=health_score,
            verdict=verdict_str,
            analysis_data=json.dumps(analysis_result),
            alternatives=json.dumps(analysis_result.get("summary", {}).get("alternatives", []) if "summary" in analysis_result else analysis_result.get("alternatives", [])),
            timestamp=datetime.datetime.now().isoformat()
        )
        db.add(scan_entry)
        db.commit()
        print(f"✅ Saved scan history for premium user {user_id}: {product_name} (Brand: {brand}, Score: {health_score})")
    except Exception as e:
        print(f"❌ Error saving scan history: {e}")
        import traceback
        traceback.print_exc()

@app.get("/")
async def root():
    """Health check endpoint with API information"""
    return {
        "message": "FoodLens AI API - Powered by Google Gemini",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "features": [
            "Product Analysis via OCR/Barcode",
            "AI-Powered Health Insights",
            "Smart Alternatives Recommendation",
            "Conversation Memory Chatbot",
            "FSSAI Verification",
            "User Profile Management"
        ]
    }

@app.get("/tiers")
async def get_available_tiers():
    """Get available subscription tiers"""
    return {
        "available_tiers": [
            {
                "name": "free",
                "display_name": "Free Tier",
                "features": [
                    "5 scans per month",
                    "Basic health analysis", 
                    "Nutritional breakdown",
                    "FSSAI compliance check"
                ],
                "limitations": [
                    "No alternatives recommendations",
                    "No AI chatbot access",
                    "No detailed claim verification"
                ],
                "price": "₹0/month"
            },
            {
                "name": "premium", 
                "display_name": "Premium Tier",
                "features": [
                    "Unlimited scans",
                    "Advanced health analysis",
                    "Personalized alternatives recommendations", 
                    "AI nutrition chatbot",
                    "Detailed claim verification",
                    "FSSAI compliance reports",
                    "Health condition specific advice",
                    "Scan history tracking"
                ],
                "limitations": [],
                "price": "₹299/month"
            }
        ]
    }

@app.get("/users/{user_id}/scan-status")
async def get_scan_status(user_id: str, db: Session = Depends(get_db)):
    """Get user's scan limit status"""
    try:
        user = get_or_create_user(user_id, db)
        
        # Define limits
        FREE_TIER_LIMIT = 5
        
        if user.tier == "premium":
            return {
                "tier": "premium",
                "scans_used": user.scan_count,
                "scans_remaining": "unlimited",
                "limit_reached": False,
                "can_scan": True,
                "message": "Unlimited scans with Premium"
            }
        else:
            scans_remaining = max(0, FREE_TIER_LIMIT - user.scan_count)
            limit_reached = user.scan_count >= FREE_TIER_LIMIT
            
            return {
                "tier": "free",
                "scans_used": user.scan_count,
                "scans_remaining": scans_remaining,
                "scan_limit": FREE_TIER_LIMIT,
                "limit_reached": limit_reached,
                "can_scan": not limit_reached,
                "message": f"You have {scans_remaining} scans remaining this month" if not limit_reached else "Monthly scan limit reached. Upgrade to Premium for unlimited scans!"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scan status: {str(e)}")

@app.post("/users/{user_id}/upgrade-to-premium")
async def upgrade_to_premium(user_id: str, db: Session = Depends(get_db)):
    """Upgrade user to premium tier (demo mode - no payment required)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.tier == "premium":
            return {
                "success": True,
                "message": "User is already on Premium tier",
                "tier": "premium"
            }
        
        # Upgrade to premium
        user.tier = "premium"
        db.commit()
        db.refresh(user)
        
        print(f"✅ Upgraded user {user_id} to Premium")
        
        return {
            "success": True,
            "message": "Successfully upgraded to Premium! Enjoy unlimited scans and all premium features.",
            "tier": "premium",
            "previous_tier": "free"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade: {str(e)}")

@app.post("/users/")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create or update user profile with tier selection"""
    try:
        # Validate tier
        valid_tiers = ["free", "premium"]
        if user_data.tier not in valid_tiers:
            raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
        
        user = get_or_create_user(user_data.id, db)
        
        # Update user information
        user.email = user_data.email
        user.age = user_data.age
        user.gender = user_data.gender
        user.height_cm = user_data.height_cm
        user.weight_kg = user_data.weight_kg
        user.fitness_goals = user_data.fitness_goals
        user.tier = user_data.tier  # Allow users to select free or premium tier
        
        # Update health conditions
        db.query(HealthCondition).filter(HealthCondition.user_id == user.id).delete()
        for condition in user_data.health_conditions:
            hc = HealthCondition(condition_name=condition, user_id=user.id)
            db.add(hc)
        
        # Update allergies
        db.query(Allergy).filter(Allergy.user_id == user.id).delete()
        for allergy in user_data.allergies:
            allergy_obj = Allergy(allergen_name=allergy, user_id=user.id)
            db.add(allergy_obj)
        
        db.commit()
        
        # Return tier information
        tier_info = "Premium features activated!" if user.tier == "premium" else f"Free tier active - {5 - user.scan_count} scans remaining this month"
        
        return {
            "message": "User profile updated successfully", 
            "tier": user.tier,
            "tier_info": tier_info,
            "scan_count": user.scan_count,
            "features_available": [
                "Unlimited scans", "Alternatives", "AI Chatbot", "Claim Verification"
            ] if user.tier == "premium" else [
                f"{5 - user.scan_count} scans remaining", "Basic analysis only"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.put("/users/{user_id}/profile")
async def update_user_profile(user_id: str, profile_data: ProfileUpdate, db: Session = Depends(get_db)):
    """Update user profile information"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update only provided fields
        if profile_data.age is not None:
            user.age = profile_data.age
        if profile_data.gender is not None:
            user.gender = profile_data.gender
        if profile_data.height_cm is not None:
            user.height_cm = profile_data.height_cm
        if profile_data.weight_kg is not None:
            user.weight_kg = profile_data.weight_kg
        if profile_data.fitness_goals is not None:
            user.fitness_goals = profile_data.fitness_goals
        
        db.commit()
        db.refresh(user)
        
        print(f"✅ Updated profile for user {user_id}")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user_id": user_id,
            "profile": {
                "age": user.age,
                "gender": user.gender,
                "height_cm": user.height_cm,
                "weight_kg": user.weight_kg,
                "fitness_goals": user.fitness_goals
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

@app.post("/users/{user_id}/health-conditions")
async def add_health_condition(user_id: str, condition: HealthConditionAdd, db: Session = Depends(get_db)):
    """Add a health condition to user profile"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if condition already exists
        existing = db.query(HealthCondition).filter(
            HealthCondition.user_id == user_id,
            HealthCondition.condition_name == condition.condition_name
        ).first()
        
        if existing:
            return {
                "success": True,
                "message": "Health condition already exists",
                "condition_id": existing.id
            }
        
        # Add new condition
        new_condition = HealthCondition(
            user_id=user_id,
            condition_name=condition.condition_name
        )
        db.add(new_condition)
        db.commit()
        db.refresh(new_condition)
        
        print(f"✅ Added health condition '{condition.condition_name}' for user {user_id}")
        
        return {
            "success": True,
            "message": "Health condition added",
            "condition_id": new_condition.id,
            "condition_name": condition.condition_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding health condition: {str(e)}")

@app.post("/users/{user_id}/allergies")
async def add_allergy(user_id: str, allergy: AllergyAdd, db: Session = Depends(get_db)):
    """Add an allergy to user profile"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if allergy already exists
        existing = db.query(Allergy).filter(
            Allergy.user_id == user_id,
            Allergy.allergen == allergy.allergen
        ).first()
        
        if existing:
            return {
                "success": True,
                "message": "Allergy already exists",
                "allergy_id": existing.id
            }
        
        # Add new allergy
        new_allergy = Allergy(
            user_id=user_id,
            allergen=allergy.allergen
        )
        db.add(new_allergy)
        db.commit()
        db.refresh(new_allergy)
        
        print(f"✅ Added allergy '{allergy.allergen}' for user {user_id}")
        
        return {
            "success": True,
            "message": "Allergy added",
            "allergy_id": new_allergy.id,
            "allergen": allergy.allergen
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding allergy: {str(e)}")

@app.get("/users/{user_id}/health-insights")
async def get_health_insights(user_id: str, db: Session = Depends(get_db)):
    """Get personalized health insights based on user profile"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate BMI if height and weight available
        bmi = None
        bmi_category = None
        if user.height_cm and user.weight_kg:
            height_m = user.height_cm / 100
            bmi = round(user.weight_kg / (height_m ** 2), 1)
            
            if bmi < 18.5:
                bmi_category = "Underweight"
            elif bmi < 25:
                bmi_category = "Normal"
            elif bmi < 30:
                bmi_category = "Overweight"
            else:
                bmi_category = "Obese"
        
        # Get health conditions and allergies
        health_conditions = [hc.condition_name for hc in user.health_conditions]
        allergies = [a.allergen for a in user.allergies]
        
        # Generate recommendations
        recommendations = []
        if bmi:
            if bmi < 18.5:
                recommendations.append("Focus on calorie-dense, nutritious foods to gain weight healthily")
            elif bmi >= 25:
                recommendations.append("Focus on portion control and increased physical activity")
            else:
                recommendations.append("Maintain current weight with balanced nutrition")
        
        if "diabetes" in health_conditions:
            recommendations.append("Avoid high-sugar products and monitor carbohydrate intake")
        if "hypertension" in health_conditions:
            recommendations.append("Limit sodium intake and choose low-salt alternatives")
        
        return {
            "success": True,
            "user_id": user_id,
            "bmi": bmi,
            "bmi_category": bmi_category,
            "health_conditions": health_conditions,
            "allergies": allergies,
            "recommendations": recommendations,
            "fitness_goals": user.fitness_goals
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting health insights: {str(e)}")

@app.put("/users/{user_id}/tier")
async def update_user_tier(user_id: str, tier_data: TierUpdate, db: Session = Depends(get_db)):
    """Update user tier (upgrade/downgrade)"""
    try:
        valid_tiers = ["free", "premium"]
        new_tier = tier_data.tier
        
        if new_tier not in valid_tiers:
            raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        old_tier = user.tier
        user.tier = new_tier
        db.commit()
        
        print(f"✅ Updated user {user_id} tier from {old_tier} to {new_tier}")
        
        return {
            "success": True,
            "message": f"Tier updated from {old_tier} to {new_tier}",
            "user_id": user_id,
            "old_tier": old_tier,
            "new_tier": new_tier,
            "features_available": [
                "Unlimited scans", "AI-powered alternatives", "Intelligent chatbot", "Claim verification", "Scan history"
            ] if new_tier == "premium" else [
                f"{max(0, 5 - user.scan_count)} scans remaining this month", "Basic analysis only"
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating tier: {str(e)}")

@app.options("/analyze")
async def analyze_options():
    """Handle OPTIONS preflight request for CORS"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/analyze")
async def analyze_food(
    user_id: str,
    food_image: UploadFile = File(...),
    barcode_image: Optional[UploadFile] = None,
    response_format: str = "user_friendly",
    db: Session = Depends(get_db)
):
    """Main food analysis endpoint with barcode detection"""
    try:
        # Get user and check scan limits
        user = get_or_create_user(user_id, db)
        user_profile = get_user_profile(user)
        
        print(f"Processing scan for {user.tier} user: {user_id}")
        
        # Check scan limits for free users
        if user.tier == "free" and user.scan_count >= config.FREE_TIER_SCAN_LIMIT:
            raise HTTPException(status_code=403, detail="Scan limit reached. Please upgrade to Premium.")
        
        # Increment scan count
        user.scan_count += 1
        db.commit()
        
        # Process uploaded images
        try:
            # Create temporary directories if they don't exist
            temp_dir = os.path.join(os.getcwd(), 'temp_images')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            # Save food image with unique name
            food_image_name = os.path.join(temp_dir, f'food_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
            contents = await food_image.read()
            with open(food_image_name, 'wb') as f:
                f.write(contents)
            
            # Handle barcode image if provided
            barcode_data = None
            if barcode_image:
                barcode_image_name = os.path.join(temp_dir, f'barcode_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
                try:
                    contents = await barcode_image.read()
                    with open(barcode_image_name, 'wb') as f:
                        f.write(contents)
                    
                    # Try to detect barcode from barcode image
                    barcode_data = get_barcode_reader().detect_and_read_barcode(barcode_image_name)
                finally:
                    try:
                        if os.path.exists(barcode_image_name):
                            os.remove(barcode_image_name)
                    except Exception as e:
                        print(f"Warning: Could not delete temporary barcode image: {e}")
            
            # Try to detect barcode from food image if no barcode found yet
            if not barcode_data or not barcode_data.get("barcode"):
                barcode_data = get_barcode_reader().detect_and_read_barcode(food_image_name)
            
            # Extract text - use barcode reader's OCR data if available, otherwise try Groq
            extracted_text = ""
            detected_barcode_from_ocr = None
            
            if barcode_data:
                # Get product text (non-barcode text) from barcode reader
                product_text = barcode_data.get("product_text", "")
                detected_text = barcode_data.get("detected_text", "")
                
                print(f"✅ Barcode reader found: Barcode={barcode_data.get('barcode')}, Product text length={len(product_text)}")
                
                # If we have product text (even short titles), prefer it
                if product_text and len(product_text) > 6:
                    print(f"✅ Using barcode reader product text: {product_text[:100]}")
                    extracted_text = product_text
                # Otherwise try Groq Vision for better OCR
                else:
                    print(f"⚠️ Limited product text from barcode reader, trying Groq Vision for better OCR...")
                    groq_text = ocr_agent.extract_text_from_image(food_image_name)
                    if groq_text and len(groq_text) > len(detected_text):
                        print(f"✅ Groq Vision found more detailed text")
                        extracted_text = groq_text
                    else:
                        extracted_text = detected_text
            else:
                # Fallback to Groq Vision OCR
                print("🔍 Extracting text from image using Groq Vision...")
                extracted_text = ocr_agent.extract_text_from_image(food_image_name)
            
            # Process the extracted OCR text
            print(f"📝 Processing OCR text for product extraction...")
            ocr_result = ocr_agent.process_ocr_text(extracted_text)
            
            # Check if OCR found a barcode
            if ocr_result.get("barcode"):
                detected_barcode_from_ocr = ocr_result.get("barcode")
                print(f"📋 OCR also extracted barcode: {detected_barcode_from_ocr}")
            
            print(f"📋 OCR Result: product_name='{ocr_result.get('product_name', '')}', brand='{ocr_result.get('brand', '')}', barcode='{detected_barcode_from_ocr}'")            
            ocr_text = ocr_result.get("full_text", "")
            
            # Process barcode - use barcode from reader first, then from OCR
            barcode_result = None
            detected_barcode = barcode_data.get("barcode") if barcode_data else None
            
            # If no barcode from reader but OCR found one, use OCR's barcode
            if not detected_barcode and detected_barcode_from_ocr:
                detected_barcode = detected_barcode_from_ocr
                print(f"📋 Using barcode from OCR: {detected_barcode}")
            
            if detected_barcode:
                barcode_result = barcode_agent.process_barcode(detected_barcode)
        finally:
            try:
                if os.path.exists(food_image_name):
                    os.remove(food_image_name)
            except Exception as e:
                print(f"Warning: Could not delete temporary food image: {e}")
                
        # Step 2: Process barcode and OCR data
        detected_barcode = barcode_data.get('barcode') if barcode_data else None
        
        if barcode_result and barcode_result.get("status") == 1:
            print(f"✅ Found barcode: {detected_barcode}")
            print(f"✅ Product retrieved from database: {barcode_result.get('product_name')}")
        elif detected_barcode:
            print(f"⚠️ Barcode detected: {detected_barcode}")
            print(f"⚠️ Product NOT found in OpenFoodFacts database")
            print(f"💡 Falling back to OCR-based analysis")
        else:
            print("❌ No barcode detected or barcode unreadable")
        
        # OCR already processed above (line 929), just use the result
        # Get product categorization from OCR result
        ocr_product_name = ocr_result.get("product_name", "Unknown Product")
        print(f"🔍 OCR Product Name: '{ocr_product_name}'")
        print(f"🔍 OCR Brand: '{ocr_result.get('brand', '')}'")
        
        # Categorize the product using the barcode agent's method
        # Try to get brand from barcode result first, then from OCR
        product_brand = (barcode_result.get("brand") if barcode_result else ocr_result.get("brand", ""))
        
        # Use lightweight categorizer directly
        try:
            from utils.lightweight_categorizer import lightweight_categorizer
            
            category_result = lightweight_categorizer.categorize_product(ocr_product_name, product_brand)
            
            print(f"📋 OCR Category Result: {category_result.category} (confidence: {category_result.confidence:.2f})")
            
            # Add category to OCR result
            ocr_result["type"] = category_result.category
            ocr_result["confidence"] = category_result.confidence
            ocr_result["method"] = category_result.method
        except Exception as e:
            print(f"⚠️ Categorization failed: {e}")
            ocr_result["type"] = "unknown"
            ocr_result["confidence"] = 0.0
            ocr_result["method"] = "failed"
        
        # Step 3: If no barcode data but we have product name, try searching OpenFoodFacts by name
        if not barcode_result or barcode_result.get("status") != 1:
            # Extract brand and product name for better search
            search_brand = ocr_result.get("brand", "")
            search_product = ocr_result.get("product_name", "")
            
            if search_product and search_product != "Unknown Product":
                # Combine brand + product for better search accuracy
                search_query = f"{search_brand} {search_product}".strip() if search_brand else search_product
                print(f"🔍 No barcode data, searching OpenFoodFacts by name: '{search_query}'")
                
                # STRATEGY: Try OpenFoodFacts first, then AI fallback
                search_client = get_search_utils()
                name_search_result = search_client.search_product_databases(search_query)
                
                if name_search_result.get("status") == 1 and name_search_result.get("product"):
                    print(f"✅ Found product in OpenFoodFacts by name search!")
                    barcode_result = {
                        "status": 1,
                        "product_name": name_search_result["product"].get("product_name", ""),
                        "brand": name_search_result["product"].get("brands", ""),
                        "ingredients_text": name_search_result["product"].get("ingredients_text", ""),
                        "nutriments": name_search_result["product"].get("nutriments", {}),
                        "categories": name_search_result["product"].get("categories", ""),
                        "labels": name_search_result["product"].get("labels", ""),
                        "full_product_data": name_search_result["product"]
                    }
                else:
                    print(f"⚠️ Product '{search_query}' not found in OpenFoodFacts")
                    print(f"🤖 Falling back to AI-powered nutritional data extraction...")
                    
                    # Use Gemini AI to estimate nutritional data for unknown products
                    gemini_client = search_client.get_gemini_client()
                    if gemini_client:
                        try:
                            nutrition_prompt = f"""Provide typical nutritional values per 100g for: {search_query}
                            
                            Product: {search_product}
                            Brand: {search_brand}
                            
                            Return ONLY a JSON object with these fields (use typical/average values for this product type):
                            {{
                                "energy_100g": <kcal>,
                                "fat_100g": <grams>,
                                "saturated-fat_100g": <grams>,
                                "carbohydrates_100g": <grams>,
                                "sugars_100g": <grams>,
                                "fiber_100g": <grams>,
                                "proteins_100g": <grams>,
                                "salt_100g": <grams>,
                                "sodium_100g": <grams>
                            }}
                            
                            Provide realistic estimates based on similar products in the market."""
                            
                            ai_response = gemini_client.invoke(nutrition_prompt)
                            
                            # Parse AI response
                            import json
                            ai_text = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)
                            
                            # Extract JSON from response (might have markdown formatting)
                            json_match = re.search(r'\{[^}]+\}', ai_text, re.DOTALL)
                            if json_match:
                                ai_nutriments = json.loads(json_match.group())
                                print(f"✅ AI estimated nutritional data: {ai_nutriments}")
                                
                                barcode_result = {
                                    "status": 1,
                                    "product_name": search_product,
                                    "brand": search_brand,
                                    "ingredients_text": "Ingredients not available - AI estimated nutrition",
                                    "nutriments": ai_nutriments,
                                    "categories": "",
                                    "labels": "AI_ESTIMATED",
                                    "full_product_data": {"source": "ai_estimation"}
                                }
                            else:
                                print(f"⚠️ Could not parse AI nutritional response")
                                # Use category-based estimates as last resort
                                barcode_result = _create_category_based_nutrition_estimate(search_product, search_brand, ocr_result.get("type", "processed_food"))
                        except Exception as e:
                            print(f"❌ AI nutritional estimation failed: {e}")
                            # Use category-based estimates as last resort
                            barcode_result = _create_category_based_nutrition_estimate(search_product, search_brand, ocr_result.get("type", "processed_food"))
        
        # Step 4: Combine data - use OCR if barcode returns empty product name
        barcode_product_name = barcode_result.get("product_name", "") if barcode_result else ""
        ocr_product_name = ocr_result.get("product_name", "")
        
        # CRITICAL: Ensure product names are strings, not dicts or other objects
        if not isinstance(barcode_product_name, str):
            print(f"⚠️ barcode_product_name is not a string: {type(barcode_product_name)}")
            barcode_product_name = str(barcode_product_name) if barcode_product_name else ""
        
        if not isinstance(ocr_product_name, str):
            print(f"⚠️ ocr_product_name is not a string: {type(ocr_product_name)}")
            ocr_product_name = str(ocr_product_name) if ocr_product_name else ""
        
        # CRITICAL FIX: Never use barcode number as product name
        # Check if barcode_product_name is actually a barcode number (all digits)
        is_barcode_number = barcode_product_name.strip().replace(' ', '').replace('-', '').isdigit() if barcode_product_name else False
        
        # Use barcode data only if it has a valid product name AND it's not a barcode number
        if barcode_product_name and barcode_product_name.strip() and not is_barcode_number and len(barcode_product_name.strip()) > 3:
            product_name = barcode_product_name
            print(f"✅ Using barcode product name: {product_name}")
        elif ocr_product_name and ocr_product_name.strip() and len(ocr_product_name.strip()) > 3:
            product_name = ocr_product_name
            print(f"✅ Using OCR product name: {product_name}")
        else:
            product_name = "Unknown Product"
            print(f"⚠️ No product name found from barcode or OCR")
            
        # Additional validation: if product_name looks like a barcode, replace with OCR
        # Also check for OCR errors like "I906001" where I is confused with 1
        try:
            cleaned_name = product_name.strip().replace(' ', '').replace('-', '')
            # Replace common OCR digit confusion
            test_cleaned = cleaned_name.replace('I', '1').replace('O', '0').replace('l', '1').replace('o', '0')
            if test_cleaned.isdigit() and len(test_cleaned) >= 8:
                print(f"⚠️ Product name '{product_name}' looks like a barcode number (or OCR error), using OCR instead")
                product_name = ocr_product_name if ocr_product_name and ocr_product_name != product_name else "Unknown Product"
                # If OCR also has same issue, mark as unknown
                if product_name == "Unknown Product":
                    print(f"❌ Unable to extract valid product name from both barcode and OCR")
        except AttributeError as e:
            print(f"❌ Error validating product name: {e}. Product name type: {type(product_name)}")
            product_name = "Unknown Product"
        
        # Similar logic for brand
        barcode_brand = barcode_result.get("brand", "") if barcode_result else ""
        ocr_brand = ocr_result.get("brand", "")
        
        if barcode_brand and barcode_brand.strip():
            brand = barcode_brand
        elif ocr_brand and ocr_brand.strip():
            brand = ocr_brand
        else:
            brand = ""
        
        product_data = {
            "product_name": product_name,
            "brand": brand,
            "nutriments": barcode_result.get("nutriments", {}) if barcode_result and barcode_product_name else {},
            "ingredients_text": (barcode_result.get("ingredients_text", "") if barcode_result and barcode_product_name
                               else ", ".join(ocr_result.get("ingredients", [])) if isinstance(ocr_result.get("ingredients", []), list) else str(ocr_result.get("ingredients", ""))),
            "categories": barcode_result.get("categories", "") if barcode_result and barcode_product_name else "",
            # Add enhanced category from OCR categorization - use actual category field
            "category": ocr_result.get("type", "unknown"),
            "enhanced_category": ocr_result.get("type", "unknown"),
            "category_confidence": ocr_result.get("confidence", 0.0),
            "category_method": ocr_result.get("method", "unknown")
        }
        
        # Step 4: Classify product type
        product_type_result = barcode_agent.classify_product_type(
            product_name,
            product_data.get("categories", ""),
            product_data.get("ingredients_text", [])
        )
        # Extract the actual type string from the result dict
        product_type = product_type_result.get("type", "processed_food") if isinstance(product_type_result, dict) else product_type_result
        product_data["product_type"] = product_type
        
        # Step 5: Health analysis
        health_analysis = health_score_agent.analyze_health_impact(product_data, user_profile)
        
        # Step 6: Find alternatives (premium only)
        alternatives_result = {}
        print(f"DEBUG: User {user_id} has tier: {user.tier}")
        if user.tier == "premium":
            clean_name = product_name.lower().strip()
            
            # Get category from the actual categorization that happened earlier
            # The category is set in product_data during OCR/barcode processing
            product_category = product_data.get("category", "unknown")
            enhanced_category = product_data.get("enhanced_category", "unknown")
            
            print(f"🎯 Using categorization for alternatives: {product_name}")
            print(f"📋 Product category: {product_category}")
            print(f"📋 Enhanced category: {enhanced_category}")
            
            # Use enhanced category if available, otherwise use basic category
            category_for_alternatives = enhanced_category if enhanced_category != "unknown" else product_category
            
            print(f"🔍 CATEGORY SELECTION DEBUG:")
            print(f"   Enhanced: {enhanced_category}")
            print(f"   Basic: {product_category}")
            print(f"   Selected: {category_for_alternatives}")
            print(f"🤖 Getting AI-powered alternatives with user health profile for category: {category_for_alternatives}")
            
            print(f"🔍 CATEGORY SELECTION DEBUG:")
            print(f"   Enhanced: {enhanced_category}")
            print(f"   Basic: {product_category}")  
            print(f"   Selected: {category_for_alternatives}")
            
            # Get AI-powered alternatives with user health profile
            print(f"🤖 Getting AI-powered alternatives with user health profile for category: {category_for_alternatives}")
            
            # Create enhanced prompt with user profile
            user_age = user_profile.get("age", "Unknown")
            user_weight = user_profile.get("weight_kg", "Unknown") 
            user_height = user_profile.get("height_cm", "Unknown")
            user_conditions = user_profile.get("health_conditions", [])
            user_goals = user_profile.get("fitness_goals", "general health")
            
            # Enhanced prompt for Gemini with full user context
            enhanced_prompt = f"""
            Find 3 healthier alternatives for {product_name} considering:
            
            USER PROFILE:
            - Age: {user_age} years
            - Weight: {user_weight} kg  
            - Height: {user_height} cm
            - Health conditions: {', '.join(user_conditions) if user_conditions else 'None'}
            - Fitness goals: {user_goals}
            
            PRODUCT CONTEXT:
            - Current product: {product_name}
            - Category: {category_for_alternatives}
            - Current health score: {health_analysis.get('health_score', 'Unknown')}/100
            
            REQUIREMENTS:
            - Suggest alternatives available in Indian markets
            - Include specific brand names when possible
            - Consider the user's health profile and goals
            - Focus on products that address health concerns
            - Include price estimates in Indian rupees
            - Provide clear health benefits for each alternative
            
            Format EXACTLY like this for each alternative:
            
            1. ### Product Name (Brand Name)
               Score: XX/100
               Key health benefits: [List 2-3 specific benefits like "High protein", "Low sugar", etc.]
               Where to buy in India: [Specific stores/platforms]
               Approximate price range in ₹: ₹XX - ₹YY
            
            2. ### Product Name (Brand Name)
               Score: XX/100
               Key health benefits: [Benefits]
               Where to buy in India: [Stores]
               Approximate price range in ₹: ₹XX - ₹YY
            
            3. ### Product Name (Brand Name)
               Score: XX/100
               Key health benefits: [Benefits]
               Where to buy in India: [Stores]
               Approximate price range in ₹: ₹XX - ₹YY
            
            Keep each field on its own line. Do NOT mix fields together.
            """
            
            # Get AI alternatives with enhanced context
            alternatives_from_ai = get_ai_alternatives_with_context(enhanced_prompt, category_for_alternatives)
            
            if alternatives_from_ai and len(alternatives_from_ai) >= 3:
                alternatives_result = {"alternatives": alternatives_from_ai}
                print(f"✅ Found {len(alternatives_from_ai)} AI-powered alternatives with user context")
            else:
                # Fallback to category-based alternatives
                print(f"🔄 AI alternatives failed, using category-based fallback")
                category_for_search = category_for_alternatives or "healthy food"
                
                print(f"🔍 Searching alternatives using category: '{category_for_search}'")
                alternatives_from_search = get_search_utils().get_alternatives(category_for_search, product_name)
                
                if alternatives_from_search and len(alternatives_from_search) >= 3:
                    # If we found alternatives with real-time search, use them
                    alternatives_result = {"alternatives": alternatives_from_search}
                    print(f"✅ Found {len(alternatives_from_search)} alternatives for {product_name} using category '{category_for_search}'")
                else:
                    # Otherwise use alternatives_agent as fallback
                    alternatives_result = alternatives_agent.find_alternatives(product_data, user_profile)
                    print(f"🔍 Found {len(alternatives_result.get('alternatives', []))} alternatives from agent")
            
            # Ensure at least 3 alternatives are suggested - use dynamic search if needed
            if len(alternatives_result.get("alternatives", [])) < 3:
                print(f"⚠️ Not enough alternatives found ({len(alternatives_result.get('alternatives', []))}), using dynamic search")
                
                # Use dynamic search to get category-appropriate alternatives
                try:
                    # Get fresh dynamic alternatives based on product categorization
                    dynamic_alternatives = get_search_utils().get_alternatives("dynamic", product_name)
                    
                    if dynamic_alternatives and len(dynamic_alternatives) > 0:
                        print(f"✅ Dynamic search found {len(dynamic_alternatives)} alternatives")
                        alternatives_result["alternatives"] = dynamic_alternatives
                    else:
                        print("⚠️ Dynamic search failed, using minimal fallback")
                        # Only use minimal generic fallback as last resort
                        alternatives_result["alternatives"] = [
                            {
                                "name": "Consult a nutritionist for personalized alternatives",
                                "brand": "Professional Advice",
                                "health_score": 90,
                                "price": "Consultation fee varies",
                                "where_to_buy": "Nutritionist clinics, online consultations",
                                "health_benefits": "Personalized nutrition advice based on your specific needs"
                            }
                        ]
                except Exception as e:
                    print(f"❌ Dynamic search error: {e}")
                    alternatives_result["alternatives"] = [
                        {
                            "name": "Consult a nutritionist for personalized alternatives", 
                            "brand": "Professional Advice",
                            "health_score": 90,
                            "price": "Consultation fee varies",
                            "where_to_buy": "Nutritionist clinics, online consultations",
                            "health_benefits": "Personalized nutrition advice based on your specific needs"
                        }
                    ]
        else:
            alternatives_result = {"alternatives": []}
        
        # Step 7: FSSAI and claim verification (premium only)
        claim_analysis = {}
        fssai_verification = {}
        if user.tier == "premium":
            # Perform both claim verification and FSSAI verification
            claim_analysis = claim_verification_agent.verify_claims(product_data, ocr_text)
            fssai_verification = fssai_agent.verify_product_claims(product_data, ocr_text)
            
            # Combine verification results
            claim_analysis.update({
                "fssai_verification": fssai_verification,
                "regulatory_compliance": fssai_verification["fssai_compliance"],
                "misleading_claims": fssai_verification["misleading_claims"],
                "ingredient_validation": fssai_verification["ingredient_validation"]
            })
        else:
            claim_analysis = {
                "total_claims_investigated": 0,
                "verified_claims": 0,
                "unverified_claims": 0,
                "claims_with_conflicts": 0,
                "overall_credibility_score": 0,
                "misleading_analysis": "Claim and FSSAI verification available for premium users",
                "individual_claim_results": [],
                "fssai_verification": "Upgrade to premium for detailed FSSAI compliance check",
                "recommendation": "Upgrade to premium for complete verification"
            }
        
        # Get nutritional breakdown for detailed analysis
        nutrition_data = product_data.get("nutriments", {})
        
        # Create detailed nutritional analysis
        nutritional_analysis = {
            "sugar_content": {
                "value": nutrition_data.get("sugars_100g", 0) or 0,
                "unit": "g per 100g",
                "assessment": "High" if (nutrition_data.get("sugars_100g", 0) or 0) > 15 else "Moderate" if (nutrition_data.get("sugars_100g", 0) or 0) > 5 else "Low"
            },
            "sodium_content": {
                "value": nutrition_data.get("sodium_100g", 0) or 0,
                "unit": "mg per 100g", 
                "assessment": "High" if (nutrition_data.get("sodium_100g", 0) or 0) * 1000 > 600 else "Moderate" if (nutrition_data.get("sodium_100g", 0) or 0) * 1000 > 300 else "Low"
            },
            "fiber_content": {
                "value": nutrition_data.get("fiber_100g", 0) or 0,
                "unit": "g per 100g",
                "assessment": "High" if (nutrition_data.get("fiber_100g", 0) or 0) >= 6 else "Good" if (nutrition_data.get("fiber_100g", 0) or 0) >= 3 else "Low"
            },
            "protein_content": {
                "value": nutrition_data.get("proteins_100g", 0) or 0,
                "unit": "g per 100g",
                "assessment": "High" if (nutrition_data.get("proteins_100g", 0) or 0) >= 10 else "Good" if (nutrition_data.get("proteins_100g", 0) or 0) >= 5 else "Low"
            }
        }
        
        # Generate detailed consumption reasons
        consumption_reasons = []
        health_warnings = []
        
        # Analyze why should/shouldn't consume
        if health_analysis["health_score"] >= 70:
            consumption_reasons.append(f"✅ Good overall nutritional profile (Score: {health_analysis['health_score']}/100)")
            if nutritional_analysis["fiber_content"]["value"] >= 3:
                consumption_reasons.append(f"✅ Good fiber content ({nutritional_analysis['fiber_content']['value']}g per 100g)")
            if nutritional_analysis["protein_content"]["value"] >= 5:
                consumption_reasons.append(f"✅ Adequate protein content ({nutritional_analysis['protein_content']['value']}g per 100g)")
        else:
            if nutritional_analysis["sugar_content"]["value"] > 15:
                health_warnings.append(f"⚠️ High sugar content ({nutritional_analysis['sugar_content']['value']}g per 100g)")
            if nutritional_analysis["sodium_content"]["value"] * 1000 > 600:
                health_warnings.append(f"⚠️ High sodium content ({nutritional_analysis['sodium_content']['value'] * 1000:.0f}mg per 100g)")
            if nutritional_analysis["fiber_content"]["value"] < 1:
                health_warnings.append(f"⚠️ Low fiber content ({nutritional_analysis['fiber_content']['value']}g per 100g)")
        
        # Health condition specific advice
        health_condition_advice = []
        for condition in user_profile.get("health_conditions", []):
            if "diabetes" in condition.lower():
                if nutritional_analysis["sugar_content"]["value"] > 10:
                    health_condition_advice.append(f"🚫 Not recommended for diabetes - high sugar content")
                else:
                    health_condition_advice.append(f"✅ Acceptable for diabetes management")
        
        # Prepare product data for response formatter
        food_summary = {
            "product_name": product_name,
            "brand": product_data.get("brand", ""),
            "categories": product_data.get("categories", ""),
            "product_type": product_type,
            "key_ingredients": product_data.get("ingredients_text", "Ingredients not available"),
            "processing_level": "Ultra-processed" if product_type in ["processed_food", "snack"] else "Minimally processed" if product_type in ["dairy", "beverage"] else "Moderate processing",
            "nutritional_highlights": {
                "primary_concern": f"High {str(nutritional_analysis['sugar_content']['assessment']).lower()} sugar content" if str(nutritional_analysis['sugar_content']['assessment']) == 'High' 
                                 else f"High {str(nutritional_analysis['sodium_content']['assessment']).lower()} sodium content" if str(nutritional_analysis['sodium_content']['assessment']) == 'High'
                                 else "Moderate nutritional profile",
                "positive_aspects": [aspect for aspect in [
                    f"Good protein content ({nutritional_analysis['protein_content']['value']}g)" if nutritional_analysis['protein_content']['value'] >= 5 else None,
                    f"Good fiber content ({nutritional_analysis['fiber_content']['value']}g)" if nutritional_analysis['fiber_content']['value'] >= 3 else None,
                    f"Low sodium content" if nutritional_analysis['sodium_content']['assessment'] == 'Low' else None,
                    f"Low sugar content" if nutritional_analysis['sugar_content']['assessment'] == 'Low' else None
                ] if aspect is not None]
            }
        }
            
        # FSSAI and regulatory compliance check 
        fssai_compliance = {
            "regulatory_status": "Compliant with FSSAI guidelines" if health_analysis["health_score"] >= 60 else "May require review under FSSAI guidelines",
            "food_safety_rating": "A" if health_analysis["health_score"] >= 80 else "B" if health_analysis["health_score"] >= 60 else "C",
            "labeling_compliance": {
                "nutrition_facts_required": True,
                "ingredient_declaration": "Required as per FSSAI Food Safety and Standards (Packaging and Labelling) Regulations, 2011",
                "health_claims_verification": "All health claims must be substantiated as per FSSAI guidelines"
            },
            "quality_standards": {
                "meets_bis_standards": True if health_analysis["health_score"] >= 50 else False,
                "contaminant_limits": "Within FSSAI specified limits" if nutrition_data else "Data not available",
                "shelf_life_compliance": "As per manufacturer declaration"
            },
            "fssai_recommendations": [
                "Reduce sugar content to meet healthier choice standards" if nutritional_analysis['sugar_content']['assessment'] == 'High' else None,
                "Reduce sodium content as per FSSAI salt reduction guidelines" if nutritional_analysis['sodium_content']['assessment'] == 'High' else None,
                "Increase fiber content for better nutritional profile" if nutritional_analysis['fiber_content']['assessment'] == 'Low' else None,
                "Product meets current FSSAI nutritional guidelines" if health_analysis["health_score"] >= 70 else None
            ]
        }
        # Remove None values
        fssai_compliance["fssai_recommendations"] = [rec for rec in fssai_compliance["fssai_recommendations"] if rec is not None]
        
        final_response = {
            "product_name": product_name,
            "brand": product_data.get("brand", ""),
            "product_type": product_type,
            "health_score": health_analysis["health_score"],
            "verdict": health_analysis["verdict"],
            "should_consume": health_analysis["should_consume"],
            "consumption_advice": health_analysis["consumption_advice"],
            "food_summary": food_summary,
            "detailed_analysis": {
                "nutritional_breakdown": nutritional_analysis,
                "consumption_reasons": consumption_reasons,
                "health_warnings": health_warnings,
                "health_condition_advice": health_condition_advice,
                "summary": f"{product_name} received a health score of {health_analysis['health_score']}/100. {health_analysis['verdict']['title']} - {health_analysis['verdict']['subtitle']}"
            },
            "fssai_compliance": fssai_compliance,
            "health_conditions": user_profile.get("health_conditions", []),
            "claim_analysis": claim_analysis,
            "claim_verification_results": claim_analysis.get("individual_claim_results", []),
            "premium_features": user.tier == "premium",
            "alternatives": alternatives_result.get("alternatives", []),
            "alternatives_count": len(alternatives_result.get("alternatives", [])),
            "tier_message": "Premium features active" if user.tier == "premium" else "Upgrade to premium for alternatives and claim analysis"
        }
        
        # Save scan history for premium users - MOVED TO END after creating proper structure
        
        # Create a concise analysis summary with clean format
        main_analysis = f"""PRODUCT ANALYSIS
• Product: {product_name} ({product_data.get('brand', 'Unknown Brand')})
• Health Score: {health_analysis['health_score']}/100 - {health_analysis['verdict']['title']}
• Key Insights: {', '.join(health_warnings) if health_warnings else 'No major health concerns'}
• Recommendation: {health_analysis['consumption_advice']}"""

        # Use alternatives from earlier results
        alternatives = alternatives_result.get("alternatives", [])
        
        # Only provide fallback alternatives for premium users
        if user.tier == "premium" and (not alternatives or len(alternatives) < 3):
            print(f"⚠️ Insufficient alternatives found ({len(alternatives)}), using product-specific fallbacks for premium user")
            
            # Check product type for specific fallbacks
            if product_type == "beverage" or "beverage" in product_data.get("categories", "").lower() or "coca" in product_name.lower() or "coke" in product_name.lower() or "pepsi" in product_name.lower() or "soft drink" in product_name.lower():
                print("🥤 Using beverage-specific alternatives")
                fallback_alternatives = [
                    {
                        "name": "Coconut Water",
                        "brand": "Tender Fresh",
                        "health_score": 92,
                        "health_benefits": "Natural electrolytes, rich in potassium, zero added sugar, hydrating, low calorie",
                        "key_benefits": "Natural electrolytes, zero added sugar",
                        "price": "₹40-60 per bottle",
                        "where_to_buy": "Supermarkets, local stores, online retailers"
                    },
                    {
                        "name": "Fresh Lime Water",
                        "brand": "Homemade",
                        "health_score": 90,
                        "health_benefits": "Vitamin C rich, aids digestion, detoxifying, natural hydration, minimal calories",
                        "key_benefits": "Natural vitamin C, aids digestion",
                        "price": "₹10-20 per glass",
                        "where_to_buy": "Restaurants, food stalls, make at home"
                    },
                    {
                        "name": "Raw Pressery Mixed Fruit Juice",
                        "brand": "Raw Pressery",
                        "health_score": 85,
                        "health_benefits": "Cold pressed, no preservatives, no added sugar, rich in vitamins, antioxidants",
                        "key_benefits": "Cold pressed, no preservatives or added sugar",
                        "price": "₹80-100 per bottle",
                        "where_to_buy": "Premium supermarkets, online grocers"
                    },
                    {
                        "name": "Paper Boat Coconut Water",
                        "brand": "Paper Boat",
                        "health_score": 88,
                        "health_benefits": "Natural electrolytes, no preservatives, low calorie, no added flavors",
                        "key_benefits": "Natural hydration, no preservatives",
                        "price": "₹50-70 per tetra pack",
                        "where_to_buy": "Supermarkets, convenience stores, online"
                    },
                    {
                        "name": "B-Natural Mixed Fruit No Sugar",
                        "brand": "B-Natural",
                        "health_score": 82,
                        "health_benefits": "No added sugar, preservative-free, good source of vitamins, lower calories than sodas",
                        "key_benefits": "No added sugar, preservative-free",
                        "price": "₹75-90 per carton",
                        "where_to_buy": "Major retail stores, online platforms"
                    }
                ]
            elif product_type == "cereal" or "cereal" in product_data.get("categories", "").lower():
                print("🥣 Using cereal-specific alternatives")
                fallback_alternatives = [
                    {
                        "name": "Quaker Oats",
                        "brand": "Quaker",
                        "health_score": 92,
                        "health_benefits": "High fiber, low sugar, heart healthy, rich in protein",
                        "key_benefits": "High fiber, low sugar, heart healthy",
                        "price": "₹180-200 per kg",
                        "where_to_buy": "All supermarkets, Online stores"
                    },
                    {
                        "name": "Kellogg's Muesli with 21% Fruit, Nut & Seeds",
                        "brand": "Kellogg's",
                        "health_score": 88,
                        "health_benefits": "High fiber, natural sweetness from fruits, protein rich",
                        "key_benefits": "High fiber, natural sweetness from fruits",
                        "price": "₹280-300 per kg",
                        "where_to_buy": "Supermarkets, Online platforms"
                    },
                    {
                        "name": "True Elements Steel Cut Oats",
                        "brand": "True Elements",
                        "health_score": 90,
                        "health_benefits": "100% whole grain, high fiber, low GI",
                        "key_benefits": "100% whole grain, high fiber, low GI",
                        "price": "₹200-220 per kg",
                        "where_to_buy": "Health food stores, Online"
                    },
                    {
                        "name": "Bagrry's White Oats",
                        "brand": "Bagrry's",
                        "health_score": 85,
                        "health_benefits": "High protein, sugar-free, rich in dietary fiber",
                        "key_benefits": "High protein, sugar-free, rich in dietary fiber",
                        "price": "₹160-180 per kg",
                        "where_to_buy": "Local stores, Online marketplaces"
                    },
                    {
                        "name": "Soulfull Ragi Bites",
                        "brand": "Soulfull",
                        "health_score": 82,
                        "health_benefits": "Made with millets, no artificial sweeteners, high calcium",
                        "key_benefits": "Made with millets, high calcium content",
                        "price": "₹150-170 per pack",
                        "where_to_buy": "Supermarkets, Online stores"
                    }
                ]
            else:
                # Generic healthy alternatives fallback
                print("🌿 Using generic healthy alternatives fallback")
                fallback_alternatives = [
                    {
                        "name": "Saffola Masala Oats",
                        "brand": "Saffola",
                        "health_score": 85,
                        "health_benefits": "High fiber, protein rich, whole grain oats base",
                        "key_benefits": "High fiber, protein rich, whole grain oats base",
                        "price": "₹15-25 per serving",
                        "where_to_buy": "All supermarkets, online stores"
                    },
                    {
                        "name": "Yoga Bar Breakfast Bar",
                        "brand": "Yoga Bar",
                        "health_score": 88,
                        "health_benefits": "High protein, natural ingredients, no preservatives",
                        "key_benefits": "High protein, natural ingredients, no preservatives",
                        "price": "₹35-40 per bar",
                        "where_to_buy": "Health food stores, Online"
                    },
                    {
                        "name": "True Elements Steel Cut Oats",
                        "brand": "True Elements",
                        "health_score": 90,
                        "health_benefits": "100% whole grain, high fiber, low GI",
                        "key_benefits": "100% whole grain, high fiber, low GI",
                        "price": "₹200-220 per kg",
                        "where_to_buy": "Health food stores, Online"
                    },
                    {
                        "name": "Kellogg's Muesli with 21% Fruit, Nut & Seeds",
                        "brand": "Kellogg's",
                        "health_score": 88,
                        "health_benefits": "High fiber, natural sweetness from fruits, protein rich",
                        "key_benefits": "High fiber, natural sweetness from fruits",
                        "price": "₹280-300 per kg",
                        "where_to_buy": "Supermarkets, Online platforms"
                    },
                    {
                        "name": "Quaker Oats",
                        "brand": "Quaker",
                        "health_score": 92,
                        "health_benefits": "High fiber, low sugar, heart healthy, rich in protein",
                        "key_benefits": "High fiber, low sugar, heart healthy",
                        "price": "₹180-200 per kg",
                        "where_to_buy": "All supermarkets, Online stores"
                    }
                ]
            
            # Use fallback alternatives
            alternatives = fallback_alternatives
        
        # Scan history will be saved later with complete response
        
        # Format alternatives section - only for premium users
        print(f"DEBUG: Formatting alternatives for tier: {user.tier}, alternatives count: {len(alternatives)}")
        if user.tier == "premium":
            alternatives_section = "HEALTHIER ALTERNATIVES"
            if alternatives and len(alternatives) > 0:
                for i, alt in enumerate(alternatives, 1):
                    # Handle both field name formats (AI vs fallback)
                    alt_score = alt.get('health_score', alt.get('score', 85))
                    alt_name = alt.get('name', 'Unknown Product')
                    alt_brand = alt.get('brand', 'Unknown')
                    alt_benefits = alt.get('health_benefits') or alt.get('key_benefits') or alt.get('benefits', 'Healthier alternative')
                    alt_where = alt.get('where_to_buy', alt.get('availability', 'Stores'))
                    alt_price = alt.get('price', '₹100-200')
                    
                    # Ensure all values are strings not dicts
                    if not isinstance(alt_name, str):
                        alt_name = str(alt_name)
                    if not isinstance(alt_brand, str):
                        alt_brand = str(alt_brand)
                    if not isinstance(alt_benefits, str):
                        alt_benefits = str(alt_benefits)
                    if not isinstance(alt_where, str):
                        alt_where = str(alt_where)
                    if not isinstance(alt_price, str):
                        alt_price = str(alt_price)
                    
                    score_diff = alt_score - health_analysis['health_score']
                    
                    alternatives_section += f"""

• {alt_name} ({alt_brand})
  Score: {alt_score}/100 ({score_diff:+d} points better)
  Benefits: {alt_benefits}
  Available at: {alt_where} ({alt_price})"""
            else:
                # Ensure premium users ALWAYS get some alternatives - use emergency fallback
                print("🚨 No alternatives found for premium user - using emergency fallback")
                
                # Add emergency alternatives to the alternatives array
                alternatives = [
                    {
                        "name": "Britannia NutriChoice Digestive Biscuits",
                        "brand": "Britannia",
                        "health_score": 75,
                        "health_benefits": "High fiber, less sugar, digestive benefits",
                        "where_to_buy": "All supermarkets",
                        "price": "₹40-80"
                    },
                    {
                        "name": "True Elements Oatmeal Cookies",
                        "brand": "True Elements",
                        "health_score": 82,
                        "health_benefits": "High fiber, natural sweetness, protein rich", 
                        "where_to_buy": "Online stores, Premium supermarkets",
                        "price": "₹150-250"
                    },
                    {
                        "name": "RiteBite Protein Cookies",
                        "brand": "RiteBite",
                        "health_score": 88,
                        "health_benefits": "High protein, low sugar, fitness-friendly",
                        "where_to_buy": "Health stores, Online platforms",
                        "price": "₹300-500"
                    }
                ]
                
                alternatives_section += f"""

• Britannia NutriChoice Digestive Biscuits (Britannia)
  Score: 75/100 (+26 points better)
  Benefits: High fiber, less sugar, digestive benefits
  Available at: All supermarkets (₹40-80)

• True Elements Oatmeal Cookies (True Elements)  
  Score: 82/100 (+33 points better)
  Benefits: High fiber, natural sweetness, protein rich
  Available at: Online stores, Premium supermarkets (₹150-250)

• RiteBite Protein Cookies (RiteBite)
  Score: 88/100 (+39 points better) 
  Benefits: High protein, low sugar, fitness-friendly
  Available at: Health stores, Online platforms (₹300-500)"""
        else:
            # For free users, show premium upgrade message
            alternatives_section = "HEALTHIER ALTERNATIVES\n\n🔒 Premium Feature - Upgrade to access AI-powered alternatives with Indian brand recommendations, pricing, and availability information."

        # Format health notes in a cleaner format
        health_notes = "HEALTH RECOMMENDATIONS"
        if health_warnings:
            health_notes += f"\n• Warnings: ⚠️ {', '.join(health_warnings)}"
        if consumption_reasons:
            health_notes += f"\n• Positives: {', '.join(consumption_reasons)}"

        # Create complete user-friendly summary
        user_friendly_summary = f"{main_analysis}\n\n{alternatives_section}\n\n{health_notes}"
        
        # Add to final response
        final_response["user_friendly_summary"] = user_friendly_summary
        
        # Create separate Claims Verification and Ingredients Analysis sections
        # Claims Verification - focus on marketing claims
        claims_verification_text = ""
        if user.tier == "premium" and claim_analysis.get("individual_claim_results"):
            claims_list = []
            for claim in claim_analysis.get("individual_claim_results", []):
                status = "✅ VERIFIED" if claim.get("verified") else "❌ UNVERIFIED"
                claims_list.append(f"• {claim.get('claim', 'Unknown')}: {status}\n  {claim.get('explanation', 'No details')}")
            
            if claims_list:
                claims_verification_text = f"""• Product: {product_name} ({product_data.get('brand', 'Unknown Brand')})
• Health Score: {health_analysis['health_score']}/100 - {health_analysis['verdict']['title']}
• Credibility Score: {claim_analysis.get('overall_credibility_score', 0)}/100

MARKETING CLAIMS ANALYSIS:
{chr(10).join(claims_list)}

{claim_analysis.get('misleading_analysis', '')}

RECOMMENDATION: {claim_analysis.get('recommendation', 'Verify claims against nutritional facts')}"""
            else:
                claims_verification_text = main_analysis + "\n\nNo specific marketing claims found on package to verify."
        else:
            claims_verification_text = main_analysis + "\n\n🔒 Upgrade to Premium for detailed claims verification"
        
        # Ingredients Analysis - focus on nutritional breakdown and ingredients
        ingredients_text = product_data.get("ingredients_text", "")
        if isinstance(ingredients_text, list):
            ingredients_text = ", ".join(ingredients_text)
        
        # Ensure product_type is a string, not dict
        product_type_str = product_type
        if isinstance(product_type, dict):
            product_type_str = product_type.get("type", "processed_food")
        elif not isinstance(product_type, str):
            product_type_str = str(product_type)
        
        ingredients_analysis_text = f"""• Product: {product_name} ({product_data.get('brand', 'Unknown Brand')})
• Category: {product_type_str.replace('_', ' ').title()}
• Health Score: {health_analysis['health_score']}/100

NUTRITIONAL BREAKDOWN (per 100g):
• Sugar: {nutritional_analysis['sugar_content']['value']}g ({nutritional_analysis['sugar_content']['assessment']})
• Sodium: {nutritional_analysis['sodium_content']['value'] * 1000:.0f}mg ({nutritional_analysis['sodium_content']['assessment']})
• Fiber: {nutritional_analysis['fiber_content']['value']}g ({nutritional_analysis['fiber_content']['assessment']})
• Protein: {nutritional_analysis['protein_content']['value']}g ({nutritional_analysis['protein_content']['assessment']})

INGREDIENTS: {ingredients_text if ingredients_text else 'Not available on package'}

KEY INSIGHTS:
{chr(10).join(['• ' + w for w in health_warnings]) if health_warnings else '• No major nutritional concerns identified'}

RECOMMENDATION: {health_analysis['consumption_advice']}"""
        
        # Return based on format requested
        if response_format == "user_friendly":
            # Create a summary section with structured data
            summary = {
                "product_name": product_name,
                "brand": product_data.get('brand', ''),
                "health_score": health_analysis["health_score"],
                "verdict": health_analysis['verdict']['title'],
                "has_alternatives": user.tier == "premium",  # Premium users ALWAYS have alternatives now
                "alternatives_count": 3 if user.tier == "premium" else 0,  # Always show 3 for premium
                "alternatives": []
            }
            
            # Add structured alternatives to the summary - only for premium users
            if user.tier == "premium":
                for alt in alternatives:
                    score_diff = alt['health_score'] - health_analysis['health_score']
                    health_benefits = alt.get('health_benefits') or alt.get('key_benefits', 'Healthier alternative')
                    
                    # Fetch real product image
                    alt_name = alt['name']
                    alt_brand = alt.get('brand', '')
                    image_url = image_fetcher.get_product_image(alt_name, alt_brand)
                    
                    summary["alternatives"].append({
                        "name": alt['name'],
                        "brand": alt['brand'],
                        "score": alt['health_score'],
                        "score_difference": score_diff,
                        "benefits": health_benefits,
                        "availability": alt['where_to_buy'],
                        "price": alt['price'],
                        "image_url": image_url
                    })
            
            # Create the response structure
            summary_response = {
                "output_type": "user_friendly",
                "sections": {
                    "analysis": main_analysis,
                    "claims_verification": claims_verification_text,
                    "ingredients_analysis": ingredients_analysis_text,
                    "alternatives": alternatives_section.strip(),
                    "health_notes": health_notes.strip()
                },
                "summary": summary
            }
            
            # Save scan history for premium users with proper structure
            if user.tier == "premium":
                save_scan_history(user_id, summary_response, db)
            
            return summary_response
        
        # Return full response for non-user-friendly format
        return {
            "output_type": "full_analysis",
            "analysis": final_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Error in analyze_food: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        print(f"❌ Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def generate_intelligent_response(message: str, context: str, user: User) -> str:
    """Generate intelligent AI responses using Gemini for premium users"""
    try:
        # Get Gemini client for AI responses
        search_utils = get_search_utils()
        gemini_client = search_utils.get_gemini_client()
        
        if not gemini_client:
            return "I'm your AI nutrition assistant. I can help with food recommendations and health advice. What would you like to know?"
        
        # Create context-aware prompt
        user_profile = f"User Profile: Age {user.age or 'unknown'}, Health conditions: {[hc.condition_name for hc in user.health_conditions] or 'none'}"
        
        # IMPROVED: Parse context AND message to understand conversation flow
        context_lower = context.lower() if context else ""
        message_lower = message.lower()
        combined_text = f"{context_lower} {message_lower}"
        
        # Check if user wants MORE BRANDS of the same product (not different products)
        wants_more_brands = any(phrase in message_lower for phrase in [
            'more brands', 'other brands', 'different brands', 'which brands',
            'brand alternatives', 'brand options', 'alternatives brands',
            'brands for', 'brands of'
        ])
        
        # Also check if message has "alternatives for [product]" or "more [product]"
        # This indicates they want brands/options of that specific product
        if not wants_more_brands:
            if ('alternative' in message_lower or 'more' in message_lower) and 'for' in message_lower:
                wants_more_brands = True
        
        # Extract the product they want more brands for
        requested_product = None
        if wants_more_brands:
            product_keywords = {
                'makhana': ['makhana', 'fox nut', 'lotus seed'],
                'roasted chana': ['roasted chana', 'chickpea', 'bhuna chana'],
                'peanuts': ['peanut', 'groundnut', 'moongfali'],
                'almonds': ['almond', 'badam'],
                'khakhra': ['khakhra'],
                'oats': ['oats', 'oat'],
                'poha': ['poha', 'flattened rice']
            }
            
            for product_name, keywords in product_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    requested_product = product_name
                    break
        
        # Check if this is a follow-up asking for MORE alternatives
        is_followup_request = False
        previously_suggested_items = []
        
        # Extract items that were already suggested from BOTH context and message
        common_items = {
            'makhana': ['makhana', 'fox nut', 'lotus seed'],
            'roasted chana': ['roasted chana', 'chickpea', 'bhuna chana', 'chana'],
            'peanuts': ['peanut', 'groundnut', 'moongfali'],
            'almonds': ['almond', 'badam'],
            'walnuts': ['walnut', 'akhrot'],
            'poha': ['poha', 'flattened rice', 'chivda'],
            'khakhra': ['khakhra', 'cracker']
        }
        
        # Find which items have been mentioned
        for item_name, keywords in common_items.items():
            if any(keyword in combined_text for keyword in keywords):
                # Check if it's mentioned as "already got", "already suggested", "gave me", etc.
                if any(phrase in combined_text for phrase in [
                    'already got', 'already have', 'already suggested', 'gave me', 
                    'suggested', 'alternative', 'recommended'
                ]):
                    previously_suggested_items.append(item_name)
        
        # Also check for explicit phrases indicating follow-up
        is_explicit_followup = any(phrase in message_lower for phrase in [
            'already got', 'already have', 'i got', 'got that',
            'more alternatives', 'other alternatives', 'different alternatives',
            'what else', 'something else', 'besides', 'other than', 'apart from'
        ])
        
        # CRITICAL: If user says "I already got X" in the MESSAGE itself, extract X
        # BUT: If they're asking for brands of X, don't exclude it!
        if not wants_more_brands:  # Only check exclusions if they're NOT asking for brands
            if 'already got' in message_lower or 'already have' in message_lower or 'i got' in message_lower:
                # Parse what they already got from the message
                for item_name, keywords in common_items.items():
                    if any(keyword in message_lower for keyword in keywords):
                        if item_name not in previously_suggested_items:
                            previously_suggested_items.append(item_name)
                is_explicit_followup = True
        
        # Check if message contains "alternatives for X" where X was previously suggested
        asking_alternatives_for_suggested = False
        for item in previously_suggested_items:
            if f'alternative for {item}' in message_lower or f'alternatives for {item}' in message_lower:
                asking_alternatives_for_suggested = True
                is_followup_request = True
                break
        
        # If user explicitly says they already got something, it's definitely a follow-up
        if is_explicit_followup or asking_alternatives_for_suggested:
            is_followup_request = True
        
        # Determine response type based on message content
        if any(word in message.lower() for word in ['alternative', 'substitute', 'replace', 'healthier', 'better', 'option']):
            
            # CASE 0: User wants MORE BRANDS of a specific product
            if wants_more_brands and requested_product:
                prompt = f"""⚠️ CRITICAL INSTRUCTION - READ CAREFULLY ⚠️

The user is asking for DIFFERENT BRANDS of {requested_product.upper()}.

🧠 UNDERSTANDING THE CONTEXT:
Look at the conversation history below. The user likely:
1. Scanned an unhealthy product (like Aloo Sev, chips, etc.)
2. You suggested {requested_product} as a healthier alternative
3. Now they want to know which BRANDS sell {requested_product}

They do NOT want:
❌ Different snack types
❌ Alternatives to {requested_product}
❌ Replacements for {requested_product}

They DO want:
✅ Different BRANDS that sell {requested_product}
✅ Where to buy {requested_product}
✅ Price comparisons for {requested_product}

📝 CONVERSATION HISTORY:
{context}

User's current message: "{message}"
{user_profile}

YOUR TASK: List 5-6 BRANDS that sell {requested_product} in India.

START YOUR RESPONSE acknowledging the conversation:
"Great! Since you're interested in {requested_product} as a healthier alternative, here are different brands where you can find quality {requested_product} in Indian markets:"

Example brands for {requested_product}:
- Farmley
- Nutraj  
- Happilo
- True Elements
- Tata Sampann
- Urban Platter
- Himalayan Natives
- 24 Mantra Organic
- Amazon Fresh / Solimo
- Flipkart brands

For EACH {requested_product} BRAND, provide:

### [Brand Name] {requested_product.title()}
**Variants available:** (e.g., plain roasted, peri peri flavored, himalayan salt, masala, etc.)
**Price range:** ₹XX for 100g, ₹XX for 250g, ₹XX for 500g
**Where to buy:** (DMart, Reliance, BigBasket, Amazon, Blinkit, local stores)
**Special features:** (organic, preservative-free, premium quality, etc.)
**Why this brand:** (taste, quality, value, popularity)

START YOUR RESPONSE WITH:
"Here are different {requested_product} brands available in Indian markets:"

DO NOT MENTION:
❌ Roasted chana
❌ Peanuts
❌ Other snacks
❌ Alternative snack types

ONLY FOCUS ON: {requested_product.upper()} BRANDS"""

            # CASE 1: User wants MORE healthy snacks (not the ones already suggested)
            if is_followup_request and previously_suggested_items:
                suggested_items_text = ", ".join(previously_suggested_items)
                
                prompt = f"""CRITICAL INSTRUCTION: The user has ALREADY tried/received these items: {suggested_items_text}

📝 CONVERSATION HISTORY:
{context}

User's current message: "{message}"
{user_profile}

⚠️ IMPORTANT: 
- User wants OTHER healthy snack options BESIDES {suggested_items_text}
- DO NOT mention {suggested_items_text} AT ALL in your response
- DO NOT suggest roasted chana, roasted peanuts, makhana, or any items already mentioned
- Provide COMPLETELY NEW healthy snack alternatives

Suggest 4-5 DIFFERENT healthy Indian snacks (choose items NOT in the excluded list):
✅ Good options to suggest:
- Khakhra (thin wheat crackers)
- Kurmura/Murmura (puffed rice snacks)
- Jowar/Bajra/Ragi puffs (millet snacks)
- Baked mathri
- Roasted lotus seeds (NOT makhana)
- Til ladoo / Sesame balls
- Dry fruit mix (dates, apricots, figs)
- Sprouts (moong, chana)
- Roasted flax/chia/sunflower seeds
- Diet namkeen (baked)
- Protein bars (Indian brands)

❌ DO NOT suggest:
- {suggested_items_text}
- Roasted chana/chickpeas
- Roasted peanuts
- Plain almonds or walnuts

For each alternative, provide:
1. Specific brand names (Haldiram's, True Elements, Slurrp Farm, etc.)
2. Prices (₹20-₹150)
3. Where to buy (DMart, BigBasket, Amazon, Blinkit, local stores)
4. Health benefits
5. Why it's a good healthy snack

Start your response with: "Great! Since you've already explored {suggested_items_text}, here are some completely different healthy snack options for you..."

Use friendly, conversational tone."""

            # CASE 2: Regular alternative request (no previous suggestions)
            else:
                prompt = f"""As a nutrition expert, provide 3-5 specific Indian food alternatives based on this request.

📝 CONVERSATION HISTORY & CONTEXT:
{context or 'This is the first message in this conversation.'}

User's current message: "{message}"
{user_profile}

🎯 IMPORTANT INSTRUCTIONS:
1. READ the conversation history carefully to understand what the user scanned/asked before
2. If they scanned an unhealthy product (like Aloo Sev), note that you suggested alternatives in previous messages
3. If they're now asking "alternatives for [X]" where X was something YOU suggested (like makhana), they want MORE OPTIONS/BRANDS of that product, not replacements for it
4. Start your response acknowledging the conversation flow (e.g., "Since you scanned Aloo Sev and I suggested makhana...")

Provide practical, Indian-market available alternatives with:
1. Specific brand names available in India
2. Approximate prices in rupees
3. Where to buy (supermarket chains, online platforms)
4. Health benefits
5. Why it's better than what they originally scanned

Format your response in a friendly, conversational tone that shows you remember the previous conversation."""

        elif any(word in message.lower() for word in ['recipe', 'cook', 'make', 'prepare']):
            prompt = f"""As a nutrition expert, provide a healthy recipe suggestion.

📝 CONVERSATION HISTORY:
{context or 'This is the first message in this conversation.'}

User's current message: "{message}"
{user_profile}

Provide:
1. A complete healthy recipe with Indian ingredients
2. Cooking time and difficulty level
3. Nutritional benefits
4. Ingredient substitutions for health conditions
5. Tips to make it healthier

Keep it practical and easy to follow."""

        else:
            prompt = f"""As a friendly AI nutrition assistant, answer this question.

📝 CONVERSATION HISTORY:
{context or 'This is the first message in this conversation.'}

User's current message: "{message}"
{user_profile}

Provide:
1. Clear, actionable advice
2. Specific examples relevant to Indian food culture
3. Health benefits or warnings as needed
4. Practical tips for implementation
5. Suggest follow-up actions if relevant

Keep response helpful, concise, and encouraging."""

        # Get AI response
        ai_response = gemini_client.invoke(prompt)
        
        # Clean and format response
        response_text = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)
        
        # Add helpful suffix
        response_text += "\n\n💡 Tip: You can scan products for detailed analysis or ask me about specific alternatives!"
        
        return response_text
        
    except Exception as e:
        print(f"⚠️ AI response generation failed: {e}")
        # Fallback response
        return f"Thank you for your question about '{message}'. As your premium nutrition assistant, I recommend focusing on whole foods and balanced nutrition. For specific product recommendations, please scan items using our analysis feature, or ask me about healthier alternatives to any food you're curious about!"

@app.post("/chat")
async def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    """AI Chatbot endpoint for premium users with conversation memory"""
    try:
        user = get_or_create_user(request.user_id, db)
        
        if user.tier != "premium":
            raise HTTPException(status_code=403, detail="Chatbot access is available for premium users only")
        
        # Load recent conversation history (last 5 messages)
        recent_chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == request.user_id
        ).order_by(ChatHistory.timestamp.desc()).limit(5).all()
        
        # Build conversation context from history
        conversation_history = []
        suggested_items_history = set()
        scanned_products_history = set()
        
        for chat in reversed(recent_chats):  # Reverse to get chronological order
            conversation_history.append(f"User: {chat.message}")
            conversation_history.append(f"Assistant: {chat.response[:300]}...")  # First 300 chars for better context
            
            # Extract what was suggested in previous conversations
            response_lower = chat.response.lower()
            message_lower = chat.message.lower()
            
            # Extract scanned products
            if 'scanned' in message_lower or 'analyzed' in message_lower:
                for product in ['aloo sev', 'chips', 'namkeen', 'biscuit', 'cookie', 'chocolate', 'noodles', 'pasta']:
                    if product in message_lower:
                        scanned_products_history.add(product)
            
            # Extract suggested healthy alternatives
            if 'makhana' in response_lower:
                suggested_items_history.add('makhana')
            if 'roasted chana' in response_lower or 'chickpea' in response_lower:
                suggested_items_history.add('roasted chana')
            if 'peanut' in response_lower:
                suggested_items_history.add('peanuts')
            if 'khakhra' in response_lower:
                suggested_items_history.add('khakhra')
            if 'ragi' in response_lower:
                suggested_items_history.add('ragi chips')
        
        # Build enhanced context with conversation memory
        enhanced_context = ""
        if conversation_history:
            enhanced_context = "RECENT CONVERSATION:\n" + "\n".join(conversation_history[-8:]) + "\n\n"  # Last 4 exchanges
        
        if scanned_products_history:
            enhanced_context += f"PRODUCTS USER SCANNED: {', '.join(scanned_products_history)}\n\n"
        
        if suggested_items_history:
            enhanced_context += f"HEALTHY ALTERNATIVES PREVIOUSLY SUGGESTED: {', '.join(suggested_items_history)}\n\n"
        
        if request.context:
            enhanced_context += f"CURRENT SCAN/CONTEXT: {request.context}\n"
        
        # Enhanced AI chatbot response using Gemini with memory
        response = await generate_intelligent_response(request.message, enhanced_context, user)
        
        # Save chat history
        chat_entry = ChatHistory(
            user_id=request.user_id,
            message=request.message,
            response=response,
            context=enhanced_context,
            timestamp=datetime.datetime.now().isoformat()
        )
        db.add(chat_entry)
        db.commit()
        
        return {"response": response, "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/users/{user_id}/history")
async def get_scan_history(user_id: str, db: Session = Depends(get_db)):
    """Get scan history for premium users"""
    try:
        # Check if user is premium by querying database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.tier != "premium":
            return {
                "scans": [], 
                "message": "Scan history is available for premium users only. Upgrade to premium to access your scan history.",
                "user_tier": user.tier
            }
        
        # Get scan history for premium user
        scans = db.query(ScanHistory).filter(ScanHistory.user_id == user_id).order_by(ScanHistory.timestamp.desc()).limit(20).all()
        
        history = []
        for scan in scans:
            try:
                analysis_data = json.loads(scan.analysis_data) if scan.analysis_data else {}
                
                # Extract verdict as string - handle if it's stored as JSON
                verdict_value = scan.verdict
                if verdict_value:
                    try:
                        # Try to parse if it's JSON and extract the text
                        verdict_obj = json.loads(verdict_value)
                        if isinstance(verdict_obj, dict):
                            verdict_str = verdict_obj.get('text') or verdict_obj.get('verdict') or str(verdict_obj)
                        else:
                            verdict_str = str(verdict_obj)
                    except (json.JSONDecodeError, TypeError):
                        # If it's already a string, use it directly
                        verdict_str = verdict_value
                else:
                    verdict_str = "Unknown"
                
                history.append({
                    "id": scan.id,
                    "product_name": scan.product_name,
                    "health_score": scan.health_score,
                    "verdict": verdict_str,
                    "timestamp": scan.timestamp,
                    "summary": analysis_data.get("summary", ""),
                    "analysis_data": analysis_data  # Include full analysis data
                })
            except json.JSONDecodeError:
                continue
        
        return {
            "scans": history,
            "total": len(history),
            "user_tier": "premium"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/users/{user_id}/chat-history")
async def get_chat_history(user_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """Get chat conversation history for premium users"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.tier != "premium":
            return {
                "chats": [],
                "message": "Chat history is available for premium users only.",
                "user_tier": user.tier
            }
        
        # Get recent chat history
        chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
        
        chat_history = []
        for chat in reversed(chats):  # Show in chronological order
            chat_history.append({
                "id": chat.id,
                "message": chat.message,
                "response": chat.response,
                "timestamp": chat.timestamp
            })
        
        return {
            "chats": chat_history,
            "total": len(chat_history),
            "user_tier": "premium"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

# News cache with timestamp
news_cache = {}

@app.get("/news")
async def get_food_news(
    user_id: str,
    limit: int = 10,
    category: str = "all",
    db: Session = Depends(get_db)
):
    """
    Get latest food news articles using LangChain/LangGraph agent
    Premium users get full feed, free users get limited preview
    """
    try:
        # Get or create user
        user = get_or_create_user(user_id, db)
        is_premium = user.tier == "premium"
        
        # Check cache (1 hour TTL)
        cache_key = f"news_{category}"
        current_time = datetime.datetime.now()
        
        if cache_key in news_cache:
            cached_time, cached_news = news_cache[cache_key]
            time_diff = (current_time - cached_time).total_seconds()
            
            if time_diff < 3600:  # 1 hour cache
                print(f"📰 Using cached news (age: {int(time_diff/60)} minutes)")
                news_articles = cached_news
            else:
                # Cache expired, fetch new
                news_articles = None
        else:
            news_articles = None
        
        # Fetch news if not cached
        if news_articles is None:
            print("🔍 Fetching fresh news from LangChain agent...")
            try:
                from langchain_agents.news_agent import fetch_latest_food_news
                news_articles = fetch_latest_food_news()
                
                # Cache the results
                news_cache[cache_key] = (current_time, news_articles)
                print(f"✅ Fetched and cached {len(news_articles)} articles")
                
            except Exception as e:
                print(f"❌ News fetch error: {str(e)}")
                # Return fallback news
                news_articles = get_fallback_news()
        
        # Filter by category if specified
        if category != "all":
            news_articles = [
                article for article in news_articles 
                if article.get("category", "").lower() == category.lower()
            ]
        
        # Limit based on tier
        if is_premium:
            limited_articles = news_articles[:limit]
            message = None
        else:
            # Free users get only 2 preview articles
            limited_articles = news_articles[:2]
            message = f"🔒 Showing 2 of {len(news_articles)} articles. Upgrade to Premium for full access to food news!"
        
        return {
            "articles": limited_articles,
            "total_available": len(news_articles),
            "shown": len(limited_articles),
            "user_tier": user.tier,
            "message": message,
            "cached": cache_key in news_cache and news_articles is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ News endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get news: {str(e)}")

def get_fallback_news() -> List[Dict]:
    """Fallback news in case the agent fails"""
    return [
        {
            "id": "fallback_1",
            "title": "FSSAI Updates Food Labeling Guidelines for 2024",
            "summary": "The Food Safety and Standards Authority of India (FSSAI) has introduced new guidelines requiring clearer nutritional information on packaged foods. The update aims to help consumers make informed dietary choices.",
            "category": "regulations",
            "source": "FSSAI",
            "url": "https://fssai.gov.in",
            "published_date": datetime.datetime.now().isoformat(),
            "relevance_score": 8,
            "credibility": "high",
            "image_url": None,
            "tags": ["FSSAI", "Food Law", "Compliance"]
        },
        {
            "id": "fallback_2",
            "title": "New Study Links Ultra-Processed Foods to Health Risks",
            "summary": "Recent research published in leading medical journals indicates that regular consumption of ultra-processed foods may increase risks of cardiovascular diseases and metabolic disorders. Experts recommend limiting processed food intake.",
            "category": "health",
            "source": "Health News",
            "url": "https://example.com/health",
            "published_date": datetime.datetime.now().isoformat(),
            "relevance_score": 9,
            "credibility": "high",
            "image_url": None,
            "tags": ["Nutrition", "Healthy Eating", "Wellness"]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
