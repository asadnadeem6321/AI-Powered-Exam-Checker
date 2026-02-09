"""
GPT Handler for contextual evaluation using OpenAI API
"""
from openai import OpenAI
from django.conf import settings
import logging
import json
import time
from exam_checker.exceptions import GPTException

logger = logging.getLogger(__name__)


class GPTHandler:
    """
    Handler for GPT API to perform contextual evaluation
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.GPT_MODEL
            self.max_tokens = settings.GPT_MAX_TOKENS
            self.temperature = settings.GPT_TEMPERATURE
            logger.info("GPT client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GPT client: {str(e)}")
            raise GPTException(f"Failed to initialize GPT client: {str(e)}")
    
    def evaluate_answer(self, student_answer, model_answer, question_text="", max_retries=3):
        """
        Evaluate a student answer using GPT
        
        Args:
            student_answer (str): Student's answer
            model_answer (str): Expected/model answer
            question_text (str): The question (optional)
            max_retries (int): Maximum number of retry attempts
        
        Returns:
            dict: Evaluation result containing score and feedback
        """
        system_prompt = """You are an academic evaluator specializing in descriptive answer evaluation. 
Your task is to evaluate student answers fairly and objectively based ONLY on the provided model answer.

CRITICAL RULES:
1. Only compare the student answer with the provided model answer
2. Do not introduce external knowledge or information
3. Evaluate based on: completeness, conceptual accuracy, and clarity
4. Use an educational and constructive tone
5. Provide specific, actionable feedback
6. Score on a scale of 0-100

Return your evaluation in JSON format with the following structure:
{
    "score": <number between 0-100>,
    "completeness": <number between 0-100>,
    "accuracy": <number between 0-100>,
    "clarity": <number between 0-100>,
    "feedback": "<detailed feedback string>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "suggestions": "<improvement suggestions>"
}"""

        user_prompt = f"""Question: {question_text}

Model Answer (Expected Answer):
{model_answer}

Student Answer:
{student_answer}

Please evaluate the student answer based on the model answer and provide your assessment in the specified JSON format."""

        for attempt in range(max_retries):
            try:
                logger.info(f"Sending evaluation request to GPT (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    response_format={"type": "json_object"}
                )
                
                # Parse the response
                result_text = response.choices[0].message.content
                result = json.loads(result_text)
                
                # Validate the response structure
                required_keys = ['score', 'feedback']
                if not all(key in result for key in required_keys):
                    raise ValueError("Invalid response structure from GPT")
                
                # Ensure score is within range
                result['score'] = max(0, min(100, float(result['score'])))
                
                # Set defaults for optional fields
                result.setdefault('completeness', result['score'])
                result.setdefault('accuracy', result['score'])
                result.setdefault('clarity', result['score'])
                result.setdefault('strengths', [])
                result.setdefault('weaknesses', [])
                result.setdefault('suggestions', '')
                
                logger.info(f"GPT evaluation completed successfully. Score: {result['score']}")
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT response as JSON: {str(e)}")
                if attempt == max_retries - 1:
                    raise GPTException(f"Failed to parse GPT response: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Error calling GPT API: {str(e)}")
                if attempt == max_retries - 1:
                    raise GPTException(f"Error calling GPT API: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise GPTException("Failed to get evaluation from GPT after all retries")
    
    def batch_evaluate(self, qa_pairs, max_retries=3):
        """
        Evaluate multiple question-answer pairs
        
        Args:
            qa_pairs (list): List of dicts with keys: student_answer, model_answer, question_text
            max_retries (int): Maximum retry attempts
        
        Returns:
            list: List of evaluation results
        """
        results = []
        for qa_pair in qa_pairs:
            try:
                result = self.evaluate_answer(
                    student_answer=qa_pair['student_answer'],
                    model_answer=qa_pair['model_answer'],
                    question_text=qa_pair.get('question_text', ''),
                    max_retries=max_retries
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to evaluate answer: {str(e)}")
                # Add a failed result
                results.append({
                    'score': 0,
                    'feedback': f"Evaluation failed: {str(e)}",
                    'completeness': 0,
                    'accuracy': 0,
                    'clarity': 0,
                    'strengths': [],
                    'weaknesses': ['Evaluation failed'],
                    'suggestions': 'Please try again'
                })
        
        return results
