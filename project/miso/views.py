from audioop import max
from numbers import Real
from operator import is_

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
    timeList = ['D', 'N', 'N1','D1','N2','D2', 'M', 'M1', 'M2', 'M3', 'M4']

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
    # 4. 가능 스케쥴의 is_assigned 초기화
    # ===============================================================

    # 1. 실제 스케줄 데이터 초기화
    Real_schedule.objects.all().delete()
    print(Real_schedule.objects.all())

    # 2. 요일/날짜 마다 실제 배치 인원 초기화
    # day의 real_origin과 real_newcomer 초기화
    for day in Day.objects.all():
        day.real_newcomer = 0
        day.real_origin = 0
        day.modifiable_origin = True
        day.save()

    # 3. 모든 미소지기의 complete Boolean Set : 실제 스케줄 배치가 완료되었는가에 관한 Data 초기화
      # Staff.min_complete , Staff.max_complete 초기화
    for staff in Staff.objects.all():
        staff.min_complete = False
        staff.max_complete = False
        staff.save()

    # 4. Possible_schedule의 is_assigned 초기화
    for schedule in Possible_schedule.objects.all():
        schedule.is_assigned = False
        schedule.save()


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
        possible = Possible_schedule.objects.filter(staff_id=staff)

        for day in dayList:
            day_success = 0 # 그 날에 scheduling이 되었는가

            for time in timeList:
                if day_success != 0:
                    break
                temp2 = Day.objects.get(day=day, time=time) #### day model
                if temp2.needs - temp2.needs_newcomer <= temp2.real_origin: # 충분한 자리가 있는가?
                    continue # 다음 시간대로 넘김, 요일은 그대로라서 continue
                for pos in possible:
                    if pos.day_id == temp2:
                        # day에 자리가 있으면 추가
                        createRealSchedule(pos.id)
                        day_success = 1
                        count = count + 1

                        break

            if count >= limit:
                staff.min_complete = True
                staff.save()
                break

        if staff.min_complete == False :
            origin_minFailList.append(staff)

    print(origin_minFailList)


    # 신규 스태프 스케쥴링 - 3일 먼저
    for staff in newList:
        count = 0
        limit = 3
        possible = Possible_schedule.objects.filter(staff_id=staff)

        for day in dayList:
            day_success = 0  # 그 날에 scheduling이 되었는가

            for time in timeList:
                if day_success != 0:
                    break
                temp2 = Day.objects.get(day=day, time=time)  #### day model
                if temp2.needs_newcomer <= temp2.real_newcomer: # 충분한 자리가 있는가?
                    continue
                for pos in possible:
                    if pos.day_id == temp2:
                        createRealSchedule(pos.id)
                        day_success = 1
                        count = count + 1

                        break

            if count >= limit:
                staff.min_complete = True
                staff.save()
                break

        if staff.min_complete == False:
            new_minFailList.append(staff)


    # Modify
    # minFailList에서 3일 배정
    for staff in origin_minFailList:
        modifyFailStaff(staff)

    for staff in new_minFailList :
        modifyFailStaff(staff)


    #추가필요부분
    # 3일분 먼저 처리 init + modify / 4일 희망자 처리 / 5일 희망자 처리
    # 스키마변경 - > 실제스케줄 반영 후 다시 남는 가능한 시간대만 따로 정리된 모델 추가
    # 스케줄링 실패 미소지기 목록 모델 추가
    # Real_schedule 추가

    return True

def modifyFailStaff(staff):
    dayList2 = ['토요일', '일요일', '금요일', '월요일', '화요일', '수요일', '목요일']
    timeList2 = ['D', 'N', 'N1', 'D1', 'N2', 'D2', 'M', 'M1', 'M2', 'M3', 'M4'].reverse()

    count = Real_schedule.objects.filter(staff_id=staff).count() # 현재까지 배치된 실제스케줄 수

    possible = Possible_schedule.objects.filter(staff_id=staff, is_assigned=False)
    for day in dayList2:
        for time in timeList2:
            # temp2 는 dayList2 와 timeList2를 활용하여 재정렬한 결과임
            # EX) ['토요일':'M1','토요일':'M' ..... '목요일':'N', '목요일':'D']
            temp2 = Day.objects.get(day=day, time=time)  #### day model
            for pos in possible:
                if count >= 3: # 3일 planning module 이기 때문에 limit = 3 
                    # 실제 스케줄이 3일 이상이면 함수종료
                    return count
                
                if pos.day_id == temp2:    
                    # 강제 변경해야 될 시간대에 실제로 배치된 스케줄들을 뽑아옴
                    #  (이 instance 안에 배치된 미소지기 정보가 있음)
                    candidateRealscheudles = Real_schedule.objects.filter(day_id=temp2).reverse()

                    if staff.newcomer:
                        # 실제로 배치된 스케줄들에서 for 문 반복하며 개별 staff를 뽑음
                        for candidateReal in candidateRealscheudles:

                            # candidateStaff 는 실제 스케줄에 배치 된 개별 미소지기
                            candidateStaff = candidateReal.staff_id
                            if candidateStaff.newcomer :
                                # 실패한 미소지기가 강제로 들어가야 될 스케줄에서
                                # 후보 미소지기를 다른 시간대로 옮기는 작업 : modifyCandidates()
                                if modifyCandidates(candidateStaff) : # 다른 시간대로 옮기기에 성공했다면

                                    # 다른시간대로 옮겨진 미소지기의 실제 스케줄 삭제
                                    updateRealSchedule(candidateReal.id,pos.id)
                                    count += 1
                                    break

                    else :
                        for candidateReal in candidateRealscheudles:
                            # candidateStaff 는 실제 스케줄에 배치 된 개별 미소지기
                            candidateStaff = candidateReal.staff_id
                            if candidateStaff.newcomer == False :
                                # 실패한 미소지기가 강제로 들어가야 될 스케줄에서
                                # 후보 미소지기를 다른 시간대로 옮기는 작업 : modifyCandidates()
                                if modifyCandidates(candidateStaff) : # 다른 시간대로 옮기기에 성공했다면
                                    updateRealSchedule(candidateReal.id, pos.id)
                                    count += 1
                                    break
    return count

def modifyCandidates(candidateStaff):
    candidatePossibles = Possible_schedule.objects.filter(staff_id=candidateStaff,
                                                          is_assigned=False)

    if candidateStaff.newcomer :
        for candidatePos in candidatePossibles:
            candidateDay = candidatePos.day_id
            if candidateDay.needs_newcomer > candidateDay.real_newcomer:
                createRealSchedule(candidatePos.id)
                return True

    else :
        for candidatePos in candidatePossibles:
            candidateDay = candidatePos.day_id
            if candidateDay.needs - candidateDay.needs_newcomer > candidateDay.real_origin:
                createRealSchedule(candidatePos.id)
                return True

    return False


    

'''
# 실행하는 경우 :  Real_schedule이 삭제된 경우, Day.needs <= Day.real_origin이 되는 경우
# Modifiable을 체크하고 결과를 반환한다.
def checkModifiableOrigin(da): # Day의 id
    day = Day.objects.get(pk=da)
    # 1. day의 Staff가 부족한 경우 : True
    if day.real_origin > day.needs:
        day.modifiable_origin = True
        day.save()
        return True

    # 2. day의 Staff가 충분한 경우 :
    # 배정된 Staff중 하나라고 다른 Day에 Schedule을 가질 수 있는 경우 True
    # 아닌 경우 False

    # day의 Staff들
    staff = []
    for real in Real_schedule.objects.filter(day_id=da):
        staff.append(real.staff_id)

    # 한명의 Staff라도 변경 가능하다면 Modifiable
    for stf in Staff:
        # Staff의 가능 스케쥴의 Day들
        days = Possible_schedule.objects.filter(staff_id=stf, is_assigned=False).day_id

        for day2 in days:
            if day2.modifiable_origin:
                day.modifiable_origin = True
                day.save()
                return True

    day.modifiable_origin = False
    day.save()
    return False
'''


def createRealSchedule(possible):  # Possible_schedule의 id
    print("Real Schedule 생성 ...")

    pos = Possible_schedule.objects.get(pk=possible)
    stf = pos.staff_id
    da = pos.day_id
    print(pos)

    # Possible_schedule 동기화
    pos.is_assigned = True
    pos.save()

    # Day 동기화
    if stf.newcomer:
        da.real_newcomer = da.real_newcomer + 1
    else:
        da.real_origin = da.real_origin + 1
    da.save()

    # Real_schedule 생성
    rs = Real_schedule(staff_id=stf, day_id=da)
    rs.save()
    return


def updateRealSchedule(real_id, pos_id): # Real_schedule의 id, Possible_schedule의 id
    real = Real_schedule.objects.get(pk=real_id)
    staff = real.staff_id
    day = real.day_id
    pos = Possible_schedule.objects.get(staff_id=staff, day_id=day)
    new_pos = Possible_schedule.objects.get(pk=pos_id)

    # Possible_schedule 동기화
    pos.is_assigned = False
    pos.save()
    new_pos.is_assigned = True
    new_pos.save()

    # 결과적으로 Day 변화 없음

    # Real_schedule 수정
    real.staff_id = new_pos.staff_id
    real.day_id = new_pos.day_id
    real.save()
    return

'''
def createRealSchedule(staff, day):  # Staff의 id, Day의 id
    print("Real Schedule 생성 ...")
    stf = Staff.objects.get(pk=staff)
    da = Day.objects.get(pk=day)
    rs = Real_schedule(staff_id=stf, day_id=da)
    rs.save()

    return
'''

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
    '''
    Day.objects.all().delete()
    dayList = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    timeList = ['D', 'D1', 'D2', 'M', 'M1', 'M2', 'M3', 'M4', 'N', 'N1', 'N2']
    for day in dayList:
       for time in timeList:
           Day(day=day, time=time).save()
    '''
    context = {}
    if request.method == 'POST':
        post = request.POST
        staffName=post.get('name')
        staffPhone=post.get('phone')
        context['staffName'] = staffName
        context['staffPhone'] = staffPhone

        if (staffName == 'manager'):
            if(staffPhone == '01012345678'):
                return redirect('../manager/')
            else:
                context['message'] = "권한오류 : 매니저 정보를 다시 입력하세요"
                context['mode'] = 1
                return render_to_response('plan/loginAlert.html', context)

        print(staffName + ':' + staffPhone)
        qs = Staff.objects.filter(name=staffName)
        if qs.count()==0:
            context['message'] = "경고 : "+staffName+" 은 등록 되어 있지 않습니다. 새로 추가하시겠습니까?"
            context['mode'] = 2
            newInstance = Staff(name=staffName, phone=staffPhone)
            newInstance.save()

        else:
            qs = Staff.objects.filter(phone=staffPhone)
            if (qs.count==0):
                context['message'] = "경고 : " + staffName + "미소지기는 이미 등록 되어 있습니다.\n" + staffPhone + "번호로 추가하시겠습니까?"
                context['mode'] = 2
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
    print("==========")
    timeList = ['D', 'D1', 'D2', 'M', 'M1', 'M2', 'M3', 'M4', 'N', 'N1', 'N2']
    timeStr = ['D, 6.75h', '06:30 - 13:30, 6.75h', '09:00 - 16:00, 6.75h', '09:30 - 16:30, 6.75h', '13:00 - 20:00, 6.75h', '14:00 - 21:00, 6.75h', '15:00 - 22:00, 6.75h', '16:00 - 23:00, 6.75h', '20:00 - 27:00, 6.75h', '21:00 - 28:00, 6.75h']
    possibleDays=[]
    bolt=0
    weekendCount = 0
    context = {"staffName" : staffName, "staffPhone" : staffPhone, "dayList" : dayList, "timeList": timeList, "timeStr":timeStr }

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
        timeList = ['D', 'D1', 'D2', 'M', 'M1', 'M2', 'M3', 'M4', 'N', 'N1', 'N2']
        dayAll = Day.objects.all()
        context = {'dayAll':dayAll, 'timeList':timeList}

    elif request.method == 'POST':
        post = request.POST
        print(post)
        return redirect('./')
    return render(request, 'plan/manager_needs.html',context)


def manageNeedsUpdate(request, day):
    timeList = ['D', 'D1', 'D2', 'M', 'M1', 'M2', 'M3', 'M4', 'N', 'N1', 'N2']
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