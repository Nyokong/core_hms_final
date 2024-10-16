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
    path('usr/update-std-number/', views.AddStudentNumberView.as_view(), name="add-student-number"),
    path('usr/change-password', views.ChangePasswordView.as_view(), name ='change-password'),
    path('usr/reset-password', views.PasswordResetRequestView.as_view(), name ='reset-password'),
    path('usr/reset-password-confirm', views.PasswordResetConfirmView.as_view(), name ='reset-password-confirm'),


    # i hate allatuh urls
    path('thank-you', views.GoogAftermathView.as_view(), name='thank-you'),

    # token login
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # assignments endpoints
    path('assign/view/',views.AssignmentListView.as_view(), name='list-assignment'),
    path('assign/view/<int:created_by>',views.AssignmentLecturerView.as_view(), name='lecturer-assignment'),
    path('assign/create',views. AssignmentCreateView.as_view(), name='create-assignments'),
    path('assign/update/<int:id>', views.AssignmentUpdateView.as_view(), name='assignment-update'),
    path('assign/delete/<int:pk>',views.AssignmentDeleteView.as_view(), name= 'assignment-delete'),

    # video views
    path('vd/view', views.VideoView.as_view(), name='video-list'), 
    path('vd/view/<int:id>', views.VideoPlayView.as_view(), name='video-Play'), 
    path('vd/upload',views.UploadVideoView.as_view(), name='video-upload'),
    path('vd/del/<int:pk>',views.DeleteVideoView.as_view(), name='video-delete'),
    path('vd/download/<int:video_id>/', views.DownloadVideoView.as_view(), name='download_video'),

    path('vd/stream/<int:video_id>/<str:quality>', views.VideoStreamView.as_view(), name='stream_video'),
    path('vd/stream/<int:video_id>/<str:segment>', views.VideoStreamSegmentsView.as_view(), name='segments_video'),

    path('vd/masterstream/<int:video_id>', views.MasterVideoStreamView.as_view(), name='masterstream_video'),
    # path('vd/masterstream/<int:video_id>', views.MasterVideoStreamSegmentsView.as_view(), name='mastersegments_video'),

    # feedback http endpoints
    path('feedback/msgs', views.FeedbackMessages.as_view(), name='feedback-msgs-read'),
    # make update of feedback
    path('feedback/<int:id>/rooms', views.AllRoomsView.as_view(), name='rooms'),
    path('feedback-room/<int:room_id>/messages', views.FeedbackMessages.as_view(), name='feedback_room_messages'),
    path('feedback/update/<int:pk>', views.UpdateFeedbackMessage.as_view(), name ='feedback-update'),
    path('feedback/delete/<int:pk>', views.DeleteFeedbackMessage.as_view(), name ='feedback-delete'),

    #downloading 
    path('download/csv', views.ExportCSVView.as_view(), name='export-csv'),
    # path('download/video/<int:id>', views.DownloadVideoView.as_view(), name='export-video'),

    #grade
    path('grades/create', views.GradeCreateView.as_view(), name='grade-create'),
    path('grades/update/<int:pk>', views.GradeUpdateView.as_view(), name ='grade-update'),
    path('grades', views.GradeListView.as_view(), name='grade-list'),
    path('grades/delete/<int:pk>', views.GradeDeleteView.as_view(), name ='grade-delete'),

    # submissions
    path('submission/create', views.SubmissionCreateView.as_view(), name='submission-create'),
    path('submission/list/<int:user_id>', views.SubmissionListView.as_view(), name='submission-list'),
    path('submission/delete/<int:id>', views.SubmissionDeleteView.as_view(), name='submission-delete'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)