from django.db import models
import time
from django.utils import timezone


class Strategy_pnl(models.Model):
    str_name = models.CharField(max_length=10,default="未输入策略名")
    pnl = models.CharField(max_length=6,default='0')
    # 这里偷懒，直接让pnl用varchar类型，后续可改
    updated_time = models.DateTimeField(default=timezone.now)
    # time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    def __str__(self):
        "返回一个对象的描述信息"
        return self.str_name



class User(models.Model):
    username=models.CharField(max_length=16)
    password=models.CharField(max_length=32)
