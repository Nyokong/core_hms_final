from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # testing/sample views
    # path('sample', views.MyView.as_view(), name='sample-view'),
    # path('', include(router.urls)),
    path('usr/create', views.UserCreateView.as_view(), name="create-user"),
    path('usr/update', views.UserUpdateView.as_view(), name='user-update'),
    path('usr/login', views.LoginAPIView.as_view(), name="login-user"),
    path('usrs', views.UserListViewSet.as_view(), name='users'),
    path('verify-email/<uidb64>/<token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('usr/delete/<int:pk>/', views.DeleteUserView.as_view(), name='user-delete'),

    path('list/assign/',views.AssignmentListView.as_view(), name='list-assignment'),
    path('assign/assignment/',views. AssignmentCreateView.as_view(), name='create-assignments'),
    path('update/assign/<int:id>', views.AssignmentUpdateView.as_view(), name='assignment-update'),
    path('delete/assign/<int:pk>',views.AssignmentDeleteView.as_view(), name= 'assignment-delete'),

    # video views
    path('vd/lst', views.VideoView.as_view(), name='video-list'), 
    path('vd/upload-old',views.UploadVideoView.as_view(), name='video-upload'),
    path('vd/up',views.UploadVideoViewTask.as_view(), name='video-task-upload'),
    path('vd/del/<int:pk>',views.DeleteVideoView.as_view(), name='video-delete'),

    # feedback http endpoints
    path('feedback/msgs', views.FeedbackMessages.as_view(), name='feedback-msgs'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)