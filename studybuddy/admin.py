from django.contrib import admin

from .models import Profile, Course, StudySession, MessageTwo

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(StudySession)
admin.site.register(MessageTwo)