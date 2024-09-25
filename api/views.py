from django.shortcuts import render

from rest_framework import viewsets, permissions, generics, permissions, status
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

# dajngo auth
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate, login

from .serializers import UserSerializer, UserUpdateSerializer, Videoviewlist,LoginSerializer
from .serializers import UserDeleteSerializer, AssignmentForm , VideoSerializer, ChangePasswordSerializer
from .models import custUser, Video, Assignment, Grade
from .models import VerificationToken

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

from django.contrib.sessions.models import Session
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import FeedbackMessage, PasswordResetToken
from .serializers import FeedbackMsgSerializer, StudentNumberUpdateSerializer, FeebackListSerializer, AssignUpdateSerializer, GradeSerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer

import os
import random
import csv


# settings
from django.conf import settings

# Create your views here.

# create user viewset api endpoint
class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data, context={'request': request})

        # is not valid = "this data does not match"
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Call the send_verification_email method with the newly created user
        if user:
            # self.send_verification_email(user)
            pass

        return Response({
            "user": serializer.data,
            "message": "User created successfully. Please check your email to verify account."            
        }, status=status.HTTP_201_CREATED)

    def send_verification_email(self, user, *args, **kwargs):

        # Generate a 5-digit verification code
        verification_code = random.randint(10000, 99999)

        key = get_random_string(length=32)
        
        VerificationToken.objects.create(user=user, token=key)

        verification_link = f'http://127.0.0.1:8000/api/usr/verify/?key={key}'

        # get user email
        email = user.email

        # sender email
        sender = settings.EMAIL_HOST_USER

        # defining subject and message
        subject = "Non-reply | Account Verification"
        message = f'Hey-ya \nYour verfication code is {verification_code} \n\n Click this link to verify account: {verification_link}\n non-reply email'

        # send the email
        send_mail(subject, message, sender, [f'{email}'], fail_silently=False)

        return Response({'Success': "Verification email sent"}, status=status.HTTP_200_OK)

class VerificationView(generics.GenericAPIView):
    queryset = custUser.objects.all()

    permission_classes = [permissions.AllowAny]

    def get_object(self):
        # Get the user instance based on the verification token
        # get token on the verification url
        token = self.request.query_params.get('token')

        try:
            user = VerificationToken.objects.get(token=token)
        except VerificationToken.DoesNotExist:
            return Response({'error': 'Invalid verification token'}, status=status.HTTP_400_BAD_REQUEST)

        # return user
        return user

    def get(self, request):
        # token = request.query_params.get('token')
        token_user = self.get_object()

        # get user from custom user and acivate user
        try:
            user = custUser.objects.get(username=token_user.user)

            user.is_active = True
            user.save()

            return Response({'message': 'User activated successfully'}, status=status.HTTP_200_OK)
        except custUser.DoesNotExist:
            return Response({'error': 'User DoesntExisist'}, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(generics.RetrieveUpdateAPIView):

    queryset = custUser.objects.all()
    serializer_class = UserUpdateSerializer 

    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        # if user is valid - check 
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST) 

from django.shortcuts import redirect
from django.conf import settings
from django.views import View
from urllib.parse import urlencode
from rest_framework_simplejwt.tokens import RefreshToken
import requests

class GoogleLoginView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            "redirect_uri": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": "random_state_string",  # You should generate a random state string for security
        }
        url = f"{base_url}?{urlencode(params)}"
        return redirect(url)

class GoogleCallbackView(View):

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state = request.GET.get('state')

        # Exchange the authorization code for access and refresh tokens
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            "redirect_uri": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()

        # Use the tokens to get user info and log the user in
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        user_info = requests.get(user_info_url, headers=headers).json()

        # Create or get the user and log them in
        # (You need to implement this part according to your user model and authentication system)

        # Generate your own JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Redirect to your frontend with the tokens
        response = redirect('http://localhost:3000')
        response.set_cookie('access_token', access_token, httponly=True, secure=True)
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)

        return response


def google_login(request):
    base_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        "redirect_uri": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": "random_state_string",  # You should generate a random state string for security
    }
    url = f"{base_url}?{urlencode(params)}"
    return redirect(url)


class AddStudentNumberView(generics.RetrieveUpdateAPIView):

    queryset = custUser.objects.all()
    serializer_class = UserUpdateSerializer 
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserProfileView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user

        user_data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'email': user.email,
        # Add any other user fields you need
        }
        
        return Response(user_data, status=status.HTTP_200_OK)

# DELETE VIEW USER
class DeleteUserView(generics.DestroyAPIView):
    queryset = custUser.objects.all()
    serializer_class = UserDeleteSerializer
    permission_class = (IsAuthenticated,)

    def get_object(self):
        user_id = self.kwargs.get("pk")
        return get_object_or_404(custUser, id=user_id)
    
    def destroy(self, request, *args, **kwargs):
        user =self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# this is the Login View
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    # post 
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Extract validated data
            user_data = serializer.validated_data
            # print(user_data)

            # Authenticate the user
            user = authenticate(username=user_data['username'], password=user_data['password'])

            print("Existing user: ",user) # error handling 

            # this checks if the user exists
            if user is not None:
                # Create or get the token for the user
                loggedUser = custUser.objects.get(username=user)

                # Log the user in
                login(request, user)

                # Send back a response with the token
                return Response({'sessionid': request.session.session_key},status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class verify Email view 
class VerifyEmailView(generics.GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            uid=urlsafe_base64_decode(uidb64).decode('utf-8')
            user=custUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, custUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator(user, token):
            user.is_active=True
            user.save()
            return Response({"message":"Email verified successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)

# user display viewset
class UserListViewSet(APIView):

    # gets users who are authenticated
    # for later purpose permissions might change
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        query = custUser.objects.all()
        serializer = UserSerializer(query, many=True)

        return Response(serializer.data)

class GoogAftermathView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'thank_you.html')
    
class VideoView(generics.GenericAPIView):
    # a class the views all the videos
    # in the database all of them
    permission_classes = [permissions.AllowAny]
    serializer_class = Videoviewlist

    # overwrite the get query method
    def get_queryset(self):
        return Video.objects.all()

    def get(self, request, format=None):
        query = self.get_queryset()

        serializer = self.get_serializer(query, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteVideoView(generics.DestroyAPIView):
    # a class the views all the videos
    # in the database all of them
    permission_classes = [permissions.AllowAny]

    # retrieve all videos
    def get_queryset(self):
        return Video.objects.all()  


# create assignments
class AssignmentCreateView(generics.CreateAPIView):
    serializer_class = AssignmentForm
    permission_class = [permissions.AllowAny]

    def get_queryset(self):
        return Assignment.objects.all()

    # post 
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            video = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.info(f'serializer is not valid {request.data}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#display assignments created
class AssignmentListView(generics.GenericAPIView):
        permission_classes = [permissions.AllowAny]

        def get_queryset(self):
            return Assignment.objects.all() 

        def get(self, request, format=None):
            queryset = self.get_queryset() 
            serializer = AssignmentForm(queryset, many=True)
            return Response(serializer.data)

# update assignments - only logged the lecturer
class AssignmentUpdateView(generics.RetrieveUpdateAPIView):
    queryset= Assignment.objects.all()
    serializer_class = AssignUpdateSerializer
    permission_classes = [permissions.AllowAny,]

    def get_object(self):
        obj = get_object_or_404(self.queryset, id=self.kwargs["id"])
        return obj
    
    def update(self, request, *args, **kwargs):
        assignment = self.get_object()
        serializer = self.get_serializer(assignment, data=request.data)

        # if assignment is valid - check 
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST) 
    
# delete assignments - only lecturer and admin can access
class AssignmentDeleteView(generics.DestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentForm
    permission_classes = [IsAuthenticated]

    def get_object(self):
        assignment_id = self.kwargs.get("pk")
        return get_object_or_404(Assignment, id =assignment_id)

    def destroy(self, request, *args, **kwargs):
        assignment =self.get_object()
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# feedback messages go here
# Read all feed back messages
class CreateFeedbackMessageView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = FeedbackMessage.objects.all()
    serializer_class = FeedbackMsgSerializer

    def post(self, request, *args, **kwargs):
        serializer= self.get_serializer(data=request.data)

        if serializer.is_valid():
            #print data to console
            serializer.save()
            #return the success response
            return Response ({"msg": "feedback creation is a success!"}, status=status.HTTP_201_CREATED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#update feedback
class UpdateFeedbackMessage(generics.UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = FeedbackMessage.objects.all()
    serializer_class = FeedbackMsgSerializer


    def get_object(self):
        obj = get_object_or_404(self.queryset, id=self.kwargs["pk"])
        return obj
    
    def update(self, request, *args, **kwargs):
        message = self.get_object()
        serializer = self.get_serializer(message, data=request.data)

    
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        
#delete feedback

class DeleteFeedbackMessage (generics.DestroyAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = FeedbackMessage.objects.all()
    serializer_class = FeedbackMsgSerializer


    def get_object(self):
        feedback_id = self.kwargs.get("pk")
        return get_object_or_404(FeedbackMessage, id =feedback_id)

    def destroy(self, request, *args, **kwargs):
        feedback=self.get_object()
        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class FeedbackMessages(generics.GenericAPIView):
    # gets users who are authenticated
    # for later purpose permissions might change
    permission_classes = [permissions.AllowAny]
    serializer_class = FeebackListSerializer

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return FeedbackMessage.objects.filter(feedback_room=room_id)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class ExportCSVView(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data.csv"'

        writer = csv.writer(response)

        writer.writerow(['Feedback  Room', 'Sender', 'Feedback', 'Timestamp'])

        data = FeedbackMessage.objects.all().values_list('feedback_room','sender', 'message', 'timestamp')

        for row in data:
            writer.writerow(row)

        return response

#change password

class ChangePasswordView(generics.UpdateAPIView):
    queryset = custUser.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user= self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            #update the user's password
            serializer.update_password(user, serializer.validated_data)
            return Response({"msg": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#creating grades
class GradeCreateView(generics.CreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.AllowAny,]

    



#update grades
class GradeUpdateView(generics.UpdateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        # Fetch the object based on the primary key (id)
        obj = get_object_or_404(self.queryset, id=self.kwargs["pk"])
        return obj

    def update(self, request, *args, **kwargs):
    
        grade = self.get_object()

        serializer = self.get_serializer(grade, data=request.data)

      
        if serializer.is_valid():
          
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
     
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#delete grades

class GradeDeleteView(generics.DestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.AllowAny,]


    def get_object(self):
        grade_id = self.kwargs.get("pk")
        return get_object_or_404(Grade, id =grade_id)

    def destroy(self, request, *args, **kwargs):
        grade=self.get_object()
        grade.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#viewing grades

class GradeListView(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.AllowAny,]



class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = custUser.objects.get(email=email)
        except custUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate token
        reset_token = get_random_string(length=32)
        
        # Store the token in a PasswordResetToken model (you need to create this model)
        PasswordResetToken.objects.create(user=user, token=reset_token)

        # Send email with the reset link
        reset_link = f'http://127.0.0.1:8000/api/reset-password-confirm/?token={reset_token}'
        subject = "Password Reset Request"
        message = f"Hello,\n\nPlease click the link below to reset your password:\n{reset_link}\n\nIf you did not request this, please ignore this email."
        sender = settings.EMAIL_HOST_USER

        send_mail(subject, message, sender, [email], fail_silently=False)

        return Response({"message": "Password reset email sent successfully."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")

        if password1 != password2:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.password = make_password(password1)
        user.save()

        # Optionally, delete the used token
        reset_token.delete()

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
    
