from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.quiz.models import Test
from apps.quiz.serializers import TestSerializer, QuizStateSerializer, QuizAnswerSerializer
from apps.quiz.quiz_services import QuizService


class TestAPIView(generics.RetrieveAPIView):
    queryset = Test.objects.prefetch_related('questions')
    serializer_class = TestSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'test_id'
    permission_classes = [AllowAny]


class QuizStateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id):
        service = QuizService(request.user, test_id)
        state = service.get_state()
        return Response(QuizStateSerializer(state).data)

    def post(self, request, test_id):
        service = QuizService(request.user, test_id)
        # Передаём тип текущего вопроса в сериализатор
        state = service.get_state()
        if state['status'] == 'completed':
            return Response(QuizStateSerializer(state).data)

        current_question_type = state['current_question']['type']
        serializer = QuizAnswerSerializer(
            data={**request.data, "question_type": current_question_type}
        )
        serializer.is_valid(raise_exception=True)

        # Берём уже валидный ответ
        answer = serializer.validated_data['answer']
        new_state = service.answer_current(answer)
        return Response(QuizStateSerializer(new_state).data)

