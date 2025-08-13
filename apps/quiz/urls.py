from django.urls import path
from apps.quiz.views import TestAPIView, QuizStateAPIView

urlpatterns = [
    path('test/<uuid:test_id>/', TestAPIView.as_view(), name='test'),
    path('quiz/<uuid:test_id>/state/', QuizStateAPIView.as_view(), name='quiz-state'),
]
