from django.contrib.auth import login
from django.core.files import temp
from django.urls import path, re_path
from .views import *

urlpatterns = [
    re_path(r'^possibles/$', possibleCreateRetrieveView, name='possible-create-retrieve'),
    re_path(r'^login/$', loginView, name='staff-create'),
    re_path(r'^manager/$', managerView, name='manager-admin'),
    path('staff/<str:staffName>/<str:staffPhone>/', staffView, name='staff-main'),
]
