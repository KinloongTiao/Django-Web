# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render, redirect, HttpResponse
from interface.datapath import *

from interface.models import User


# 数据库操作
def add_user(request):
    print(request)
    test1 = User(username='admin001',password='123456')
    test1.save()
    # return HttpResponse("<p>数据添加成功！</p>")
    fp = open(HTML_INTEMPLATE_PATH+"add_user.html",
              encoding='UTF-8')
    html = fp.read()
    fp.close()
    return HttpResponse(html)
    # return render(request,'add_user.html')

def add_user_success(request):
    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:

            print("添加新用户准备。。。")

            username = request.POST.get('username',0)
            password = request.POST.get('password',0)
            new_user = User(username=username,password=password)
            new_user.save()
            # return HttpResponse("<p>数据添加成功！</p>")
            fp = open(HTML_INTEMPLATE_PATH+"login.html",
                      encoding='UTF-8')
            html = fp.read()
            fp.close()
            return HttpResponse(html)
            # return render(request,'login.html')