"""
Question-Answer Segmentation Module
Handles proper segmentation of questions and answers with academic grading support
"""
import logging
import re
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class QuestionAnswerSegmenter:
    """
    Segments exam documents into question-answer pairs.
    Handles different document structures and question formats.
    """
    
    def __init__(self):
        """Initialize segmenter"""
        logger.info("QuestionAnswerSegmenter initialized")
    
    def segment_questions_and_answers(self, questions_data: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Process extracted questions and properly segment them with marks calculation
        
        Args:
            questions_data (List[Dict]): List of question objects from Claude extraction
            
        Returns:
            Tuple[List[Dict], Dict]: Segmented questions with marks and metadata
        """
        try:
            total_marks = questions_data.get('metadata', {}).get('total_marks')
            questions = questions_data.get('questions', [])
            
            # Calculate marks per question
            segmented_questions = []
            marks_per_question = self._calculate_marks_distribution(
                total_marks=total_marks,
                num_questions=len(questions)
            )
            
            for idx, question in enumerate(questions):
                segmented_q = {
                    'question_number': question.get('question_number', idx + 1),
                    'question_text': question.get('question_text', ''),
                    'question_type': question.get('question_type', 'short_answer'),
                    'options': question.get('options'),
                    'student_answer': question.get('student_answer'),
                    'model_answer': question.get('model_answer', ''),
                    'marks': marks_per_question[idx] if marks_per_question else None
                }
                segmented_questions.append(segmented_q)
            
            metadata = {
                'total_questions': len(questions),
                'total_marks': total_marks,
                'marks_distribution': marks_per_question,
                'subject': questions_data.get('metadata', {}).get('subject'),
                'has_answers': questions_data.get('metadata', {}).get('has_answers', False),
                'extraction_notes': questions_data.get('metadata', {}).get('extraction_notes', '')
            }
            
            logger.info(f"Segmented {len(questions)} questions with marks allocation")
            return segmented_questions, metadata
            
        except Exception as e:
            logger.error(f"Error in question segmentation: {str(e)}")
            raise
    
    def _calculate_marks_distribution(self, total_marks: int = None, num_questions: int = 1) -> List[int]:
        """
        Calculate marks per question using equal distribution or proportional weighting
        
        Args:
            total_marks (int): Total marks for exam
            num_questions (int): Number of questions
            
        Returns:
            List[int]: Marks allocated to each question
        """
        if not total_marks or num_questions == 0:
            logger.warning(f"Cannot calculate marks: total_marks={total_marks}, num_questions={num_questions}")
            return [None] * num_questions
        
        try:
            # Equal distribution approach
            base_marks = total_marks // num_questions
            remainder = total_marks % num_questions
            
            marks_distribution = [base_marks] * num_questions
            
            # Distribute remainder marks to first questions
            for i in range(remainder):
                marks_distribution[i] += 1
            
            logger.debug(f"Marks distribution: {marks_distribution}")
            return marks_distribution
            
        except Exception as e:
            logger.error(f"Error calculating marks distribution: {str(e)}")
            return [None] * num_questions
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text according to specification:
        - Lowercase
        - Remove special characters
        - Remove noise
        - Normalize spacing
        
        Args:
            text (str): Raw text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        try:
            # Lowercase
            text = text.lower()
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove leading/trailing whitespace
            text = text.strip()
            
            # Preserve alphanumeric, basic punctuation (period, question mark), and spaces
            # Remove special characters but keep common punctuation
            text = re.sub(r'[^a-z0-9\s.,?!]', '', text)
            
            logger.debug(f"Preprocessed text length: {len(text)}")
            return text
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            return text
    
    def validate_qa_pairs(self, questions: List[Dict]) -> Tuple[bool, str]:
        """
        Validate quality of Q/A segmentation
        
        Args:
            questions (List[Dict]): List of question objects
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            if not questions:
                return False, "No questions found"
            
            for idx, q in enumerate(questions, 1):
                if not q.get('question_text', '').strip():
                    return False, f"Question {idx}: Empty question text"
                
                if not q.get('model_answer', '').strip():
                    return False, f"Question {idx}: Empty model answer"
                
                if not q.get('student_answer', '').strip():
                    return False, f"Question {idx}: Empty student answer"
            
            return True, "All Q/A pairs valid"
            
        except Exception as e:
            logger.error(f"Error validating Q/A pairs: {str(e)}")
            return False, f"Validation error: {str(e)}"
