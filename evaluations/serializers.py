"""
Serializers for Evaluation-related models
"""
from rest_framework import serializers
from .models import Evaluation, QuestionEvaluation
from exams.serializers import ExamListSerializer, QuestionAnswerSerializer


class QuestionEvaluationSerializer(serializers.ModelSerializer):
    """Serializer for QuestionEvaluation model"""
    
    question = QuestionAnswerSerializer(read_only=True)
    
    class Meta:
        model = QuestionEvaluation
        fields = [
            'id',
            'question',
            'similarity_score',
            'contextual_score',
            'final_score',
            'feedback',
            'strengths',
            'weaknesses',
            'suggestions',
            'completeness',
            'accuracy',
            'clarity',
            'created_at'
        ]
        read_only_fields = fields


class EvaluationSerializer(serializers.ModelSerializer):
    """Serializer for Evaluation model"""
    
    exam = ExamListSerializer(read_only=True)
    question_evaluations = QuestionEvaluationSerializer(many=True, read_only=True)
    grade = serializers.CharField(source='get_grade', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = [
            'id',
            'exam',
            'similarity_score',
            'contextual_score',
            'final_score',
            'grade',
            'overall_feedback',
            'evaluation_metadata',
            'question_evaluations',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class EvaluationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for evaluation list view"""
    
    exam_file_name = serializers.CharField(source='exam.file_name', read_only=True)
    grade = serializers.CharField(source='get_grade', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = [
            'id',
            'exam_file_name',
            'final_score',
            'grade',
            'created_at'
        ]
        read_only_fields = fields
