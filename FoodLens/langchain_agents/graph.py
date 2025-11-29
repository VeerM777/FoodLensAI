"""
FoodLens AI Graph using LangGraph for workflow orchestration
"""
from typing import Dict, Any, List, Annotated, TypedDict, Literal, Optional, Union
import operator
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END

# Import our tools and agent utilities
from .tools import (
    process_ocr, 
    process_barcode, 
    categorize_product, 
    calculate_health_score,
    find_alternatives,
    verify_claims,
    verify_fssai
)

# Define the state for our graph
class FoodLensState(TypedDict):
    """State for the FoodLens AI agent graph"""
    messages: Annotated[List[Union[HumanMessage, SystemMessage, AIMessage]], operator.add]
    ocr_text: str
    barcode_data: Optional[str]
    product_info: Dict[str, Any]
    category: Dict[str, Any]
    health_score: Dict[str, Any]
    alternatives: List[Dict[str, Any]]
    claim_verification: Dict[str, Any]
    fssai_verification: Dict[str, Any]
    user_profile: Dict[str, Any]
    errors: List[str]

def extract_product_info(state: FoodLensState) -> FoodLensState:
    """
    Extract product information from OCR text and barcode data
    """
    messages = state["messages"]
    ocr_text = state["ocr_text"]
    barcode_data = state["barcode_data"]
    product_info = {}
    errors = []
    
    # Try to get product info from OCR
    try:
        if ocr_text:
            ocr_result = process_ocr(ocr_text)
            product_info.update(ocr_result)
    except Exception as e:
        errors.append(f"Error processing OCR text: {str(e)}")
    
    # Try to get product info from barcode
    try:
        if barcode_data:
            barcode_result = process_barcode(barcode_data)
            # Merge barcode data, giving precedence to it over OCR data
            if barcode_result:
                product_info.update(barcode_result)
    except Exception as e:
        errors.append(f"Error processing barcode: {str(e)}")
    
    # Update state
    state["product_info"] = product_info
    state["errors"].extend(errors)
    
    # Add message about progress
    if product_info.get("product_name"):
        messages.append(AIMessage(content=f"I've identified the product as {product_info['product_name']}"))
    else:
        messages.append(AIMessage(content="I couldn't identify the product from the provided information."))
    
    return state

def categorize_product(state: FoodLensState) -> FoodLensState:
    """
    Categorize the product using Gemini AI
    """
    messages = state["messages"]
    product_info = state["product_info"]
    errors = []
    category = {}
    
    if not product_info.get("product_name"):
        messages.append(AIMessage(content="I need a product name to categorize the product."))
        errors.append("No product name available for categorization")
    else:
        try:
            product_name = product_info["product_name"]
            ingredients = product_info.get("ingredients", [])
            
            category = categorize_product(product_name)
            
            messages.append(AIMessage(
                content=f"The product '{product_name}' is categorized as {category.get('category', 'unknown')}"
            ))
            
        except Exception as e:
            errors.append(f"Error categorizing product: {str(e)}")
            messages.append(AIMessage(content="I encountered an error while trying to categorize the product."))
    
    # Update state
    state["category"] = category
    state["errors"].extend(errors)
    
    return state

def calculate_health_score(state: FoodLensState) -> FoodLensState:
    """
    Calculate health score based on product information and user profile
    """
    messages = state["messages"]
    product_info = state["product_info"]
    user_profile = state["user_profile"]
    category = state["category"]
    errors = []
    health_score_data = {}
    
    if not product_info.get("product_name"):
        messages.append(AIMessage(content="I need a product name to calculate a health score."))
        errors.append("No product name available for health score calculation")
    else:
        try:
            # Gather required inputs
            product_name = product_info["product_name"]
            nutrition = product_info.get("nutrition", {})
            ingredients = product_info.get("ingredients", [])
            product_type = category.get("type", "food")
            health_conditions = user_profile.get("health_conditions", [])
            
            # Calculate health score
            health_score_data = calculate_health_score(nutrition, health_conditions)
            
            score = health_score_data.get("score", 0)
            messages.append(AIMessage(
                content=f"Health Score: {score}/100 - {health_score_data.get('verdict', 'No verdict available')}"
            ))
            
        except Exception as e:
            errors.append(f"Error calculating health score: {str(e)}")
            messages.append(AIMessage(content="I encountered an error while calculating the health score."))
    
    # Update state
    state["health_score"] = health_score_data
    state["errors"].extend(errors)
    
    return state

def find_alternatives(state: FoodLensState) -> FoodLensState:
    """
    Find healthier alternatives for the product
    """
    messages = state["messages"]
    product_info = state["product_info"]
    category = state["category"]
    errors = []
    alternatives = []
    
    if not product_info.get("product_name"):
        messages.append(AIMessage(content="I need a product name to find alternatives."))
        errors.append("No product name available for finding alternatives")
    else:
        try:
            # Gather required inputs
            product_name = product_info["product_name"]
            product_type = category.get("type", "food")
            category_name = category.get("category", "")
            
            # Find alternatives
            alternatives = find_alternatives(product_name, product_type)
            
            if alternatives and len(alternatives) > 0:
                messages.append(AIMessage(
                    content=f"I found {len(alternatives)} healthier alternatives to {product_name}."
                ))
            else:
                messages.append(AIMessage(
                    content=f"I couldn't find specific alternatives for {product_name}."
                ))
            
        except Exception as e:
            errors.append(f"Error finding alternatives: {str(e)}")
            messages.append(AIMessage(content="I encountered an error while searching for alternatives."))
    
    # Update state
    state["alternatives"] = alternatives
    state["errors"].extend(errors)
    
    return state

def verify_claims_and_compliance(state: FoodLensState) -> FoodLensState:
    """
    Verify health claims and FSSAI compliance
    """
    messages = state["messages"]
    product_info = state["product_info"]
    ocr_text = state["ocr_text"]
    user_profile = state["user_profile"]
    errors = []
    claim_verification = {}
    fssai_verification = {}
    
    # Only proceed with verification for premium users
    is_premium = user_profile.get("tier", "") == "premium"
    
    if not is_premium:
        messages.append(AIMessage(
            content="Detailed claim verification and FSSAI compliance check is available for premium users only."
        ))
        return state
    
    if not product_info.get("product_name") or not ocr_text:
        messages.append(AIMessage(
            content="I need both product information and OCR text to verify claims and compliance."
        ))
        errors.append("Insufficient data for claim and compliance verification")
    else:
        # Verify claims
        try:
            claim_verification = verify_claims(ocr_text)
            
            if claim_verification:
                if claim_verification.get("has_misleading_claims", False):
                    messages.append(AIMessage(
                        content="⚠️ This product has potentially misleading health claims on its packaging."
                    ))
                else:
                    messages.append(AIMessage(
                        content="✅ No misleading health claims detected on the packaging."
                    ))
        except Exception as e:
            errors.append(f"Error verifying claims: {str(e)}")
        
        # Verify FSSAI compliance
        try:
            fssai_verification = verify_fssai(ocr_text)
            
            if fssai_verification:
                if fssai_verification.get("is_compliant", False):
                    messages.append(AIMessage(
                        content="✅ This product appears to be FSSAI compliant."
                    ))
                else:
                    messages.append(AIMessage(
                        content="⚠️ This product may not be fully FSSAI compliant."
                    ))
        except Exception as e:
            errors.append(f"Error verifying FSSAI compliance: {str(e)}")
    
    # Update state
    state["claim_verification"] = claim_verification
    state["fssai_verification"] = fssai_verification
    state["errors"].extend(errors)
    
    return state

def should_continue_to_categorize(state: FoodLensState) -> Literal["categorize", "end"]:
    """Determine if we should continue to categorization"""
    if state["product_info"] and state["product_info"].get("product_name"):
        return "categorize"
    else:
        return "end"

def should_continue_to_health_score(state: FoodLensState) -> Literal["calculate_health_score", "end"]:
    """Determine if we should continue to health score calculation"""
    if state["category"] and state["product_info"].get("product_name"):
        return "calculate_health_score"
    else:
        return "end"

def should_continue_to_alternatives(state: FoodLensState) -> Literal["find_alternatives", "end"]:
    """Determine if we should continue to finding alternatives"""
    if state["health_score"] and state["product_info"].get("product_name"):
        return "find_alternatives"
    else:
        return "end"

def should_continue_to_verification(state: FoodLensState) -> Literal["verify_claims", "end"]:
    """Determine if we should continue to verification"""
    user_profile = state["user_profile"]
    is_premium = user_profile.get("tier", "") == "premium"
    
    if is_premium and state["product_info"].get("product_name") and state["ocr_text"]:
        return "verify_claims"
    else:
        return "end"

# Create the graph
def create_foodlens_graph() -> StateGraph:
    """
    Create the LangGraph workflow for FoodLens AI
    """
    workflow = StateGraph(FoodLensState)
    
    # Add nodes
    workflow.add_node("extract_product_info", extract_product_info)
    workflow.add_node("categorize", categorize_product)
    workflow.add_node("calculate_health_score", calculate_health_score)
    workflow.add_node("find_alternatives", find_alternatives)
    workflow.add_node("verify_claims", verify_claims_and_compliance)
    
    # Set entry point
    workflow.set_entry_point("extract_product_info")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "extract_product_info",
        should_continue_to_categorize,
        {
            "categorize": "categorize",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "categorize",
        should_continue_to_health_score,
        {
            "calculate_health_score": "calculate_health_score",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "calculate_health_score",
        should_continue_to_alternatives,
        {
            "find_alternatives": "find_alternatives",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "find_alternatives",
        should_continue_to_verification,
        {
            "verify_claims": "verify_claims",
            "end": END
        }
    )
    
    workflow.add_edge("verify_claims", END)
    
    # Compile the graph
    return workflow.compile()

# Create compiled graph
foodlens_graph = create_foodlens_graph()

def run_foodlens_analysis(
    ocr_text: str,
    barcode_data: str = None,
    user_profile: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Run the FoodLens analysis workflow and return results
    
    Args:
        ocr_text: Text extracted from food product image
        barcode_data: Optional barcode data
        user_profile: Optional user profile information
    
    Returns:
        Dict containing analysis results
    """
    if user_profile is None:
        user_profile = {
            "tier": "free",
            "health_conditions": []
        }
    
    # Initialize state
    initial_state = {
        "messages": [
            SystemMessage(content="""You are FoodLens AI, an assistant that analyzes food products
            and provides health information, alternatives, and regulatory verification.""")
        ],
        "ocr_text": ocr_text,
        "barcode_data": barcode_data,
        "product_info": {},
        "category": {},
        "health_score": {},
        "alternatives": [],
        "claim_verification": {},
        "fssai_verification": {},
        "user_profile": user_profile,
        "errors": []
    }
    
    # Invoke the graph
    final_state = foodlens_graph.invoke(initial_state)
    
    # Construct result
    result = {
        "product_info": final_state["product_info"],
        "category": final_state["category"],
        "health_score": final_state["health_score"],
        "alternatives": final_state["alternatives"],
        "claim_verification": final_state["claim_verification"],
        "fssai_verification": final_state["fssai_verification"],
        "errors": final_state["errors"],
        "messages": [msg.content for msg in final_state["messages"] if isinstance(msg, AIMessage)]
    }
    
    return result