"""
Serializers for Exam-related models
"""
from rest_framework import serializers
from .models import Exam, QuestionAnswer
from django.conf import settings


class QuestionAnswerSerializer(serializers.ModelSerializer):
    """Serializer for QuestionAnswer model"""
    
    class Meta:
        model = QuestionAnswer
        fields = [
            'id',
            'question_number',
            'question_text',
            'student_answer',
            'model_answer',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ExamSerializer(serializers.ModelSerializer):
    """Serializer for Exam model"""
    
    questions = QuestionAnswerSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Exam
        fields = [
            'id',
            'user',
            'user_email',
            'file',
            'file_name',
            'file_type',
            'file_size',
            'raw_text',
            'status',
            'error_message',
            'uploaded_at',
            'processed_at',
            'is_guest',
            'questions'
        ]
        read_only_fields = [
            'id',
            'file_name',
            'file_type',
            'file_size',
            'raw_text',
            'status',
            'error_message',
            'uploaded_at',
            'processed_at',
            'user_email',
            'questions'
        ]
    
    def validate_file(self, file):
        """Validate uploaded file"""
        # Check file size
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.2f}MB"
            )
        
        # Check file extension
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise serializers.ValidationError(
                f"File type '{file_extension}' not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        
        return file


class ExamUploadSerializer(serializers.ModelSerializer):
    """Serializer for exam file upload"""
    
    class Meta:
        model = Exam
        fields = ['file']
    
    def validate_file(self, file):
        """Validate uploaded file"""
        # Check file size
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.2f}MB"
            )
        
        # Check file extension
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise serializers.ValidationError(
                f"File type '{file_extension}' not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        
        return file


class ExamListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for exam list view"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    has_evaluation = serializers.BooleanField(
        source='evaluation',
        read_only=True,
        default=False
    )
    
    class Meta:
        model = Exam
        fields = [
            'id',
            'user_email',
            'file_name',
            'file_type',
            'file_size',
            'status',
            'uploaded_at',
            'is_guest',
            'has_evaluation'
        ]
        read_only_fields = fields
