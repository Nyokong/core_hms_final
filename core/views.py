from django.shortcuts import render
from django.views.generic import TemplateView

class BaseAPI(TemplateView):
    template_name = 'index.html'
