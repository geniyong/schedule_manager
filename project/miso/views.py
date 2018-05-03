from django.shortcuts import render
from .models import *

# Create your views here.

class PossibleList(TemplateView):
	template_name = ‘main.html’

	def get_context_data(self,**wargs):
		qs=