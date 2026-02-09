from django.contrib import admin
from .models import Evaluation, QuestionEvaluation


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """Admin configuration for Evaluation model"""
    
    list_display = ['id', 'get_exam_name', 'final_score', 'get_grade', 'created_at']
    list_filter = ['created_at']
    search_fields = ['exam__file_name', 'overall_feedback']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Exam Information', {
            'fields': ('exam',)
        }),
        ('Scores', {
            'fields': ('similarity_score', 'contextual_score', 'final_score')
        }),
        ('Feedback', {
            'fields': ('overall_feedback',)
        }),
        ('Metadata', {
            'fields': ('evaluation_metadata',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_exam_name(self, obj):
        return obj.exam.file_name
    get_exam_name.short_description = 'Exam'


@admin.register(QuestionEvaluation)
class QuestionEvaluationAdmin(admin.ModelAdmin):
    """Admin configuration for QuestionEvaluation model"""
    
    list_display = ['evaluation', 'get_question_number', 'final_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['feedback', 'suggestions']
    ordering = ['evaluation', 'question__question_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('evaluation', 'question')
        }),
        ('Scores', {
            'fields': ('similarity_score', 'contextual_score', 'final_score', 'completeness', 'accuracy', 'clarity')
        }),
        ('Feedback', {
            'fields': ('feedback', 'strengths', 'weaknesses', 'suggestions')
        }),
    )
    
    def get_question_number(self, obj):
        return f"Q{obj.question.question_number}"
    get_question_number.short_description = 'Question'
