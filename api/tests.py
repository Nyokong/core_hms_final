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

from django.core import mail
from decimal import Decimal
from rest_framework.test import APITestCase
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

class FeedbackRoomModelTest(TestCase):

    def setUp(self):
        self.lecturer = custUser.objects.create(username='lecturer', student_number='12345678', is_lecturer=True)
        self.student = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        self.assignment = Assignment.objects.create(created_by=self.lecturer, title='Test Assignment', due_date=timezone.now() + timezone.timedelta(days=1))
        self.submission = Submission.objects.create(assignment=self.assignment, student=self.student, video=self.student)
        self.feedback_room = FeedbackRoom.objects.create(lecturer=self.lecturer, student=self.student, submission=self.submission)

    def test_feedback_room_creation(self):
        self.assertEqual(self.feedback_room.lecturer.username, 'lecturer')
        self.assertEqual(self.feedback_room.student.username, 'student')
        self.assertEqual(self.feedback_room.submission.assignment.title, 'Test Assignment')

class FeedbackMessageModelTest(TestCase):

    def setUp(self):
        self.lecturer = custUser.objects.create(username='lecturer', student_number='12345678', is_lecturer=True)
        self.student = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        self.assignment = Assignment.objects.create(created_by=self.lecturer, title='Test Assignment', due_date=timezone.now() + timezone.timedelta(days=1))
        self.submission = Submission.objects.create(assignment=self.assignment, student=self.student, video=self.student)
        self.feedback_room = FeedbackRoom.objects.create(lecturer=self.lecturer, student=self.student, submission=self.submission)
        self.feedback_message = FeedbackMessage.objects.create(feedback_room=self.feedback_room, sender=self.lecturer, message='Great job!')

    def test_feedback_message_creation(self):
        self.assertEqual(self.feedback_message.feedback_room.lecturer.username, 'lecturer')
        self.assertEqual(self.feedback_message.sender.username, 'lecturer')
        self.assertEqual(self.feedback_message.message, 'Great job!')

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

class VerificationViewTests(TestCase):

    def setUp(self):
        self.user = custUser.objects.create_user(
            username='testuser', email='testuser@example.com', password='password123')
        self.verification_token = VerificationToken.objects.create(user=self.user)

    def test_verification_success(self):
        url = reverse('verify-email', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)), 'token': self.verification_token.token})
        response = self.client.get(url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verification_invalid_token(self):
        url = reverse('verify-email', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)), 'token': 'invalid_token'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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


# class DeleteUserViewTests(TestCase):

#     def setUp(self):
#         # Create users
#         self.admin_user = custUser.objects.create_user(username='adminuser', password='adminpass', is_staff=True)
#         self.user = custUser.objects.create_user(username='testuser', password='testpass')
#         self.other_user = custUser.objects.create_user(username='otheruser', password='otherpass')
#         self.client.login(username='adminuser', password='adminpass')
#         self.url = reverse('user-delete', args=[self.other_user.id])
#         self.self_delete_url = reverse('user-delete', args=[self.admin_user.id])

#     def test_delete_user_success(self):
#         response = self.client.delete(self.url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(custUser.objects.filter(id=self.other_user.id).exists())

#     def test_delete_self_forbidden(self):
#         response = self.client.delete(self.self_delete_url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertTrue(custUser.objects.filter(id=self.admin_user.id).exists())
      
class FeedbackMessagesTests(TestCase):
    def setUp(self):
        self.user = custUser.objects.create_user(username='feedbackuser', password='feedbackpass')
        self.feedback_message = FeedbackMessage.objects.create(user=self.user, content='Test feedback')

    def test_get_feedback_messages(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('feedback-list') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


#Test Serializers
class CustomSignupSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_valid_data_creates_user(self):
        request = self.factory.post('/signup/')
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!'
        }
        serializer = CustomSignupSerializer(data=data, context={'request': request})
        
        self.assertTrue(serializer.is_valid(), serializer.errors)  # Print errors for debugging
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('ComplexPassword123!'))

    def test_invalid_email(self):
        custUser.objects.create_user(username='existinguser', email='existing@example.com', password='password')
        data = {
            'email': 'existing@example.com',
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password123'
        }
        serializer = CustomSignupSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_password_mismatch(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'ComplexPassword123!',
            'password2': 'DifferentComplexPassword123!'
        }
        serializer = CustomSignupSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class UserSerializerTests(TestCase):
    
    def test_valid_data_creates_user(self):
        data = {
            'username': 'studentuser',
            'student_number': '12345678',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'student@example.com',
            'password': 'password123',
            'password2': 'password123'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'studentuser')
        self.assertTrue(user.check_password('password123'))

    def test_password_mismatch(self):
        data = {
            'username': 'studentuser',
            'student_number': '12345678',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'student@example.com',
            'password': 'password123',
            'password2': 'differentpassword'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_email_already_exists(self):
        custUser.objects.create_user(username='existinguser', email='student@example.com', password='password')
        data = {
            'username': 'newuser',
            'student_number': '87654321',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'student@example.com',
            'password': 'password123',
            'password2': 'password123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class UserUpdateSerializerTests(TestCase):
    
    def test_valid_update(self):
        user = custUser.objects.create_user(username='updateuser', password='password123')
        data = {
            'username': 'updateduser',
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast'
        }
        serializer = UserUpdateSerializer(instance=user, data=data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, 'updateduser')

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
    
    def test_delete_user(self):
        user = custUser.objects.create_user(username='deleteuser', password='password123')
        serializer = UserDeleteSerializer()
        self.assertEqual(user.id, serializer.delete_user(user))
        self.assertRaises(custUser.DoesNotExist, custUser.objects.get, id=user.id)

class LoginSerializerTests(TestCase):
    
    def test_valid_login(self):
        custUser.objects.create_user(username='loginuser', password='password123')
        data = {
            'username': 'loginuser',
            'password': 'password123'
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_credentials(self):
        data = {
            'username': 'nonexistentuser',
            'password': 'wrongpassword'
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class AssignmentFormTests(TestCase):
    
    def test_valid_assignment_creation(self):
        user = custUser.objects.create_user(username='lecturer', password='password123', is_lecturer=True)
        self.client.login(username='lecturer', password='password123')
        data = {
            'title': 'Test Assignment',
            'description': 'This is a test assignment.',
            'due_date': timezone.now()
        }
        serializer = AssignmentForm(data=data, context={'request': self.client})
        self.assertTrue(serializer.is_valid())
        assignment = serializer.save()
        self.assertEqual(assignment.title, 'Test Assignment')

    def test_invalid_assignment_creation(self):
        user = custUser.objects.create_user(username='lecturer', password='password123', is_lecturer=True)
        self.client.login(username='lecturer', password='password123')
        data = {
            'title': '',
            'description': 'This is a test assignment.',
            'due_date': timezone.now()
        }
        serializer = AssignmentForm(data=data, context={'request': self.client})
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

class VideoSerializerTests(TestCase):
    
    def test_valid_video_creation(self):
        user = custUser.objects.create_user(username='student', password='password123')
        self.client.login(username='student', password='password123')
        data = {
            'title': 'Test Video',
            'description': 'This is a test video.',
            'cmp_video': self.get_test_video_file()  # Assume this is a helper method that returns a valid video file
        }
        serializer = VideoSerializer(data=data, context={'request': self.client})
        self.assertTrue(serializer.is_valid())
        video = serializer.save()
        self.assertEqual(video.title, 'Test Video')

    def test_invalid_video_creation(self):
        user = custUser.objects.create_user(username='student', password='password123')
        self.client.login(username='student', password='password123')
        data = {
            'title': '',
            'description': 'This is a test video.',
            'cmp_video': self.get_test_video_file()
        }
        serializer = VideoSerializer(data=data, context={'request': self.client})
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

class FeedbackMsgSerializerTests(TestCase):
    
    def test_valid_feedback_creation(self):
        user = custUser.objects.create_user(username='feedbackuser', password='password123')
        self.client.login(username='feedbackuser', password='password123')
        data = {
            'feedback_room': 'Room 1',
            'message': 'This is a feedback message.',
            'timestamp': timezone.now()
        }
        serializer = FeedbackMsgSerializer(data=data, context={'request': self.client})
        self.assertTrue(serializer.is_valid())
        feedback_message = serializer.save()
        self.assertEqual(feedback_message.message, 'This is a feedback message.')

    def test_invalid_feedback_creation(self):
        user = custUser.objects.create_user(username='feedbackuser', password='password123')
        self.client.login(username='feedbackuser', password='password123')
        data = {
            'feedback_room': 'Room 1',
            'message': '',
            'timestamp': timezone.now()
        }
        serializer = FeedbackMsgSerializer(data=data, context={'request': self.client})
        self.assertFalse(serializer.is_valid())
        self.assertIn('message', serializer.errors)


