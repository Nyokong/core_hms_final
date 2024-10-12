"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

# from . import views
from api import views as api_views
from . import views

from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from allauth.socialaccount.providers.google.views import oauth2_login, oauth2_callback


from allauth.socialaccount.providers.google.urls import urlpatterns as google_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # home 
    path('', views.IndexView.as_view(), name='home'),

    # socials all auth login
    path('accounts/', include('allauth.urls')),
    path('accounts/google/login/callback/', views.custom_google_login, name='custom_google_login'),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),

    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/google/', views.GoogleLogin.as_view(), name='google_login'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
