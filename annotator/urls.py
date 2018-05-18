from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('class_selection', views.class_selection, name='class_selection'),
    path('video', views.random_video, name='random_video'),
    path('nothing', views.nothing, name='nothing'),
]
