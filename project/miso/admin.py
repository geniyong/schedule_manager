from django.contrib import admin
from .models import *
# Register your models here.


class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'score', 'possible_N_days')


admin.site.register(Staff, StaffAdmin)


class DayAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'time', 'needs')


admin.site.register(Day, DayAdmin)


class RealscheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff_id', 'day_id')


admin.site.register(Real_schedule, RealscheduleAdmin)


class PossiblescheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff_id', 'day_id')


admin.site.register(Possible_schedule, PossiblescheduleAdmin)