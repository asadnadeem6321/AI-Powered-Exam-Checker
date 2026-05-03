"""
Enhanced Evaluation Endpoint - Includes Marks Calculation
Implements proper hybrid evaluation with academic grading
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from exams.models import Exam, QuestionAnswer
from evaluations.models import Evaluation, QuestionEvaluation
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def evaluate_exam_with_marks(request, exam_id):
    """
    API endpoint to evaluate exam with proper hybrid scoring and marks calculation
    POST /api/evaluations/evaluate-with-marks/{exam_id}/
    
    This endpoint:
    1. Retrieve saved Q/A pairs with marks from database
    2. Validate model answers are present
    3. Use Enhanced Evaluator (SBERT + deterministic context scoring)
    4. Calculate obtained marks based on scores
    5. Save evaluation results
    6. Return comprehensive feedback
    
    Returns:
    - total_obtained_marks: Sum of marks for all questions
    - total_allocated_marks: Total exam marks
    - percentage: Overall percentage
    - grade: Letter grade
    - question_results: Detailed evaluation per question
    - feedback: Comprehensive feedback
    """
    try:
        # Get exam
        if request.user.is_authenticated:
            exam = get_object_or_404(Exam, id=exam_id, user=request.user)
        else:
            exam = get_object_or_404(Exam, id=exam_id, is_guest=True)
        
        logger.info(f"Starting evaluation for exam {exam_id}")
        
        # Check if questions have been extracted
        questions = exam.questions.all()
        if not questions.exists():
            return Response({
                'error': 'No questions found',
                'detail': 'Please extract questions first'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Apply optional frontend edits before evaluation.
        incoming_questions = request.data.get('questions', [])
        if incoming_questions and isinstance(incoming_questions, list):
            for incoming in incoming_questions:
                question_number = incoming.get('question_number')
                if question_number is None:
                    continue

                try:
                    question_obj = questions.get(question_number=question_number)
                except QuestionAnswer.DoesNotExist:
                    continue

                question_obj.question_text = incoming.get('question_text', question_obj.question_text)
                question_obj.student_answer = incoming.get('student_answer', question_obj.student_answer)
                question_obj.model_answer = incoming.get('model_answer', question_obj.model_answer)

                incoming_marks = incoming.get('marks')
                if incoming_marks is not None:
                    question_obj.marks = incoming_marks

                question_obj.save()

            questions = exam.questions.all()
        
        # Validate all model answers are present
        qa_pairs = []
        for q in questions.order_by('question_number'):
            if not q.model_answer or not q.model_answer.strip():
                return Response({
                    'error': 'Missing model answer',
                    'detail': f'Q{q.question_number}: Model answer is required for evaluation'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            qa_pairs.append({
                'question_number': q.question_number,
                'question_text': q.question_text,
                'student_answer': q.student_answer or '',
                'model_answer': q.model_answer,
                'marks': q.marks
            })
        
        logger.info(f"Evaluating {len(qa_pairs)} questions")
        
        # Use Enhanced Evaluator for hybrid scoring
        from exam_checker.ai_engine.enhanced_evaluator import EnhancedHybridEvaluator
        
        evaluator = EnhancedHybridEvaluator()
        evaluation_result = evaluator.evaluate_multiple_with_marks(
            qa_pairs=qa_pairs,
            total_marks=exam.total_marks
        )
        
        logger.info(f"Evaluation complete: {evaluation_result['total_obtained_marks']}/{evaluation_result['total_allocated_marks']}")
        
        # Save Evaluation to database (for users only, not guests)
        evaluation_obj = None
        if request.user.is_authenticated:
            try:
                question_results = evaluation_result.get('question_results', [])
                successful_results = [q for q in question_results if not q.get('error')]
                avg_similarity = (
                    sum(q.get('similarity_score', 0) for q in successful_results) / len(successful_results)
                    if successful_results else 0
                )
                avg_context = (
                    sum(q.get('contextual_score', 0) for q in successful_results) / len(successful_results)
                    if successful_results else 0
                )

                evaluation_obj = Evaluation.objects.create(
                    exam=exam,
                    similarity_score=round(avg_similarity, 2),
                    contextual_score=round(avg_context, 2),
                    final_score=evaluation_result['percentage'],
                    overall_feedback=evaluation_result['feedback'],
                    evaluation_metadata={
                        'total_questions': evaluation_result['total_questions'],
                        'total_allocated_marks': evaluation_result['total_allocated_marks'],
                        'total_obtained_marks': evaluation_result['total_obtained_marks'],
                        'evaluation_method': 'hybrid_with_manual_context',
                        'sbert_weight': 0.7,
                        'context_weight': 0.3,
                        'question_results': evaluation_result.get('question_results', [])
                    }
                )
                
                # Save individual question evaluations
                for q_result in evaluation_result['question_results']:
                    try:
                        question = questions.get(question_number=q_result['question_number'])
                        
                        QuestionEvaluation.objects.create(
                            evaluation=evaluation_obj,
                            question=question,
                            similarity_score=q_result.get('similarity_score', 0),
                            contextual_score=q_result.get('contextual_score', 0),
                            final_score=q_result.get('final_score_pct', 0),
                            feedback=q_result.get('feedback', ''),
                            strengths=q_result.get('strengths', []),
                            weaknesses=q_result.get('weaknesses', []),
                            suggestions=q_result.get('suggestions', ''),
                            completeness=q_result.get('completeness'),
                            accuracy=q_result.get('accuracy'),
                            clarity=q_result.get('clarity')
                        )
                        
                        # Save obtained marks to question
                        question.obtained_marks = q_result.get('obtained_marks')
                        question.save()
                        
                    except Exception as e:
                        logger.error(f"Error saving Q{q_result.get('question_number')} evaluation: {str(e)}")
                
                logger.info(f"Evaluation {evaluation_obj.id} saved to database")
                
            except Exception as e:
                logger.error(f"Error saving evaluation to database: {str(e)}")
                # Continue - return results even if DB save fails
        else:
            # For guest users, save obtained marks to questions in memory
            for q_result in evaluation_result['question_results']:
                try:
                    question = questions.get(question_number=q_result['question_number'])
                    question.obtained_marks = q_result.get('obtained_marks')
                    # Note: Not saving for guests to preserve privacy
                except Exception as e:
                    logger.error(f"Error processing Q{q_result.get('question_number')}: {str(e)}")
        
        # Prepare response
        response_data = {
            'message': 'Evaluation completed successfully',
            'exam_id': exam_id,
            'evaluation': {
                'total_questions': evaluation_result['total_questions'],
                'total_allocated_marks': evaluation_result['total_allocated_marks'],
                'total_obtained_marks': evaluation_result['total_obtained_marks'],
                'percentage': evaluation_result['percentage'],
                'grade': evaluation_result['grade'],
                'feedback': evaluation_result['feedback'],
                'question_results': evaluation_result['question_results'],
                'low_confidence_questions': evaluation_result.get('low_confidence_questions', [])
            }
        }
        
        if evaluation_obj:
            response_data['evaluation']['evaluation_id'] = evaluation_obj.id
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        return Response({
            'error': 'Evaluation failed',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
