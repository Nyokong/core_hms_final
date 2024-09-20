from django.shortcuts import render

from rest_framework import viewsets, permissions, generics, permissions, status
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from django.contrib.auth import authenticate, login

from .serializers import UserSerializer, UserUpdateSerializer, Videoviewlist,LoginSerializer
from .serializers import UserDeleteSerializer, AssignmentForm , VideoSerializer
from .models import custUser, Video, Assignment

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

from django.contrib.sessions.models import Session
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import FeedbackMessage
from .serializers import FeedbackMsgSerializer

import os
import random

# settings
from django.conf import settings

# Create your views here.

# create user viewset api endpoint
class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data, context={'request': request})

        # is not valid = "this data does not match"
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Call the send_verification_email method with the newly created user
        if user:
            self.send_verification_email(user)

        return Response({
            "user": serializer.data,
            "message": "User created successfully. Please check your email to verify account."            
        }, status=status.HTTP_201_CREATED)

    def send_verification_email(self, user, *args, **kwargs):

        # Generate a 5-digit verification code
        verification_code = random.randint(10000, 99999)

        # get user email
        email = user.email

        # sender email
        sender = settings.EMAIL_HOST_USER

        # defining subject and message
        subject = "Account Verification"
        message = f'Your verfication code is {verification_code}'

        # send the email
        send_mail(subject, message, sender, [f'{email}'], fail_silently=False)

        return Response({'Success': "Verification email sent"}, status=status.HTTP_200_OK)

class UserUpdateView(generics.RetrieveUpdateAPIView):

    queryset = custUser.objects.all()
    serializer_class = UserUpdateSerializer 

    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data,instance=user)

        # if user is valid - check 
        if serializer.is_valid():
            user.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST) 

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



# feedback messages go here
# Read all feed back messages
class FeedbackMessages(generics.GenericAPIView):

    # gets users who are authenticated
    # for later purpose permissions might change
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        query = FeedbackMessage.objects.all()
        serializer = FeedbackMsgSerializer(query, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    