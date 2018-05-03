from django.shortcuts import render
from .models import *

# Create your views here.

class PossibleList(TemplateView):
	template_name = ‘main.html’

	def get_context_data(self,**kwargs):
		qs=Possible_schedule.objects.all
		
		context = super(PossibleList, self).get_context_data(**kwargs)
		context[‘PossilbeAll’] = qs
		
		return context