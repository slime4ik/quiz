from rest_framework import serializers
from apps.quiz.models import Test, Question


class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'type', 'text', 'choices')


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionsSerializer(many=True, read_only=True)
    class Meta:
        model = Test
        fields = ('id', 'title', 'questions')


class QuizStateSerializer(serializers.Serializer):
    status = serializers.CharField()
    current_question = serializers.DictField(required=False)
    current_index = serializers.IntegerField(required=False)
    total_questions = serializers.IntegerField(required=False)
    score = serializers.FloatField(required=False)

class QuizAnswerSerializer(serializers.Serializer):
    answer = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )
    question_type = serializers.CharField()

    def validate(self, data):
        answer = data['answer']
        q_type = data['question_type']

        if q_type == Question.Type.SINGLE and len(answer) != 1:
            raise serializers.ValidationError(
                "Для одиночного ответа можно отправлять только один вариант."
            )
        return data