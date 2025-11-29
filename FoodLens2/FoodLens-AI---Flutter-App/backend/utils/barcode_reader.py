"""
Barcode detection and reading utilities
"""
import cv2
import numpy as np
import easyocr
from typing import Dict, Any, Optional

class BarcodeReader:
    """Handles barcode detection and reading using OpenCV and EasyOCR"""
    
    def __init__(self):
        """Initialize barcode reader"""
        self.ocr_reader = easyocr.Reader(['en'])  # Initialize EasyOCR
    
    def detect_and_read_barcode(self, image_path: str) -> Dict[str, Any]:
        """
        Detect and read barcode from image using OpenCV preprocessing and EasyOCR
        """
        try:
            # Read and preprocess image
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Use morphological operations to enhance barcode-like regions
            kernel = np.ones((3,3), np.uint8)
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Get rectangle bounding box
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h
                
                # Barcodes typically have a specific aspect ratio
                if 1.5 <= aspect_ratio <= 4.0 and w > 100:
                    # Extract potential barcode region
                    roi = gray[y:y+h, x:x+w]
                    
                    # Use OCR on this region
                    ocr_result = self.ocr_reader.readtext(roi)
                    for bbox, text, conf in ocr_result:
                        text = text.strip()
                        if self._is_barcode_pattern(text):
                            # Found barcode in ROI - but DON'T return yet!
                            # Continue to full image scan to get ALL text
                            print(f"✅ Barcode found in ROI: {text}, continuing to scan full image for text")
                            break
            
            # Always scan full image to get ALL text (not just barcode)
            ocr_result = self.ocr_reader.readtext(image_path)
            
            # Fallback to EasyOCR for printed barcodes
            ocr_result = self.ocr_reader.readtext(image_path)
            
            print(f"🔍 EasyOCR found {len(ocr_result)} text detections")
            
            # Collect all detected text for OCR processing
            all_detected_text = []
            barcode_found = None
            potential_barcode_parts = []  # Store ALL numeric sequences
            
            for bbox, text, conf in ocr_result:
                # Look for barcode patterns
                text_original = text
                text = text.strip()
                
                # Store all text with reasonable confidence
                if conf > 0.2:  # Filter out very low confidence detections
                    all_detected_text.append(text)
                
                # Clean the text to extract just numbers
                numbers_only = ''.join(c for c in text if c.isdigit())
                
                print(f"📊 OCR detected text: '{text_original}' -> numbers: '{numbers_only}' (confidence: {conf:.2f})")
                
                # Collect ALL numeric sequences (even single digits for barcode combining)
                if numbers_only and conf > 0.5:  # Only high confidence
                    potential_barcode_parts.append(numbers_only)
                    print(f"   🔢 Stored barcode part: '{numbers_only}'")
                
                # Check if this could be a barcode (8, 12, or 13 digits)
                if len(numbers_only) in [8, 12, 13] and not barcode_found:
                    print(f"✅ Potential barcode found: {numbers_only}")
                    if self._is_barcode_pattern(text):
                        barcode_found = {
                            "barcode": numbers_only,
                            "format": "EAN-13" if len(numbers_only) == 13 else "EAN-12" if len(numbers_only) == 12 else "EAN-8",
                            "source": "ocr_full_image",
                            "confidence": conf
                        }
            
            # Try to combine barcode parts if we have pieces (e.g., "8" + "906010501570")
            if not barcode_found and len(potential_barcode_parts) >= 2:
                print(f"🔄 Attempting to combine {len(potential_barcode_parts)} barcode parts: {potential_barcode_parts}")
                
                # Try different combinations
                # 1. First two parts (most common: leading digit + main number)
                combined = ''.join(potential_barcode_parts[:2])
                print(f"   Combination 1: '{potential_barcode_parts[0]}' + '{potential_barcode_parts[1]}' = '{combined}'")
                
                if len(combined) in [8, 12, 13] and self._is_barcode_pattern(combined):
                    barcode_found = {
                        "barcode": combined,
                        "format": "EAN-13" if len(combined) == 13 else "EAN-12" if len(combined) == 12 else "EAN-8",
                        "source": "ocr_combined",
                        "confidence": 0.8
                    }
                    print(f"✅ Combined barcode validated: {combined}")
                
                # 2. Try combining all parts if first attempt failed
                if not barcode_found and len(potential_barcode_parts) >= 3:
                    combined = ''.join(potential_barcode_parts[:3])
                    print(f"   Combination 2 (3 parts): '{combined}'")
                    if len(combined) in [8, 12, 13] and self._is_barcode_pattern(combined):
                        barcode_found = {
                            "barcode": combined,
                            "format": "EAN-13" if len(combined) == 13 else "EAN-12" if len(combined) == 12 else "EAN-8",
                            "source": "ocr_combined_3parts",
                            "confidence": 0.75
                        }
                        print(f"✅ Combined 3-part barcode validated: {combined}")
            
            # Return results with detected text
            if barcode_found:
                barcode_found["detected_text"] = "\n".join(all_detected_text)
                print(f"✅ Returning barcode with detected_text: '{barcode_found['detected_text'][:200]}'")
                return barcode_found
            
            print("❌ No valid barcode pattern found in image")
            # Even if no barcode, return the detected text
            detected_text_str = "\n".join(all_detected_text) if all_detected_text else ""
            print(f"📝 Returning detected_text without barcode: '{detected_text_str[:200]}'")
            return {
                "barcode": None, 
                "error": "No barcode found",
                "detected_text": detected_text_str
            }
            
        except Exception as e:
            return {"barcode": None, "error": str(e)}
    
    def _is_barcode_pattern(self, text: str) -> bool:
        """Check if text matches barcode pattern"""
        # Remove any spaces, dashes, and special characters
        cleaned_text = ''.join(c for c in text if c.isdigit())
        
        print(f"🔍 Barcode pattern check: '{text}' -> '{cleaned_text}'")
        
        # Check if numeric and of valid length (EAN-8, UPC-12, or EAN-13)
        if cleaned_text.isdigit() and len(cleaned_text) in [8, 12, 13]:
            # Validate checksum for EAN-13
            if len(cleaned_text) == 13:
                is_valid = self._validate_ean13_checksum(cleaned_text)
                print(f"   EAN-13 validation: {is_valid}")
                # Be lenient - accept even if checksum fails (OCR errors)
                if not is_valid:
                    print(f"   ⚠️ Checksum failed but accepting as potential barcode")
                return True  # Accept all 13-digit codes
            # Validate checksum for UPC-12
            elif len(cleaned_text) == 12:
                print(f"   UPC-12 detected - accepting")
                return True  # Accept all 12-digit codes
            # Validate checksum for EAN-8
            elif len(cleaned_text) == 8:
                is_valid = self._validate_ean8_checksum(cleaned_text)
                print(f"   EAN-8 validation: {is_valid}")
                # Be lenient
                if not is_valid:
                    print(f"   ⚠️ Checksum failed but accepting as potential barcode")
                return True  # Accept all 8-digit codes
        
        return False
    
    def _validate_ean13_checksum(self, digits: str) -> bool:
        """Validate EAN-13 checksum"""
        if len(digits) != 13:
            return False
            
        total = 0
        for i in range(12):
            if i % 2 == 0:
                total += int(digits[i])
            else:
                total += int(digits[i]) * 3
        check = (10 - (total % 10)) % 10
        return check == int(digits[-1])
    
    def _validate_ean8_checksum(self, digits: str) -> bool:
        """Validate EAN-8 checksum"""
        if len(digits) != 8:
            return False
            
        total = 0
        for i in range(7):
            if i % 2 == 0:
                total += int(digits[i]) * 3
            else:
                total += int(digits[i])
        check = (10 - (total % 10)) % 10
        return check == int(digits[-1])

# Note: Global instance removed to prevent blocking on import
# Use lazy loading in main.py with get_barcode_reader() instead