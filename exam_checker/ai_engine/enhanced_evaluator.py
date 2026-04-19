"""
Enhanced Hybrid Evaluator with Academic Marks Calculation
Combines SBERT (60%) + Claude GPT (40%) with proper marks allocation
"""
import logging
from django.conf import settings
from exam_checker.exceptions import EvaluationException

logger = logging.getLogger(__name__)


class EnhancedHybridEvaluator:
    """
    Enhanced evaluation engine that:
    1. Computes hybrid scores (SBERT 60% + GPT 40%)
    2. Calculates obtained marks from scores and total marks
    3. Provides academic grading with proper feedback
    """
    
    def __init__(self):
        """Initialize evaluator"""
        try:
            from .sbert_handler import SBERTHandler
            from .gpt_handler import GPTHandler
            from .preprocessor import TextPreprocessor
            
            self.sbert = SBERTHandler()
            self.gpt = GPTHandler()
            self.preprocessor = TextPreprocessor()
            self.similarity_weight = getattr(settings, 'SIMILARITY_WEIGHT', 0.6)
            self.context_weight = getattr(settings, 'CONTEXT_WEIGHT', 0.4)
            
            logger.info(f"Enhanced Evaluator initialized (SBERT={self.similarity_weight}, GPT={self.context_weight})")
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Evaluator: {str(e)}")
            raise EvaluationException(f"Failed to initialize evaluator: {str(e)}")
    
    def evaluate_answer_with_marks(self, student_answer, model_answer, question_text="", marks=None):
        """
        Evaluate a single answer and calculate obtained marks
        
        Args:
            student_answer (str): Student's answer
            model_answer (str): Expected/correct answer
            question_text (str): The question
            marks (int): Total marks for this question
        
        Returns:
            dict: Evaluation with obtained marks
        """
        try:
            # Validate inputs
            if not student_answer or not model_answer:
                raise EvaluationException("Student answer and model answer required")
            
            # Clean texts
            clean_student = self.preprocessor.clean_text(student_answer)
            clean_model = self.preprocessor.clean_text(model_answer)
            
            # Compute SBERT similarity and normalize to percentage.
            # SBERTHandler may return either 0-1 or 0-100 depending on environment/fallback path.
            similarity_score = self.sbert.compute_similarity(clean_student, clean_model)
            similarity_pct = similarity_score * 100 if similarity_score <= 1 else similarity_score
            similarity_pct = min(100, max(0, similarity_pct))
            
            # Get GPT contextual evaluation (0-100 range)
            gpt_result = self.gpt.evaluate_answer(
                student_answer=student_answer,
                model_answer=model_answer,
                question_text=question_text
            )
            contextual_score = gpt_result.get('score', 50)
            
            # Hybrid scoring formula: (0.6 × SBERT%) + (0.4 × GPT%)
            final_score_pct = (self.similarity_weight * similarity_pct) + (self.context_weight * contextual_score)
            final_score_pct = min(100, max(0, final_score_pct))  # Clamp to 0-100
            
            # Calculate obtained marks
            obtained_marks = None
            if marks:
                obtained_marks = (final_score_pct / 100) * marks
                obtained_marks = round(obtained_marks, 2)
            
            result = {
                'similarity_score': round(similarity_pct, 2),
                'contextual_score': round(contextual_score, 2),
                'final_score_pct': round(final_score_pct, 2),
                'marks_allocated': marks,
                'obtained_marks': obtained_marks,
                'feedback': gpt_result.get('feedback', ''),
                'completeness': gpt_result.get('completeness', final_score_pct),
                'accuracy': gpt_result.get('accuracy', final_score_pct),
                'clarity': gpt_result.get('clarity', final_score_pct),
                'strengths': gpt_result.get('strengths', []),
                'weaknesses': gpt_result.get('weaknesses', []),
                'suggestions': gpt_result.get('suggestions', ''),
                'confidence': 'high' if similarity_pct >= 50 else 'low'
            }
            
            if result['confidence'] == 'low':
                result['confidence_note'] = "Low confidence evaluation. Manual review recommended."
            
            logger.info(f"Answer evaluated: Score={final_score_pct:.2f}%, Obtained Marks={obtained_marks}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}")
            raise EvaluationException(f"Evaluation failed: {str(e)}")
    
    def evaluate_multiple_with_marks(self, qa_pairs, total_marks=None):
        """
        Evaluate multiple Q/A pairs with marks calculation
        
        Args:
            qa_pairs (list): List of dicts with question_number, question_text, 
                           student_answer, model_answer, marks
            total_marks (int): Total marks for the exam
        
        Returns:
            dict: Overall evaluation with marks breakdown
        """
        try:
            logger.info(f"Evaluating {len(qa_pairs)} Q/A pairs (Total Marks={total_marks})")
            
            question_results = []
            total_obtained = 0
            total_allocated = 0
            
            for qa in qa_pairs:
                try:
                    result = self.evaluate_answer_with_marks(
                        student_answer=qa.get('student_answer', ''),
                        model_answer=qa.get('model_answer', ''),
                        question_text=qa.get('question_text', ''),
                        marks=qa.get('marks')
                    )
                    
                    result['question_number'] = qa.get('question_number')
                    result['question_text'] = qa.get('question_text', '')
                    
                    question_results.append(result)
                    
                    if result['obtained_marks']:
                        total_obtained += result['obtained_marks']
                    if result['marks_allocated']:
                        total_allocated += result['marks_allocated']
                    
                except Exception as e:
                    logger.error(f"Q{qa.get('question_number')} evaluation failed: {str(e)}")
                    question_results.append({
                        'question_number': qa.get('question_number'),
                        'question_text': qa.get('question_text', ''),
                        'error': str(e),
                        'obtained_marks': 0,
                        'marks_allocated': qa.get('marks')
                    })
            
            # Calculate percentages
            overall_pct = (total_obtained / total_allocated * 100) if total_allocated > 0 else 0
            overall_pct = round(min(100, max(0, overall_pct)), 2)
            
            grade = self._get_grade(overall_pct)
            feedback = self._generate_comprehensive_feedback(question_results, overall_pct)
            
            result = {
                'total_questions': len(qa_pairs),
                'total_allocated_marks': total_allocated,
                'total_obtained_marks': round(total_obtained, 2),
                'percentage': overall_pct,
                'grade': grade,
                'feedback': feedback,
                'question_results': question_results,
                'low_confidence_questions': [
                    q['question_number'] for q in question_results 
                    if q.get('confidence') == 'low'
                ]
            }
            
            logger.info(f"Evaluation complete: {total_obtained:.2f}/{total_allocated} ({overall_pct}%) - Grade: {grade}")
            return result
            
        except Exception as e:
            logger.error(f"Multi-answer evaluation error: {str(e)}")
            raise EvaluationException(f"Evaluation failed: {str(e)}")
    
    def _get_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 85:
            return 'A'
        elif percentage >= 80:
            return 'A-'
        elif percentage >= 75:
            return 'B+'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 65:
            return 'B-'
        elif percentage >= 60:
            return 'C+'
        elif percentage >= 55:
            return 'C'
        elif percentage >= 50:
            return 'C-'
        else:
            return 'F'
    
    def _generate_comprehensive_feedback(self, question_results, overall_pct):
        """Generate comprehensive feedback with suggestions"""
        performance_map = {
            'A+': ('Excellent', 'outstanding work'),
            'A': ('Excellent', 'very strong performance'),
            'A-': ('Very Good', 'strong performance'),
            'B+': ('Good', 'solid understanding'),
            'B': ('Good', 'satisfactory performance'),
            'B-': ('Good', 'acceptable performance'),
            'C+': ('Satisfactory', 'basic competency'),
            'C': ('Satisfactory', 'minimum competency'),
            'C-': ('Satisfactory', 'marginal competency'),
            'F': ('Needs Improvement', 'significant gaps')
        }
        
        grade = self._get_grade(overall_pct)
        rating, descriptor = performance_map.get(grade, ('Unknown', 'performance'))
        
        feedback = f"""
EVALUATION SUMMARY
==================
Final Grade: {grade}
Overall Performance: {rating} - {descriptor}
Overall Score: {overall_pct}%

DETAILED ANALYSIS:
- Total Questions: {len(question_results)}
- Questions Answered: {len([q for q in question_results if not q.get('error')])}
- Low Confidence Evaluations: {len([q for q in question_results if q.get('confidence') == 'low'])}

KEY STRENGTHS:
"""
        
        strengths = {}
        weaknesses = {}
        
        for q in question_results:
            if not q.get('error'):
                for s in q.get('strengths', [])[:2]:
                    strengths[s] = strengths.get(s, 0) + 1
                for w in q.get('weaknesses', [])[:2]:
                    weaknesses[w] = weaknesses.get(w, 0) + 1
        
        if strengths:
            top_strengths = sorted(strengths.items(), key=lambda x: x[1], reverse=True)[:3]
            for strength, count in top_strengths:
                feedback += f"- {strength}\n"
        else:
            feedback += "- Developing (continue to practice)\n"
        
        feedback += "\nAREAS FOR IMPROVEMENT:\n"
        if weaknesses:
            top_weaknesses = sorted(weaknesses.items(), key=lambda x: x[1], reverse=True)[:3]
            for weakness, count in top_weaknesses:
                feedback += f"- {weakness}\n"
        else:
            feedback += "- Continue building on existing strengths\n"
        
        feedback += "\nRECOMMENDATIONS:\n"
        if overall_pct < 50:
            feedback += "- Review core concepts and fundamentals\n"
            feedback += "- Practice more sample questions\n"
            feedback += "- Seek additional help or tutoring\n"
        elif overall_pct < 70:
            feedback += "- Focus on areas flagged as problematic\n"
            feedback += "- Practice similar question types\n"
            feedback += "- Review explanations for incorrect answers\n"
        else:
            feedback += "- Maintain current preparation level\n"
            feedback += "- Try more challenging questions\n"
            feedback += "- Help peers with similar content\n"
        
        return feedback
