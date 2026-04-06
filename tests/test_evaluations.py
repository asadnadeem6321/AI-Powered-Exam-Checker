"""
Test Cases for Evaluation functionality
Location: tests/test_evaluations.py
"""
from django.test import TestCase, Client
from django.urls import reverse
from exams.models import Exam, QuestionAnswer
from evaluations.models import Evaluation, QuestionEvaluation
from users.models import User
from rest_framework import status
import json


class EvaluationTestCase(TestCase):
    """Test evaluation functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='securepass123!'
        )
        
        # Login
        login_response = self.client.post(
            reverse('users:login'),
            data=json.dumps({
                'email': 'testuser@example.com',
                'password': 'securepass123!'
            }),
            content_type='application/json'
        )
        self.token = login_response.json()['tokens']['access']
        
        # Create exam
        self.exam = Exam.objects.create(
            user=self.user,
            file='test.txt',
            file_name='exam.txt',
            file_type='txt',
            file_size=1024,
            status='completed'
        )
    
    def test_evaluate_exam_single_question(self):
        """Test evaluating exam with single question"""
        evaluate_url = reverse('evaluations:evaluate', args=[self.exam.id])
        
        evaluation_data = {
            'questions': [
                {
                    'question_number': 1,
                    'question_text': 'What is machine learning?',
                    'student_answer': 'Machine learning is learning from data',
                    'model_answer': 'Machine learning is a subset of AI that learns from data'
                }
            ]
        }
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        response = self.client.post(
            evaluate_url,
            data=json.dumps(evaluation_data),
            content_type='application/json',
            **headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('evaluation', response.json())
        self.assertIn('final_score', response.json()['evaluation'])
    
    def test_evaluate_exam_multiple_questions(self):
        """Test evaluating exam with multiple questions"""
        evaluate_url = reverse('evaluations:evaluate', args=[self.exam.id])
        
        evaluation_data = {
            'questions': [
                {
                    'question_number': 1,
                    'question_text': 'What is ML?',
                    'student_answer': 'Machine learning from data',
                    'model_answer': 'ML is subset of AI'
                },
                {
                    'question_number': 2,
                    'question_text': 'Types of ML?',
                    'student_answer': 'Supervised, Unsupervised, Reinforcement',
                    'model_answer': 'Supervised and Unsupervised'
                }
            ]
        }
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        response = self.client.post(
            evaluate_url,
            data=json.dumps(evaluation_data),
            content_type='application/json',
            **headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        evaluation = response.json()['evaluation']
        self.assertIn('question_evaluations', evaluation)
    
    def test_evaluate_exam_no_questions(self):
        """Test evaluation with no questions"""
        evaluate_url = reverse('evaluations:evaluate', args=[self.exam.id])
        
        evaluation_data = {'questions': []}
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        response = self.client.post(
            evaluate_url,
            data=json.dumps(evaluation_data),
            content_type='application/json',
            **headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_evaluation(self):
        """Test retrieving evaluation results"""
        # Create evaluation
        evaluation = Evaluation.objects.create(
            exam=self.exam,
            similarity_score=75.5,
            contextual_score=80.0,
            final_score=77.5,
            overall_feedback='Good answer with room for improvement'
        )
        
        exam_eval_url = reverse('evaluations:exam_evaluation', args=[self.exam.id])
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        response = self.client.get(exam_eval_url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['final_score'], 77.5)
    
    def test_list_user_evaluations(self):
        """Test listing user's evaluations"""
        # Create evaluation
        Evaluation.objects.create(
            exam=self.exam,
            similarity_score=75.5,
            contextual_score=80.0,
            final_score=77.5,
            overall_feedback='Test feedback'
        )
        
        list_url = reverse('evaluations:list')
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        response = self.client.get(list_url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
    
    def test_evaluation_grade_calculation(self):
        """Test grade calculation based on score"""
        grades_map = {
            95: 'A+',
            85: 'A',
            75: 'B+',
            65: 'B',
            55: 'C',
            45: 'D',
            30: 'F'
        }
        
        for score, expected_grade in grades_map.items():
            evaluation = Evaluation.objects.create(
                exam=Exam.objects.create(
                    user=self.user,
                    file=f'test_{score}.txt',
                    file_name=f'exam_{score}.txt',
                    file_type='txt',
                    file_size=1024
                ),
                similarity_score=score,
                contextual_score=score,
                final_score=score,
                overall_feedback='Test'
            )
            
            grade = evaluation.get_grade()
            self.assertEqual(grade, expected_grade, f"Score {score} should give {expected_grade}, got {grade}")
