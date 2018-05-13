from django.shortcuts import render,redirect, render_to_response
from .models import *
from .forms import *
from .coremodule import *
# from django_tables2 import RequestConfig
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponseRedirect
# Create your views here.


def runSchedule():
    originList = []
    newList = []
    dayList = ['일요일', '금요일', '토요일', '월요일', '화요일', '수요일', '목요일', '금요일']
    timeList = ['D','N','D1','M','M1']
    dayOrder = []

    qs = Staff.objects.all().order_by('-score')
    for staff in qs:
        if(staff.newcomer == True):
            newList.append(staff)

        else:
            originList.append(staff)

    print(originList)
    print(newList)

    dayAll = Day.objects.all()
    for day in dayList:
        for dayInstance in dayAll:
            if dayInstance.day == day:
                pass

    print("==========")
    print(dayOrder)
    for staff in originList:
        count = 0
        limit = staff.possible_N_days
        possible = Possible_schedule.objects.filter(staff_id=staff)
        print(possible)
        for day in dayList:
            for dayInstance in dayAll:
                if dayInstance.day == day:
                    pass

        while(count < limit):
            break

    return True


def runScheduleView(request):
    if(runSchedule()):
        return redirect('/manager/')
    return render(request, 'plan/planning_running.html')


class PossibleList(TemplateView):
    template_name = 'plan/main.html'

    def get_context_data(self,**kwargs):
        qs=Possible_schedule.objects.all
        context = super(PossibleList, self).get_context_data(**kwargs)
        context['possibleAll'] = qs
        return context

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


def possibleCreateRetrieveView(request):
    dayList = ['월요일', '화요일', '수요일', '목요일','금요일','토요일','일요일']
    print(request.POST.get('id'))
    if request.method == 'POST':
        staff_name=request.POST.get('name') # 천재용으로 받아옴 웹에서
        query_result = Staff.objects.get(name=staff_name) # 이름으로 staff 를 필터링

        print(query_result.id)
        print(type(query_result))

        for day in dayList:
            dayTime = request.POST.get(day)
            print("==========dayTIme===============" + dayTime)
            print(type(dayTime))
            if(dayTime == '0'):
                continue
            dayInstance = Day.objects.filter(day=day).get(time=dayTime)
            print(dayInstance)

            new_instance = Possible_schedule(staff_id=query_result, day_id=dayInstance)
            new_instance.save()

        return redirect('./')

    elif request.method =='GET':
        possibleAll = Possible_schedule.objects.all()
        context = {'possibleAll': possibleAll}

    return render(request, 'plan/main.html', context)



def loginView(request):
    if request.method == 'POST':
        post = request.POST
        staffName=post.get('name')
        staffPhone=post.get('phone')

        if (staffName == 'manager'):
            if(staffPhone == '01012345678'):
                return redirect('../manager/')

            else:
                return render_to_response('plan/loginAlert.html')

        print(staffName + ':' + staffPhone)
        qs = Staff.objects.filter(name=staffName)
        if qs.count()==0:
            newInstance = Staff(name=staffName, phone=staffPhone)
            newInstance.save()

        else:
            qs = Staff.objects.filter(phone=staffPhone)
            if (qs.count==0):
                newInstance = Staff(name=staffName, phone=staffPhone)
                newInstance.save()

        return redirect('../staff/'+staffName+'/'+staffPhone+'/')

    elif request.method == 'GET':
        pass

    return render(request, 'plan/login.html')


def managerView(request):

    return render(request, 'plan/manager.html')


def staffView(request, staffName, staffPhone):
    print("---==========")
    print(staffName)
    print(staffPhone)

    if request.method == "POST":
        post = request.POST
        print(post)

    return render(request, 'plan/staff_schedule_enrollment.html')


def manageStaffView(request):
    staffAll = Staff.objects.all().order_by('name')

    if request.method=="GET":
        context = {'staffAll':staffAll,}

    elif request.method == 'POST':
        post = request.POST
        print("what is a post : ", end="")
        print(post)
        for staff in staffAll:
            postedList=post.getlist(str(staff))
            print(postedList)
            if(postedList[0] != ''): # score 평가점수 수정
                staff.score=postedList[0]

            if(len(postedList) == 2) : # newcomer 신입여부 수정
                staff.newcomer = True
            else:
                staff.newcomer = False

            staff.save()

        return redirect('./')

    return render(request, 'plan/manager_staff.html', context)


def manageNeedsView(request):
    if request.method =="GET":
        dayAll = Day.objects.all()
        context = {'dayAll':dayAll}

    elif request.method == 'POST':
        post = request.POST
        print(post)
        return redirect('./')
    return render(request, 'plan/manager_needs.html',context)


def manageNeedsUpdate(request, day):
    timeList=['D','D1','M','M1','N']
    dayList =['월요일','화요일','수요일','목요일','금요일','토요일','일요일']
    if request.method =="GET":
        dayAll = Day.objects.all()
        context = {'dayAll':dayAll, 'timeList':timeList, 'dayList':dayList, 'currentDay': day}

    elif request.method == 'POST':
        post = request.POST
        print(post)
        currentday = day
        for time in timeList:
            forupdate = Day.objects.filter(day=currentday)
            needsList = post.getlist(time)
            forupdate = forupdate.get(time=time)

            if needsList[0] == '':
                if needsList[1] == '':
                    forupdate.needs_newcomer = int(forupdate.needs) // 3
                else:
                    forupdate.needs_newcomer= needsList[1]
            else:
                forupdate.needs = needsList[0]
                if needsList[1] == '':
                    forupdate.needs_newcomer = int(forupdate.needs) // 3
                else:
                    forupdate.needs_newcomer= needsList[1]
            forupdate.save()

        return redirect('/manager/hr/')

    return render(request, 'plan/manager_needs_update.html',context)

# 페이지 확인을 위한 임시 뷰
def indexTest(request):
    return render(request, 'plan/index.html')

# 가능스케줄 페이지 임시 뷰
def possibleSchedulesView(request):
    dayList =['월요일','화요일','수요일','목요일','금요일','토요일','일요일']
    if request.method=="GET":
        staffAll = Staff.objects.all().order_by('name')
        possibleAll = Possible_schedule.objects.all().order_by('day_id')
        context = {'staffAll':staffAll,'possibleAll':possibleAll, 'dayList':dayList}
    return render(request, 'plan/manager_possibles.html', context)
'''
instance 뽑아내는 예제
    if request.method=="GET":
        staffAll = Staff.objects.all()
        for instance in staffAll:
            staffName = instance.name
            staffPhone = instance.phone
            staffScore = instance.score
            staffPossibleDay = instance.possible_N_days
        context = {'staffAll' : staffAll}
'''