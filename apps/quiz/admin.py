from django.contrib import admin
from .models import Test, Question, UserTestResult

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(UserTestResult)