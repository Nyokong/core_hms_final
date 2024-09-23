from django.views.generic import TemplateView
from rest_framework.viewsets import generics

class IndexView(TemplateView):
    template_name = 'home.html'
    # context_object_name = 'items'