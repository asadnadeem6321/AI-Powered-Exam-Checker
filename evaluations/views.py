"""
Views for Evaluation processing and results
"""
from rest_framework import status, generics, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Evaluation, QuestionEvaluation
from exams.models import Exam, QuestionAnswer
from .serializers import (
    EvaluationSerializer,
    EvaluationListSerializer,
    QuestionEvaluationSerializer
)
from exam_checker.ai_engine import HybridEvaluator
from exam_checker.ai_engine.preprocessor import TextPreprocessor
from exam_checker.exceptions import EvaluationException
import logging
import json

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def evaluate_exam(request, exam_id):
    """
    API endpoint to evaluate an exam
    POST /api/evaluations/evaluate/{exam_id}/
    
    Request body should contain:
    {
        "questions": [
            {
                "question_number": 1,
                "question_text": "...",
                "student_answer": "...",
                "model_answer": "..."
            },
            ...
        ]
    }
    """
    try:
        # Get exam
        if request.user.is_authenticated:
            exam = get_object_or_404(Exam, id=exam_id, user=request.user)
        else:
            exam = get_object_or_404(Exam, id=exam_id, is_guest=True)
        
        # Check if exam is already evaluated
        if hasattr(exam, 'evaluation'):
            return Response({
                'message': 'Exam already evaluated',
                'evaluation': EvaluationSerializer(exam.evaluation).data
            }, status=status.HTTP_200_OK)
        
        # Get question-answer pairs from request
        questions_data = request.data.get('questions', [])
        
        if not questions_data:
            return Response({
                'error': 'No questions provided for evaluation'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create QuestionAnswer objects
        for q_data in questions_data:
            QuestionAnswer.objects.create(
                exam=exam,
                question_number=q_data['question_number'],
                question_text=q_data.get('question_text', ''),
                student_answer=q_data['student_answer'],
                model_answer=q_data['model_answer']
            )
        
        logger.info(f"Starting evaluation for exam {exam_id}")
        
        # Initialize evaluator
        evaluator = HybridEvaluator()
        
        # Prepare QA pairs for evaluation
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
            similarity_score=evaluation_result['average_score'] * (1 / (1 / 0.6)),  # Reverse engineer similarity portion
            contextual_score=evaluation_result['average_score'] * (1 / (1 / 0.4)),  # Reverse engineer contextual portion
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
        
        logger.info(f"Evaluation completed for exam {exam_id}. Score: {evaluation.final_score}")
        
        # Delete guest exam after evaluation
        if exam.is_guest:
            logger.info(f"Scheduling guest exam {exam_id} for deletion")
            # Note: In production, you might want to schedule this with Celery
        
        return Response({
            'message': 'Evaluation completed successfully',
            'evaluation': EvaluationSerializer(evaluation).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error evaluating exam {exam_id}: {str(e)}")
        return Response({
            'error': 'Evaluation failed',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def evaluate_manual(request):
    """
    API endpoint to evaluate manually entered question-answer pairs.
    POST /api/evaluations/manual/

    Request body:
    {
        "questions": [
            {
                "question_text": "...",
                "student_answer": "...",
                "model_answer": "..."
            }
        ]
    }
    """
    try:
        questions_data = request.data.get('questions', [])

        if not isinstance(questions_data, list) or len(questions_data) == 0:
            return Response({
                'error': 'No questions provided for evaluation'
            }, status=status.HTTP_400_BAD_REQUEST)

        qa_pairs = []
        for idx, q_data in enumerate(questions_data, start=1):
            question_text = (q_data.get('question_text') or '').strip()
            student_answer = (q_data.get('student_answer') or '').strip()
            model_answer = (q_data.get('model_answer') or '').strip()

            if not question_text or not student_answer or not model_answer:
                return Response({
                    'error': f'Question {idx} is incomplete. Question, student answer, and model answer are required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            qa_pairs.append({
                'question_number': idx,
                'question_text': question_text,
                'student_answer': student_answer,
                'model_answer': model_answer
            })

        evaluator = HybridEvaluator()
        evaluation_result = evaluator.evaluate_multiple_answers(qa_pairs)

        return Response({
            'message': 'Manual evaluation completed successfully',
            'evaluation': evaluation_result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in manual evaluation: {str(e)}")
        return Response({
            'error': 'Manual evaluation failed',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


class EvaluationListView(generics.ListAPIView):
    """
    API endpoint to list user's evaluations
    GET /api/evaluations/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EvaluationListSerializer
    
    def get_queryset(self):
        return Evaluation.objects.filter(exam__user=self.request.user)


class EvaluationDetailView(generics.RetrieveAPIView):
    """
    API endpoint to get evaluation details
    GET /api/evaluations/{id}/
    """
    permission_classes = [AllowAny]
    serializer_class = EvaluationSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Evaluation.objects.filter(exam__user=self.request.user)
        else:
            return Evaluation.objects.filter(exam__is_guest=True)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_exam_evaluation(request, exam_id):
    """
    API endpoint to get evaluation for a specific exam
    GET /api/evaluations/exam/{exam_id}/
    """
    try:
        if request.user.is_authenticated:
            exam = get_object_or_404(Exam, id=exam_id, user=request.user)
        else:
            exam = get_object_or_404(Exam, id=exam_id, is_guest=True)
        
        if not hasattr(exam, 'evaluation'):
            return Response({
                'error': 'Exam has not been evaluated yet'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EvaluationSerializer(exam.evaluation)
        
        return Response({
            'evaluation': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting evaluation for exam {exam_id}: {str(e)}")
        return Response({
            'error': 'Failed to get evaluation',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
