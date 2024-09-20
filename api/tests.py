from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .views import MyView, FeedbackMessage
from .models import FeedbackMessage
from .serializers import FeedbackMessage
from django.core.exceptions import ValidationError
from .models import custUser, Lecturer, Student, FeedbackMessage

# Model Tests
class CustUserModelTest(TestCase):
    def setUp(self):
        self.user = custUser.objects.create(username="testuser", password="testpass")

    def test_email_default(self):
        self.assertEqual(self.user.email, "testuser@mynwu.ac.za")

    def test_email_validation(self):
        with self.assertRaises(ValidationError):
            self.user.email = "invalid-email"
            self.user.full_clean()  # This triggers model validation

    def test_valid_email(self):
        try:
            self.user.email = "valid.email@mynwu.ac.za"
            self.user.full_clean()  # This triggers model validation
        except ValidationError:
            self.fail("Valid email raised ValidationError")

class LecturerModelTest(TestCase):
    def test_lecturer_creation(self):
        lecturer = Lecturer.objects.create(emp_num='12345678')
        self.assertEqual(lecturer.emp_num, '12345678')

class StudentModelTest(TestCase):
    def test_student_creation(self):
        student = Student.objects.create(student_num='87654321')
        self.assertEqual(student.student_num, '87654321')

#Test Urls

class UrlsTestCase(TestCase):
    
    def test_feedback_msgs_url(self):
        response = self.client.get(reverse('feedback-msgs'))
        self.assertEqual(response.status_code, 200)

    def test_sample_view_url(self):
        response = self.client.get(reverse('sample-view'))
        self.assertEqual(response.status_code, 200)


#Test Views

class MyViewTest(TestCase):
    def test_my_view(self):
        response = self.client.get(reverse('sample-view'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'token works.'})

class FeedbackMessagesTest(TestCase):
    def setUp(self):
        # Create a sample feedback message for testing
        self.user = custUser.objects.create_user(username='testuser', password='testpass')
        self.feedback_message = FeedbackMessage.objects.create(user=self.user, message="This is a test message.")

    def test_get_feedback_messages(self):
        response = self.client.get(reverse('feedback-msgs'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming one message exists
        self.assertEqual(response.data[0]['message'], self.feedback_message.message)

    def test_get_feedback_messages_empty(self):
        # Clear all feedback messages
        FeedbackMessage.objects.all().delete()
        response = self.client.get(reverse('feedback-msgs'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # Expect an empty list