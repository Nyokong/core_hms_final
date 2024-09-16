from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from .models import FeedbackMessage, custUser, Student, Lecturer   

class CustomUserAdmin(UserAdmin): 

    exclude = ('date joined' ,'custom_user_perms', 'last login', 'custom_users', 'superuser status')

    # If you're using fieldsets:
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name' ,'email', 'password', 'is_staff', 'is_active')}),
    )

# Register your models here.
admin.site.register(custUser, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(FeedbackMessage)

