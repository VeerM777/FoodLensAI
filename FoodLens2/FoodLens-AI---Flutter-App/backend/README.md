# 🍎 FoodLens AI Backend

AI-powered food analysis backend using FastAPI, Google Gemini, and SQLAlchemy with intelligent conversation memory.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API Key
- Virtual environment

### Installation & Startup

```bash
# Navigate to backend folder
cd d:\Mumbaihacks\FoodLens

# Activate virtual environment
.\env\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install -r requirements.txt

# Start server
python start_server.py
```

**Server URL:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

---

## 📚 Documentation

- **[Complete API Reference](./API_DOCUMENTATION.md)** - All endpoints with examples
- **[OpenAPI Schema](./scripts/api_schema.json)** - For Flutter/frontend integration
- **Interactive Docs:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc

---

## 🎯 Features

- **Product Identification**: Analyze food products using OCR text and barcode scanning
- **Product Categorization**: Classify food products into categories using Gemini AI
- **Health Assessment**: Calculate health scores based on nutritional information
- **Alternative Recommendation**: Suggest healthier alternative products
- **Claim Verification**: Verify health claims on product packaging (Premium feature)
- **FSSAI Compliance Check**: Verify regulatory compliance (Premium feature)
- **LangGraph Workflow**: Orchestrated workflow using LangGraph for agentic AI

## Architecture

The application uses a modular architecture with the following components:

1. **FastAPI Backend**: Provides RESTful API endpoints
2. **LangChain Tools**: Wraps core functionality in LangChain-compatible tools
3. **LangGraph Workflow**: Orchestrates the analysis workflow using a state-based graph
4. **OCR Processing**: Extracts text from product images
5. **Barcode Scanning**: Retrieves product information from barcodes
6. **Gemini AI Integration**: Powers product categorization and analysis

## Project Structure

```
FoodLens/
│
├── langchain_agents/        # LangChain and LangGraph components
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # LangChain agent definition
│   ├── graph.py             # LangGraph workflow definition
│   └── tools.py             # LangChain tools implementation
│
├── main.py                  # FastAPI application
├── search_utils.py          # Core search functionality
├── demo.py                  # Demo script for testing
└── requirements.txt         # Project dependencies
```

## Installation

1. Clone the repository
2. Set up a Python virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables:

```bash
# Set your Google API key for Gemini AI
export GOOGLE_API_KEY="your-api-key-here"
```

## Usage

### Running the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

### API Endpoints

- **POST /api/v1/analyze_food**: Analyze food product with OCR text and/or barcode data
- **POST /api/v1/analyze_image**: Analyze food product from an uploaded image
- **GET /api/v1/health**: Health check endpoint

### Running the Demo

```bash
python demo.py
```

This will run a sample analysis using predefined OCR text.

## LangGraph Workflow

The application uses LangGraph to orchestrate the analysis workflow:

1. **Extract Product Info**: Process OCR text and barcode data
2. **Categorize Product**: Determine product category and type
3. **Calculate Health Score**: Analyze nutritional data and calculate health score
4. **Find Alternatives**: Search for healthier alternative products
5. **Verify Claims and Compliance**: Check health claims and regulatory compliance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.