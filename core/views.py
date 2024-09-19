from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework import status 
import redis


class BaseAPI(TemplateView):
    template_name = 'index.html'

    # def get(self):
    #     r = redis.Redis(host='redis', port=6379)
    #     # Use the Redis connection for your operations
    #     result = r.get('my_key')

    #     print(result)

    #     return Response({"result: ", result}, status=status.HTTP_200_OK)
