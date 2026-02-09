from django.db import models
from django.conf import settings
from exams.models import Exam, QuestionAnswer
import json


class Evaluation(models.Model):
    """Model to store evaluation results"""
    
    exam = models.OneToOneField(
        Exam,
        on_delete=models.CASCADE,
        related_name='evaluation',
        help_text='Associated exam'
    )
    
    # Overall scores
    similarity_score = models.FloatField(
        help_text='SBERT semantic similarity score (0-100)'
    )
    contextual_score = models.FloatField(
        help_text='GPT contextual evaluation score (0-100)'
    )
    final_score = models.FloatField(
        help_text='Weighted final score (0-100)'
    )
    
    # Feedback
    overall_feedback = models.TextField(
        help_text='Overall evaluation feedback'
    )
    
    # Metadata
    evaluation_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata about the evaluation process'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'evaluations'
        verbose_name = 'Evaluation'
        verbose_name_plural = 'Evaluations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['final_score']),
        ]
    
    def __str__(self):
        return f"Evaluation for {self.exam.file_name} - Score: {self.final_score:.2f}"
    
    def get_grade(self):
        """Return letter grade based on final score"""
        if self.final_score >= 90:
            return 'A+'
        elif self.final_score >= 85:
            return 'A'
        elif self.final_score >= 80:
            return 'A-'
        elif self.final_score >= 75:
            return 'B+'
        elif self.final_score >= 70:
            return 'B'
        elif self.final_score >= 65:
            return 'B-'
        elif self.final_score >= 60:
            return 'C+'
        elif self.final_score >= 55:
            return 'C'
        elif self.final_score >= 50:
            return 'C-'
        else:
            return 'F'


class QuestionEvaluation(models.Model):
    """Model to store individual question evaluations"""
    
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='question_evaluations'
    )
    question = models.OneToOneField(
        QuestionAnswer,
        on_delete=models.CASCADE,
        related_name='evaluation_result'
    )
    
    # Scores
    similarity_score = models.FloatField(
        help_text='SBERT similarity score for this question (0-100)'
    )
    contextual_score = models.FloatField(
        help_text='GPT contextual score for this question (0-100)'
    )
    final_score = models.FloatField(
        help_text='Weighted final score for this question (0-100)'
    )
    
    # Detailed feedback
    feedback = models.TextField(
        help_text='Detailed feedback for this answer'
    )
    strengths = models.JSONField(
        default=list,
        blank=True,
        help_text='List of strengths identified in the answer'
    )
    weaknesses = models.JSONField(
        default=list,
        blank=True,
        help_text='List of weaknesses/areas for improvement'
    )
    suggestions = models.TextField(
        blank=True,
        help_text='Suggestions for improvement'
    )
    
    # Evaluation details
    completeness = models.FloatField(
        null=True,
        blank=True,
        help_text='How complete is the answer (0-100)'
    )
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text='How accurate is the answer (0-100)'
    )
    clarity = models.FloatField(
        null=True,
        blank=True,
        help_text='How clear is the answer (0-100)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'question_evaluations'
        verbose_name = 'Question Evaluation'
        verbose_name_plural = 'Question Evaluations'
        ordering = ['evaluation', 'question__question_number']
    
    def __str__(self):
        return f"Evaluation for Q{self.question.question_number} - Score: {self.final_score:.2f}"
