from django.contrib import admin
from .models import TeaLesson
from .models import User

admin.site.register(User)
admin.site.register(TeaLesson)
