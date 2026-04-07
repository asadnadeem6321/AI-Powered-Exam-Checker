"""
Views for Exam management and file processing
"""
from rest_framework import status, generics, views
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Exam, QuestionAnswer
from .serializers import (
    ExamSerializer,
    ExamListSerializer,
    ExamUploadSerializer,
    QuestionAnswerSerializer
)
from exam_checker.ai_engine import TextExtractor, QuestionExtractor
from exam_checker.ai_engine.preprocessor import TextPreprocessor
from exam_checker.exceptions import TextExtractionException, FileUploadException, GPTException
import logging
import os

logger = logging.getLogger(__name__)


class ExamUploadView(views.APIView):
    """
    API endpoint for uploading exam files
    POST /api/exams/upload/
    """
    permission_classes = [AllowAny]  # Allow guest uploads
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        try:
            # Check if user is authenticated or guest
            is_guest = not request.user.is_authenticated
            user = request.user if not is_guest else None
            
            serializer = ExamUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            uploaded_file = serializer.validated_data['file']
            
            # Create exam instance
            exam = Exam.objects.create(
                user=user,
                file=uploaded_file,
                file_name=uploaded_file.name,
                file_type=uploaded_file.name.split('.')[-1].lower(),
                file_size=uploaded_file.size,
                is_guest=is_guest,
                status='uploaded'
            )
            
            logger.info(f"Exam uploaded: {exam.id} - {exam.file_name} (Guest: {is_guest})")
            
            # Extract text from file
            try:
                text_extractor = TextExtractor()
                result = text_extractor.extract(exam.file.path)
                
                exam.raw_text = result['text']
                exam.status = 'completed'
                exam.processed_at = timezone.now()
                exam.save()
                
                logger.info(f"Text extracted successfully from exam {exam.id}")
            except Exception as e:
                logger.error(f"Error extracting text from exam {exam.id}: {str(e)}")
                exam.status = 'failed'
                exam.error_message = str(e)
                exam.save()
                
                return Response({
                    'error': 'Failed to extract text from file',
                    'detail': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'message': 'File uploaded and processed successfully',
                'exam': ExamSerializer(exam).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error uploading exam: {str(e)}")
            return Response({
                'error': 'File upload failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ExamListView(generics.ListAPIView):
    """
    API endpoint to list user's exams
    GET /api/exams/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ExamListSerializer
    
    def get_queryset(self):
        return Exam.objects.filter(user=self.request.user, is_guest=False)


class ExamDetailView(generics.RetrieveAPIView):
    """
    API endpoint to get exam details
    GET /api/exams/{id}/
    """
    permission_classes = [AllowAny]  # Allow guest access
    serializer_class = ExamSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Exam.objects.filter(user=self.request.user)
        else:
            return Exam.objects.filter(is_guest=True)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_exam(request, exam_id):
    """
    API endpoint to delete an exam
    DELETE /api/exams/{id}/delete/
    """
    try:
        exam = get_object_or_404(Exam, id=exam_id, user=request.user)
        exam.delete()
        
        logger.info(f"Exam deleted: {exam_id} by user {request.user.email}")
        
        return Response({
            'message': 'Exam deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deleting exam {exam_id}: {str(e)}")
        return Response({
            'error': 'Failed to delete exam',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def extract_questions(request, exam_id):
    """
    API endpoint to extract questions from exam text
    POST /api/exams/{exam_id}/extract-questions/
    
    This endpoint:
    1. Gets the exam's raw text
    2. Uses Claude AI to extract questions and answers
    3. Returns structured question data for user review
    """
    try:
        # Get exam
        if request.user.is_authenticated:
            exam = get_object_or_404(Exam, id=exam_id, user=request.user)
        else:
            exam = get_object_or_404(Exam, id=exam_id, is_guest=True)
        
        # Check if exam has raw text
        if not exam.raw_text:
            return Response({
                'error': 'Exam text not extracted yet',
                'detail': 'Please ensure the file was successfully processed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Extracting questions from exam {exam_id}")
        
        # Initialize question extractor
        extractor = QuestionExtractor()
        
        # Extract questions using Claude API
        questions_data = extractor.extract_questions(exam.raw_text)
        
        # Validate extracted questions
        is_valid, error_msg = extractor.validate_questions(questions_data)
        if not is_valid:
            logger.error(f"Question validation failed: {error_msg}")
            return Response({
                'error': 'Failed to extract questions',
                'detail': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Successfully extracted {questions_data.get('total_questions', 0)} questions")
        
        return Response({
            'message': 'Questions extracted successfully',
            'exam_id': exam_id,
            'data': questions_data
        }, status=status.HTTP_200_OK)
        
    except GPTException as e:
        logger.error(f"Claude API error: {str(e)}")
        return Response({
            'error': 'Failed to extract questions using AI',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error extracting questions from exam {exam_id}: {str(e)}")
        return Response({
            'error': 'Failed to extract questions',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
