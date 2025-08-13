from django.utils import timezone
from django.core.cache import cache
from apps.quiz.constants import ANSWERS_TTL
from apps.quiz.models import Test, UserTestResult


class QuizService:
    def __init__(self, user, test_id):
        self.user = user
        self.test_id = test_id
        self.cache_key = f'quiz_progress:{user.id}:{test_id}'
        self.init_cache()

    def init_cache(self):
        """Инициализация кеша если его нет"""
        if not cache.get(self.cache_key):
            cache.set(self.cache_key, {
                'current_question': 0,
                'answers': {},
                'started_at': timezone.now().isoformat(),
                'is_completed': False,
                'score': 0
            }, timeout=ANSWERS_TTL)

    def get_state(self):
        """Текущее состояние теста"""
        data = cache.get(self.cache_key)
        test = Test.objects.prefetch_related('questions').get(pk=self.test_id)
        questions = list(test.questions.all())

        if data['is_completed']:
            return {'status': 'completed', 'score': data['score']}

        if data['current_question'] >= len(questions):
            return self.complete_test(data, test)

        current_question = questions[data['current_question']]

        return {
            'status': 'in_progress',
            'current_question': {
                'id': current_question.id,
                'text': current_question.text,
                'choices': current_question.choices,
                'type': current_question.type
            },
            'current_index': data['current_question'],
            'total_questions': len(questions)
        }

    def answer_current(self, answer):
        """Сохранение ответа и переход к следующему вопросу"""
        data = cache.get(self.cache_key)
        test = Test.objects.prefetch_related('questions').get(pk=self.test_id)
        questions = list(test.questions.all())

        if data['is_completed'] or data['current_question'] >= len(questions):
            return self.get_state()

        current_question = questions[data['current_question']]
        data['answers'][str(current_question.id)] = answer

        # Подсчет баллов для текущего вопроса
        correct = set(current_question.answers)
        given = set(answer) if isinstance(answer, list) else {answer}
        if correct == given:
            data['score'] += 1

        data['current_question'] += 1

        if data['current_question'] >= len(questions):
            return self.complete_test(data, test)

        cache.set(self.cache_key, data, timeout=ANSWERS_TTL)
        return self.get_state()

    def complete_test(self, data, test):
        """Завершение теста и сохранение результата"""
        data['is_completed'] = True
        cache.set(self.cache_key, data, timeout=ANSWERS_TTL)
        UserTestResult.objects.update_or_create(
            user=self.user,
            test=test,
            defaults={'score': data['score']}
        )
        return {'status': 'completed', 'score': data['score']}
