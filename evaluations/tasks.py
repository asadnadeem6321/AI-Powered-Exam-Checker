"""
Celery tasks for evaluation processing
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_exam_evaluation(self, exam_id, questions_data):
    """
    Background task to process exam evaluation
    
    Args:
        exam_id (int): ID of the exam to evaluate
        questions_data (list): List of question-answer pairs
    """
    try:
        from exams.models import Exam, QuestionAnswer
        from evaluations.models import Evaluation, QuestionEvaluation
        from exam_checker.ai_engine import HybridEvaluator
        
        logger.info(f"Starting background evaluation for exam {exam_id}")
        
        exam = Exam.objects.get(id=exam_id)
        
        # Create QuestionAnswer objects if not exist
        for q_data in questions_data:
            QuestionAnswer.objects.get_or_create(
                exam=exam,
                question_number=q_data['question_number'],
                defaults={
                    'question_text': q_data.get('question_text', ''),
                    'student_answer': q_data['student_answer'],
                    'model_answer': q_data['model_answer']
                }
            )
        
        # Initialize evaluator
        evaluator = HybridEvaluator()
        
        # Prepare QA pairs
        qa_pairs = []
        for question in exam.questions.all():
            qa_pairs.append({
                'question_number': question.question_number,
                'question_text': question.question_text,
                'student_answer': question.student_answer,
                'model_answer': question.model_answer
            })
        
        # Perform evaluation
        evaluation_result = evaluator.evaluate_multiple_answers(qa_pairs)
        
        # Create Evaluation object
        evaluation = Evaluation.objects.create(
            exam=exam,
            similarity_score=evaluation_result['average_score'],
            contextual_score=evaluation_result['average_score'],
            final_score=evaluation_result['average_score'],
            overall_feedback=evaluation_result['overall_feedback'],
            evaluation_metadata={
                'total_questions': evaluation_result['total_questions'],
                'percentage': evaluation_result['percentage'],
                'grade': evaluation_result['grade']
            }
        )
        
        # Create QuestionEvaluation objects
        for q_result in evaluation_result['question_results']:
            question = exam.questions.get(question_number=q_result['question_number'])
            
            QuestionEvaluation.objects.create(
                evaluation=evaluation,
                question=question,
                similarity_score=q_result['similarity_score'],
                contextual_score=q_result['contextual_score'],
                final_score=q_result['final_score'],
                feedback=q_result.get('feedback', ''),
                strengths=q_result.get('strengths', []),
                weaknesses=q_result.get('weaknesses', []),
                suggestions=q_result.get('suggestions', ''),
                completeness=q_result.get('completeness'),
                accuracy=q_result.get('accuracy'),
                clarity=q_result.get('clarity')
            )
        
        # Update exam status
        exam.status = 'completed'
        exam.processed_at = timezone.now()
        exam.save()
        
        logger.info(f"Background evaluation completed for exam {exam_id}")
        
        return {
            'status': 'success',
            'exam_id': exam_id,
            'evaluation_id': evaluation.id,
            'final_score': evaluation.final_score
        }
        
    except Exception as e:
        logger.error(f"Error in background evaluation for exam {exam_id}: {str(e)}")
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_guest_exams():
    """
    Periodic task to clean up old guest exam files
    """
    from exams.models import Exam
    from datetime import timedelta
    
    cutoff_time = timezone.now() - timedelta(hours=24)
    
    old_guest_exams = Exam.objects.filter(
        is_guest=True,
        created_at__lt=cutoff_time
    )
    
    count = old_guest_exams.count()
    old_guest_exams.delete()
    
    logger.info(f"Cleaned up {count} old guest exam(s)")
    
    return {'cleaned_count': count}
