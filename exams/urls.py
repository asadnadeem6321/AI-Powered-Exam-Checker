"""
URL Configuration for exams app
"""
from django.urls import path
from .views import (
    ExamUploadView,
    ExamListView,
    ExamDetailView,
    delete_exam
)

app_name = 'exams'

urlpatterns = [
    path('upload/', ExamUploadView.as_view(), name='upload'),
    path('', ExamListView.as_view(), name='list'),
    path('<int:pk>/', ExamDetailView.as_view(), name='detail'),
    path('<int:exam_id>/delete/', delete_exam, name='delete'),
]
