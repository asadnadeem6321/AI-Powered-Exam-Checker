"""
Text Preprocessing Utilities
"""
import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    Preprocess text for evaluation
    """
    
    @staticmethod
    def clean_text(text):
        """
        Clean and normalize text
        
        Args:
            text (str): Raw text
        
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-z0-9\s.,!?;:\-\'\"()]', ' ', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    @staticmethod
    def segment_questions(text):
        """
        Segment text into question-answer pairs
        
        Args:
            text (str): Full text containing multiple Q&A
        
        Returns:
            list: List of dict with question_number, question_text, answer
        """
        try:
            # Pattern to match questions: Q1, Q.1, Question 1, etc.
            pattern = r'(?:Q|Question)\s*[.:]?\s*(\d+)\s*[.:]?\s*(.*?)(?=(?:Q|Question)\s*[.:]?\s*\d+|$)'
            
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            
            questions = []
            for match in matches:
                q_num = int(match.group(1))
                content = match.group(2).strip()
                
                # Try to split question and answer
                # Look for patterns like "Answer:", "A:", "Ans:", etc.
                answer_pattern = r'(?:Answer|Ans|A)\s*[.:]?\s*(.*)'
                answer_match = re.search(answer_pattern, content, re.DOTALL | re.IGNORECASE)
                
                if answer_match:
                    # Split into question and answer
                    question_text = content[:answer_match.start()].strip()
                    answer_text = answer_match.group(1).strip()
                else:
                    # Assume first sentence is question, rest is answer
                    parts = content.split('\n', 1)
                    question_text = parts[0].strip() if parts else content
                    answer_text = parts[1].strip() if len(parts) > 1 else content
                
                questions.append({
                    'question_number': q_num,
                    'question_text': question_text,
                    'answer': answer_text
                })
            
            # If no questions found, treat entire text as one answer
            if not questions:
                questions = [{
                    'question_number': 1,
                    'question_text': '',
                    'answer': text
                }]
            
            logger.info(f"Segmented text into {len(questions)} question(s)")
            return questions
            
        except Exception as e:
            logger.error(f"Error segmenting questions: {str(e)}")
            # Return entire text as single question
            return [{
                'question_number': 1,
                'question_text': '',
                'answer': text
            }]
    
    @staticmethod
    def remove_stopwords(text, stopwords=None):
        """
        Remove stopwords from text (optional preprocessing)
        
        Args:
            text (str): Input text
            stopwords (set): Set of stopwords to remove
        
        Returns:
            str: Text with stopwords removed
        """
        if not stopwords:
            # Basic English stopwords
            stopwords = {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with'
            }
        
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in stopwords]
        
        return ' '.join(filtered_words)
    
    @staticmethod
    def tokenize_sentences(text):
        """
        Split text into sentences
        
        Args:
            text (str): Input text
        
        Returns:
            list: List of sentences
        """
        # Simple sentence tokenization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    @staticmethod
    def get_word_count(text):
        """
        Get word count of text
        
        Args:
            text (str): Input text
        
        Returns:
            int: Word count
        """
        return len(text.split())
    
    @staticmethod
    def get_stats(text):
        """
        Get text statistics
        
        Args:
            text (str): Input text
        
        Returns:
            dict: Text statistics
        """
        sentences = TextPreprocessor.tokenize_sentences(text)
        words = text.split()
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }
