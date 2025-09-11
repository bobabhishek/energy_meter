import cv2
import pytesseract
import numpy as np
from datetime import datetime
import random
import os
import re


class MeterReader:
    def __init__(self):
        # Configure pytesseract path via environment variable with Windows-friendly fallback
        tesseract_cmd = os.environ.get('TESSERACT_CMD')
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            default_windows_path = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
            if os.path.exists(default_windows_path):
                pytesseract.pytesseract.tesseract_cmd = default_windows_path

    def preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE to improve contrast (helps on dim displays)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Adaptive thresholding (more robust to lighting)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 31, 10)

        # Noise removal using median blur and slight dilation to close gaps
        denoised = cv2.medianBlur(thresh, 3)
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.dilate(denoised, kernel, iterations=1)

        return processed

    def extract_reading(self, image_path):
        """Extract meter reading from image"""
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not read image")

        # Preprocess image
        processed = self.preprocess_image(image)

        # Perform OCR with multiple strategies
        ocr_configs = [
            '--psm 7 -c tessedit_char_whitelist=0123456789.',
            '--psm 6 -c tessedit_char_whitelist=0123456789.',
            '--psm 8 -c tessedit_char_whitelist=0123456789.'
        ]

        texts = []
        for cfg in ocr_configs:
            try:
                texts.append(pytesseract.image_to_string(processed, config=cfg))
            except Exception:
                continue
        text = max(texts, key=lambda s: len(s.strip())) if texts else ''

        # Clean and validate the reading
        reading = self._clean_reading(text)

        return reading

    def _clean_reading(self, text):
        """Clean OCR output and extract numerical reading"""
        if not text:
            raise ValueError("No OCR text extracted")

        # Normalize common OCR mistakes
        normalized = text.replace('O', '0').replace('o', '0').replace('S', '5').replace(',', '.')

        # Find the first plausible decimal or integer number
        match = re.search(r'(\d+\.\d+|\d+)', normalized)
        if not match:
            # As a fallback, strip to digits and assume 2 decimals if length > 2
            digits_only = ''.join(ch for ch in normalized if ch.isdigit())
            if not digits_only:
                raise ValueError("No numerical reading found")
            if len(digits_only) > 2:
                return float(digits_only) / 100.0
            return float(digits_only)

        return float(match.group(0))

    def generate_metadata(self):
        """Generate timestamp and simulated geolocation"""
        return {
            'timestamp': datetime.now().isoformat(),
            'latitude': round(random.uniform(12.8, 13.2), 6),  # Simulated coordinates
            'longitude': round(random.uniform(77.5, 77.7), 6)  # for Bangalore region
        }


