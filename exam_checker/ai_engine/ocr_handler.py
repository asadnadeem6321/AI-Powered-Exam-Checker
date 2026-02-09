"""
OCR Handler for extracting text from images
"""
import pytesseract
import cv2
import numpy as np
from PIL import Image
from django.conf import settings
import logging
from exam_checker.exceptions import OCRException

logger = logging.getLogger(__name__)


class OCRHandler:
    """
    Handler for OCR processing using Tesseract
    """
    
    def __init__(self):
        """Initialize OCR handler"""
        try:
            # Set Tesseract command path (for Windows)
            if settings.TESSERACT_CMD:
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            logger.info("OCR handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OCR handler: {str(e)}")
            raise OCRException(f"Failed to initialize OCR handler: {str(e)}")
    
    def preprocess_image(self, image_path):
        """
        Preprocess image for better OCR results
        
        Args:
            image_path (str): Path to the image file
        
        Returns:
            numpy.ndarray: Preprocessed image
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            
            if img is None:
                raise OCRException(f"Failed to load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Apply thresholding (binarization)
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Deskew if needed (optional enhancement)
            # coords = np.column_stack(np.where(thresh > 0))
            # angle = cv2.minAreaRect(coords)[-1]
            # if angle < -45:
            #     angle = -(90 + angle)
            # else:
            #     angle = -angle
            # (h, w) = thresh.shape[:2]
            # center = (w // 2, h // 2)
            # M = cv2.getRotationMatrix2D(center, angle, 1.0)
            # thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            logger.info("Image preprocessing completed")
            return thresh
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise OCRException(f"Error preprocessing image: {str(e)}")
    
    def extract_text(self, image_path, preprocess=True, lang='eng'):
        """
        Extract text from image using OCR
        
        Args:
            image_path (str): Path to the image file
            preprocess (bool): Whether to preprocess the image
            lang (str): Language for OCR (default: 'eng')
        
        Returns:
            dict: Extracted text and confidence score
        """
        try:
            logger.info(f"Starting OCR extraction from: {image_path}")
            
            if preprocess:
                # Use preprocessed image
                processed_img = self.preprocess_image(image_path)
                pil_img = Image.fromarray(processed_img)
            else:
                # Use original image
                pil_img = Image.open(image_path)
            
            # Extract text with confidence data
            ocr_data = pytesseract.image_to_data(pil_img, lang=lang, output_type=pytesseract.Output.DICT)
            
            # Extract text
            text = pytesseract.image_to_string(pil_img, lang=lang)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            logger.info(f"OCR extraction completed. Confidence: {avg_confidence:.2f}%")
            
            if avg_confidence < 50:
                logger.warning(f"Low OCR confidence: {avg_confidence:.2f}%")
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence,
                'word_count': len(text.split())
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise OCRException(f"Error extracting text from image: {str(e)}")
    
    def extract_from_multiple_images(self, image_paths, preprocess=True):
        """
        Extract text from multiple images
        
        Args:
            image_paths (list): List of image file paths
            preprocess (bool): Whether to preprocess images
        
        Returns:
            dict: Combined text and metadata
        """
        try:
            all_text = []
            all_confidences = []
            
            for img_path in image_paths:
                result = self.extract_text(img_path, preprocess=preprocess)
                all_text.append(result['text'])
                all_confidences.append(result['confidence'])
            
            combined_text = '\n\n'.join(all_text)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            
            return {
                'text': combined_text,
                'confidence': avg_confidence,
                'page_count': len(image_paths)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from multiple images: {str(e)}")
            raise OCRException(f"Error extracting text from multiple images: {str(e)}")
