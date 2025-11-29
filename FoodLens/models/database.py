"""
Database models for FoodLens AI
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from config.settings import config

# Database setup
DATABASE_URL = config.DATABASE_URL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """User model with health profile and tier information"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    height_cm = Column(Float, nullable=True)  
    weight_kg = Column(Float, nullable=True)  
    fitness_goals = Column(String, nullable=True)
    tier = Column(String, default="free")  # "free" or "premium"
    scan_count = Column(Integer, default=0)
    last_scan_reset = Column(String, nullable=True)  # ISO format for monthly reset
    
    # Relationships
    health_conditions = relationship("HealthCondition", back_populates="user", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="user", cascade="all, delete-orphan")
    scan_history = relationship("ScanHistory", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

class HealthCondition(Base):
    """User health conditions for personalized recommendations"""
    __tablename__ = "health_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    condition_name = Column(String)
    user_id = Column(String, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="health_conditions")

class Allergy(Base):
    """User allergies for safety recommendations"""
    __tablename__ = "allergies"
    
    id = Column(Integer, primary_key=True, index=True)
    allergen_name = Column(String)
    user_id = Column(String, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="allergies")

class ScanHistory(Base):
    """History of product scans with analysis results"""
    __tablename__ = "scan_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    product_name = Column(String)
    health_score = Column(Integer)
    verdict = Column(String)
    analysis_data = Column(Text)  # JSON string of full analysis
    alternatives = Column(Text)  # JSON string of alternatives
    timestamp = Column(String)  # ISO format
    
    user = relationship("User", back_populates="scan_history")

class ChatHistory(Base):
    """Chatbot conversation history"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    context = Column(Text, nullable=True)  # Relevant context (e.g., last scanned product)
    timestamp = Column(String)  # ISO format
    
    user = relationship("User", back_populates="chat_history")

# Create tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Database dependency for FastAPI
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()