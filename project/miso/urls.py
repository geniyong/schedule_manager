from django.contrib.auth import login
from django.core.files import temp
from django.urls import path, re_path
from .views import *

urlpatterns = [
    re_path(r'^possibles/$', possibleCreateRetrieveView, name='possible-create-retrieve'),
    re_path(r'^login/$', loginView, name='staff-create'),
    re_path(r'^manager/$', managerView, name='manager-main'),
    path('staff/<str:staffName>/<str:staffPhone>/', staffView, name='staff-main'),
    
    #manager 관리 페이지
    #미소지기 관리 페이지
    path('manager/staff/', manageStaffView, name='manager-staff'),

    #가능한스케줄 관리 페이지
    path('manager/possible/', manageStaffView, name='manager-possible'),
    path('manager/possible/<str:staffName>/', manageStaffView, name='manager-possible'), # 이름으로찾기
    path('manager/possible/<str:possibleDay>/', manageStaffView, name='manager-possible'), # 요일로 찾기
    path('manager/possible/<str:possibleDay>/<str:possibleTime>', manageStaffView, name='manager-possible'),#요일+시간

    #필요인력 관리 페이지
    path('manager/hr/', manageNeedsView, name='manager-hr'),
    path('manager/hr/update/<str:day>/', manageNeedsUpdate, name='manager-hr-update'),
    #실제스케줄 관리 페이지
    path('manager/real/', manageStaffView, name='manager-real'),

]
