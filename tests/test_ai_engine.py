"""
Test Cases for AI Engine Components
Location: tests/test_ai_engine.py
"""
from django.test import TestCase
from exam_checker.ai_engine.sbert_handler import SBERTHandler
from exam_checker.ai_engine.preprocessor import TextPreprocessor
from exam_checker.exceptions import SBERTException


class SBERTHandlerTestCase(TestCase):
    """Test SBERT semantic similarity"""
    
    def setUp(self):
        self.sbert = SBERTHandler()
    
    def test_similarity_identical_texts(self):
        """Test similarity score for identical texts"""
        text = "Machine learning is a subset of artificial intelligence"
        similarity = self.sbert.compute_similarity(text, text)
        
        # Should be very close to 100
        self.assertGreater(similarity, 95)
    
    def test_similarity_very_different_texts(self):
        """Test similarity score for very different texts"""
        text1 = "The weather is sunny today"
        text2 = "Machine learning algorithms process data"
        similarity = self.sbert.compute_similarity(text1, text2)
        
        # Should be low
        self.assertLess(similarity, 30)
    
    def test_similarity_similar_semantics(self):
        """Test similarity for semantically similar texts"""
        text1 = "Machine learning learns from data"
        text2 = "Algorithms trained on datasets improve performance"
        similarity = self.sbert.compute_similarity(text1, text2)
        
        # Should be moderately high due to semantic similarity
        self.assertGreater(similarity, 40)
    
    def test_similarity_empty_text(self):
        """Test similarity with empty text"""
        similarity = self.sbert.compute_similarity("", "Some text")
        
        self.assertEqual(similarity, 0.0)
    
    def test_batch_similarity(self):
        """Test batch similarity computation"""
        text_pairs = [
            ("Machine learning", "Machine learning"),
            ("Hello world", "Goodbye world"),
            ("AI is great", "Artificial intelligence is wonderful")
        ]
        
        similarities = self.sbert.batch_compute_similarity(text_pairs)
        
        self.assertEqual(len(similarities), 3)
        self.assertGreater(similarities[0], 95)  # Identical
        self.assertGreater(similarities[1], 0)   # Different
        self.assertGreater(similarities[2], 40)  # Similar


class TextPreprocessorTestCase(TestCase):
    """Test text preprocessing"""
    
    def test_clean_text_lowercasing(self):
        """Test text is lowercased"""
        text = "HELLO WORLD"
        cleaned = TextPreprocessor.clean_text(text)
        
        self.assertEqual(cleaned, "hello world")
    
    def test_clean_text_special_chars(self):
        """Test special character removal"""
        text = "Hello@#$%^&*() World!!!"
        cleaned = TextPreprocessor.clean_text(text)
        
        # Should only have alphanumeric and basic punctuation
        self.assertNotIn('@', cleaned)
        self.assertNotIn('#', cleaned)
    
    def test_clean_text_url_removal(self):
        """Test URL removal"""
        text = "Check this https://example.com for more"
        cleaned = TextPreprocessor.clean_text(text)
        
        self.assertNotIn('https://example.com', cleaned)
    
    def test_clean_text_whitespace_normalization(self):
        """Test excessive whitespace removal"""
        text = "Hello    world    with    extra    spaces"
        cleaned = TextPreprocessor.clean_text(text)
        
        self.assertEqual(cleaned, "hello world with extra spaces")
    
    def test_clean_text_empty_string(self):
        """Test cleaning empty string"""
        cleaned = TextPreprocessor.clean_text("")
        
        self.assertEqual(cleaned, "")
    
    def test_segment_questions_standard_format(self):
        """Test question segmentation with standard format"""
        text = """Q1: What is machine learning?
        Answer: Machine learning is learning from data.
        
        Q2: Name types of ML
        Answer: Supervised and Unsupervised"""
        
        segments = TextPreprocessor.segment_questions(text)
        
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]['question_number'], 1)
        self.assertEqual(segments[1]['question_number'], 2)
    
    def test_segment_questions_no_questions(self):
        """Test segmentation when no questions found"""
        text = "This is just plain text with no questions"
        segments = TextPreprocessor.segment_questions(text)
        
        # Should treat entire text as one question
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]['question_number'], 1)
    
    def test_get_stats(self):
        """Test text statistics generation"""
        text = "This is a test sentence. It has multiple words."
        stats = TextPreprocessor.get_stats(text)
        
        self.assertIn('word_count', stats)
        self.assertIn('char_count', stats)
        self.assertGreater(stats['word_count'], 0)


class HybridScoringTestCase(TestCase):
    """Test hybrid scoring formula"""
    
    def test_hybrid_score_calculation(self):
        """Test hybrid score = (0.6 * SBERT) + (0.4 * GPT)"""
        sbert_score = 80.0
        gpt_score = 90.0
        expected_hybrid = (0.6 * sbert_score) + (0.4 * gpt_score)
        
        self.assertEqual(expected_hybrid, 84.0)
    
    def test_hybrid_score_bounds(self):
        """Test hybrid score stays within 0-100"""
        test_cases = [
            (0, 0, 0),      # Both 0
            (100, 100, 100),  # Both 100
            (50, 100, 70),   # Mixed
        ]
        
        for sbert, gpt, expected in test_cases:
            hybrid = (0.6 * sbert) + (0.4 * gpt)
            self.assertEqual(hybrid, expected)
            self.assertGreaterEqual(hybrid, 0)
            self.assertLessEqual(hybrid, 100)
