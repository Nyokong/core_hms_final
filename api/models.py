import re
from django.core.exceptions import ValidationError

from django.db import models

import os
import logging
logger = logging.getLogger('api')

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
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(Group, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_perms')

    USERNAME_FIELD = 'username'
    
    # overwrite the model save function
    # this will do something before saving
    def save(self, *args, **kwargs):
        # overwrite the default email to the school email
        # this will set the default email into the default school email
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


# video uploading model
class Video(models.Model):
    user = models.ForeignKey(custUser, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="title", max_length=255)
    description = models.TextField(verbose_name="description", blank=True, null=True)
    cmp_video = models.FileField(verbose_name="cmp_video",upload_to='compressed_videos/', null=True, blank=False,)
    thumbnail = models.FileField(verbose_name="thumbail",upload_to='compressed_videos/thumbnail/', null=True, blank=True,)
    hls_name = models.CharField(verbose_name="Streaming_Path",max_length=255, blank=True, null=True)
    hls_path = models.FileField(verbose_name="hls_video",upload_to='compressed_videos/link_hls/', null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'uploaded by: {self.user} | {self.id} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the object is being created
            self.cmp_video.name = self.generate_filename()
        super(Video, self).save(*args, **kwargs)
        
        # save file path for streaming
        if not self.hls_path:
            name_without_extension = os.path.splitext(self.generate_filename())[0]
            self.hls_name = f"hls_videos/{name_without_extension}"
        super().save(*args, **kwargs)

    # generate a searchable file name
    def generate_filename(self):
        # Get the user ID
        user_id = self.user.id

        # Get the first 3 letters of the title
        title_code = self.title[:3].upper()

        # default
        new_number_str = "00001"

        if Video.objects.exists():
            # Get the last video
            last_video = Video.objects.order_by('-id').first()
            print(f"Last video: {last_video}\n")

            if last_video:
                try:
                    # Extract the numeric part of the filename
                    match = re.search(r'(\d+)(?=\.\w+$)', last_video.cmp_video.name)
                    if not match:
                        raise ValueError("No numeric part found in the filename")

                    number_str = match.group(1)
                    number = int(number_str)

                    # Increment the number
                    new_number = number + 1

                    # Pad the new number with leading zeros to match the original length
                    new_number_str = str(new_number)
                    # new_number_str = str(new_number).zfill(len(number_str))

                except (IndexError, ValueError)as e:
                    logger.warning(f"Error extracting number from filename: {e}")
            else:
                logger.warning('Last video was not found')
        else:
            print("No videos found.")

        # 1_TES00001.mp4
        # Combine elements to form the filename
        filename = f"{user_id}_{title_code}{new_number_str}.mp4"
        return filename

# assignment
class Assignment(models.Model):
    created_by = models.ForeignKey(custUser, on_delete=models.CASCADE, related_name='lecturer_creator')
    title = models.CharField(verbose_name="title", max_length=255)
    description = models.TextField(verbose_name="description", blank=True, null=True)

    # attachment is optional
    attachment= models.FileField(verbose_name="attachment",upload_to='attachments/', unique=False, null=True, blank=True)
    # the time it was created
    due_date = models.DateTimeField(verbose_name="due_date")
    created_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f'{self.title} - created: {self.created_at}'

    def clean(self):
        if not self.created_by.is_lecturer:
            raise ValidationError("Only lecturers can create assignments.")

# submitted
class Submission(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='assignment_being_submitted')
    student = models.ForeignKey(custUser, on_delete=models.CASCADE, related_name='student_submitting_assignment')
    # what they submitting
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video_being_submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.student.is_lecturer:
            raise ValidationError("Only students can submit assignments.")

# Grade
class Grade(models.Model):
    lecturer = models.ForeignKey(custUser, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    grade = models.DecimalField(verbose_name="Percentage Grade",max_digits=5, decimal_places=2)  # e.g.,'A++', 'A+', 'B-', etc.
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        def __str__(self):
            return f'Mark: {self.grade}/100'

    # get the letter grade
    def get_letter_grade(self):
        if self.grade >= 90:
            return 'A'
        elif self.grade >= 80:
            return 'B'
        elif self.grade >= 70:
            return 'C'
        elif self.grade >= 60:
            return 'D'
        else:
            return 'F'
        
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