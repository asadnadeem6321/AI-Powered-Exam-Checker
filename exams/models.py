from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import os


def exam_upload_path(instance, filename):
    """Generate upload path for exam files"""
    if instance.user:
        return f'exams/{instance.user.id}/{filename}'
    else:
        return f'exams/guest/{filename}'


class Exam(models.Model):
    """Model to store uploaded exam files"""
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exams',
        null=True,
        blank=True,
        help_text='User who uploaded the exam (null for guest users)'
    )
    file = models.FileField(
        upload_to=exam_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'jpg', 'jpeg', 'png'])],
        help_text='Uploaded exam file'
    )
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)
    file_size = models.IntegerField(help_text='File size in bytes')
    
    # Exam content
    raw_text = models.TextField(blank=True, help_text='Extracted text from file')
    
    # Processing status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded'
    )
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Guest users - automatically delete after evaluation
    is_guest = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'exams'
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', '-uploaded_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.file_name} - {self.status}"
    
    def delete(self, *args, **kwargs):
        """Delete file from storage when model is deleted"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class QuestionAnswer(models.Model):
    """Model to store individual question-answer pairs from an exam"""
    
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_number = models.IntegerField()
    question_text = models.TextField()
    student_answer = models.TextField()
    model_answer = models.TextField(help_text='Expected/correct answer')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'question_answers'
        verbose_name = 'Question Answer'
        verbose_name_plural = 'Question Answers'
        ordering = ['exam', 'question_number']
        unique_together = ['exam', 'question_number']
    
    def __str__(self):
        return f"Q{self.question_number} - {self.exam.file_name}"
