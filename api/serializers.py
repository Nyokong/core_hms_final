from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .validators import validate_file_size
from django.utils import timezone

from .models import FeedbackMessage, custUser, Assignment, Video, Grade, Submission
from .models import Lecturer

from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password


class CustomSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate_username(self, username):
        if custUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if custUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user is already registered with this email address.")
        return email
    
    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        email = self.validate_email(data['email'])
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data

    def create(self, validated_data):
        user = custUser(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password1'])
        user.needs_password = False  # Set needs_password to False for regular signups
        user.save()
        setup_user_email(self.context['request'], user, [])
        return user
    
    class Meta:
        model = custUser
        fields = ('username', 'first_name', 'last_name' , 'email','is_lecturer', 'password', 'password2')
        # passwords should not be returned upon response
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

# user creation serializer/form
class UserSerializer(serializers.ModelSerializer):
    # password confirmation
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = custUser
        fields = ('username', 'student_number','first_name', 'last_name' , 'email','password', 'password2')
        # passwords should not be returned upon response
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        # password = validate_password.pop('password')
        # password2 = validate_password.pop('password2')

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password field didnt match."})
        
        return attrs

    def create(self, validated_data):
        user = custUser(
            username=validated_data['username'],
            student_number=validated_data['student_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])

        # wait until account is verified before activating
        user.is_active=False
        user.save()

        # after all return user
        return user

# user can only change details password change will done differently
class UserUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = custUser
        fields = ('username', )

class StudentNumberUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lecturer
        fields = ('student_number',)
        extra_kwargs = {
            'student_number': {'required': True}
        }

# delete -serializer
class UserDeleteSerializer(serializers.ModelSerializer):
    def validate(self, data):

        return data
    def delete_user(self, user):
        user.delete()

# user login serializer - only need username and password
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=8)
    password = serializers.CharField(max_length=80)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not custUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("Invalid username or password.")
        
        return attrs
    
    class Meta:
        model = custUser
        fields = ('username', 'password')

class AssignUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'due_date')

# create assignment serializer - only lecturer can access this.
class  AssignmentForm(serializers.Serializer):
    title = serializers.CharField(max_length=240)
    description = serializers.CharField()
    due_date = serializers.DateTimeField(default=timezone.now)
    attachment = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField(max_length=10)

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'attachment','status','total_submissions']
        read_only_fields = ['total_submissions']

    def create(self, validated_data):
        assignment = Assignment.objects.create(
            created_by=self.context['request'].user,
            title=validated_data['title'],
            description=validated_data['description'],
            due_date=validated_data.get('due_date', timezone.now()),  # Ensure due_date is included
            attachment=validated_data.get('attachment', ''),  # Include attachment if necessary
            status=validated_data['status']
        )
        return assignment

class AssignmentLectureViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = '__all__'

# video create serializer - only students can see this
class VideoSerializer(serializers.ModelSerializer):
    cmp_video = serializers.FileField(validators=[validate_file_size])
    
    class Meta:
        model = Video
        fields = ['assignment','title', 'description', 'cmp_video', 'thumbnail','hls_name' ,'hls_path','status','is_running']

    def validate(self, data):
        validate_file_size(data['cmp_video'])
        return data

    def create(self, validated_data):
        
        file = Video(
            user=self.context['request'].user,
            title=validated_data['title'],
            description=validated_data['description'],
            cmp_video=validated_data['cmp_video'],
            thumbnail=validated_data['thumbnail'],
            hls_name=validated_data['hls_name'],
            hls_path=validated_data['hls_path'],
            status=validated_data['status'],
            is_running=validated_data['is_running'],
        )

        # save the video if is succesful
        file.save()
        # after all return user
        return file

# video view list 
class Videoviewlist(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id','assignment','title', 'description', 'cmp_video', 'thumbnail','hls_name' ,'hls_path','status','is_running']


# feedback serializer goes here
class FeedbackMsgSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = FeedbackMessage
        fields = ['feedback_room','sender', 'message', 'timestamp']

    def create(self, validated_data):
        feedback_room = validated_data.get('feedback_room')
        
        msg = FeedbackMessage(
            feedback_room=feedback_room,
            sender=self.context['request'].user, # logged in user
            message=validated_data['message'], # the message
            timestamp=validated_data['timestamp'] # the time of posting
        )

        # save the video if is succesful
        msg.save()
        # after all return user
        return msg

class FeebackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackMessage
        fields = ['feedback_room','sender', 'message', 'timestamp']


#change password serializer

class ChangePasswordSerializer(serializers.ModelSerializer):
   
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model= custUser
        fields = ['password1', 'password2']

 
    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({"password2": "New passwords do not match"})
        return data


    def update_password(self, instance, validated_data):
        instance.set_password(validated_data['password1'])
        instance.save()
        return instance

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['lecturer', 'submission', 'grade', 'created_at']
        read_only_fields =['created_at']

    def validate_grade(self, value):
        if value <0 or value > 100:
            raise serializers.ValidationError("Grade must be between 0 and 100.")
        return value

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email exists.")
        return value
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
   
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        
        try:
            User = get_user_model()
            user = self.context['request'].user
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user ID.")

        # Check if the token is valid
        # if not default_token_generator.check_token(user, data['token']):
        #     raise serializers.ValidationError("Invalid or expired token.")

        # Check if the two passwords match
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({"password2": "The two password fields didn't match."})

        return data

    def save(self, **kwargs):
        # Reset the user's password
        # user = User.objects.get(pk=uid)
        user = self.context['request'].user
        user.set_password(self.validated_data['password1'])
        user.save()
        return user


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['assignment','student','video', 'submitted_at']