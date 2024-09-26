from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse, resolve

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.core.files.base import ContentFile
from unittest.mock import MagicMock
import tempfile
import os

from django.core import mail
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserSerializer, CustomSignupSerializer, UserUpdateSerializer, UserDeleteSerializer, LoginSerializer, AssignmentForm, VideoSerializer, FeedbackMsgSerializer
from .models import custUser, Lecturer, Student, Video, Assignment, Submission, Grade, FeedbackRoom, FeedbackMessage, VerificationToken
from .views import (
    UserCreateView, UserUpdateView, LoginAPIView, UserListViewSet, VerifyEmailView, DeleteUserView, UserProfileView, AddStudentNumberView,
    GoogAftermathView, AssignmentListView, AssignmentCreateView, AssignmentUpdateView, AssignmentDeleteView, VideoView, DeleteVideoView, FeedbackMessages, GoogleLoginView
)

# Model Tests

class CustUserModelTest(TestCase):

    def setUp(self):
        self.user = custUser.objects.create(username='testuser', student_number='12345678')

    def test_email_default_generation(self):
        self.assertEqual(self.user.email, '12345678@mynwu.ac.za')

    def test_invalid_email_raises_validation_error(self):
        self.user.email = 'invalid-email'
        with self.assertRaises(ValidationError):
            self.user.full_clean()

class LecturerModelTest(TestCase):

    def setUp(self):
        self.lecturer = Lecturer.objects.create(emp_num='L1234567')

    def test_lecturer_creation(self):
        self.assertEqual(self.lecturer.emp_num, 'L1234567')

class StudentModelTest(TestCase):

    def setUp(self):
        self.student = Student.objects.create(student_num='S1234567')

    def test_student_creation(self):
        self.assertEqual(self.student.student_num, 'S1234567')

class VideoModelTest(TestCase):

    def setUp(self):
        self.user = custUser.objects.create(username='testuser', student_number='12345678')
        self.video = Video.objects.create(user=self.user, title='Test Video')

    def test_video_creation(self):
        self.assertEqual(self.video.title, 'Test Video')
        self.assertEqual(self.video.user.username, 'testuser')

class AssignmentModelTest(TestCase):

    def setUp(self):
        self.user = custUser.objects.create(username='lecturer', student_number='12345678', is_lecturer=True)
        self.assignment = Assignment.objects.create(created_by=self.user, title='Test Assignment', due_date=timezone.now() + timezone.timedelta(days=1))

    def test_assignment_creation(self):
        self.assertEqual(self.assignment.title, 'Test Assignment')
        self.assertEqual(self.assignment.created_by.username, 'lecturer')

    def test_invalid_assignment_creation_by_non_lecturer(self):
        non_lecturer = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        assignment = Assignment(created_by=non_lecturer, title='Invalid Assignment', due_date=timezone.now())
        with self.assertRaises(ValidationError):
            assignment.full_clean()

class SubmissionModelTest(TestCase):

    def setUp(self):
        self.lecturer = custUser.objects.create(username='lecturer', student_number='12345678', is_lecturer=True)
        self.student = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        self.assignment = Assignment.objects.create(created_by=self.lecturer, title='Test Assignment', due_date=timezone.now() + timezone.timedelta(days=1))
        self.submission = Submission.objects.create(assignment=self.assignment, student=self.student, video=self.student)

    def test_submission_creation(self):
        self.assertEqual(self.submission.assignment.title, 'Test Assignment')
        self.assertEqual(self.submission.student.username, 'student')

    def test_invalid_submission_by_lecturer(self):
        with self.assertRaises(ValidationError):
            Submission.objects.create(assignment=self.assignment, student=self.lecturer, video=self.lecturer).full_clean()

class GradeModelTest(TestCase):

    def setUp(self):
        self.lecturer = custUser.objects.create(username='lecturer', student_number='12345678', is_lecturer=True)
        self.student = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        self.assignment = Assignment.objects.create(created_by=self.lecturer, title='Test Assignment', due_date=timezone.now())
        self.submission = Submission.objects.create(assignment=self.assignment, student=self.student, video=self.student)
        self.grade = Grade.objects.create(lecturer=self.lecturer, submission=self.submission, grade=Decimal('85.00'))

    def test_grade_creation(self):
        self.assertEqual(self.grade.grade, Decimal('85.00'))
        self.assertEqual(self.grade.lecturer.username, 'lecturer')
        self.assertEqual(self.grade.submission.assignment.title, 'Test Assignment')

    def test_get_letter_grade(self):
        self.assertEqual(self.grade.get_letter_grade(), 'B')

class VerificationTokenModelTest(TestCase):

    def setUp(self):
        self.user = custUser.objects.create(username='testuser', student_number='12345678')
        self.token = VerificationToken.objects.create(user=self.user, token='abcd1234')

    def test_verification_token_creation(self):
        self.assertEqual(self.token.user.username, 'testuser')
        self.assertEqual(self.token.token, 'abcd1234')


#Test Urls
class TestUrls(TestCase):

    def test_create_user_url_is_resolved(self):
        url = reverse('create-user')
        self.assertEqual(resolve(url).func.view_class, UserCreateView)

    def test_update_user_url_is_resolved(self):
        url = reverse('user-update')
        self.assertEqual(resolve(url).func.view_class, UserUpdateView)

    def test_login_user_url_is_resolved(self):
        url = reverse('login-user')
        self.assertEqual(resolve(url).func.view_class, LoginAPIView)

    def test_users_url_is_resolved(self):
        url = reverse('users')
        self.assertEqual(resolve(url).func.view_class, UserListViewSet)

    def test_verify_email_url_is_resolved(self):
        url = reverse('verify-email', args=['uidb64', 'token'])
        self.assertEqual(resolve(url).func.view_class, VerifyEmailView)

    def test_delete_user_url_is_resolved(self):
        url = reverse('user-delete', args=[1])
        self.assertEqual(resolve(url).func.view_class, DeleteUserView)
    def test_user_profile_url_is_resolved(self):
        url = reverse('user-profile-read')
        self.assertEqual(resolve(url).func.view_class, UserProfileView)

    def test_add_student_number_url_is_resolved(self):
        url = reverse('add-student-number')
        self.assertEqual(resolve(url).func.view_class, AddStudentNumberView)

    def test_thank_you_url_is_resolved(self):
        url = reverse('thank-you')
        self.assertEqual(resolve(url).func.view_class, GoogAftermathView)

    def test_token_obtain_pair_url_is_resolved(self):
        url = reverse('token_obtain_pair')
        self.assertEqual(resolve(url).func.view_class, TokenObtainPairView)

    def test_token_refresh_url_is_resolved(self):
        url = reverse('token_refresh')
        self.assertEqual(resolve(url).func.view_class, TokenRefreshView)

    def test_list_assignment_url_is_resolved(self):
        url = reverse('list-assignment')
        self.assertEqual(resolve(url).func.view_class, AssignmentListView)

    def test_create_assignment_url_is_resolved(self):
        url = reverse('create-assignments')
        self.assertEqual(resolve(url).func.view_class, AssignmentCreateView)

    def test_update_assignment_url_is_resolved(self):
        url = reverse('assignment-update', args=[1])
        self.assertEqual(resolve(url).func.view_class, AssignmentUpdateView)

    def test_delete_assignment_url_is_resolved(self):
        url = reverse('assignment-delete', args=[1])
        self.assertEqual(resolve(url).func.view_class, AssignmentDeleteView)

    def test_video_list_url_is_resolved(self):
        url = reverse('video-list')
        self.assertEqual(resolve(url).func.view_class, VideoView)

    def test_delete_video_url_is_resolved(self):
        url = reverse('video-delete', args=[1])
        self.assertEqual(resolve(url).func.view_class, DeleteVideoView)

    def test_feedback_room_messages_url_is_resolved(self):
        url = reverse('feedback_room_messages', args=[1])
        self.assertEqual(resolve(url).func.view_class, FeedbackMessages)

#Test Views
class UserCreateViewTests(TestCase):

    def test_create_user(self):
        url = reverse('create-user')
        data = {
            'username': 'testuser',
            'student_number': '12345678',
            'email': 'testuser@example.com',
            'password': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
            'first_name': 'Test',  # Add the first_name field here
            'last_name': 'User'    # You might also need to add last_name if required
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "User created successfully. Please check your email to verify account.")

    def test_create_user_invalid_data(self):
        url = reverse('create-user')
        data = {
            'username': '',
            'student_number': '12345678',
            'email': 'invalid-email',
            'password': 'password123',
            'password2': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)

# class VerificationViewTests(TestCase):

#     def setUp(self):
#         self.user = custUser.objects.create_user(
#             username='testuser', email='testuser@example.com', password='password123')
#         self.verification_token = VerificationToken.objects.create(user=self.user)

#     def test_verification_success(self):
#         url = reverse('verify-email', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)), 'token': self.verification_token.token})
#         response = self.client.get(url)
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.is_active)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_verification_invalid_token(self):
#         url = reverse('verify-email', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)), 'token': 'invalid_token'})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserUpdateViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = custUser.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')  # Log in the user

    def test_user_update_success(self):
        url = reverse('user-update')  # Make sure to use the correct URL name
        data = {
            'username': 'testuser',  # Include the username
            'email': 'validemail@example.com',  # Use a valid email
            'first_name': 'UpdatedName'  # Provide the first name
        }
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class LoginAPIViewTests(TestCase):

    def setUp(self):
        self.user = custUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.url = reverse('login-user')

    def test_login_success(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sessionid', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class DeleteUserViewTests(TestCase):

    def setUp(self):
        self.admin_user = custUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')
        self.user_to_delete = custUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Astrongpassword123!'
        )

    def test_delete_user_success(self):
        url = reverse('user-delete', args=[self.user_to_delete.id])  # Adjust based on your URL conf
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_self_forbidden(self):
        self.client.logout()  # Ensure the previous user is logged out
        self.client.login(username='testuser', password='Astrongpassword123!')
        url = reverse('user-delete', args=[self.user_to_delete.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


#Test Serializers

class CustomSignupSerializerTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.valid_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }
        
        self.invalid_data = {
            'email': 'invalid_email',
            'username': '',
            'password1': 'StrongPassword123!',
            'password2': 'DifferentPassword123!',
        }
        
        # Create a mock request object with a session
        self.request = self.factory.post('/signup/', data=self.valid_data)
        self.request.session = {}  # Mock session

    def test_valid_signup(self):
        serializer = CustomSignupSerializer(data=self.valid_data, context={'request': self.request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.username, self.valid_data['username'])
        self.assertEqual(user.email, self.valid_data['email'])

    def test_unique_username(self):
        custUser.objects.create_user(username='testuser', email='existing@example.com', password='password123')
        
        serializer = CustomSignupSerializer(data=self.valid_data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_unique_email(self):
        custUser.objects.create_user(username='otheruser', email='test@example.com', password='password123')
        
        serializer = CustomSignupSerializer(data=self.valid_data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_passwords_do_not_match(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'DifferentPassword123!'  # Change the second password
        serializer = CustomSignupSerializer(data=invalid_data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)  # Check for password mismatch error

    def test_invalid_email(self):
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid_email'  # Invalid email format
        serializer = CustomSignupSerializer(data=invalid_data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)  # Ensure invalid email error is captured

class UserSerializerTests(TestCase):

    def setUp(self):
        self.valid_data = {
            'username': 'testuser',
            'student_number': '12345678',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'Astrongpassword123!',
            'password2': 'Astrongpassword123!'
        }
        
        self.invalid_data = {
            'username': '',
            'student_number': '12345678',
            'first_name': '',
            'last_name': '',
            'email': '',  # Intentionally blank for testing
            'password': '',
            'password2': ''
        }

    def test_valid_user_creation(self):
        serializer = UserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.username, self.valid_data['username'])

    def test_required_fields(self):
        serializer = UserSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        
        # Check for specific required fields
        self.assertIn("username", serializer.errors)
        self.assertIn("email", serializer.errors)
        self.assertIn("password", serializer.errors)
        self.assertIn("password2", serializer.errors)

    def test_email_validation(self):
        invalid_email_data = self.invalid_data.copy()
        invalid_email_data['email'] = 'invalid_email'  # Invalid format
        serializer = UserSerializer(data=invalid_email_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)  # This should be present for invalid email format

        empty_email_data = self.invalid_data.copy()
        empty_email_data['email'] = ''  # Blank email
        serializer = UserSerializer(data=empty_email_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)  # Ensure this is captured as an error

class UserUpdateSerializerTests(TestCase):
    
    def test_valid_update(self):
        serializer = UserUpdateSerializer(data={
            'username': 'newuser',
            'email': 'newemail@example.com',
        })

    def test_invalid_update(self):
        user = custUser.objects.create_user(username='updateuser', password='password123')
        data = {
            'username': '',
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast'
        }
        serializer = UserUpdateSerializer(instance=user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

class UserDeleteSerializerTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_delete_user(self):
        serializer = UserDeleteSerializer()
        serializer.delete_user(self.user)
        self.assertFalse(get_user_model().objects.filter(id=self.user.id).exists())

class LoginSerializerTests(TestCase):
    def test_valid_login(self):
        custUser.objects.create_user(username='testuser', password='testpassword')

        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        serializer = LoginSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_credentials(self):
        data = {
            'username': 'invalidu',  
            'password': 'wrongpas'
        }
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class AssignmentFormTests(TestCase):

    def setUp(self):
        self.assignment_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        self.assignment_file.write(b'This is a test assignment file.')
        self.assignment_file.close()

        # Create a student user
        self.student = custUser.objects.create_user(username='student', password='password', is_lecturer=False)

        self.request = MagicMock()
        self.request.user = self.student

    def tearDown(self):
        # Remove the temporary assignment file after tests
        if os.path.exists(self.assignment_file.name):
            os.remove(self.assignment_file.name)

    def test_valid_assignment_creation(self):
        data = {
            'title': 'Test Assignment',
            'description': 'A description for the test assignment.',
            'file': ContentFile(open(self.assignment_file.name, 'rb').read(), name='test_assignment.pdf'),
            'due_date': timezone.now() + timezone.timedelta(days=7)  # Ensure a valid due date is provided
        }
        serializer = AssignmentForm(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid(), serializer.errors)  # Check if the serializer is valid
        assignment = serializer.save()
        self.assertEqual(assignment.title, 'Test Assignment')
        self.assertEqual(assignment.description, 'A description for the test assignment.')
        self.assertIsNotNone(assignment.due_date)  # Ensure due_date is set

    def test_invalid_assignment_creation(self):
        data = {
            'title': '',  # Invalid title
            'description': 'A description for the test assignment.',
            'file': ContentFile(open(self.assignment_file.name, 'rb').read(), name='test_assignment.pdf'),
            'due_date': None  # Make due_date invalid
        }
        serializer = AssignmentForm(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())  # Check if the serializer is invalid
        self.assertIn('title', serializer.errors)  # Ensure the error is related to the title
        self.assertIn('due_date', serializer.errors)  # Ensure that due_date error is also checked

class VideoSerializerTests(TestCase):

    def setUp(self):
        # Create a temporary video file for testing
        self.video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        self.video_file.write(b'This is a test video file.')
        self.video_file.close()

        # Assuming you have a student user created for the tests
        self.student = custUser.objects.create_user(username='student', password='password', is_lecturer=False)

        # Create a mock request object
        self.request = MagicMock()
        self.request.user = self.student

    def tearDown(self):
        # Remove the temporary video file after tests
        if os.path.exists(self.video_file.name):
            os.remove(self.video_file.name)

    def test_valid_video_creation(self):
        data = {
            'title': 'Test Video',
            'description': 'A description for the test video.',
            'cmp_video': ContentFile(open(self.video_file.name, 'rb').read(), name='test_video.mp4')
        }
        serializer = VideoSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid(), serializer.errors)  # Check if the serializer is valid
        video = serializer.save()
        self.assertEqual(video.title, 'Test Video')
        self.assertEqual(video.description, 'A description for the test video.')

    def test_invalid_video_creation(self):
        data = {
            'title': '',  # Invalid title
            'description': 'A description for the test video.',
            'cmp_video': ContentFile(open(self.video_file.name, 'rb').read(), name='test_video.mp4')
        }
        serializer = VideoSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())  # Check if the serializer is invalid
        self.assertIn('title', serializer.errors)  # Ensure the error is related to the title
