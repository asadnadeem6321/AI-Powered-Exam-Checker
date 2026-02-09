"""
SBERT Handler for semantic similarity computation
"""
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from django.conf import settings
import logging
from exam_checker.exceptions import SBERTException, ModelLoadException

logger = logging.getLogger(__name__)


class SBERTHandler:
    """
    Handler for Sentence-BERT model to compute semantic similarity
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times"""
        if cls._instance is None:
            cls._instance = super(SBERTHandler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize SBERT model"""
        if self._model is None:
            try:
                logger.info(f"Loading SBERT model: {settings.SBERT_MODEL_NAME}")
                self._model = SentenceTransformer(settings.SBERT_MODEL_NAME)
                logger.info("SBERT model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load SBERT model: {str(e)}")
                raise ModelLoadException(f"Failed to load SBERT model: {str(e)}")
    
    def compute_similarity(self, text1, text2):
        """
        Compute semantic similarity between two texts
        
        Args:
            text1 (str): First text (student answer)
            text2 (str): Second text (model answer)
        
        Returns:
            float: Similarity score between 0 and 100
        """
        try:
            if not text1 or not text2:
                logger.warning("Empty text provided for similarity computation")
                return 0.0
            
            # Encode both texts
            embedding1 = self._model.encode(text1, convert_to_tensor=True)
            embedding2 = self._model.encode(text2, convert_to_tensor=True)
            
            # Compute cosine similarity
            similarity = util.cos_sim(embedding1, embedding2)
            
            # Convert to percentage (0-100)
            similarity_score = float(similarity.item()) * 100
            
            # Ensure score is between 0 and 100
            similarity_score = max(0.0, min(100.0, similarity_score))
            
            logger.info(f"Computed similarity score: {similarity_score:.2f}")
            
            return similarity_score
            
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise SBERTException(f"Error computing similarity: {str(e)}")
    
    def batch_compute_similarity(self, text_pairs):
        """
        Compute similarity for multiple text pairs
        
        Args:
            text_pairs (list): List of tuples [(text1, text2), ...]
        
        Returns:
            list: List of similarity scores
        """
        try:
            similarities = []
            for text1, text2 in text_pairs:
                similarity = self.compute_similarity(text1, text2)
                similarities.append(similarity)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error in batch similarity computation: {str(e)}")
            raise SBERTException(f"Error in batch similarity computation: {str(e)}")
    
    def get_embeddings(self, texts):
        """
        Get embeddings for a list of texts
        
        Args:
            texts (list): List of text strings
        
        Returns:
            numpy.ndarray: Array of embeddings
        """
        try:
            if not texts:
                return np.array([])
            
            embeddings = self._model.encode(texts, convert_to_tensor=False)
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise SBERTException(f"Error generating embeddings: {str(e)}")
