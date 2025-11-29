"""
FoodLens AI Agent using LangGraph
"""
from typing import Dict, Any, List, Annotated, TypedDict, Literal
import operator
import json
import os
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
# Removed ChatGoogleGenerativeAI import since we're using the Google API directly
# from langchain_google_genai import ChatGoogleGenerativeAI
from google.generativeai import GenerativeModel
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

# Import our tools
from .tools import tools, process_ocr, process_barcode, categorize_product, calculate_health_score, find_alternatives, verify_claims, verify_fssai

# Define state types
class AgentState(TypedDict):
    messages: Annotated[List[Any], operator.add]
    food_image: str
    barcode_image: str 
    ocr_text: str
    barcode_data: str
    product_data: Dict[str, Any]
    health_score: int
    category: Dict[str, str]
    alternatives: List[Dict[str, Any]]
    claim_verification: Dict[str, Any]
    fssai_verification: Dict[str, Any]
    user_profile: Dict[str, Any]
    final_response: Dict[str, Any]

# Initialize LLM
try:
    # Import separately to avoid circular imports
    import os
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    
    # Configure the API
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        # Configure genai directly
        genai.configure(api_key=api_key)
        
        # Create a direct Gemini client to use instead of the LangChain wrapper
        gemini_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"temperature": 0.3},
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # We'll use the gemini_model directly instead of through LangChain
        llm = gemini_model
    else:
        print("⚠️ Warning: GOOGLE_API_KEY not found in environment variables")
        llm = None
except Exception as e:
    print(f"⚠️ Gemini AI initialization failed: {str(e)}")
    llm = None

# Define system prompt
system_prompt = """You are FoodLens AI, a sophisticated food analysis agent that helps users understand the health implications of the food products they consume.

Your goal is to analyze food products and provide accurate health information, alternatives, and regulatory verification.

Follow these steps for each food product:
1. Analyze OCR text to identify the product
2. Check barcode data if available
3. Categorize the product
4. Calculate health score based on nutritional information
5. Find healthier alternatives
6. Verify health claims on packaging
7. Check FSSAI compliance
8. Provide a comprehensive analysis to the user

If you encounter any missing information, focus on what you have available and be transparent about limitations.

Remember to consider user health conditions when making recommendations.
"""

# Define node functions for the LangGraph
def analyze_product_info(state: AgentState):
    """First node: Analyze the product information from OCR and barcode"""
    messages = state["messages"]
    
    # Process OCR and barcode data
    ocr_result = None
    barcode_result = None
    
    if state["ocr_text"]:
        ocr_result = process_ocr(state["ocr_text"])
    
    if state["barcode_data"]:
        barcode_result = process_barcode(state["barcode_data"])
    
    # Determine product name and details
    product_name = None
    product_data = {}
    
    if barcode_result:
        product_name = barcode_result.get("product_name")
        product_data = barcode_result
    
    if not product_name and ocr_result:
        product_name = ocr_result.get("product_name")
        product_data.update({
            "product_name": product_name,
            "brand": ocr_result.get("brand", ""),
            "ingredients": ocr_result.get("ingredients", [])
        })
    
    # Save product data to state
    state["product_data"] = product_data
    
    # Add an AI message explaining what was found
    if product_name:
        messages.append(AIMessage(content=f"I've analyzed the product and identified it as {product_name}."))
    else:
        messages.append(AIMessage(content="I couldn't identify the product from the provided information."))
    
    return state

def categorize_and_score(state: AgentState):
    """Second node: Categorize product and calculate health score"""
    messages = state["messages"]
    product_data = state["product_data"]
    
    if not product_data.get("product_name"):
        messages.append(AIMessage(content="I don't have enough information to categorize and score the product."))
        return state
    
    # Categorize the product
    product_name = product_data["product_name"]
    category_result = categorize_product(product_name)
    state["category"] = category_result
    product_data["product_type"] = category_result.get("type", "food")
    
    # Calculate health score
    nutrition_data = product_data.get("nutriments", {})
    health_conditions = state["user_profile"].get("health_conditions", [])
    
    if nutrition_data:
        health_score_result = calculate_health_score(nutrition_data, health_conditions)
        state["health_score"] = health_score_result
        
        # Get verdict from health score calculation
        product_data["verdict"] = health_score_result.get("verdict", {})
        
        health_score_value = health_score_result.get("score", 0)
        messages.append(AIMessage(content=f"The product {product_name} is categorized as {category_result.get('category')} with a health score of {health_score_value}/100."))
    else:
        messages.append(AIMessage(content=f"The product {product_name} is categorized as {category_result.get('category')}, but I don't have nutritional information to calculate a health score."))
    
    return state

def find_product_alternatives(state: AgentState):
    """Third node: Find healthier alternatives"""
    messages = state["messages"]
    product_data = state["product_data"]
    
    if not product_data.get("product_name") or not product_data.get("product_type"):
        messages.append(AIMessage(content="I don't have enough information to find alternatives."))
        return state
    
    # Find alternatives
    product_name = product_data["product_name"]
    product_type = product_data["product_type"]
    
    alternatives_result = find_alternatives(product_name, product_type)
    state["alternatives"] = alternatives_result
    
    if alternatives_result and len(alternatives_result) > 0:
        messages.append(AIMessage(content=f"I've found {len(alternatives_result)} healthier alternatives to {product_name}."))
    else:
        messages.append(AIMessage(content=f"I couldn't find specific alternatives to {product_name}."))
    
    return state

def verify_regulatory_compliance(state: AgentState):
    """Fourth node: Verify claims and FSSAI compliance"""
    messages = state["messages"]
    product_data = state["product_data"]
    ocr_text = state["ocr_text"]
    
    # Check if premium user to do verification
    is_premium = state["user_profile"].get("tier", "") == "premium"
    
    if is_premium and product_data and ocr_text:
        # Verify claims
        claim_result = verify_claims(product_data, ocr_text)
        state["claim_verification"] = claim_result
        
        # Verify FSSAI
        fssai_result = verify_fssai(product_data, ocr_text)
        state["fssai_verification"] = fssai_result
        
        messages.append(AIMessage(content="I've verified the product claims and regulatory compliance."))
    else:
        if not is_premium:
            messages.append(AIMessage(content="Detailed claim verification is available for premium users only."))
        else:
            messages.append(AIMessage(content="I don't have enough information to verify claims and compliance."))
    
    return state

def generate_final_response(state: AgentState):
    """Final node: Generate comprehensive response"""
    messages = state["messages"]
    product_data = state["product_data"]
    alternatives = state["alternatives"]
    
    # Create final response
    final_response = {
        "product_name": product_data.get("product_name", "Unknown Product"),
        "brand": product_data.get("brand", "Unknown Brand"),
        "product_type": product_data.get("product_type", "food"),
        "category": state["category"] if "category" in state else {},
        "health_score": state.get("health_score", 0),
        "verdict": product_data.get("verdict", {}),
        "alternatives": alternatives if alternatives else [],
        "claim_verification": state.get("claim_verification", {}),
        "fssai_verification": state.get("fssai_verification", {})
    }
    
    state["final_response"] = final_response
    
    # Format user-friendly response
    product_name = final_response["product_name"]
    health_score_value = final_response["health_score"].get("score", 0) if isinstance(final_response["health_score"], dict) else final_response["health_score"]
    verdict = final_response["verdict"].get("title", "") if final_response["verdict"] else ""
    
    response_text = f"""# FoodLens AI Analysis

## Product: {product_name}
**Health Score**: {health_score_value}/100
**Verdict**: {verdict}

"""
    
    if alternatives and len(alternatives) > 0:
        response_text += "## Healthier Alternatives\n"
        for i, alt in enumerate(alternatives[:3], 1):
            response_text += f"{i}. **{alt['name']}** ({alt['brand']}) - Health Score: {alt['health_score']}\n"
            response_text += f"   Benefits: {alt.get('health_benefits', '')}\n\n"
    
    messages.append(AIMessage(content=response_text))
    
    return state

# Define which nodes can transition to which other nodes
def decide_next_step(state: AgentState):
    """Determine the next step in the workflow"""
    messages = state["messages"]
    
    # Check state to determine next step
    if not state["product_data"] or not state["product_data"].get("product_name"):
        return "end"  # End if we couldn't identify the product
    
    if "category" not in state or not state["category"]:
        return "categorize_and_score"
    
    # If we have health score calculated but no alternatives yet
    if "health_score" in state and "alternatives" not in state:
        return "find_product_alternatives"
    
    if "alternatives" in state and "claim_verification" not in state and state["user_profile"].get("tier") == "premium":
        return "verify_regulatory_compliance"
    
    # If we've completed all steps or can't proceed further
    return "generate_final_response"

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("analyze_product_info", analyze_product_info)
workflow.add_node("categorize_and_score", categorize_and_score)
workflow.add_node("find_product_alternatives", find_product_alternatives)
workflow.add_node("verify_regulatory_compliance", verify_regulatory_compliance)
workflow.add_node("generate_final_response", generate_final_response)

# Set entry point and add edges
workflow.set_entry_point("analyze_product_info")
workflow.add_edge("analyze_product_info", "categorize_and_score")
workflow.add_edge("categorize_and_score", "find_product_alternatives")
workflow.add_edge("find_product_alternatives", "verify_regulatory_compliance")
workflow.add_edge("verify_regulatory_compliance", "generate_final_response")
workflow.add_edge("generate_final_response", END)

# Compile the graph
food_lens_agent = workflow.compile()

def analyze_food_product(
    ocr_text: str, 
    barcode_data: str = None, 
    user_profile: Dict[str, Any] = None
):
    """
    Analyze a food product using the LangGraph agent
    """
    if user_profile is None:
        user_profile = {
            "tier": "free",
            "health_conditions": []
        }
    
    # Initialize the agent state
    initial_state = {
        "messages": [SystemMessage(content=system_prompt)],
        "food_image": "",
        "barcode_image": "",
        "ocr_text": ocr_text,
        "barcode_data": barcode_data,
        "product_data": {},
        "health_score": 0,
        "category": {},
        "alternatives": [],
        "claim_verification": {},
        "fssai_verification": {},
        "user_profile": user_profile,
        "final_response": {}
    }
    
    # Run the agent
    result = food_lens_agent.invoke(initial_state)
    
    # Return the final response
    return result["final_response"]