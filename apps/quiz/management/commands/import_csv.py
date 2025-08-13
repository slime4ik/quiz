import csv
import logging
from django.core.management.base import BaseCommand
from apps.quiz.models import Test, Question

logger = logging.getLogger('quiz')

class Command(BaseCommand):
    help = "Импорт тестов и вопросов из CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Путь до CSV-файла с тестом")

    def handle(self, *args, **options):
        csv_path = options["csv_file"]
        created_count = 0
        tests_cache = {}

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Кэшируем тесты, чтобы не делать лишних запросов
                    title = row["test_title"]
                    if title not in tests_cache:
                        # В случае если тест с таким title уже есть
                        tests_cache[title], _ = Test.objects.get_or_create(title=title)
                    test = tests_cache[title]

                    choices = [c.strip() for c in row["choices"].split(";")]
                    answers = [a.strip() for a in row["answers"].split(";")]

                    Question.objects.create(
                        test=test,
                        type=row["type"],  # SN/ML
                        text=row["question_text"],
                        choices=choices,
                        answers=answers,
                    )
                    created_count += 1

                except Exception as e:
                    logger.error(f'Ошибка при импорте вопроса: {e}', exc_info=True)

        logger.info(f'Импорт из {csv_path} завершён. Добавлено {created_count} вопросов.')
