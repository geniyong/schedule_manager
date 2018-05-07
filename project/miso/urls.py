from django.urls import path, re_path
from .views import *

urlpatterns = [
    re_path(r'^possibles/$', PossibleList.as_view(), name='possible-list'),
    re_path(r'^possibles/update/$', temppossible, name='possible-update'),

]
