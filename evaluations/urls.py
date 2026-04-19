"""
URL Configuration for evaluations app
"""
from django.urls import path
from .views import (
    evaluate_exam,
    evaluate_manual,
    EvaluationListView,
    EvaluationDetailView,
    get_exam_evaluation
)
from .evaluate_with_marks import evaluate_exam_with_marks

app_name = 'evaluations'

urlpatterns = [
    path('evaluate/<int:exam_id>/', evaluate_exam, name='evaluate'),
        path('evaluate-with-marks/<int:exam_id>/', evaluate_exam_with_marks, name='evaluate_with_marks'),
    path('manual/', evaluate_manual, name='manual_evaluate'),
    path('', EvaluationListView.as_view(), name='list'),
    path('<int:pk>/', EvaluationDetailView.as_view(), name='detail'),
    path('exam/<int:exam_id>/', get_exam_evaluation, name='exam_evaluation'),
]
