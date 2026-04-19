"""
SBERT Handler for semantic similarity computation
"""
import numpy as np
from django.conf import settings
import logging
import re
from exam_checker.exceptions import SBERTException, ModelLoadException

logger = logging.getLogger(__name__)

# Lazy import for sentence_transformers and torch
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    SBERT_AVAILABLE = True
except ImportError as e:
    SBERT_AVAILABLE = False
    logger.warning(f"SBERT not available (likely due to missing torch for Python 3.14): {str(e)}")
    logger.warning("Similarity scoring will be disabled. Ensure PyTorch is installed for full functionality.")



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
        if not SBERT_AVAILABLE:
            logger.warning("SBERT model initialization skipped: torch/sentence-transformers not available")
            self._model = None
            return
            
        if self._model is None:
            try:
                logger.info(f"Loading SBERT model: {settings.SBERT_MODEL_NAME}")
                self._model = SentenceTransformer(settings.SBERT_MODEL_NAME)
                logger.info("SBERT model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load SBERT model: {str(e)}")
                self._model = None
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
            if not SBERT_AVAILABLE or self._model is None:
                logger.warning("SBERT not available, using lexical fallback similarity")
                return self._lexical_similarity(text1, text2)
            
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

    def _lexical_similarity(self, text1, text2):
        """Fallback similarity based on token overlap when SBERT is unavailable."""
        try:
            def normalize(text):
                text = (text or '').lower()
                text = re.sub(r'[^a-z0-9\s]', ' ', text)
                tokens = [t for t in text.split() if len(t) > 2]
                stopwords = {
                    'the', 'and', 'for', 'with', 'that', 'this', 'are', 'was', 'were',
                    'what', 'does', 'do', 'did', 'from', 'into', 'your', 'you', 'has',
                    'have', 'had', 'can', 'will', 'would', 'could', 'should', 'about',
                    'they', 'them', 'then', 'than', 'there', 'their', 'here', 'when',
                    'where', 'which', 'who', 'whom', 'why', 'how'
                }
                return {t for t in tokens if t not in stopwords}

            tokens1 = normalize(text1)
            tokens2 = normalize(text2)

            if not tokens1 or not tokens2:
                return 0.0

            intersection = len(tokens1 & tokens2)
            union = len(tokens1 | tokens2)
            if union == 0:
                return 0.0

            similarity_score = (intersection / union) * 100
            similarity_score = max(0.0, min(100.0, similarity_score))
            logger.info(f"Lexical fallback similarity score: {similarity_score:.2f}")
            return similarity_score
        except Exception as e:
            logger.error(f"Error computing lexical fallback similarity: {str(e)}")
            return 0.0
    
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
            if not SBERT_AVAILABLE or self._model is None:
                logger.warning("SBERT not available, returning empty embeddings array")
                return np.array([])
            
            if not texts:
                return np.array([])
            
            embeddings = self._model.encode(texts, convert_to_tensor=False)
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise SBERTException(f"Error generating embeddings: {str(e)}")
