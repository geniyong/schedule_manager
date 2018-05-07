from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponseRedirect
# Create your views here.

class PossibleList(TemplateView):
    template_name = 'plan/main.html'

    def get_context_data(self,**kwargs):
        qs=Possible_schedule.objects.all
        context = super(PossibleList, self).get_context_data(**kwargs)
        context['PossibleAll'] = qs
        return context


class PossibleUpdate(CreateView):
    template_name = 'plan/main.html'
    model = Possible_schedule
    form_class = PossibleForm

    def get_context_data(self, **kwargs):
        context = super(PossibleUpdate, self).get_context_data(**kwargs)
        context['create_form'] = PossibleForm
        context['staff_id'] = Possible_schedule.objects.all()
        return context

    def get_success_url(self):
        return reverse('possible-list')

'''
def temppossible(request):
    if request.method == 'POST':
        form = PossibleForm(request.POST)

        if form.is_valid():
            possible = form.save(commit=True)
            return redirect('../')
    else:
        form = PossibleForm()

    return render(request, 'plan/main.html', {'form':form})

'''
def temppossible(request):
    print(request.POST.get('id'))
    if request.method == 'POST':

        staff_name=request.POST.get('id') # 천재용으로 받아옴 웹에서
        
        query_result = Staff.objects.get(name=staff_name) # 이름으로 staff 를 필터링
        print(query_result.id)
        print(type(query_result))

        temp_day = Day.objects.filter(day="월요일").get(time="N")
        print(temp_day)
        new_instance = Possible_schedule(staff_id=query_result, day_id=temp_day)
        new_instance.save()

        return redirect('../')
    else:
        pass
    return render(request, 'plan/main.html')