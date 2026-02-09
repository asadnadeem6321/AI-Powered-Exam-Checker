"""
Hybrid Evaluator combining SBERT and GPT for comprehensive evaluation
"""
from django.conf import settings
import logging
from .sbert_handler import SBERTHandler
from .gpt_handler import GPTHandler
from .preprocessor import TextPreprocessor
from exam_checker.exceptions import EvaluationException

logger = logging.getLogger(__name__)


class HybridEvaluator:
    """
    Hybrid evaluation engine combining SBERT and GPT
    Implements the weighted scoring: Final = (0.6 * SBERT) + (0.4 * GPT)
    """
    
    def __init__(self):
        """Initialize evaluator with SBERT and GPT handlers"""
        try:
            self.sbert = SBERTHandler()
            self.gpt = GPTHandler()
            self.preprocessor = TextPreprocessor()
            self.similarity_weight = settings.SIMILARITY_WEIGHT
            self.context_weight = settings.CONTEXT_WEIGHT
            logger.info(f"Hybrid Evaluator initialized (weights: SBERT={self.similarity_weight}, GPT={self.context_weight})")
        except Exception as e:
            logger.error(f"Failed to initialize Hybrid Evaluator: {str(e)}")
            raise EvaluationException(f"Failed to initialize evaluator: {str(e)}")
    
    def evaluate_single_answer(self, student_answer, model_answer, question_text=""):
        """
        Evaluate a single answer using hybrid approach
        
        Args:
            student_answer (str): Student's answer
            model_answer (str): Expected/model answer
            question_text (str): The question (optional)
        
        Returns:
            dict: Comprehensive evaluation result
        """
        try:
            logger.info("Starting hybrid evaluation for single answer")
            
            # Validate inputs
            if not student_answer or not model_answer:
                raise EvaluationException("Both student answer and model answer are required")
            
            # Clean texts
            clean_student_answer = self.preprocessor.clean_text(student_answer)
            clean_model_answer = self.preprocessor.clean_text(model_answer)
            
            # Get text statistics
            student_stats = self.preprocessor.get_stats(student_answer)
            
            # Step 1: Compute semantic similarity using SBERT
            logger.info("Computing SBERT similarity...")
            similarity_score = self.sbert.compute_similarity(clean_student_answer, clean_model_answer)
            logger.info(f"SBERT similarity score: {similarity_score:.2f}")
            
            # Step 2: Get contextual evaluation from GPT
            logger.info("Getting GPT contextual evaluation...")
            gpt_result = self.gpt.evaluate_answer(
                student_answer=student_answer,
                model_answer=model_answer,
                question_text=question_text
            )
            contextual_score = gpt_result['score']
            logger.info(f"GPT contextual score: {contextual_score:.2f}")
            
            # Step 3: Calculate hybrid final score
            final_score = (self.similarity_weight * similarity_score) + (self.context_weight * contextual_score)
            final_score = round(final_score, 2)
            logger.info(f"Final hybrid score: {final_score:.2f}")
            
            # Prepare comprehensive result
            result = {
                'similarity_score': round(similarity_score, 2),
                'contextual_score': round(contextual_score, 2),
                'final_score': final_score,
                'feedback': gpt_result.get('feedback', ''),
                'completeness': gpt_result.get('completeness', final_score),
                'accuracy': gpt_result.get('accuracy', final_score),
                'clarity': gpt_result.get('clarity', final_score),
                'strengths': gpt_result.get('strengths', []),
                'weaknesses': gpt_result.get('weaknesses', []),
                'suggestions': gpt_result.get('suggestions', ''),
                'student_stats': student_stats,
                'weights': {
                    'similarity': self.similarity_weight,
                    'contextual': self.context_weight
                }
            }
            
            logger.info("Hybrid evaluation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in hybrid evaluation: {str(e)}")
            raise EvaluationException(f"Evaluation failed: {str(e)}")
    
    def evaluate_multiple_answers(self, qa_pairs):
        """
        Evaluate multiple question-answer pairs
        
        Args:
            qa_pairs (list): List of dicts with keys: 
                            question_number, question_text, student_answer, model_answer
        
        Returns:
            dict: Overall evaluation results
        """
        try:
            logger.info(f"Starting evaluation of {len(qa_pairs)} question-answer pairs")
            
            question_results = []
            total_score = 0
            
            for qa in qa_pairs:
                logger.info(f"Evaluating Question {qa.get('question_number', 'N/A')}")
                
                try:
                    result = self.evaluate_single_answer(
                        student_answer=qa['student_answer'],
                        model_answer=qa['model_answer'],
                        question_text=qa.get('question_text', '')
                    )
                    
                    # Add question metadata
                    result['question_number'] = qa.get('question_number')
                    result['question_text'] = qa.get('question_text', '')
                    
                    question_results.append(result)
                    total_score += result['final_score']
                    
                except Exception as e:
                    logger.error(f"Failed to evaluate question {qa.get('question_number')}: {str(e)}")
                    # Add failed result
                    question_results.append({
                        'question_number': qa.get('question_number'),
                        'question_text': qa.get('question_text', ''),
                        'similarity_score': 0,
                        'contextual_score': 0,
                        'final_score': 0,
                        'feedback': f"Evaluation failed: {str(e)}",
                        'error': str(e)
                    })
            
            # Calculate overall statistics
            num_questions = len(qa_pairs)
            average_score = total_score / num_questions if num_questions > 0 else 0
            
            # Generate overall feedback
            overall_feedback = self._generate_overall_feedback(question_results, average_score)
            
            overall_result = {
                'total_questions': num_questions,
                'average_score': round(average_score, 2),
                'total_score': round(total_score, 2),
                'max_possible_score': num_questions * 100,
                'percentage': round((total_score / (num_questions * 100)) * 100, 2) if num_questions > 0 else 0,
                'question_results': question_results,
                'overall_feedback': overall_feedback,
                'grade': self._get_grade(average_score)
            }
            
            logger.info(f"Multi-answer evaluation completed. Average score: {average_score:.2f}")
            return overall_result
            
        except Exception as e:
            logger.error(f"Error in multi-answer evaluation: {str(e)}")
            raise EvaluationException(f"Multi-answer evaluation failed: {str(e)}")
    
    def _generate_overall_feedback(self, question_results, average_score):
        """Generate overall feedback based on all question results"""
        if average_score >= 80:
            performance = "excellent"
        elif average_score >= 60:
            performance = "good"
        elif average_score >= 40:
            performance = "satisfactory"
        else:
            performance = "needs improvement"
        
        feedback = f"Overall performance: {performance.upper()} (Average Score: {average_score:.2f}%).\n\n"
        
        # Collect common strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        
        for result in question_results:
            all_strengths.extend(result.get('strengths', []))
            all_weaknesses.extend(result.get('weaknesses', []))
        
        if all_strengths:
            feedback += "Overall Strengths:\n"
            for strength in set(all_strengths[:5]):  # Top 5 unique strengths
                feedback += f"- {strength}\n"
            feedback += "\n"
        
        if all_weaknesses:
            feedback += "Areas for Improvement:\n"
            for weakness in set(all_weaknesses[:5]):  # Top 5 unique weaknesses
                feedback += f"- {weakness}\n"
        
        return feedback
    
    def _get_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        else:
            return 'F'
