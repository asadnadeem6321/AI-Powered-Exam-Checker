"""
URL Configuration for evaluations app
"""
from django.urls import path
from .views import (
    evaluate_exam,
    EvaluationListView,
    EvaluationDetailView,
    get_exam_evaluation
)

app_name = 'evaluations'

urlpatterns = [
    path('evaluate/<int:exam_id>/', evaluate_exam, name='evaluate'),
    path('', EvaluationListView.as_view(), name='list'),
    path('<int:pk>/', EvaluationDetailView.as_view(), name='detail'),
    path('exam/<int:exam_id>/', get_exam_evaluation, name='exam_evaluation'),
]
