from django.contrib import admin
from .models import Evaluation, QuestionEvaluation


class ScoreBandFilter(admin.SimpleListFilter):
    """Filter evaluations by score bands for monitoring."""

    title = 'score band'
    parameter_name = 'score_band'

    def lookups(self, request, model_admin):
        return (
            ('high', 'High (>= 80)'),
            ('mid', 'Mid (50-79)'),
            ('low', 'Low (< 50)'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'high':
            return queryset.filter(final_score__gte=80)
        if value == 'mid':
            return queryset.filter(final_score__gte=50, final_score__lt=80)
        if value == 'low':
            return queryset.filter(final_score__lt=50)
        return queryset


class QuestionEvaluationInline(admin.TabularInline):
    """Answer-level AI scores inline under evaluation."""

    model = QuestionEvaluation
    extra = 0
    can_delete = False
    fields = [
        'question',
        'similarity_score',
        'contextual_score',
        'final_score',
        'completeness',
        'accuracy',
        'clarity',
    ]
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """Admin configuration for Evaluation model"""
    
    list_display = [
        'id',
        'get_exam_name',
        'get_exam_owner',
        'similarity_score',
        'contextual_score',
        'final_score',
        'get_grade',
        'created_at',
    ]
    list_filter = ['created_at', ScoreBandFilter]
    search_fields = ['exam__file_name', 'exam__user__email', 'overall_feedback']
    readonly_fields = [
        'similarity_score',
        'contextual_score',
        'final_score',
        'overall_feedback',
        'evaluation_metadata',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']
    inlines = [QuestionEvaluationInline]
    
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

    def get_exam_owner(self, obj):
        if obj.exam.user:
            return obj.exam.user.email
        return 'Guest'
    get_exam_owner.short_description = 'User'


@admin.register(QuestionEvaluation)
class QuestionEvaluationAdmin(admin.ModelAdmin):
    """Admin configuration for QuestionEvaluation model"""
    
    list_display = [
        'id',
        'evaluation',
        'get_question_number',
        'similarity_score',
        'final_score',
        'created_at',
    ]
    list_filter = ['created_at', 'evaluation__created_at']
    search_fields = ['feedback', 'suggestions', 'question__question_text', 'evaluation__exam__file_name']
    ordering = ['-created_at']
    readonly_fields = [
        'evaluation',
        'question',
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
    ]
    
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

    def has_add_permission(self, request):
        return False
