"""
Configuration settings for FoodLens AI
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Database
    DATABASE_URL = "sqlite:///foodlens.db"
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Cache settings
    ALTERNATIVES_CACHE_TIMEOUT = 3600  # 1 hour
    
    # API limits
    FREE_TIER_SCAN_LIMIT = 5
    
    # Health scoring thresholds - STRICTER STANDARDS
    HEALTH_SCORE_THRESHOLDS = {
        "excellent": 80,  # 80+ = Excellent/Good choice
        "good": 70,        # 70-79 = Moderate choice  
        "average": 50,     # 50-69 = Not recommended
        "poor": 30,        # 30-49 = Avoid
        "very_poor": 0     # <30 = Strongly avoid
    }
    
    # Consumption recommendations
    CONSUMPTION_GUIDELINES = {
        "diabetes": {
            "sugar_limit_per_100g": 5,
            "sodium_limit_per_100g": 400
        },
        "hypertension": {
            "sodium_limit_per_100g": 300
        },
        "heart_disease": {
            "saturated_fat_limit_per_100g": 3,
            "trans_fat_limit_per_100g": 0
        }
    }

# Global config instance
config = Config()