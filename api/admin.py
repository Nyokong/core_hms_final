from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from .models import FeedbackMessage, custUser, Student, Lecturer, Assignment, Video, Submission
from .models import VerificationToken, FeedbackRoom

class CustomUserAdmin(UserAdmin): 

    exclude = ('date joined' ,'custom_user_perms', 'last login', 'custom_users', 'superuser status')

    # If you're using fieldsets:
    fieldsets = (
        (None, {'fields': ('username', 'student_number','first_name', 'last_name' ,'email', 'password', 'is_lecturer','is_staff', 'is_active')}),
    )

# Register your models here.
admin.site.register(custUser, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(FeedbackMessage)
admin.site.register(Video)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(VerificationToken)
admin.site.register(FeedbackRoom)

