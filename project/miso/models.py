from django.db import models

# Create your models here.
from django.db.transaction import on_commit
from django.template import defaultfilters


class Post (models.Model):
    title = models.CharField(max_length=45)
    content = models.TextField()

    def __str__(self):
        return str(self.title)

class Staff (models.Model):
    name = models.CharField(max_length=45)
    phone = models.CharField(max_length=20)
    score = models.FloatField(blank=True, default=50)
    possible_N_days = models.IntegerField(blank=True, default=3)
    newcomer = models.BooleanField(blank=True, default=False)

    class Meta:
        unique_together = ('name', 'phone')

    def __str__(self):
        return str(self.name + ":" + self.phone)

class Day (models.Model):

    day_opt = (
        ('월요일', '월요일'),
        ('화요일', '화요일'),
        ('수요일', '수요일'),
        ('목요일', '목요일'),
        ('금요일', '금요일'),
        ('토요일', '토요일'),
        ('일요일', '일요일'),
    )

    time_opt = (
        ('D', '오픈'),
        ('D1', '준오픈'),
        ('M', '미들'),
        ('M1', '늦미들'),
        ('N', '마감'),
    )

    day = models.CharField(max_length=10, choices=day_opt)
    time = models.CharField(max_length=5,choices=time_opt)
    needs = models.IntegerField(blank=True, default=5)
    needs_newcomer = models.IntegerField(blank=True, default=2)

    class Meta:
        unique_together = ('day', 'time')
    def __str__(self):
        return str(self.day) + ':' + str(self.time)


class Real_schedule (models.Model):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day_id = models.ForeignKey (Day, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.staff_id) + ':' + str(self.day_id)


class Possible_schedule(models.Model):
    staff_id = models.ForeignKey(Staff, on_delete= models.CASCADE)
    day_id = models.ForeignKey(Day, on_delete= models.CASCADE)

    class Meta:
        unique_together = ('staff_id', 'day_id')

    def __str__(self):
        return str(self.staff_id) + ':' + str(self.day_id)