from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import custUser, Lecturer, Student, Video, Assignment, Submission, Grade, FeedbackRoom, FeedbackMessage, VerificationToken

#Models Testing
class ModelsTestCase(TestCase):
    
    def setUp(self):
        self.user = custUser.objects.create(username='testuser', student_number='12345678')

    def test_email_default(self):
        self.assertEqual(self.user.email, '12345678@mynwu.ac.za')

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            self.user.email = 'invalid-email'
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
        self.assignment = Assignment.objects.create(created_by=self.user, title='Test Assignment', due_date='2024-12-31')

    def test_assignment_creation(self):
        self.assertEqual(self.assignment.title, 'Test Assignment')
        self.assertEqual(self.assignment.created_by.username, 'lecturer')

    def test_assignment_creation_by_non_lecturer(self):
        non_lecturer = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        with self.assertRaises(ValidationError):
            Assignment.objects.create(created_by=non_lecturer, title='Invalid Assignment', due_date='2024-12-31')

class SubmissionModelTest(TestCase):

    def setUp(self):
        self.lecturer = custUser.objects.create(username='lecturer', student_number='12345678', is_lecturer=True)
        self.student = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        self.assignment = Assignment.objects.create(created_by=self.lecturer, title='Test Assignment', due_date='2024-12-31')
        self.submission = Submission.objects.create(assignment=self.assignment, student=self.student, video=self.student)

    def test_submission_creation(self):
        self.assertEqual(self.submission.assignment.title, 'Test Assignment')
        self.assertEqual(self.submission.student.username, 'student')

    def test_submission_by_lecturer(self):
        with self.assertRaises(ValidationError):
            Submission.objects.create(assignment=self.assignment, student=self.lecturer, video=self.lecturer)

class GradeModelTest(TestCase):

    def setUp(self):
        self.lecturer = custUser.objects.create(username='lecturer', student_number='12345678', is_lecturer=True)
        self.student = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        self.assignment = Assignment.objects.create(created_by=self.lecturer, title='Test Assignment', due_date='2024-12-31')
        self.submission = Submission.objects.create(assignment=self.assignment, student=self.student, video=self.student)
        self.grade = Grade.objects.create(lecturer=self.lecturer, submission=self.submission, grade=85.00)

    def test_grade_creation(self):
        self.assertEqual(self.grade.grade, 85.00)
        self.assertEqual(self.grade.lecturer.username, 'lecturer')
        self.assertEqual(self.grade.submission.assignment.title, 'Test Assignment')

    def test_get_letter_grade(self):
        self.assertEqual(self.grade.get_letter_grade(), 'B')

class FeedbackRoomModelTest(TestCase):

    def setUp(self):
        self.lecturer = custUser.objects.create(username='lecturer', student_number='12345678', is_lecturer=True)
        self.student = custUser.objects.create(username='student', student_number='87654321', is_lecturer=False)
        self.assignment = Assignment.objects.create(created_by=self.lecturer, title='Test Assignment', due_date='2024-12-31')
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
        self.assignment = Assignment.objects.create(created_by=self.lecturer, title='Test Assignment', due_date='2024-12-31')
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
        
    
        

        
       
 

# #Test Urls

# class UrlsTestCase(TestCase):
    
#     def test_feedback_msgs_url(self):
#         response = self.client.get(reverse('feedback-msgs'))
#         self.assertEqual(response.status_code, 200)

#     def test_sample_view_url(self):
#         response = self.client.get(reverse('sample-view'))
#         self.assertEqual(response.status_code, 200)


# #Test Views

# class MyViewTest(TestCase):
#     def test_my_view(self):
#         response = self.client.get(reverse('sample-view'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, {'message': 'token works.'})

# class FeedbackMessagesTest(TestCase):
#     def setUp(self):
#         # Create a sample feedback message for testing
#         self.user = custUser.objects.create_user(username='testuser', password='testpass')
#         self.feedback_message = FeedbackMessage.objects.create(user=self.user, message="This is a test message.")

#     def test_get_feedback_messages(self):
#         response = self.client.get(reverse('feedback-msgs'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)  # Assuming one message exists
#         self.assertEqual(response.data[0]['message'], self.feedback_message.message)

#     def test_get_feedback_messages_empty(self):
#         # Clear all feedback messages
#         FeedbackMessage.objects.all().delete()
#         response = self.client.get(reverse('feedback-msgs'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, [])  # Expect an empty list

#Test Serializers

# User = get_user_model()

# class FeedbackMsgSerializerTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.valid_data = {
#             'message': 'This is a test message.',
#             'timestamp': '2024-09-23T12:34:56Z'
#         }
#         self.invalid_data = {
#             'message': '',
#             'timestamp': '2024-09-23T12:34:56Z'
#         }

#     def test_serializer_with_valid_data(self):
#         valid_data = {
#             'user': self.user.id,  # Add user to the valid data
#             'message': 'This is a test message.',
#             'timestamp': '2024-09-23T12:34:56Z'
#         }
#         serializer = FeedbackMsgSerializer(data=valid_data, context={'request': self._get_mock_request()})
#         if not serializer.is_valid():
#             print(serializer.errors)  # Print out any errors if validation fails
#         self.assertTrue(serializer.is_valid(), serializer.errors)  # If it fails, errors will show why
#         feedback_msg = serializer.save()
#         self.assertEqual(feedback_msg.user, self.user)
#         self.assertEqual(feedback_msg.message, 'This is a test message.')
#         self.assertEqual(feedback_msg.timestamp.isoformat(), '2024-09-23T12:34:56+00:00')  # Check if timestamp is saved correctly



#     def test_serializer_with_invalid_data(self):
#         serializer = FeedbackMsgSerializer(data=self.invalid_data, context={'request': self._get_mock_request()})
#         self.assertFalse(serializer.is_valid())


#     def _get_mock_request(self):
#         # Utility function to create a mock request object with the user
#         from rest_framework.test import APIRequestFactory
#         request_factory = APIRequestFactory()
#         request = request_factory.get('/')
#         request.user = self.user
#         return request