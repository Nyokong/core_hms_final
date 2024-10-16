import re
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models

# from datetime import datetime

import os
import logging
logger = logging.getLogger('api')
from datetime import timezone

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
    student_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_lecturer = models.BooleanField(default=False)
    # email = models.EmailField(unique=True)

    groups = models.ManyToManyField(Group, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_perms')

    USERNAME_FIELD = 'username'
    
    # overwrite the model save function
    # this will do something before saving
    def save(self, *args, **kwargs):
        # overwrite the default email to the school email
        # this will set the default email into the default school email
        if self.username.isdigit():
            if not self.email:
                self.email = f"{self.student_number}@mynwu.ac.za"
        elif self.student_number==self.username:
            if not self.email:
                self.email = f"{self.student_number}@mynwu.ac.za"
        if self.student_number:
            if not self.email:
                self.email = f"{self.student_number}@mynwu.ac.za"

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username}'
    
    class Meta:
        unique_together = ('username',)

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

# assignment
class Assignment(models.Model):
    DRAFT = 'draft'
    ACTIVE = 'active'
    FINISHED = 'finished'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (ACTIVE, 'Active'),
        (FINISHED, 'Finished'),
    ]
    created_by = models.ForeignKey(custUser, on_delete=models.CASCADE, related_name='lecturer_creator')
    title = models.CharField(verbose_name="title", max_length=255)
    description = models.TextField(verbose_name="description", blank=True, null=True)

    # attachment is optional
    attachment= models.FileField(verbose_name="attachment",upload_to='attachments/', unique=False, null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=DRAFT,
    )
    total_submissions = models.PositiveIntegerField(default=0)
    # the time it was created
    due_date = models.DateTimeField(verbose_name="due_date")
    created_at = models.DateTimeField(auto_now_add=True)
    # student = models.ForeignKey(Student, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.id}: {self.status} - {self.total_submissions} submissions - created: {self.created_at}"

    def clean(self):
        if not self.created_by.is_lecturer:
            raise ValidationError("Only lecturers can create assignments.")
    
    def formatted_date(self):
        return self.created_at.strftime("%Y-%m-%d %I:%M %p")


# video uploading model
class Video(models.Model):
    user = models.ForeignKey(custUser, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE,verbose_name="assignment", related_name='assignment', default=None)
    title = models.CharField(verbose_name="title", max_length=255)
    description = models.TextField(verbose_name="description", blank=True, null=True)
    cmp_video = models.FileField(verbose_name="cmp_video",upload_to='compressed_videos/', null=True, blank=False,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'uploaded by: {self.user} | {self.id} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the object is being created
            self.cmp_video.name = self.generate_filename()
        super(Video, self).save(*args, **kwargs)

        super().save(*args, **kwargs)

    # generate a searchable file name
    def generate_filename(self):
        # Get the user ID
        user_id = self.user.id

        # Get the first 3 letters of the title
        title_code = self.title[:3].upper()

        # default
        # new_number_str = "00001"
        new_id = 1

        if Video.objects.exists():
            # Get the last video
            last_video = Video.objects.order_by('-id').first()

            if last_video:
                try:

                    new_id = last_video.id + 1
                except (IndexError, ValueError)as e:
                    logger.warning(f"Error extracting number from filename: {e}")
            else:
                logger.warning('Last video was not found')
                new_id = 1
        else:
            print("No videos found.")

        # 1_TES00001.mp4
        # Combine elements to form the filename
        filename = f"{user_id}_{title_code}{new_id}.mp4"
        return filename


# submitted
class Submission(models.Model):
    # title = models.CharField(max_length=100, null=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='assignment_being_submitted')
    student = models.ForeignKey(custUser, on_delete=models.CASCADE, related_name='student_submitting_assignment')
    # what they submitting
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video_being_submitted')
    grade = models.DecimalField(
        verbose_name="Percentage Grade",
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        null=True,
        blank=True
    )
    letter_grade = models.CharField(max_length=2, blank=True, null=True, default=None)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marked = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        self.letter_grade = self.get_letter_grade()
        super().save(*args, **kwargs)

    def get_letter_grade(self):
        if self.grade is None:
            return None
        if self.grade >= 90:
            return 'A'
        elif self.grade >= 75:
            return 'B'
        elif self.grade >= 50:
            return 'C'
        elif self.grade >= 30:
            return 'D'
        else:
            return 'F'

    def clean(self):
        if self.student.is_lecturer:
            raise ValidationError("Only students can submit assignments.")

    def __str__(self):
        return f"Submission for assignment {self.assignment.id} time: {self.submitted_at} Mark: {self.grade}/100"

class FeedbackRoom(models.Model): 
    # this is all the conversations they've had
    lecturer = models.ForeignKey(custUser, on_delete=models.CASCADE, related_name='lecturer_in_feedback')
    student = models.ForeignKey(custUser, on_delete=models.CASCADE, related_name='student_in_feedback')
    # we want to know what they talking about 
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='submission_ref')

class FeedbackMessage(models.Model):
    feedback_room = models.ForeignKey(FeedbackRoom, on_delete=models.CASCADE, related_name='feedbackroom_ref')
    # logic is one user ia student and the other is a lecturer
    sender = models.ForeignKey(custUser, on_delete=models.CASCADE, related_name='sender_of_message')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
            

class VerificationToken(models.Model):
    user = models.ForeignKey(custUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=32,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PasswordResetToken(models.Model):
    user = models.ForeignKey(custUser, on_delete =models.CASCADE)
    token = models.CharField(max_length=100, unique =True)
    created_at = models.DateTimeField( auto_now_add=True)

    def is_token_valid(self):
        return (timezone.now() - self.created_at.days <1) #valid for 1 day