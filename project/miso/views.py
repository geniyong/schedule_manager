from audioop import max
from numbers import Real

from django.shortcuts import render,redirect, render_to_response
from .models import *
from .forms import *
from .coremodule import *
# from django_tables2 import RequestConfig
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponseRedirect


    # ===============================================================
    # ===============================================================

def runSchedule():
    originList = []
    newList = []
    dayList = ['일요일', '금요일', '토요일', '월요일', '화요일', '수요일', '목요일']
    timeList = ['D','N','D1','M','M1']
    origin_minFailList = [] # 기존미소지기 중 최소근무일수 미충족 리스트
    new_minFailList =[] # 신입미소지기 중 최소근무일수 미충족 리스트
    
    # ===============================================================
    # <Phase1>
    # 실제 스케줄링 시작 전 Pre-Process
    # 1. 실제 스케줄 데이터 초기화
    # 2. 요일/날짜 마다 실제 배치 인원 초기화
    # 3. 모든 미소지기의 complete Boolean Set : 실제 스케줄 배치가 완료되었는가에 관한 Data 초기화
    #   // min_complete : 최소 근무일을 만족시켰는가?
    #   ( 모든 미소지기가 최소 3일은 근무 해야 할 때, 3일도 못채웠을 경우 False, 3일 이상 배치되었다면 True )
    #   // max_complete : 희망 근무일을 만족시켰는가?
    #   ( 미소지기가 제출한 희망 근무일수가 5일 일 때, 5일 배치 되었을 경우 True, 4일 이하 일 경우 False )
    # ===============================================================

    # 1. 실제 스케줄 데이터 초기화
    Real_schedule.objects.all().delete()
    print(Real_schedule.objects.all())
    # 2. 요일/날짜 마다 실제 배치 인원 초기화
      # day의 real_origin과 real_newcomer 초기화
    for day in Day.objects.all():
        day.real_newcomer = 0
        day.real_origin = 0
        day.save()

    # 3. 모든 미소지기의 complete Boolean Set : 실제 스케줄 배치가 완료되었는가에 관한 Data 초기화
      # Staff.min_complete , Staff.max_complete 초기화
    for staff in Staff.objects.all():
        staff.min_complete = False
        staff.max_complete = False
        staff.save()


    # ===============================================================
    # <Phase2>
    # 스케줄링
    # ===============================================================

    # Staff 분리, ordering -> 점수 순서대로
    qs = Staff.objects.all().order_by('-score')
    for staff in qs:
        if(staff.newcomer == True):
            newList.append(staff)

        else:
            originList.append(staff)
    print(originList)
   # print(newList)

    # 기존 스태프 스케쥴링 - 3일 먼저
    for staff in originList:
        count = 0
        limit = 3
        #limit = staff.possible_N_days
        possible = Possible_schedule.objects.filter(staff_id=staff)
       # print(possible)

        for day in dayList:
            day_success = 0 # 그 날에 scheduling이 되었는가

            if count >= limit:
                staff.min_complete = True
                staff.save()
                break
                
            for time in timeList:
                if day_success != 0:
                    break
                temp2 = Day.objects.get(day=day, time=time) #### day model
                if temp2.needs - temp2.needs_newcomer <= temp2.real_origin: # 충분한 자리가 있는가?
                    continue # 다음 시간대로 넘김, 요일은 그대로라서 continue
                for pos in possible:
                    if pos.day_id == temp2:
                        # day에 자리가 있으면 추가
                        createRealSchedule(staff.id, temp2.id)
                        print(pos)
                        day_success = 1
                        count = count + 1
                        temp2.real_origin = temp2.real_origin + 1
                        temp2.save
                        break

        if staff.min_complete == False :
            origin_minFailList.append(staff)

    print(origin_minFailList)


    # 신규 스태프 스케쥴링 - 3일 먼저
    for staff in newList:
        count = 0
        limit = 3
        #limit = staff.possible_N_days
        possible = Possible_schedule.objects.filter(staff_id=staff)
        #print(possible)

        for day in dayList:
            day_success = 0  # 그 날에 scheduling이 되었는가
            if count >= limit:
                staff.min_complete = True
                staff.save()
                break
            for time in timeList:
                if day_success != 0:
                    break
                temp2 = Day.objects.get(day=day, time=time)  #### day model
                if temp2.needs_newcomer <= temp2.real_newcomer: # 충분한 자리가 있는가?
                    continue
                for pos in possible:
                    if pos.day_id == temp2:
                        createRealSchedule(staff.id, temp2.id)
                        print(pos)
                        day_success = 1
                        count = count + 1
                        temp2.real_newcomer = temp2.real_newcomer + 1
                        temp2.save
                        break

        if staff.min_complete == False:
            new_minFailList.append(staff)


#추가필요부분
# 3일분 먼저 처리 init + modify / 4일 희망자 처리 / 5일 희망자 처리
# 스키마변경 - > 실제스케줄 반영 후 다시 남는 가능한 시간대만 따로 정리된 모델 추가
# 스케줄링 실패 미소지기 목록 모델 추가
# Real_schedule 추가

    return True


def createRealSchedule(staff, day):  # Staff의 id, Day의 id
    print("Real Schedule 생성 ...")
    stf = Staff.objects.get(pk=staff)
    da = Day.objects.get(pk=day)
    rs = Real_schedule(staff_id=stf, day_id=da)
    rs.save()

    return
'''
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
'''

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
    dayList = ['월요일','화요일','수요일','목요일','금요일','토요일','일요일']
    context = {"staffName" : staffName, "staffPhone" : staffPhone, "dayList" : dayList}
    print("==========")
    timeList = ['D','D1','M','M1','N']
    possibleDays=[]
    bolt=0
    weekendCount = 0

    staff = Staff.objects.filter(name=staffName).get(phone=staffPhone)
    print(staff)
    
    if request.method == "POST":
        post = request.POST
        print(post)
        for time in timeList:            
            postList = post.getlist(time)
            for day in postList:
                for a in possibleDays:
                    bolt=0
                    if(a==day):
                        bolt=1
                        break
                if bolt != 1:
                    possibleDays.append(day)
        print("===============")
        print(possibleDays)
        for day in possibleDays:
            if day == '토요일' or day == '일요일':
                weekendCount += 1

        print("주말수 : " + str(weekendCount))
        if weekendCount == 0 :
            context['message'] = "최소한 주말 하루는 추가 해주세요!!(토요일, 일요일)"
            return render_to_response('plan/staffPossibleAlert.html', context)

        if len(possibleDays) < int(post.get("희망근무일수")) :
            context['message'] = "희망근무일수 보다 신청한 근무요일이 적습니다!!"
            return render_to_response('plan/staffPossibleAlert.html', context)
        
        staff.possible_N_days = post.get("희망근무일수")
        staff.save()
        print(staff.possible_N_days)

        # possible schedule 초기화 (모두 삭제)
        Possible_schedule.objects.filter(staff_id=staff).delete()

        for time in timeList:
            postList = post.getlist(time)
            print(postList)

            for day in postList:
                dayInstance = Day.objects.filter(day=day).get(time=time)
                new_instance = Possible_schedule(staff_id=staff, day_id=dayInstance)
                new_instance.save()

        return redirect("/staff/"+staffName+"/"+staffPhone+"/")
    elif request.method == "GET":
        possible = Possible_schedule.objects.filter(staff_id=staff)

        context["day_num"] = staff.possible_N_days
        context["possibleAll"] = possible
        print(possible)
    return render(request, 'plan/staff_schedule_enrollment.html', context)


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

def manageRealView(request):
    context = {}

    return render(request, 'plan/manager_realSchedules.html', context)