from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse, resolve

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserSerializer, CustomSignupSerializer
from .models import custUser, Lecturer, Student, Video, Assignment, Submission, Grade, FeedbackRoom, FeedbackMessage, VerificationToken
from .views import (
    UserCreateView, UserUpdateView, LoginAPIView, UserListViewSet, VerifyEmailView, DeleteUserView, UserProfileView, AddStudentNumberView,
    GoogAftermathView, AssignmentListView, AssignmentCreateView, AssignmentUpdateView, AssignmentDeleteView, VideoView, DeleteVideoView, FeedbackMessages
)

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


# class VerificationViewTest(APITestCase):

#     def setUp(self):
#         # Set up a user and a verification token for testing
#         self.user = custUser.objects.create_user(username='testuser', password='testpassword', is_active=False)
#         self.token = VerificationToken.objects.create(user=self.user, token='validtoken')
#         self.url = reverse('verification')  # Update 'verification' with the actual URL name for this view

#     def test_user_activation_success(self):
#         # Test successful activation with a valid token
#         response = self.client.get(self.url, {'token': self.token.token})
#         self.user.refresh_from_db()  # Refresh the user instance from the database

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(self.user.is_active)
#         self.assertEqual(response.data['message'], 'User activated successfully')

#     def test_invalid_token(self):
#         # Test the response with an invalid token
#         response = self.client.get(self.url, {'token': 'invalidtoken'})
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], 'Invalid verification token')

#     def test_user_does_not_exist(self):
#         # Test the response when the user does not exist (for completeness)
#         self.token.user.delete()  # Delete the user to simulate a DoesNotExist error
#         response = self.client.get(self.url, {'token': self.token.token})
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], 'User DoesntExisist')



#Test Serializers

# class CustomSignupSerializerTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.request = self.factory.post('/api/usr/create')
#         self.valid_data = {
#             'username': 'testuser',
#             'email': 'testuser@example.com',
#             'password1': 'strongpassword123',
#             'password2': 'strongpassword123'
#         }
#         self.invalid_data = {
#             'username': '',
#             'email': 'invalid-email',
#             'password1': 'password123',
#             'password2': 'password123'
#         }

#     def test_valid_data(self):
#         serializer = CustomSignupSerializer(data=self.valid_data, context={'request': self.request})
#         self.assertTrue(serializer.is_valid())
#         user = serializer.save()
#         self.assertEqual(user.username, self.valid_data['username'])
#         self.assertEqual(user.email, self.valid_data['email'])
#         self.assertTrue(user.check_password(self.valid_data['password1']))

#     def test_invalid_username(self):
#         data = self.valid_data.copy()
#         data['username'] = ''
#         serializer = CustomSignupSerializer(data=data, context={'request': self.request})
#         self.assertFalse(serializer.is_valid())
#         self.assertIn('username', serializer.errors)

#     def test_invalid_email(self):
#         data = self.valid_data.copy()
#         data['email'] = 'invalid-email'
#         serializer = CustomSignupSerializer(data=data, context={'request': self.request})
#         self.assertFalse(serializer.is_valid())
#         self.assertIn('email', serializer.errors)

#     def test_password_mismatch(self):
#         data = self.valid_data.copy()
#         data['password2'] = 'differentpassword'
#         serializer = CustomSignupSerializer(data=data, context={'request': self.request})
#         self.assertFalse(serializer.is_valid())
#         self.assertIn('non_field_errors', serializer.errors)

#     def test_duplicate_username(self):
#         custUser.objects.create_user(username='testuser', email='testuser2@example.com', password='password123')
#         serializer = CustomSignupSerializer(data=self.valid_data, context={'request': self.request})
#         self.assertFalse(serializer.is_valid())
#         self.assertIn('username', serializer.errors)

#     def test_duplicate_email(self):
#         custUser.objects.create_user(username='testuser2', email='testuser@example.com', password='password123')
#         serializer = CustomSignupSerializer(data=self.valid_data, context={'request': self.request})
#         self.assertFalse(serializer.is_valid())
#         self.assertIn('email', serializer.errors)
