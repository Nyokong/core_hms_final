import re
from django.core.exceptions import ValidationError

from django.db import models

# importing abstract user
from django.contrib.auth.models import AbstractUser, Group, Permission

# validate email
def validate_email(email):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(email_regex, email):
        raise ValidationError('Enter a valid email address.')


# my user model
class custUser(AbstractUser):
    username = models.CharField(verbose_name="Username", max_length=8, unique=True)
    is_lecturer = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_perms')

    USERNAME_FIELD = 'username'
    
    # overwrite the model save function
    # this will do something before saving
    def save(self, *args, **kwargs):
        # overwrite the default email to the school email
        # this will set the default email into the default school email
        if not self.email:
            self.email = f"{self.username}@mynwu.ac.za" 

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username}'


# lecturer model
class Lecturer(models.Model):
    emp_num = models.CharField(verbose_name="Employee Number", max_length=8, unique=True)

    def __str__(self):
        return f'{self.emp_num}'

# student model
class Student(models.Model):
    student_num = models.CharField(verbose_name="Student Number", max_length=8, unique=True)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.student_num}'

class FeedbackMessage(models.Model):
    user = models.ForeignKey(custUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
