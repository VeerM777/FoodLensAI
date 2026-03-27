# FoodLens AI

FoodLens AI is a proof-of-concept assistant that reads any packed-food barcode or label, explains what is inside, and scores the product for different health profiles. The mobile UI is written in Flutter, while a FastAPI backend runs OCR, barcode lookup, AI reasoning, and data storage.

---

## What the System Does
- **Scan or search** a product to fetch nutrition facts, additives, and regulatory claims.
- **Analyze** the ingredients with agents specialized for OCR, health scoring, FSSAI verification, and news scraping (coordinated with LangGraph + Gemini).
- **Score** the product (0-100) and flag allergens or diet conflicts using saved user profiles.
- **Suggest** safer alternatives and let users chat with an AI nutrition assistant for clarifications.

---

## How It’s Built
- **Flutter app**: Riverpod state management, Go Router navigation, Firebase Auth for sign-in, and `mobile_scanner` for barcode capture.
- **FastAPI backend**: LangChain/LangGraph agents, EasyOCR + PyZbar for text/barcodes, SQLAlchemy + SQLite for persistence, Gemini for reasoning, and OpenFoodFacts plus a local product DB for facts.
- **Flow**: App → FastAPI → agent graph → data sources → responses returned as structured JSON that the Flutter UI renders.

---

## Run It Locally
```bash
# 1. clone
git clone https://github.com/VeerM777/FoodLensAI.git
cd FoodLensAI

# 2. backend
cd FoodLens
python -m venv env && .\env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # fill keys such as GEMINI_API_KEY
python start_server.py   # serves http://localhost:8000 and creates foodlens.db

# 3. frontend
cd ../FoodLens2/FoodLens-AI---Flutter-App
flutter pub get
flutter run            # select emulator/device (android/ios/web)
```

Set the Flutter constant `ApiConstants.baseUrl` to your machine’s backend URL (e.g., `10.0.2.2` for Android emulator).

---

## Using the App
1. **Sign in** with Google/email (Firebase) and add health conditions or diet tags.
2. **Scan** a barcode or **search** for a product; the backend fetches label data, runs OCR if needed, and assembles a health report.
3. **Read the verdict**: health score, risk highlights, allergen warnings, and agent-backed explanations.
4. **Ask follow-ups** through the built-in chat agent or review suggested alternatives.
5. **Developers** can test APIs directly at `http://localhost:8000/docs`, run `pytest` inside `FoodLens`, and `flutter test` for the Flutter layer.

Health score guide: 90-100 excellent, 70-89 good, 50-69 moderate, below 50 avoid when possible.

---

## High-Level Structure
```
FoodLensAI/
├─ FoodLens/                  # FastAPI service, agents, models, utils, config
├─ FoodLens2/FoodLens-AI---Flutter-App/
│  └─ lib/                    # Flutter screens, services, state, widgets
└─ README.md                  # This overview
```

Use this repository as a reference build: the code shows how to combine barcode scanning, OCR, LangGraph agents, and a Flutter client into a single health-check experience.


