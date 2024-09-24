from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # user side endpoints
    path('usr/create', views.UserCreateView.as_view(), name="create-user"),
    path('usr/update', views.UserUpdateView.as_view(), name='user-update'),
    path('usr/login', views.LoginAPIView.as_view(), name="login-user"),
    path('usrs', views.UserListViewSet.as_view(), name='users'),
    path('verify-email/<uidb64>/<token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('usr/delete/<int:pk>/', views.DeleteUserView.as_view(), name='user-delete'),
    path('usr/profile', views.UserProfileView.as_view(), name='user-profile-read'),
    path('usr/update-std-number', views.AddStudentNumberView.as_view(), name="add-student-number"),

    # i hate allatuh urls
    path('thank-you', views.GoogAftermathView.as_view(), name='thank-you'),

    # token login
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # assignments endpoints
    path('list/assign/',views.AssignmentListView.as_view(), name='list-assignment'),
    path('assign/assignment/',views. AssignmentCreateView.as_view(), name='create-assignments'),
    path('update/assign/<int:id>', views.AssignmentUpdateView.as_view(), name='assignment-update'),
    path('delete/assign/<int:pk>',views.AssignmentDeleteView.as_view(), name= 'assignment-delete'),

    # video views
    path('vd/lst', views.VideoView.as_view(), name='video-list'), 
    # path('vd/upload-old',views.UploadVideoView.as_view(), name='video-upload'),
    path('vd/del/<int:pk>',views.DeleteVideoView.as_view(), name='video-delete'),

    # feedback http endpoints
    # path('feedback/msgs', views.FeedbackMessages.as_view(), name='feedback-msgs-read'),
    path('feedback-room/<int:room_id>/messages/', views.FeedbackMessages.as_view(), name='feedback_room_messages'),


    #downloading CSV
    path('csv', views.ExportCSVView.as_view(), name='export-csv'),

    #change password
    path('change-password', views.ChangePasswordView.as_view(), name ='change-password'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)