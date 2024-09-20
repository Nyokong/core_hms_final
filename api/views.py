from django.shortcuts import render

from rest_framework import viewsets, permissions, generics, permissions, status
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.permissions import AllowAny

from .models import FeedbackMessage
from .serializers import FeedbackMsgSerializer

# Create your views here.

# sample view
class MyView(generics.ListAPIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        response = {
            'message': 'token works.'
        }
        return Response(response, status=200)

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
    