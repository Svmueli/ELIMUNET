
# Register your models here.
from django.contrib import admin
from .models import UserProfile, Classroom, Assignment, Quiz, Announcement, Submission, Grade, ClassComment, PrivateMessage

admin.site.register(UserProfile)
admin.site.register(Classroom)
admin.site.register(Assignment)
admin.site.register(Quiz)
admin.site.register(Announcement)
admin.site.register(Submission)
admin.site.register(Grade)
admin.site.register(ClassComment)
admin.site.register(PrivateMessage)
