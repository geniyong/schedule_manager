from django.core.files import temp
from django.urls import path, re_path
from .views import *

urlpatterns = [
    re_path(r'^possibles/$', temppossible, name='possible-list'),
    re_path(r'^possibles/update/$', PossibleList.as_view(), name='possible-update'),

]
