from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
from django.contrib.postgres.fields import ArrayField
from django.conf import settings


# ========= Абстрактные модели ============
class BaseCreateModel(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid4,
                          editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
# ========= Абстрактные модели ============


class User(AbstractUser):
    pass


class Test(BaseCreateModel):
    title = models.CharField(max_length=75,
                             unique=True,
                             editable=False)

class Question(models.Model):
    # Выбор типа вопроса
    class Type(models.TextChoices):
        SINGLE = 'SN', 'Один вариант ответа'
        MULTIPLE = 'ML', 'Несколько вариантов ответа'
        

    id = models.UUIDField(primary_key=True,
                          default=uuid4,
                          editable=False)
    test = models.ForeignKey(Test,
                             on_delete=models.CASCADE,
                             related_name='questions')
    # Тип вопроса т.е. много/один ответ(ов)
    type = models.CharField(max_length=2,
                                 choices=Type.choices,
                                 default=Type.SINGLE)
    text = models.CharField(max_length=300)
    # Вариант(ы) ответа
    choices = ArrayField(
        models.CharField(max_length=300),
        blank=False
    )
    # Ответ(ы)
    answers = ArrayField(
        models.CharField(max_length=300),
        blank=True,
        default=list,
    )
    
    def __str__(self):
        return f'{self.test.title}, вопрос:{self.text[:15]}'
    
class UserTestResult(models.Model):
    """Хранение пройденных тестов пользователем"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='user_results')
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'test')