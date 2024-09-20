from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .validators import validate_file_size
from django.utils import timezone

from .models import FeedbackMessage, custUser, Assignment, Video

from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

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

# user creation serializer/form
class UserSerializer(serializers.ModelSerializer):
    # password confirmation
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = custUser
        fields = ('username', 'first_name', 'last_name' , 'email','is_lecturer', 'password', 'password2')
        # passwords should not be returned upon response
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
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
        fields = ('username', 'first_name', 'last_name')

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

    class Meta:
        model = custUser
        fields = ('username', 'password')

# create assignment serializer - only lecturer can access this.
class AssignmentForm(serializers.Serializer):
    title=serializers.CharField(max_length=240)
    description= serializers.CharField()
    due_date = serializers.DateTimeField(default=timezone.now)

    def create(self, validated_data):
        return Assignment.objects.create(**validated_data)
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'attachment']

# video create serializer - only students can see this
class VideoSerializer(serializers.ModelSerializer):
    cmp_video = serializers.FileField(validators=[validate_file_size])
    
    class Meta:
        model = Video
        fields = ['title', 'description', 'cmp_video']

    def validate(self, data):
        validate_file_size(data['cmp_video'])
        return data

    def create(self, validated_data):
        
        file = Video(
            user=self.context['request'].user,
            title=validated_data['title'],
            description=validated_data['description'],
            cmp_video=validated_data['cmp_video']
        )

        # save the video if is succesful
        file.save()
        # after all return user
        return file

# video view list 
class Videoviewlist(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id','title', 'description', 'cmp_video']


# feedback serializer goes here
class FeedbackMsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackMessage
        fields = ['user', 'message', 'timestamp']

    def create(self, validated_data):
        
        msg = FeedbackMessage(
            user=self.context['request'].user, # logged in user
            message=validated_data['message'], # the message
            timestamp=validated_data['timestamp'] # the time of posting
        )

        # save the video if is succesful
        msg.save()
        # after all return user
        return msg

