from django.contrib import admin
from django.utils.html import format_html
from .models import Exam, QuestionAnswer
from evaluations.models import QuestionEvaluation


class QuestionEvaluationInline(admin.StackedInline):
    """Show AI answer evaluation under each question answer record."""

    model = QuestionEvaluation
    extra = 0
    can_delete = False
    readonly_fields = [
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
        'created_at',
    ]
    fields = [
        'similarity_score',
        'contextual_score',
        'final_score',
        'completeness',
        'accuracy',
        'clarity',
        'feedback',
        'strengths',
        'weaknesses',
        'suggestions',
        'created_at',
    ]

    def has_add_permission(self, request, obj=None):
        return False


class QuestionAnswerInline(admin.TabularInline):
    """Inline question management under exam (question text, expected answer, marks)."""

    model = QuestionAnswer
    extra = 0
    fields = [
        'question_number',
        'question_text',
        'model_answer',
        'student_answer',
        'marks',
        'obtained_marks',
        'question_type',
    ]
    readonly_fields = ['obtained_marks']
    ordering = ['question_number']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin configuration for Exam model"""
    
    list_display = [
        'id',
        'get_title',
        'total_marks',
        'user',
        'is_guest',
        'status',
        'uploaded_at',
        'file_preview',
    ]
    list_filter = ['uploaded_at', 'processed_at', 'status', 'is_guest', 'user']
    search_fields = ['file_name', 'user__email', 'raw_text']
    readonly_fields = ['uploaded_at', 'processed_at', 'file_size', 'raw_text', 'file_preview']
    ordering = ['-uploaded_at']
    inlines = [QuestionAnswerInline]
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'file_preview', 'file_name', 'file_type', 'file_size')
        }),
        ('User Information', {
            'fields': ('user', 'is_guest')
        }),
        ('Exam Metadata', {
            'fields': ('total_marks',)
        }),
        ('Processing Status', {
            'fields': ('status', 'error_message', 'uploaded_at', 'processed_at')
        }),
        ('Content', {
            'fields': ('raw_text',),
            'classes': ('collapse',)
        }),
    )

    def get_title(self, obj):
        return obj.file_name
    get_title.short_description = 'Title'

    def file_preview(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Open File</a>', obj.file.url)
        return '-'
    file_preview.short_description = 'Uploaded File'


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    """Admin configuration for QuestionAnswer model"""
    
    list_display = [
        'id',
        'exam',
        'question_number',
        'get_question_preview',
        'marks',
        'get_obtained_marks_display',
        'created_at',
    ]
    list_filter = ['created_at', 'question_type', 'exam__uploaded_at']
    search_fields = ['question_text', 'student_answer', 'model_answer', 'exam__file_name', 'exam__user__email']
    ordering = ['exam', 'question_number']
    inlines = [QuestionEvaluationInline]
    readonly_fields = ['created_at', 'obtained_marks']

    fieldsets = (
        ('Question', {
            'fields': ('exam', 'question_number', 'question_text', 'question_type', 'options')
        }),
        ('Answer Data', {
            'fields': ('student_answer', 'model_answer')
        }),
        ('Scoring', {
            'fields': ('marks', 'obtained_marks')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def get_question_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    get_question_preview.short_description = 'Question Preview'

    def get_obtained_marks_display(self, obj):
        """Show stored obtained marks, or fall back to the linked evaluation."""
        if obj.obtained_marks is not None:
            return round(obj.obtained_marks, 2)

        evaluation = getattr(obj, 'evaluation_result', None)
        if evaluation:
            if obj.marks:
                return round((evaluation.final_score / 100) * obj.marks, 2)
            return round(evaluation.final_score, 2)

        return '-'

    get_obtained_marks_display.short_description = 'Obtained Marks'
    get_obtained_marks_display.admin_order_field = 'obtained_marks'
