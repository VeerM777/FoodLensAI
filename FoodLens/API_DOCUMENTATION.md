# FoodLens Backend API Documentation

**Base URL:** `http://localhost:8000`  
**Version:** 1.0.0  
**Server:** FastAPI with Python 3.11+

---

## 📋 Table of Contents
1. [Authentication & Users](#authentication--users)
2. [Product Analysis](#product-analysis)
3. [AI Chatbot](#ai-chatbot)
4. [Scan History](#scan-history)
5. [User Profile](#user-profile)
6. [Health & Fitness](#health--fitness)
7. [Error Handling](#error-handling)

---

## 🔐 Authentication & Users

### 1. Register User
**POST** `/register`

Create a new user account.

**Request Body:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "age": 25,
  "gender": "male",
  "height_cm": 175,
  "weight_kg": 70,
  "tier": "free",
  "fitness_goals": "weight_loss",
  "health_conditions": ["diabetes", "hypertension"],
  "allergies": ["peanuts", "milk"]
}
```

**Response:** `200 OK`
```json
{
  "message": "User registered successfully",
  "user_id": "user_123",
  "tier": "free"
}
```

---

### 2. Get or Create User
**POST** `/users`

Get existing user or create if doesn't exist.

**Request Body:**
```json
{
  "user_id": "user_123",
  "age": 25
}
```

**Response:** `200 OK`
```json
{
  "user_id": "user_123",
  "tier": "free",
  "age": 25,
  "email": "user@example.com"
}
```

---

### 3. Update User Tier
**PUT** `/users/{user_id}/tier`

Upgrade/downgrade user subscription tier.

**Request Body:**
```json
{
  "tier": "premium"
}
```

**Response:** `200 OK`
```json
{
  "message": "Tier updated successfully",
  "user_id": "user_123",
  "tier": "premium",
  "features": [
    "Unlimited scans",
    "AI-powered alternatives",
    "Detailed health insights",
    "Scan history",
    "AI chatbot access"
  ]
}
```

---

## 🔍 Product Analysis

### 4. Analyze Product
**POST** `/analyze`

Analyze product from barcode image or text.

**Query Parameters:**
- `user_id` (required): User identifier
- `barcode` (optional): Barcode number if already extracted
- `response_format` (optional): `"user_friendly"` or `"detailed"` (default: detailed)

**Request Body:** `multipart/form-data`
- `file`: Image file (JPEG/PNG)

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/analyze?user_id=user_123&response_format=user_friendly" \
  -F "file=@product_image.jpg"
```

**Response:** `200 OK`
```json
{
  "output_type": "user_friendly",
  "sections": {
    "analysis": "# Product Analysis\n\n**Product:** Maggi Noodles...",
    "alternatives": "# Healthier Alternatives\n\n1. **Whole Wheat Pasta**...",
    "health_notes": "# Health Recommendations\n\nLimit instant noodles..."
  },
  "summary": {
    "product_name": "Maggi 2-Minute Noodles",
    "brand": "Nestle",
    "health_score": 35,
    "verdict": "Not Recommended",
    "has_alternatives": true,
    "alternatives_count": 3,
    "alternatives": [
      {
        "name": "Whole Wheat Pasta",
        "brand": "Borges",
        "score": 75,
        "score_difference": 40,
        "benefits": "High in fiber, complex carbohydrates",
        "availability": "DMart, BigBasket, Amazon",
        "price": "₹150-200 for 500g"
      }
    ]
  }
}
```

**Error Codes:**
- `400`: Invalid file format
- `403`: Free user exceeded scan limit (5 scans/month)
- `500`: Analysis failed

---

## 💬 AI Chatbot

### 5. Chat with AI
**POST** `/chat`

Premium feature: Chat with AI nutrition assistant.

**Request Body:**
```json
{
  "user_id": "user_123",
  "message": "What are healthy alternatives for chips?",
  "context": "User scanned Lays Classic Salted chips"
}
```

**Response:** `200 OK`
```json
{
  "response": "Great question! Here are 3 healthy alternatives to chips:\n\n1. **Roasted Makhana (Fox Nuts)**\n   - Brand: Farmley, Nutraj\n   - Price: ₹150/200g\n   - Health Score: 85/100\n   - Where to buy: Amazon, BigBasket\n\n2. **Baked Khakhra**...",
  "status": "success"
}
```

**Error Codes:**
- `403`: Free user (chatbot is premium only)
- `500`: Chat processing failed

---

### 6. Get Chat History
**GET** `/users/{user_id}/chat-history?limit=10`

Get recent chat conversations (premium only).

**Query Parameters:**
- `limit` (optional): Number of conversations (default: 10)

**Response:** `200 OK`
```json
{
  "chats": [
    {
      "id": 1,
      "message": "What are alternatives for makhana?",
      "response": "Here are different makhana brands...",
      "timestamp": "2025-11-23T10:30:00"
    }
  ],
  "total": 5,
  "user_tier": "premium"
}
```

---

## 📊 Scan History

### 7. Get Scan History
**GET** `/users/{user_id}/history`

Get user's scan history (premium only).

**Response:** `200 OK`
```json
{
  "scans": [
    {
      "id": 1,
      "product_name": "Maggi Noodles",
      "health_score": 35,
      "verdict": "Not Recommended",
      "timestamp": "2025-11-23T09:15:00",
      "summary": "High in sodium and MSG..."
    }
  ],
  "total": 15,
  "user_tier": "premium"
}
```

**Free User Response:**
```json
{
  "scans": [],
  "message": "Scan history is available for premium users only. Upgrade to premium to access your scan history.",
  "user_tier": "free"
}
```

---

### 8. Save Scan to History
**POST** `/users/{user_id}/scan-history`

Save a scan result to user's history (automatic for premium).

**Request Body:**
```json
{
  "product_name": "Maggi Noodles",
  "barcode": "8901058843231",
  "health_score": 35,
  "category": "instant_noodles",
  "verdict": "Not Recommended",
  "analysis_data": {
    "summary": "High in sodium...",
    "alternatives": []
  }
}
```

**Response:** `200 OK`
```json
{
  "message": "Scan saved to history",
  "scan_id": 123
}
```

---

## 👤 User Profile

### 9. Update User Profile
**PUT** `/users/{user_id}/profile`

Update user profile information.

**Request Body:**
```json
{
  "age": 26,
  "weight_kg": 68,
  "height_cm": 175,
  "fitness_goals": "muscle_gain"
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile updated successfully",
  "user_id": "user_123"
}
```

---

### 10. Add Health Condition
**POST** `/users/{user_id}/health-conditions`

Add a health condition to user profile.

**Request Body:**
```json
{
  "condition_name": "diabetes"
}
```

**Response:** `200 OK`
```json
{
  "message": "Health condition added",
  "condition_id": 5
}
```

---

### 11. Add Allergy
**POST** `/users/{user_id}/allergies`

Add an allergy to user profile.

**Request Body:**
```json
{
  "allergen": "peanuts"
}
```

**Response:** `200 OK`
```json
{
  "message": "Allergy added",
  "allergy_id": 3
}
```

---

## 🏃 Health & Fitness

### 12. Get Health Insights
**GET** `/users/{user_id}/health-insights`

Get personalized health insights based on user profile.

**Response:** `200 OK`
```json
{
  "bmi": 22.9,
  "bmi_category": "Normal",
  "daily_calorie_needs": 2200,
  "recommendations": [
    "Maintain current weight",
    "Focus on protein intake for muscle gain",
    "Avoid high-sugar products"
  ],
  "health_conditions": ["diabetes"],
  "allergies": ["peanuts"]
}
```

---

## 🎯 Tier System

### Free Tier
- ✅ 5 scans per month
- ✅ Basic health analysis
- ✅ Product information
- ❌ AI chatbot
- ❌ Scan history
- ❌ Detailed alternatives

### Premium Tier (₹99/month)
- ✅ Unlimited scans
- ✅ AI-powered alternatives
- ✅ Detailed health insights
- ✅ Scan history (unlimited)
- ✅ AI chatbot access
- ✅ Priority support

---

## ⚠️ Error Handling

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Status Codes
- `200`: Success
- `400`: Bad Request (invalid input)
- `403`: Forbidden (tier restriction)
- `404`: Not Found (user/resource doesn't exist)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

### Example Error Responses

**403 - Free User Scan Limit:**
```json
{
  "detail": "Free users are limited to 5 scans per month. Upgrade to premium for unlimited scans."
}
```

**403 - Premium Feature:**
```json
{
  "detail": "Chatbot access is available for premium users only"
}
```

**500 - Analysis Failed:**
```json
{
  "detail": "Analysis failed: No module named 'easyocr'"
}
```

---

## 🔧 Testing Endpoints

### Health Check
**GET** `/`

Check if server is running.

**Response:**
```json
{
  "message": "FoodLens AI API - Powered by Google Gemini",
  "status": "healthy",
  "version": "1.0.0"
}
```

### OpenAPI Documentation
**GET** `/docs`

Interactive API documentation (Swagger UI)

### Alternative Documentation
**GET** `/redoc`

Alternative API documentation (ReDoc)

---

## 🚀 Getting Started

### 1. Start Server
```bash
cd d:\Mumbaihacks\FoodLens
python start_server.py
```

### 2. Test with cURL
```bash
# Register user
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"id":"user_123","email":"test@example.com","tier":"premium"}'

# Analyze product
curl -X POST "http://localhost:8000/analyze?user_id=user_123" \
  -F "file=@product.jpg"

# Chat with AI
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_123","message":"What are healthy snacks?"}'
```

### 3. Environment Variables
Create `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./foodlens.db
SECRET_KEY=your_secret_key_here
```

---

## 📱 Flutter Integration

### Base URL Configuration
```dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000';
  static const String androidEmulator = 'http://10.0.2.2:8000';
}
```

### Example Flutter API Call
```dart
final response = await dio.post(
  '${ApiConfig.baseUrl}/analyze',
  queryParameters: {'user_id': userId},
  data: FormData.fromMap({
    'file': await MultipartFile.fromFile(imagePath),
  }),
);
```

---

## 📞 Support

- **Email:** support@foodlens.ai
- **GitHub:** https://github.com/mohitkattungal/FoodLens-AI---Flutter-App
- **Documentation:** This file

---

**Last Updated:** November 23, 2025  
**API Version:** 1.0.0
