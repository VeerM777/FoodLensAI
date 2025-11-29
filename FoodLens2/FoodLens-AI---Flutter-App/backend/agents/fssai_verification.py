"""
FSSAI and company report verification agent
"""
from typing import Dict, Any, List
import re
import requests
from datetime import datetime

class FSSAIVerificationAgent:
    """Agent for verifying product claims against FSSAI database and company reports"""
    
    def __init__(self):
        """Initialize FSSAI verification agent"""
        self.fssai_standards = {
            "packaged_food": {
                "nutrition_label_required": True,
                "ingredients_list_required": True,
                "allergen_declaration": True,
                "net_quantity": True,
                "manufacture_date": True,
                "expiry_date": True,
                "fssai_logo": True,
                "fssai_license": True,
                "consumer_care_details": True
            }
        }
        
        self.common_misleading_claims = [
            "100% natural",
            "chemical free",
            "completely safe",
            "miracle food",
            "instant cure",
            "zero side effects",
            "100% organic"
        ]
        
    def verify_product_claims(self, product_data: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
        """
        Verify product claims against FSSAI standards and detect misleading claims
        """
        result = {
            "fssai_compliance": self.check_fssai_compliance(product_data, ocr_text),
            "claims_verification": self.verify_nutrition_claims(product_data),
            "misleading_claims": self.detect_misleading_claims(product_data, ocr_text),
            "ingredient_validation": self.validate_ingredients(product_data),
            "regulatory_status": self.check_regulatory_status(product_data)
        }
        
        # Calculate overall verification score
        compliance_score = result["fssai_compliance"]["compliance_score"]
        claims_score = result["claims_verification"]["verification_score"]
        misleading_score = 100 - (len(result["misleading_claims"]) * 10)  # Deduct 10 points per misleading claim
        ingredient_score = result["ingredient_validation"]["validation_score"]
        
        result["overall_score"] = (compliance_score + claims_score + max(0, misleading_score) + ingredient_score) / 4
        
        return result
        
    def check_fssai_compliance(self, product_data: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
        """Check FSSAI compliance requirements"""
        compliance_checks = {
            "fssai_license_number": self._extract_fssai_license(ocr_text),
            "nutrition_label_present": bool(product_data.get("nutriments")),
            "ingredients_list_present": bool(product_data.get("ingredients_text")),
            "manufacture_date_present": self._find_date_info(ocr_text, "manufacture"),
            "expiry_date_present": self._find_date_info(ocr_text, "expiry"),
            "allergen_info_present": self._check_allergen_info(product_data, ocr_text)
        }
        
        # Calculate compliance score
        total_checks = len(compliance_checks)
        passed_checks = sum(1 for check in compliance_checks.values() if check)
        compliance_score = (passed_checks / total_checks) * 100
        
        return {
            "checks": compliance_checks,
            "compliance_score": compliance_score,
            "status": "Fully Compliant" if compliance_score == 100 else 
                     "Partially Compliant" if compliance_score >= 70 else 
                     "Non-Compliant"
        }
        
    def verify_nutrition_claims(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify nutrition-related claims"""
        nutriments = product_data.get("nutriments", {})
        claims = []
        
        # Verify common nutrition claims
        if "low_fat" in str(product_data).lower():
            fat_content = nutriments.get("fat_100g", 0)
            claims.append({
                "claim": "Low Fat",
                "verified": fat_content <= 3,
                "actual_value": f"{fat_content}g/100g",
                "standard": "≤ 3g/100g"
            })
            
        if "high_protein" in str(product_data).lower():
            protein_content = nutriments.get("proteins_100g", 0)
            claims.append({
                "claim": "High Protein",
                "verified": protein_content >= 10,
                "actual_value": f"{protein_content}g/100g",
                "standard": "≥ 10g/100g"
            })
            
        if "sugar_free" in str(product_data).lower():
            sugar_content = nutriments.get("sugars_100g", 0)
            claims.append({
                "claim": "Sugar Free",
                "verified": sugar_content <= 0.5,
                "actual_value": f"{sugar_content}g/100g",
                "standard": "≤ 0.5g/100g"
            })
            
        verified_claims = sum(1 for claim in claims if claim["verified"])
        verification_score = (verified_claims / len(claims)) * 100 if claims else 100
        
        return {
            "verified_claims": claims,
            "verification_score": verification_score
        }
        
    def detect_misleading_claims(self, product_data: Dict[str, Any], ocr_text: str) -> List[Dict[str, Any]]:
        """Detect potentially misleading claims"""
        misleading_claims = []
        combined_text = f"{ocr_text} {str(product_data)}".lower()
        
        for claim in self.common_misleading_claims:
            if claim.lower() in combined_text:
                misleading_claims.append({
                    "claim": claim,
                    "reason": "Unsubstantiated or misleading claim according to FSSAI guidelines",
                    "recommendation": "Remove or modify claim to comply with FSSAI regulations"
                })
                
        # Check for specific misleading patterns
        if re.search(r"cure|heal|treat", combined_text):
            misleading_claims.append({
                "claim": "Medical/Therapeutic Claims",
                "reason": "Food products cannot make medical treatment claims",
                "recommendation": "Remove medical claims"
            })
            
        return misleading_claims
        
    def validate_ingredients(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ingredients against FSSAI standards"""
        ingredients = product_data.get("ingredients_text", "").lower()
        validation_results = []
        
        # Check for prohibited ingredients
        prohibited = self._check_prohibited_ingredients(ingredients)
        if prohibited:
            validation_results.extend(prohibited)
            
        # Check for allergen declarations
        allergens = self._check_allergen_declarations(ingredients)
        if allergens:
            validation_results.extend(allergens)
            
        # Calculate validation score
        total_checks = 2  # prohibited ingredients and allergen declarations
        passed_checks = total_checks - len(validation_results)
        validation_score = (passed_checks / total_checks) * 100
        
        return {
            "validation_results": validation_results,
            "validation_score": validation_score,
            "status": "Valid" if validation_score == 100 else "Needs Review"
        }
        
    def check_regulatory_status(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check product's regulatory status"""
        return {
            "status": "Approved",  # Would actually check FSSAI database
            "category": product_data.get("product_type", "Unknown"),
            "applicable_standards": [
                "Food Safety and Standards (Packaging and Labelling) Regulations, 2011",
                "Food Safety and Standards (Food Product Standards and Food Additives) Regulations, 2011"
            ],
            "last_updated": datetime.now().isoformat()
        }
        
    def _extract_fssai_license(self, text: str) -> bool:
        """Extract and validate FSSAI license number"""
        # FSSAI license numbers are usually 14 digits
        fssai_pattern = r"(?i)fssai\s*(?:no|number|#|=|:)?\s*(\d{14})"
        match = re.search(fssai_pattern, text)
        return bool(match)
        
    def _find_date_info(self, text: str, date_type: str) -> bool:
        """Find manufacture or expiry date information"""
        date_patterns = [
            r"(?i)" + date_type + r"\s*(?:date|dt)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(?i)" + date_type + r"\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text):
                return True
        return False
        
    def _check_allergen_info(self, product_data: Dict[str, Any], ocr_text: str) -> bool:
        """Check for allergen information"""
        allergen_indicators = [
            r"(?i)contains allergens",
            r"(?i)allergy information",
            r"(?i)may contain",
            r"(?i)allergen declaration"
        ]
        
        text = f"{ocr_text} {str(product_data)}"
        return any(re.search(pattern, text) for pattern in allergen_indicators)
        
    def _check_prohibited_ingredients(self, ingredients: str) -> List[Dict[str, Any]]:
        """Check for prohibited ingredients"""
        prohibited_ingredients = []
        
        # Example prohibited ingredients (would be expanded based on FSSAI list)
        if "brominated vegetable oil" in ingredients:
            prohibited_ingredients.append({
                "ingredient": "Brominated Vegetable Oil",
                "status": "Prohibited",
                "regulation": "FSSAI Prohibited List 2021"
            })
            
        return prohibited_ingredients
        
    def _check_allergen_declarations(self, ingredients: str) -> List[Dict[str, Any]]:
        """Check allergen declarations"""
        common_allergens = ["milk", "eggs", "fish", "shellfish", "tree nuts", "peanuts", "wheat", "soybeans"]
        missing_declarations = []
        
        for allergen in common_allergens:
            if allergen in ingredients and "allergen" not in ingredients:
                missing_declarations.append({
                    "allergen": allergen,
                    "issue": "Allergen present but not declared in allergen statement",
                    "requirement": "Must be declared in allergen statement"
                })
                
        return missing_declarations

# Create global instance
fssai_agent = FSSAIVerificationAgent()