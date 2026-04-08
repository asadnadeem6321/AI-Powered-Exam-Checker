"""
Question Extractor - Extracts questions and answers from exam text using Claude API
"""
import anthropic
import json
import time
from django.conf import settings
import logging
from exam_checker.exceptions import GPTException

logger = logging.getLogger(__name__)


class QuestionExtractor:
    """
    Extract questions and answers from exam text using Claude API
    """
    
    def __init__(self):
        """Initialize Claude client"""
        try:
            self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
            self.model = settings.CLAUDE_MODEL
            self.max_tokens = 4000
            logger.info("Question Extractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Question Extractor: {str(e)}")
            raise GPTException(f"Failed to initialize Question Extractor: {str(e)}")
    
    def extract_questions(self, exam_text, max_retries=3):
        """
        Extract questions and answers from exam text
        
        Args:
            exam_text (str): The extracted text from the exam file
            max_retries (int): Maximum number of retry attempts
        
        Returns:
            dict: Dictionary with extracted questions and metadata
        """
        system_prompt = """You are an expert at parsing exam documents and extracting structured question-answer data.
Your task is to extract questions from the provided exam text and structure them properly.

IMPORTANT INSTRUCTIONS:
1. Extract ALL questions found in the document
2. Identify the question text clearly
3. For multiple choice, list all options (A, B, C, D, etc.)
4. If student answers are visible in the document, extract them
5. Number questions sequentially starting from 1
6. Return valid JSON without markdown code blocks

Return JSON with this exact structure:
{
    "total_questions": <number>,
    "questions": [
        {
            "question_number": <1-based number>,
            "question_text": "<full question text>",
            "question_type": "<essay|multiple_choice|short_answer|fill_blank>",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."] or null if not multiple choice,
            "student_answer": "<student answer if visible, or null>",
            "model_answer": "<best possible correct answer for this question; concise but complete>",
            "marks": <marks if specified, or null>
        },
        ...
    ],
    "metadata": {
        "subject": "<subject if identifiable, else 'Unknown'>",
        "total_marks": "<total marks if specified, else null>",
        "has_answers": <true if answers visible, false otherwise>,
        "extraction_notes": "<any relevant notes about the document>"
    }
}"""

        user_prompt = f"""Please extract all questions from the following exam text:

{exam_text}

Return the extracted questions in the specified JSON format."""

        for attempt in range(max_retries):
            try:
                logger.info(f"Sending question extraction request to Claude (attempt {attempt + 1}/{max_retries})")
                logger.debug(f"Exam text length: {len(exam_text)} characters")
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=0.3,  # Lower temperature for more consistent extraction
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                # Parse the response
                result_text = response.content[0].text
                logger.debug(f"Claude response: {result_text[:200]}...")
                
                # Clean up the response if it contains markdown code blocks
                if result_text.startswith("```json"):
                    result_text = result_text.replace("```json", "").replace("```", "").strip()
                elif result_text.startswith("```"):
                    result_text = result_text.replace("```", "").strip()
                
                # Parse JSON
                result = json.loads(result_text)
                
                # Validate structure
                if 'questions' not in result or 'total_questions' not in result:
                    raise ValueError("Invalid response structure - missing required fields")
                
                # Ensure questions have required fields
                for q in result['questions']:
                    q.setdefault('question_number', None)
                    q.setdefault('question_text', '')
                    q.setdefault('question_type', 'essay')
                    q.setdefault('options', None)
                    q.setdefault('student_answer', None)
                    q.setdefault('model_answer', '')
                    q.setdefault('marks', None)
                
                logger.info(f"Successfully extracted {result['total_questions']} questions from exam")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response as JSON (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    raise GPTException(f"Failed to parse Claude response: {str(e)}")
                time.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"Error extracting questions (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    raise GPTException(f"Error extracting questions: {str(e)}")
                time.sleep(2 ** attempt)
        
        raise GPTException("Failed to extract questions after all retries")
    
    def validate_questions(self, questions_data):
        """
        Validate extracted questions structure
        
        Args:
            questions_data (dict): Extracted questions data
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            if not isinstance(questions_data, dict):
                return False, "Questions data must be a dictionary"
            
            if 'questions' not in questions_data:
                return False, "Missing 'questions' field"
            
            if not isinstance(questions_data['questions'], list):
                return False, "'questions' must be a list"
            
            if len(questions_data['questions']) == 0:
                return False, "No questions found in extracted data"
            
            # Validate each question
            for idx, q in enumerate(questions_data['questions']):
                if not isinstance(q, dict):
                    return False, f"Question {idx + 1} is not a dictionary"
                
                if 'question_text' not in q or not q['question_text'].strip():
                    return False, f"Question {idx + 1} has empty text"
                
                if 'question_type' not in q:
                    return False, f"Question {idx + 1} missing question_type"
            
            return True, ""
        
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"
