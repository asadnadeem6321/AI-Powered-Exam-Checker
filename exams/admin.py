from django.contrib import admin
from .models import Exam, QuestionAnswer


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin configuration for Exam model"""
    
    list_display = ['id', 'file_name', 'user', 'status', 'file_type', 'file_size', 'is_guest', 'uploaded_at']
    list_filter = ['status', 'is_guest', 'file_type', 'uploaded_at']
    search_fields = ['file_name', 'user__email']
    readonly_fields = ['uploaded_at', 'processed_at', 'file_size']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'file_name', 'file_type', 'file_size')
        }),
        ('User Information', {
            'fields': ('user', 'is_guest')
        }),
        ('Processing Status', {
            'fields': ('status', 'error_message', 'uploaded_at', 'processed_at')
        }),
        ('Content', {
            'fields': ('raw_text',),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    """Admin configuration for QuestionAnswer model"""
    
    list_display = ['exam', 'question_number', 'get_question_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['question_text', 'student_answer', 'model_answer']
    ordering = ['exam', 'question_number']
    
    def get_question_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    get_question_preview.short_description = 'Question Preview'
