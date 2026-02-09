"""
Text Extractor for various file formats (PDF, TXT, Images)
"""
import os
from PyPDF2 import PdfReader
from PIL import Image
import logging
from exam_checker.exceptions import TextExtractionException
from .ocr_handler import OCRHandler

logger = logging.getLogger(__name__)


class TextExtractor:
    """
    Extract text from various file formats
    """
    
    def __init__(self):
        """Initialize text extractor"""
        self.ocr_handler = OCRHandler()
    
    def extract_from_pdf(self, pdf_path):
        """
        Extract text from PDF file
        
        Args:
            pdf_path (str): Path to PDF file
        
        Returns:
            str: Extracted text
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            reader = PdfReader(pdf_path)
            text = ""
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                logger.info(f"Extracted text from page {page_num}")
            
            if not text.strip():
                logger.warning("No text extracted from PDF, might be scanned. Trying OCR...")
                # PDF might be scanned, try OCR
                # Note: For production, you'd convert PDF to images first
                raise TextExtractionException("PDF appears to be scanned. Please upload as image file for OCR processing.")
            
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise TextExtractionException(f"Error extracting text from PDF: {str(e)}")
    
    def extract_from_txt(self, txt_path):
        """
        Extract text from TXT file
        
        Args:
            txt_path (str): Path to TXT file
        
        Returns:
            str: Extracted text
        """
        try:
            logger.info(f"Reading text file: {txt_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'windows-1252']
            
            for encoding in encodings:
                try:
                    with open(txt_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    logger.info(f"Successfully read file with {encoding} encoding")
                    return text.strip()
                except UnicodeDecodeError:
                    continue
            
            raise TextExtractionException("Failed to read file with any supported encoding")
            
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            raise TextExtractionException(f"Error reading text file: {str(e)}")
    
    def extract_from_image(self, image_path):
        """
        Extract text from image file using OCR
        
        Args:
            image_path (str): Path to image file
        
        Returns:
            dict: Extracted text and metadata
        """
        try:
            logger.info(f"Extracting text from image: {image_path}")
            
            result = self.ocr_handler.extract_text(image_path, preprocess=True)
            
            if result['confidence'] < 50:
                logger.warning(f"Low OCR confidence: {result['confidence']:.2f}%. Results may be inaccurate.")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise TextExtractionException(f"Error extracting text from image: {str(e)}")
    
    def extract(self, file_path):
        """
        Extract text from file based on file extension
        
        Args:
            file_path (str): Path to file
        
        Returns:
            dict: Extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                raise TextExtractionException(f"File not found: {file_path}")
            
            # Get file extension
            file_extension = os.path.splitext(file_path)[1].lower()
            
            logger.info(f"Processing file: {file_path} (type: {file_extension})")
            
            if file_extension == '.pdf':
                text = self.extract_from_pdf(file_path)
                return {
                    'text': text,
                    'method': 'pdf_extraction',
                    'confidence': 100
                }
            
            elif file_extension == '.txt':
                text = self.extract_from_txt(file_path)
                return {
                    'text': text,
                    'method': 'text_file',
                    'confidence': 100
                }
            
            elif file_extension in ['.jpg', '.jpeg', '.png']:
                result = self.extract_from_image(file_path)
                result['method'] = 'ocr'
                return result
            
            else:
                raise TextExtractionException(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise TextExtractionException(f"Error extracting text: {str(e)}")
