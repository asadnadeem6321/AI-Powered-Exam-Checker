"""
Claude Handler for contextual evaluation using Anthropic Claude API
"""
import anthropic
from django.conf import settings
import logging
import json
import time
from exam_checker.exceptions import GPTException

logger = logging.getLogger(__name__)


class GPTHandler:
    """
    Handler for Claude API to perform contextual evaluation
    """
    
    def __init__(self):
        """Initialize Claude client"""
        try:
            self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
            self.model = settings.CLAUDE_MODEL
            self.max_tokens = settings.CLAUDE_MAX_TOKENS
            self.temperature = settings.CLAUDE_TEMPERATURE
            logger.info("Claude client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {str(e)}")
            raise GPTException(f"Failed to initialize Claude client: {str(e)}")
    
    def evaluate_answer(self, student_answer, model_answer, question_text="", max_retries=3):
        """
        Evaluate a student answer using Claude
        
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

IMPORTANT: You MUST return your evaluation as valid JSON format (not markdown code blocks).
Return your evaluation with the following structure:
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

Please evaluate the student answer based on the model answer and provide your assessment in JSON format (without markdown code blocks)."""

        for attempt in range(max_retries):
            try:
                logger.info(f"Sending evaluation request to Claude (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                # Parse the response
                result_text = response.content[0].text
                
                # Clean up the response if it contains markdown code blocks
                if result_text.startswith("```json"):
                    result_text = result_text.replace("```json", "").replace("```", "").strip()
                elif result_text.startswith("```"):
                    result_text = result_text.replace("```", "").strip()
                
                result = json.loads(result_text)
                
                # Validate the response structure
                required_keys = ['score', 'feedback']
                if not all(key in result for key in required_keys):
                    raise ValueError("Invalid response structure from Claude")
                
                # Ensure score is within range
                result['score'] = max(0, min(100, float(result['score'])))
                
                # Set defaults for optional fields
                result.setdefault('completeness', result['score'])
                result.setdefault('accuracy', result['score'])
                result.setdefault('clarity', result['score'])
                result.setdefault('strengths', [])
                result.setdefault('weaknesses', [])
                result.setdefault('suggestions', '')
                
                logger.info(f"Claude evaluation completed successfully. Score: {result['score']}")
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response as JSON: {str(e)}")
                if attempt == max_retries - 1:
                    raise GPTException(f"Failed to parse Claude response: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Error calling Claude API: {str(e)}")
                if attempt == max_retries - 1:
                    raise GPTException(f"Error calling Claude API: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise GPTException("Failed to get evaluation from Claude after all retries")

    def generate_expected_answer(self, question_text, max_retries=3):
        """Generate a concise expected/model answer from a question text."""
        system_prompt = """You are an academic assistant that writes concise model answers.
Return only valid JSON with this structure:
{
    "model_answer": "<clear, concise expected answer>",
    "key_points": ["<point 1>", "<point 2>"]
}
Rules:
1. Answer only from the question text.
2. Be concise and academically correct.
3. Do not add markdown or explanations outside JSON.
"""

        user_prompt = f"""Question:
{question_text}

Generate the expected answer in JSON format only."""

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=0.2,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )

                result_text = response.content[0].text.strip()
                if result_text.startswith("```json"):
                    result_text = result_text.replace("```json", "").replace("```", "").strip()
                elif result_text.startswith("```"):
                    result_text = result_text.replace("```", "").strip()

                result = json.loads(result_text)
                model_answer = (result.get('model_answer') or '').strip()
                if not model_answer:
                    raise ValueError('Missing model_answer in Claude response')

                result.setdefault('key_points', [])
                result['model_answer'] = model_answer
                return result

            except Exception as e:
                logger.error(f"Error generating expected answer: {str(e)}")
                if attempt == max_retries - 1:
                    raise GPTException(f"Failed to generate expected answer: {str(e)}")

        raise GPTException("Failed to generate expected answer after all retries")
    
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
