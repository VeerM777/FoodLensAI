# 🍎 FoodLens AI - Smart Food Analysis & Health Insights

<div align="center">

![FoodLens AI Banner](https://img.shields.io/badge/FoodLens-AI%20Powered-brightgreen?style=for-the-badge)
[![Flutter](https://img.shields.io/badge/Flutter-3.0+-02569B?style=for-the-badge&logo=flutter)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)](https://python.org)


**Empowering consumers with AI-driven food transparency and personalized health insights**

[Features](#-key-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Team](#-team)

---

## 🌟 Overview

**FoodLens AI** is an intelligent food analysis platform that combines computer vision, natural language processing, and agentic AI to provide comprehensive health insights about food products. By simply scanning a barcode or searching for products, users receive detailed nutritional analysis, health recommendations, and personalized alternatives tailored to their dietary needs.

### 🎯 Problem Statement

In today's market, consumers face:
- **Information Overload**: Complex nutritional labels that are hard to interpret
- **Hidden Ingredients**: Harmful additives and preservatives not clearly indicated
- **Misleading Claims**: Marketing that doesn't match nutritional reality
- **Personalization Gap**: Generic advice that doesn't consider individual health conditions

### 💡 Our Solution

FoodLens AI democratizes food transparency by:
- **Instant Analysis**: Scan any barcode for immediate health insights
- **AI-Powered Verification**: Cross-check marketing claims against actual nutritional data
- **Personalized Recommendations**: Get alternatives based on your health profile
- **Smart Chatbot**: Ask questions and get expert nutritional guidance
- **News & Trends**: Stay updated with the latest food safety and nutrition news

---

## ✨ Key Features

### 🔍 Smart Product Analysis
- **Barcode Scanning**: Instant product recognition using mobile camera
- **OCR Technology**: Extract information from product images
- **Nutritional Breakdown**: Comprehensive analysis of macros, micros, and additives
- **Health Score**: 0-100 rating based on nutritional content and ingredients

### 🎯 Personalized Health Insights
- **User Profiles**: Store health conditions, allergies, and dietary preferences
- **Custom Recommendations**: AI-generated alternatives based on your health needs
- **Allergen Warnings**: Instant alerts for ingredients you're allergic to
- **Dietary Compliance**: Check compatibility with vegan, keto, gluten-free diets

### 🤖 Agentic AI System
- **Multi-Agent Architecture**: Specialized agents for different analysis tasks
  - **OCR Agent**: Barcode and text extraction
  - **Health Analysis Agent**: Nutritional evaluation and scoring
  - **FSSAI Verification Agent**: Claim validation and compliance checking
  - **News Agent**: Real-time food safety news aggregation
- **LangGraph Integration**: Coordinated multi-agent workflows
- **Gemini AI**: Advanced natural language understanding

### 💬 Smart Chatbot
- **Natural Conversations**: Ask nutrition questions in plain language
- **Context-Aware**: Remembers your health profile and past queries
- **Expert Knowledge**: Powered by Gemini 2.0 Flash for accurate responses
- **Multi-Turn Dialogue**: Follow-up questions and clarifications

### 📊 Advanced Analytics
- **Search History**: Track all your product searches
- **Health Trends**: Visualize your dietary patterns over time
- **Comparison Tools**: Compare products side-by-side
- **Alternative Suggestions**: Healthier product recommendations

### 🔐 Premium Features
- **Unlimited Scans**: No monthly limits on product analysis
- **Priority Support**: Faster response times
- **Advanced AI Features**: Access to claim verification and news
- **Export Data**: Download your health reports

---

## 🛠 Tech Stack

### Frontend (Flutter)
```yaml
Framework: Flutter 3.0+
Language: Dart
State Management: Riverpod
Navigation: Go Router
UI Libraries: Material Design 3
Animations: Lottie, Flutter Animate
```

**Key Dependencies:**
- `flutter_riverpod` - Reactive state management
- `go_router` - Declarative routing
- `mobile_scanner` - Barcode scanning
- `firebase_auth` - Authentication
- `http` & `dio` - API communication
- `cached_network_image` - Image caching
- `google_fonts` - Typography

### Backend (FastAPI)
```python
Framework: FastAPI 0.109+
Language: Python 3.9+
AI/ML: LangChain, LangGraph, Gemini AI
Database: SQLite
OCR: EasyOCR, PyZbar
```

**Key Dependencies:**
- `fastapi` - Modern web framework
- `langchain` - LLM orchestration
- `langgraph` - Multi-agent workflows
- `google-generativeai` - Gemini AI integration
- `easyocr` - Optical character recognition
- `sqlalchemy` - Database ORM
- `uvicorn` - ASGI server

### AI & ML Stack
- **LLM**: Google Gemini 2.0 Flash
- **Agent Framework**: LangGraph with multi-agent orchestration
- **OCR**: EasyOCR for text extraction, PyZbar for barcodes
- **Data Sources**: OpenFoodFacts API, custom Indian product database

### Infrastructure
- **Authentication**: Firebase Auth with Google Sign-In
- **Database**: SQLite (production-ready for PostgreSQL migration)
- **API**: RESTful with FastAPI
- **Deployment**: Docker-ready architecture

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FoodLens AI System                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  Flutter Mobile  │◄────────┤  Firebase Auth   │        │
│  │      App         │         │   (Google SSO)   │        │
│  └────────┬─────────┘         └──────────────────┘        │
│           │                                                 │
│           │ HTTP/REST API                                   │
│           │                                                 │
│  ┌────────▼──────────────────────────────────────────┐    │
│  │           FastAPI Backend Server                   │    │
│  │  ┌──────────────────────────────────────────────┐ │    │
│  │  │         LangGraph Agent Orchestrator         │ │    │
│  │  │  ┌────────────┐  ┌──────────────────────┐  │ │    │
│  │  │  │ OCR Agent  │  │ Health Analysis Agent│  │ │    │
│  │  │  └────────────┘  └──────────────────────┘  │ │    │
│  │  │  ┌────────────┐  ┌──────────────────────┐  │ │    │
│  │  │  │FSSAI Agent │  │   News Agent         │  │ │    │
│  │  │  └────────────┘  └──────────────────────┘  │ │    │
│  │  └──────────────────────────────────────────────┘ │    │
│  │                                                      │    │
│  │  ┌───────────────┐  ┌─────────────────────────┐  │    │
│  │  │ Gemini 2.0    │  │  OpenFoodFacts API      │  │    │
│  │  │ Flash AI      │  │  (Product Database)     │  │    │
│  │  └───────────────┘  └─────────────────────────┘  │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐ │    │
│  │  │         SQLite Database                       │ │    │
│  │  │  - Users  - Scan History  - Chat History     │ │    │
│  │  │  - Health Conditions  - Allergies            │ │    │
│  │  └──────────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Workflow
```
User Scan → OCR Agent → Product Recognition
                ↓
         OpenFoodFacts API
                ↓
    Health Analysis Agent → Gemini AI Analysis
                ↓
         Health Score + Insights
                ↓
    FSSAI Verification Agent → Claim Validation
                ↓
         User Response
```

---

## 🚀 Installation

### Prerequisites
- **Flutter SDK**: 3.0 or higher
- **Python**: 3.9 or higher
- **Node.js**: 16+ (for Firebase CLI)
- **Git**: Latest version
- **Android Studio** or **Xcode** (for mobile development)

### Backend Setup

1. **Clone the Repository**
```bash
git clone https://github.com/VeerM777/FoodLensAI.git
cd FoodLensAI
```

2. **Navigate to Backend Directory**
```bash
cd FoodLens
```

3. **Create Virtual Environment**
```bash
python -m venv env

# Windows
.\env\Scripts\activate

# macOS/Linux
source env/bin/activate
```

4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

5. **Set Up Environment Variables**

Create a `.env` file in the `FoodLens` directory:
```env
# Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./foodlens.db

# Free Tier Limits
FREE_TIER_SCAN_LIMIT=5

# Optional: Groq API (for alternative LLM)
GROQ_API_KEY=your_groq_api_key_here
```

6. **Initialize Database**
```bash
python start_server.py
```
The database will be automatically created on first run.

7. **Verify Backend is Running**
- Open browser: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to Flutter App Directory**
```bash
cd FoodLens2/FoodLens-AI---Flutter-App
```

2. **Install Flutter Dependencies**
```bash
flutter pub get
```

3. **Configure Firebase**

Create `lib/firebase_options.dart` with your Firebase configuration:
```dart
// This file is generated by FlutterFire CLI
// Follow these steps:
// 1. Install Firebase CLI: npm install -g firebase-tools
// 2. Login: firebase login
// 3. Configure: flutterfire configure
```

Or manually add your Firebase config:
```dart
import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart' show defaultTargetPlatform, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      default:
        throw UnsupportedError('Firebase not configured for this platform');
    }
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'YOUR_API_KEY',
    appId: 'YOUR_APP_ID',
    messagingSenderId: 'YOUR_SENDER_ID',
    projectId: 'YOUR_PROJECT_ID',
    storageBucket: 'YOUR_STORAGE_BUCKET',
  );

  // Add iOS configuration if needed
}
```

4. **Update API Base URL**

Edit `lib/core/constants/api_constants.dart`:
```dart
class ApiConstants {
  static const String baseUrl = 'http://10.0.2.2:8000'; // Android Emulator
  // static const String baseUrl = 'http://localhost:8000'; // iOS Simulator
  // static const String baseUrl = 'http://YOUR_IP:8000'; // Physical Device
}
```

5. **Run the App**

For Android:
```bash
flutter run -d android
```

For iOS:
```bash
flutter run -d ios
```

For Web (Development):
```bash
flutter run -d chrome
```

---

## 📖 Usage Guide

### For Users

#### 1. Getting Started
1. **Sign Up / Sign In**
   - Open the app
   - Sign in with Google or email
   - Complete your health profile

2. **Scan a Product**
   - Tap the camera icon on home screen
   - Point camera at barcode
   - Wait for analysis results

3. **Search Products**
   - Tap search icon
   - Type product name
   - Browse results and view details

4. **Chat with AI**
   - Navigate to Chat tab
   - Ask nutrition questions
   - Get personalized advice

#### 2. Understanding Health Scores

- **90-100**: Excellent - Highly nutritious, minimal processing
- **70-89**: Good - Decent nutrition, some concerns
- **50-69**: Fair - Moderate concerns, consume occasionally
- **0-49**: Poor - High in harmful ingredients, avoid if possible

#### 3. Premium Features
- Upgrade to Premium in Profile → Subscription
- Unlock unlimited scans, alternatives, and AI features
- Cancel anytime

### For Developers

#### Running Tests
```bash
# Backend tests
cd FoodLens
pytest tests/

# Flutter tests
cd FoodLens2/FoodLens-AI---Flutter-App
flutter test
```

#### API Testing
Use the interactive API docs at `http://localhost:8000/docs` to test endpoints.

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Key Endpoints

#### 1. Product Analysis
```http
POST /analyze/barcode
Content-Type: application/json

{
  "barcode": "8901058000290",
  "user_id": "firebase_user_id",
  "response_format": "user_friendly"
}
```

**Response:**
```json
{
  "output_type": "user_friendly",
  "summary": {
    "product_name": "Maggi 2-Minute Noodles",
    "brand": "Nestle",
    "health_score": 45,
    "verdict": "Avoid",
    "alternatives": [...]
  }
}
```

#### 2. Product Search
```http
GET /search?query=maggi&user_id=user123&limit=20
```

#### 3. Chat with AI
```http
POST /chat
Content-Type: application/json

{
  "user_id": "user123",
  "message": "Is this product good for diabetics?",
  "context": {
    "product_name": "Maggi Noodles"
  }
}
```

#### 4. User Management
```http
# Get user tier
GET /users/{user_id}/tier

# Update tier
PUT /users/{user_id}/tier
Content-Type: application/json

{
  "tier": "premium"
}
```

Full API documentation available at: `http://localhost:8000/docs`

---

## 📁 Project Structure

```
FoodLensAI/
├── FoodLens/                      # Backend (FastAPI)
│   ├── api/
│   │   └── main.py               # Main API routes
│   ├── agents/                    # Agentic AI modules
│   │   ├── ocr_barcode.py        # OCR & barcode scanning
│   │   ├── health_analysis.py    # Health scoring
│   │   └── fssai_verification.py # Claim verification
│   ├── langchain_agents/          # LangGraph agents
│   │   ├── agent.py              # Agent definitions
│   │   ├── graph.py              # Agent workflows
│   │   ├── tools.py              # Custom tools
│   │   └── news_agent.py         # News aggregation
│   ├── models/
│   │   └── database.py           # SQLAlchemy models
│   ├── utils/
│   │   ├── search_utils_dynamic.py # Product search
│   │   ├── health_calculator.py  # Health metrics
│   │   └── indian_products_db.py # Product database
│   ├── config/
│   │   └── settings.py           # Configuration
│   ├── requirements.txt          # Python dependencies
│   └── start_server.py           # Server entry point
│
├── FoodLens2/
│   └── FoodLens-AI---Flutter-App/ # Frontend (Flutter)
│       ├── lib/
│       │   ├── main.dart         # App entry point
│       │   ├── core/
│       │   │   ├── constants/    # App constants
│       │   │   ├── models/       # Data models
│       │   │   ├── services/     # API services
│       │   │   └── theme/        # App theming
│       │   ├── features/
│       │   │   ├── home/         # Home screen
│       │   │   ├── scan/         # Barcode scanning
│       │   │   ├── search/       # Product search
│       │   │   ├── chat/         # AI chatbot
│       │   │   ├── profile/      # User profile
│       │   │   └── auth/         # Authentication
│       │   └── shared/
│       │       ├── widgets/      # Reusable widgets
│       │       └── providers/    # Riverpod providers
│       ├── assets/
│       │   ├── images/           # App images
│       │   ├── icons/            # App icons
│       │   └── animations/       # Lottie animations
│       ├── pubspec.yaml          # Flutter dependencies
│       └── android/              # Android config
│
└── README.md                     # This file
```

---

## 📸 Screenshots

*(Add screenshots of your app here)*

### Home Screen
![Home Screen](screenshots/home.png)

### Barcode Scanning
![Scan](screenshots/scan.png)

### Health Analysis
![Analysis](screenshots/analysis.png)

### AI Chatbot
![Chat](screenshots/chat.png)

---

## 🗺 Roadmap

### Phase 1: MVP (Completed ✅)
- [x] Barcode scanning and OCR
- [x] Basic health analysis
- [x] Product search
- [x] User authentication
- [x] SQLite database

### Phase 2: AI Enhancement (Current 🚧)
- [x] Multi-agent AI system with LangGraph
- [x] Gemini AI integration
- [x] FSSAI claim verification
- [x] Smart chatbot
- [x] News aggregation
- [ ] Advanced health recommendations

### Phase 3: Personalization (Next 📋)
- [ ] Machine learning-based recommendations
- [ ] Meal planning assistant
- [ ] Nutrition tracking
- [ ] Recipe suggestions
- [ ] Social features (share findings)

### Phase 4: Scale & Polish (Future 🚀)
- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] Kubernetes deployment
- [ ] Multi-language support
- [ ] Offline mode
- [ ] Wearable integration

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Bugs
1. Check if the bug already exists in [Issues](https://github.com/VeerM777/FoodLensAI/issues)
2. Create a new issue with detailed description
3. Include steps to reproduce
4. Add screenshots if applicable

### Suggesting Features
1. Open an issue with `[Feature Request]` tag
2. Describe the feature and use case
3. Explain why it would be valuable

### Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style
- Write meaningful commit messages
- Add tests for new features
- Update documentation
- Keep PRs focused and small

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**FoodLens AI** is built by a passionate team dedicated to food transparency and health.

- **Backend Development**: FastAPI, LangChain, Gemini AI integration
- **Frontend Development**: Flutter UI/UX, State Management
- **AI/ML**: Multi-agent systems, Health analysis algorithms
- **Design**: UI/UX design, Brand identity

---

## 🙏 Acknowledgments

- [OpenFoodFacts](https://world.openfoodfacts.org/) - Comprehensive food product database
- [Google Gemini](https://deepmind.google/technologies/gemini/) - Advanced AI capabilities
- [LangChain](https://langchain.com/) - LLM orchestration framework
- [Flutter](https://flutter.dev/) - Beautiful cross-platform framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

---

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/VeerM777/FoodLensAI/issues)
- **Email**: support@foodlensai.com *(if applicable)*
- **Documentation**: [Wiki](https://github.com/VeerM777/FoodLensAI/wiki)

---

## ⚡ Quick Start Commands

```bash
# Backend
cd FoodLens
python -m venv env
.\env\Scripts\activate  # Windows
pip install -r requirements.txt
python start_server.py

# Frontend (new terminal)
cd FoodLens2/FoodLens-AI---Flutter-App
flutter pub get
flutter run
```

---

<div align="center">

**Made with ❤️ for healthier food choices**

⭐ Star us on GitHub if you find this project helpful!

</div>

