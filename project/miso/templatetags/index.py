from django import template
register = template.Library()

    # ===============================================================
    # Template Custom Language
    # 커스텀 태그 : Index
    # 기능 : template 에서 서버로부터 전달된 list 에 index로 접근하기
    ### ex) :
    ### {% load index %}
    ### {{ List|index:x }}
    ### for문 loop counter 활용 예시
    ### {{ List|index:forloop.counter0 }}
    # ===============================================================

@register.filter
def index(List, i):
    return List[int(i)]


@register.filter
def get_needs(day):
    return day.needs


@register.filter
def get_needs_new(day):
    return day.needs_newcomer


@register.filter
def get_real_origin(day):
    return day.real_origin


@register.filter
def get_real_new(day):
    return day.real_newcomer


@register.filter
def filter_day(dayAll, day):
    return dayAll.filter(day=day)


@register.filter
def filter_time(days, time):
    return days.get(time=time)


@register.filter
def filter_real(dayid, realAll):
    return realAll.filter(day_id=dayid)


@register.filter
def get_real_staff(realAll, staff):
    return realAll.get(staff_id=staff)


@register.filter
def get_staff(reals):
    staffList = []
    string=' '
    for real in reals:
        staffList.append(real.staff_id.name)

    return string.join(staffList)
