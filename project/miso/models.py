from django.db import models

# Create your models here.
from django.db.transaction import on_commit


class Post (models.Model):
    title = models.CharField(max_length=45)
    content = models.TextField()

    def __str__(self):
        return str(self.title)

class Staff (models.Model):
    name = models.CharField(max_length=45)
    phone = models.CharField(max_length=20)
    score = models.FloatField(null=True)
    possible_N_days = models.IntegerField(null=True)

    def __str__(self):
        return str(self.name)

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

    def __str__(self):
        return str(self.day) + ':' + str(self.time)


class Real_schedule (models.Model):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day_id = models.ForeignKey (Day, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.staff_id) + ':' + str(self.day_id)


class Possible_schedule (models.Model):
    staff_id = models.ForeignKey(Staff, on_delete= models.CASCADE)
    day_id = models.ForeignKey(Day, on_delete= models.CASCADE)

    def __str__(self):
        return str(self.staff_id) + ':' + str(self.day_id)