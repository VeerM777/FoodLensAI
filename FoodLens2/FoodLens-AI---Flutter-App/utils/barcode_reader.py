"""
Barcode detection and reading utilities
"""
import cv2
import numpy as np
import easyocr
from pyzbar import pyzbar
from typing import Dict, Any, Optional

class BarcodeReader:
    """Handles barcode detection and reading using pyzbar (ZBar - retail-grade), Groq OCR, and EasyOCR"""
    
    def __init__(self):
        """Initialize barcode reader"""
        self.ocr_reader = easyocr.Reader(['en'])  # Initialize EasyOCR as fallback
        print("✅ BarcodeReader initialized with pyzbar (hardware-grade) + EasyOCR fallback")
    
    def detect_and_read_barcode(self, image_path: str) -> Dict[str, Any]:
        """
        Detect and read barcode using:
        1. pyzbar (ZBar) - hardware-grade retail scanner
        2. EasyOCR (fallback for damaged/unclear barcodes)
        """
        try:
            # Read and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                return {"barcode": None, "error": "Could not read image file"}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # ═══════════════════════════════════════════════════════════
            # METHOD 1: pyzbar (ZBar) - HARDWARE-GRADE RETAIL SCANNER
            # ═══════════════════════════════════════════════════════════
            print("🔍 [METHOD 1] Trying pyzbar (ZBar) hardware-grade barcode scanner...")
            try:
                # pyzbar can detect multiple barcode types: EAN13, EAN8, UPC-A, UPC-E, Code128, etc.
                detected_barcodes = pyzbar.decode(image)
                
                if detected_barcodes:
                    for barcode in detected_barcodes:
                        barcode_data = barcode.data.decode('utf-8')
                        barcode_type = barcode.type
                        print(f"✅ [pyzbar] Found {barcode_type} barcode: {barcode_data}")
                        
                        # Validate length
                        if len(barcode_data) in [8, 12, 13]:
                            # Now get product text from OCR (separate from barcode)
                            print(f"🔍 [pyzbar] Barcode validated, now extracting product text with EasyOCR...")
                            
                            # Get product text using EasyOCR (but exclude the barcode area)
                            ocr_result = self.ocr_reader.readtext(image_path)
                            all_product_text = []
                            
                            for bbox, text, conf in ocr_result:
                                text = text.strip()
                                # Only include text with letters (product names) and exclude barcode numbers
                                if any(c.isalpha() for c in text) and conf > 0.4:
                                    # Skip if text is just the barcode
                                    if text.replace(' ', '').replace('-', '') != barcode_data:
                                        all_product_text.append(text)
                            
                            product_text_str = "\n".join(all_product_text) if all_product_text else ""
                            
                            print(f"✅ [pyzbar SUCCESS] Barcode: {barcode_data}, Product text: '{product_text_str[:100]}'")
                            return {
                                "barcode": barcode_data,
                                "format": barcode_type,
                                "source": "pyzbar_hardware_scan",
                                "confidence": 0.95,
                                "product_text": product_text_str,
                                "detected_text": product_text_str
                            }
                
                print("⚠️ [pyzbar] No barcode detected, falling back to OCR methods...")
            except Exception as e:
                print(f"⚠️ [pyzbar] Scan failed: {e}, falling back to OCR...")
            
            # ═══════════════════════════════════════════════════════════
            # METHOD 2: EasyOCR - FALLBACK FOR DAMAGED BARCODES
            # ═══════════════════════════════════════════════════════════
            print("🔍 [METHOD 2] Trying EasyOCR fallback for damaged/unclear barcodes...")
            
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
            
            # Always scan full image to get ALL text (not just barcode)
            ocr_result = self.ocr_reader.readtext(image_path)
            
            print(f"🔍 EasyOCR found {len(ocr_result)} text detections")
            
            # Collect all detected text for OCR processing
            all_detected_text = []
            all_product_text = []  # Separate list for product names
            barcode_found = None
            potential_barcode_parts = []  # Store ALL numeric sequences
            
            for bbox, text, conf in ocr_result:
                # Look for barcode patterns
                text_original = text
                text = text.strip()
                
                # Store all text with reasonable confidence
                if conf > 0.2:  # Filter out very low confidence detections
                    all_detected_text.append(text)
                    
                    # Separate product text from numeric barcodes
                    # Product names typically have letters
                    if any(c.isalpha() for c in text) and conf > 0.5:
                        all_product_text.append(text)
                
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

                # Try joining contiguous sequences of parts (preserve detected order)
                n = len(potential_barcode_parts)
                for start in range(0, n):
                    for end in range(start+1, min(n, start+4)+1):
                        combined = ''.join(potential_barcode_parts[start:end])
                        if len(combined) in [8, 12, 13] and self._is_barcode_pattern(combined):
                            barcode_found = {
                                "barcode": combined,
                                "format": "EAN-13" if len(combined) == 13 else "EAN-12" if len(combined) == 12 else "EAN-8",
                                "source": "ocr_combined_range",
                                "confidence": 0.85
                            }
                            print(f"✅ Combined contiguous parts validated: {combined} (parts {start}:{end})")
                            break
                    if barcode_found:
                        break

                # If still not found, try prepending earlier short parts to a long core part
                if not barcode_found:
                    # Look for a core part that looks like main body (>=6 digits)
                    for i, core in enumerate(potential_barcode_parts):
                        if len(core) >= 6 and core.isdigit():
                            # Try prefixes made of up to 3 earlier parts (in order)
                            for pref_len in range(1, min(4, i+1)+1):
                                prefix = ''.join(potential_barcode_parts[i-pref_len:i])
                                combined = prefix + core
                                if len(combined) in [8, 12, 13] and self._is_barcode_pattern(combined):
                                    barcode_found = {
                                        "barcode": combined,
                                        "format": "EAN-13" if len(combined) == 13 else "EAN-12" if len(combined) == 12 else "EAN-8",
                                        "source": f"ocr_prefixed_{pref_len}",
                                        "confidence": 0.78
                                    }
                                    print(f"✅ Prefixed combination validated: prefix({i-pref_len}:{i}) + core({i}) -> {combined}")
                                    break
                            if barcode_found:
                                break

                # Final attempt: try all small permutations for up to 4 parts (limited search)
                if not barcode_found and n <= 6:
                    from itertools import permutations
                    for r in range(2, min(5, n+1)):
                        for perm in permutations(potential_barcode_parts, r):
                            combined = ''.join(perm)
                            if len(combined) in [8, 12, 13] and self._is_barcode_pattern(combined):
                                barcode_found = {
                                    "barcode": combined,
                                    "format": "EAN-13" if len(combined) == 13 else "EAN-12" if len(combined) == 12 else "EAN-8",
                                    "source": "ocr_permutation",
                                    "confidence": 0.7
                                }
                                print(f"✅ Permutation-based barcode validated: {combined}")
                                break
                        if barcode_found:
                            break
            
            # Return results with detected text
            if barcode_found:
                # Return product text separately from barcode
                product_text_str = "\\n".join(all_product_text) if all_product_text else ""
                barcode_found["product_text"] = product_text_str
                barcode_found["detected_text"] = "\\n".join(all_detected_text)
                print(f"✅ Returning barcode: {barcode_found['barcode']}")
                print(f"📝 Product text (non-barcode): '{product_text_str[:100]}'")
                return barcode_found
            
            print("❌ No valid barcode pattern found in image")
            # Even if no barcode, return the detected text
            detected_text_str = "\n".join(all_detected_text) if all_detected_text else ""
            product_text_str = "\n".join(all_product_text) if all_product_text else ""

            # If product text is short or missing, try a central crop OCR pass to capture the packaging title
            try:
                if not product_text_str or len(product_text_str) < 6:
                    h, w = gray.shape[:2]
                    # Crop the central horizontal band where product title usually appears
                    top = int(h * 0.30)
                    bottom = int(h * 0.70)
                    left = int(w * 0.05)
                    right = int(w * 0.95)
                    center_roi = image[top:bottom, left:right]
                    print(f"🔎 Performing center-crop OCR on region: top={top}, bottom={bottom}, left={left}, right={right}")
                    center_results = self.ocr_reader.readtext(center_roi)
                    center_texts = [t.strip() for bbox, t, c in center_results if c > 0.2 and any(ch.isalpha() for ch in t)]
                    if center_texts:
                        center_joined = "\n".join(center_texts)
                        print(f"✅ Center crop OCR found product text: '{center_joined[:120]}'")
                        # Prefer center crop result if it's longer than previous
                        if len(center_joined) > len(product_text_str):
                            product_text_str = center_joined
            except Exception as e:
                print(f"⚠️ Center crop OCR failed: {e}")

            print(f"📝 Returning text without barcode - Product text: '{product_text_str[:200]}'")
            return {
                "barcode": None,
                "error": "No barcode found",
                "product_text": product_text_str,
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