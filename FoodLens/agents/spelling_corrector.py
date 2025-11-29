"""
Spelling correction agent for OCR text
Uses AI to fix common OCR errors in product names and brands
"""
import os
from groq import Groq

class SpellingCorrectorAgent:
    """AI-powered spelling correction for OCR text"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def correct_text(self, text: str, context: str = "food product") -> str:
        """
        Correct spelling errors in text using AI
        
        Args:
            text: The text to correct (brand name, product name, etc.)
            context: Context hint (e.g., "food product", "brand name")
        
        Returns:
            Corrected text
        """
        if not text or len(text.strip()) < 2:
            return text
        
        try:
            prompt = f"""You are a spelling correction expert for Indian food products.

INPUT TEXT: "{text}"
CONTEXT: {context}

TASK: Fix OCR spelling errors in the text above.

COMMON OCR ERRORS TO FIX:
• EVBREST → EVEREST (B confused with E)
• AMIJL → AMUL (J confused with U)
• PARLL → PARLE (L confused with E)
• HAIIDIRAM → HALDIRAM (I confused with L)
• MAGCJI → MAGGI (C confused with G)
• BISCUTT → BISCUIT (double T)
• CHOCOIATE → CHOCOLATE (I confused with L)
• MASAIA → MASALA (I confused with L)
• 0 (zero) → O (letter O)
• 1 (one) → I (letter I)

RULES:
1. Only fix clear spelling mistakes
2. Keep brand capitalization (EVEREST, Amul, etc.)
3. If text looks correct, return it unchanged
4. Don't add or remove words
5. Focus on well-known Indian food brands

RETURN ONLY THE CORRECTED TEXT, nothing else.

Examples:
Input: "EVBREST" → Output: "EVEREST"
Input: "Pav Bhaji" → Output: "Pav Bhaji"
Input: "Amul" → Output: "Amul"
Input: "MASAIA" → Output: "MASALA"

Corrected text:"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast and accurate model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100,
            )
            
            if response and response.choices:
                corrected = response.choices[0].message.content.strip()
                # Remove any quotes or extra formatting
                corrected = corrected.strip('"\'').strip()
                
                if corrected and corrected != text:
                    print(f"✅ Spelling corrected: '{text}' → '{corrected}'")
                    return corrected
                else:
                    return text
            else:
                return text
                
        except Exception as e:
            print(f"⚠️ Spelling correction failed: {e}")
            return text
    
    def correct_product_info(self, brand: str, product: str, variant: str = None) -> dict:
        """
        Correct spelling in brand, product, and variant fields
        
        Returns:
            Dictionary with corrected fields
        """
        result = {
            "brand": self.correct_text(brand, "brand name") if brand else "",
            "product": self.correct_text(product, "product name") if product else "",
            "variant": self.correct_text(variant, "product variant") if variant else ""
        }
        
        return result

# Global instance
spelling_corrector = SpellingCorrectorAgent()
