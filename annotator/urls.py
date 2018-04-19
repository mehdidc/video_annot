from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video', views.random_video, name='random_video'),
    path('video/<int:video_id>', views.video, name='video'),
    path('nothing', views.nothing, name='nothing'),
]
