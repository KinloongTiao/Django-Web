
from django.http import HttpResponse, JsonResponse
from datetime import datetime,timedelta
import pandas as pd
import json
from interface.datapath import *
from interface.models import User
from interface.task import *
# 这个是定时任务，在task里面，不能删除
import time
from django.shortcuts import redirect, HttpResponse, render
from functools import wraps
from werkzeug.security   import  generate_password_hash, check_password_hash
import numpy as np


def login(request):
    # 如果是POST请求，则说明是点击登录按扭 FORM表单跳转到此的，那么就要验证密码，并进行保存session
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=User.objects.filter(username=username,password=password)

        if user:
            #登录成功
            # 1，生成特殊字符串
            # 2，这个字符串当成key，此key在数据库的session表（在数据库存中一个表名是session的表）中对应一个value
            # 3，在响应中,用cookies保存这个key ,(即向浏览器写一个cookie,此cookies的值即是这个key特殊字符）
            request.session['is_login']='1'  # 这个session是用于后面访问每个页面（即调用每个视图函数时要用到，即判断是否已经登录，用此判断）
            # request.session['username']=username  # 这个要存储的session是用于后面，每个页面上要显示出来，登录状态的用户名用。
            request.session['user_id']=user[0].id
            request.session['user_name']=user[0].username
            print("{}")
            return redirect('/real-time/')
    # 如果是GET请求，就说明是用户刚开始登录，使用URL直接进入登录页面的
    fp = open(HTML_INTEMPLATE_PATH+"login.html",encoding='UTF-8')
    html = fp.read()
    fp.close()
    return HttpResponse(html)
    # return render(request,'login.html')

def logout(request):
    if not request.session.get('is_login', None): # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()

    return redirect("/login/")

def check_login(f):
    @wraps(f)
    def inner(request,*arg,**kwargs):
        if request.session.get('is_login')=='1':

            login_user = request.session.get('user_name')
            if  login_user == "root" or login_user == 'ling':
                return f(request,*arg,**kwargs)
            # 非root用户会强制转换成该专户自己对应的网页，其没有权限访问其他网页
            else:
                web_url = '/'+ login_user +'/'
                return redirect(web_url)
        else:
            return redirect('/login/')
    return inner


#=================================================================================#
""" 策略管理 """

def generate_group_file(file_name, file_content_df):
    file_content = file_content_df
    group_json = [dict(file_content.loc[i]) for i in file_content.index]

    with open(TABLE_DATA_PATH + file_name + "_group_pnl.json", "w") as f:
        json.dump(group_json, f)

def correct_capital(request):

    file_name = request.GET['product_name']
    correct_capital = float(request.GET['correct_capital'])
    correct_nv = float(request.GET['correct_nv'])
    is_product = True

    print(file_name,correct_capital,correct_nv)

    if is_product:
        product_path = MANAGEMENT_PATH + "product_manage.json"
        with open(product_path,'r') as f:
            product_json = json.load(f)

        for index,pro in enumerate(product_json):
            if pro["account"] == file_name:
                new_product = pro
                new_product["total_asset"] = str(float(correct_capital))
                product_json[index] = new_product

        with open(product_path,"w") as f:
            json.dump(product_json,f)

    file_tsdata_path = HISTORY_NETVALUE_PATH + file_name + '_tsdata.json'
    file_nv_detail_path = HISTORY_NETVALUE_PATH + file_name + "_nv_detail.json"

    with open(file_tsdata_path, 'r') as f:
        load_ts_json = json.load(f)
        ts_capital = list(load_ts_json['ts_capital'])
        ts_data = list(load_ts_json['ts_data'])
        ts_date = list(load_ts_json['ts_date'])
        amount = load_ts_json["amount"]

        ts_capital[-1] = round(float(correct_capital),3)
        ts_data[-1] = round(float(correct_nv),6)

        new_ts_json = dict(ts_capital=ts_capital, ts_data=ts_data, ts_date=ts_date,amount = amount)

        with open(file_tsdata_path, 'w') as f:
            json.dump(new_ts_json, f)

    CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
    with open(file_nv_detail_path, 'r') as f:
        load_nv_json = json.load(f)
        new_insert_json = {}

        new_insert_json["trade_date"] = CURRENT_DATE
        new_insert_json["PNL"] = "校准"
        new_insert_json["capital"] = format(round(float(correct_capital),3),",")
        new_insert_json["net_value"] = round(float(correct_nv),6)
        new_insert_json["market_value"] = load_nv_json[0]["market_value"]
        new_insert_json["holding_rate"] = load_nv_json[0]["holding_rate"]

        load_nv_json.insert(0, new_insert_json)

        with open(file_nv_detail_path, 'w') as f:
            json.dump(load_nv_json, f)

    fp = open(HTML_INTEMPLATE_PATH+"tanchuang.html",encoding='UTF-8')
    html = fp.read()
    fp.close()
    return HttpResponse(html)

def in_out_money_change_json(file_name,in_out_money,is_product=False):

    if is_product:
        product_path = MANAGEMENT_PATH + "product_manage.json"
        with open(product_path,'r') as f:
            product_json = json.load(f)

        for index,pro in enumerate(product_json):
            if pro["account"] == file_name:
                new_product = pro
                new_product["total_asset"] = str(float(new_product["total_asset"]) + in_out_money)
                product_json[index] = new_product

        with open(product_path,"w") as f:
            json.dump(product_json,f)

    file_tsdata_path = HISTORY_NETVALUE_PATH + file_name + '_tsdata.json'
    file_nv_detail_path = HISTORY_NETVALUE_PATH + file_name + "_nv_detail.json"

    with open(file_tsdata_path, 'r') as f:
        load_ts_json = json.load(f)
        ts_capital = list(load_ts_json['ts_capital'])
        ts_data = list(load_ts_json['ts_data'])
        ts_date = list(load_ts_json['ts_date'])
        amount = load_ts_json["amount"]

        """因为nv_detail的净值也是从tsdata算出来的，所以只要对tsdata首日初始资金除权即可"""

        amount = amount  + in_out_money / ts_data[-1]

        # ts_data.append(ts_data[-1])  # 入金操作不会对净值造成影响
        ts_capital[-1] = round(float(ts_capital[-1]) + in_out_money,3)

        new_ts_json = dict(ts_capital=ts_capital, ts_data=ts_data, ts_date=ts_date,amount = amount)

        with open(file_tsdata_path, 'w') as f:
            json.dump(new_ts_json, f)
            print("校准：{}".format(in_out_money))

    CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
    with open(file_nv_detail_path, 'r') as f:
        load_nv_json = json.load(f)
        new_insert_json = {}

        new_insert_json["trade_date"] = CURRENT_DATE
        new_insert_json["PNL"] = "校准：{}".format(in_out_money)
        new_insert_json["capital"] = round((float(load_nv_json[0]["capital"].replace(",","")) + in_out_money),3)
        new_insert_json["net_value"] = load_nv_json[0]["net_value"]

        load_nv_json.insert(0, new_insert_json)

        with open(file_nv_detail_path, 'w') as f:
            json.dump(load_nv_json, f)

def add_strategy(request):
    # 添加或修改策略配置
    # admin_password
    strategy_name = request.GET['strategy_name']
    account_number = str(request.GET['account_number'])
    origin_capital = float(request.GET['origin_capital'])
    group = request.GET['group']
    strategy_type = request.GET['strategy_type']
    real_or_simulate = request.GET['real_or_simulate']
    show = request.GET['show_or_not']
    strategy_class = request.GET['strategy_class']
    yesterday_capital = request.GET['total_asset']

    trading_date = datetime.now().strftime("%Y-%m-%d")
    new_strategy = dict(PNL=0, market_value=0, position_profit=0, trade_profit=0, account_number=account_number, strategy_type=strategy_type, trade_date=trading_date,
                        capital=origin_capital, group=group, real_or_simulate=real_or_simulate, show=show, strategy_class=strategy_class, strategy_name=strategy_name,
                        accum_pnl=0,total_asset=yesterday_capital)

    try:
        # 此处选用all_strategy_pnl.json作为添加新策略的初始文件，目的是为了防止收盘后添加新策略造成初始化策略表的问题,如果没有则使用manage表
        with open(ALL_STRATEGY_PNL_PATH, 'r') as f:
            SM_TABLE_json = json.load(f)
            SM_TABLE = pd.DataFrame(SM_TABLE_json)
    except:
        with open(MANAGEMENT_PATH + "strategy_manage.json", 'r') as f:
            SM_TABLE_json = json.load(f)
            SM_TABLE = pd.DataFrame(SM_TABLE_json)

    if strategy_name not in list(SM_TABLE['strategy_name']):
        # 生成position,order,nv_detail,tsdata四个基本文件
        with open(TABLE_DATA_PATH + strategy_name + "_position.json", "w") as f:
            default_position = []
            json.dump(default_position, f)
        with open(TABLE_DATA_PATH +  strategy_name + "_order.json", "w") as f:
            default_order = []
            json.dump(default_order, f)
        with open(HISTORY_NETVALUE_PATH + strategy_name + "_tsdata.json", "w") as f:
            default_tsdata = dict(ts_capital=[origin_capital], ts_data=[1], ts_date=[trading_date],amount=origin_capital)
            json.dump(default_tsdata, f)
        with open(HISTORY_NETVALUE_PATH + strategy_name + "_nv_detail.json", "w") as f:
            default_nv_detail = [{"strategy_name": strategy_name, "PNL": "0","trade_date": trading_date, "market_value": 0.0, "net_value": 1, "capital": origin_capital}]
            json.dump(default_nv_detail, f)
        print("新策略{}四个基本文件已生成。".format(strategy_name))
    else:
        print("策略{}已存在，您将对其配置进行修改！".format(strategy_name))

    SM_TABLE = SM_TABLE.append(new_strategy, ignore_index=True)
    SM_TABLE_NEW_ALL = SM_TABLE.drop_duplicates(subset='strategy_name', keep='last')
    # 先删除再排序
    SM_TABLE_NEW_ALL = SM_TABLE_NEW_ALL.sort_values(by=["strategy_class","strategy_name"])
    SM_TABLE_SHOW = SM_TABLE_NEW_ALL.loc[SM_TABLE['show']=="1"]
    SM_TABLE_SHOW['holding_rate'] = SM_TABLE_SHOW['market_value'].apply(float) / SM_TABLE_SHOW['total_asset'].apply(float)

    df_group = SM_TABLE_SHOW.groupby(by=["group", "real_or_simulate"])
    for name, group in df_group:
        file_name = '_'.join(name)
        generate_group_file(file_name, group)

    df_group = SM_TABLE_SHOW.groupby(by=["real_or_simulate","strategy_type"])
    for name, group in df_group:
        file_name = '_'.join(name)
        generate_group_file(file_name, group)


    # 生成添加了新策略之后的json文件
    all_json = [dict(SM_TABLE_NEW_ALL.loc[i]) for i in SM_TABLE_NEW_ALL.index]

    with open(MANAGEMENT_PATH + "strategy_manage.json", "w") as f:
        json.dump(all_json, f)
    with open(ALL_STRATEGY_PNL_PATH, "w") as g:
        json.dump(all_json, g)

    fp = open(HTML_INTEMPLATE_PATH + "tanchuang.html", encoding='UTF-8')
    html = fp.read()
    fp.close()
    return HttpResponse(html)

def change_strategy(request):

    strategy_name = request.GET['strategy_name']
    in_out_money = float(request.GET['strategy_in_out_money'])
    # show = request.GET['show_or_not']

    """出入金还没写完"""
    if in_out_money != 0:
        in_out_money_change_json(strategy_name,in_out_money)

    fp = open(HTML_INTEMPLATE_PATH+"tanchuang.html",encoding='UTF-8')
    html = fp.read()
    fp.close()
    return HttpResponse(html)

def add_account(request):

    product_name = request.GET['product_name']
    account_name = str(request.GET['account_name'])
    django_name = request.GET['django_name']
    # show_or_not = request.GET['show_or_not']

    submit_product_account_key = product_name + account_name

    jsonFileRoot_product = MANAGEMENT_PATH + 'product_account_manage.json'
    with open(jsonFileRoot_product, 'r') as f:
        load_json = json.load(f)
        exist_product_account_keys = [exist_product['product_name']+exist_product['account_number'] for exist_product in load_json]

        print(exist_product_account_keys)
        reset_product_dict = dict(zip(exist_product_account_keys, load_json))

        if submit_product_account_key in reset_product_dict.keys():
            print(submit_product_account_key + "已存在，您将修改该产品的配置信息")
            # new_asset = reset_product_dict[product_name]["total_asset"] + in_out_money
            reset_product_dict[submit_product_account_key] = dict(product_name=product_name,account_number=account_name,django_name=django_name)
            new_json = list(reset_product_dict.values())
            with open(jsonFileRoot_product, 'w') as f:
                json.dump(new_json, f)

        else:
            print(product_name + " is not in exist_products.")
            new_product_json = dict(product_name=product_name,account_number=account_name,django_name=django_name)
            load_json.append(new_product_json)

            with open(jsonFileRoot_product, 'w') as f:
                json.dump(load_json, f)

    fp = open(HTML_INTEMPLATE_PATH+"tanchuang.html",encoding='UTF-8')
    html = fp.read()
    fp.close()
    return HttpResponse(html)

def add_product(request):

    product_name = request.GET['product_name']
    asset = request.GET['asset']
    show_or_not = request.GET['show_or_not']
    in_out_money = float(request.GET['in_out_money'])

    trading_date = datetime.now().strftime("%Y-%m-%d")

    jsonFileRoot_product = MANAGEMENT_PATH + 'product_manage.json'
    with open(jsonFileRoot_product, 'r') as f:
        load_json = json.load(f)
        exist_product_names = [exist_product['account'] for exist_product in load_json]
        reset_product_dict = dict(zip(exist_product_names, load_json))

        if product_name in reset_product_dict.keys():
            print(product_name + "已存在，您将修改该产品的配置信息")
            # new_asset = reset_product_dict[product_name]["total_asset"] + in_out_money
            reset_product_dict[product_name] = dict(account=product_name,PNL='0',trade_date=datetime.now().strftime("%Y-%m-%d"),total_asset=asset,show=show_or_not)
            new_json = list(reset_product_dict.values())
            with open(jsonFileRoot_product, 'w') as f:
                json.dump(new_json, f)

            if in_out_money != 0:
                in_out_money_change_json(product_name,in_out_money,is_product=True)

        else:

            print(product_name + " is not in exist_products.")
            new_product_json = dict(account=product_name,PNL='0',trade_date=datetime.now().strftime("%Y-%m-%d"),total_asset=asset,show=show_or_not)
            load_json.append(new_product_json)

            with open(jsonFileRoot_product, 'w') as f:
                json.dump(load_json, f)

            with open(HISTORY_NETVALUE_PATH + product_name + "_tsdata.json", "w") as f:
                default_tsdata = dict(ts_capital=[float(asset)], ts_data=[1], ts_date=[trading_date],amount=float(asset))
                json.dump(default_tsdata, f)

            with open(HISTORY_NETVALUE_PATH + product_name + "_nv_detail.json", "w") as f:
                default_nv_detail = [{ "PNL": "0","trade_date": trading_date, "market_value": 0.0, "net_value": 1, "capital": float(asset)}]
                json.dump(default_nv_detail, f)


    fp = open(HTML_INTEMPLATE_PATH+"tanchuang.html",encoding='UTF-8')
    html = fp.read()
    fp.close()
    return HttpResponse(html)


#=================================================================================#
""" Web展示 """

@check_login
def main(request):
    return render(request,HTML_INTEMPLATE_PATH+"main_page.html")

@check_login
def real_time(request):
    return render(request,HTML_INTEMPLATE_PATH+"real_time.html")

@check_login
def quant_simulate(request):
    return render(request,HTML_INTEMPLATE_PATH+"quant_simulate.html")

@check_login
def quant_real(request):
    return render(request,HTML_INTEMPLATE_PATH+"quant_real.html")

@check_login
def zhang_simulate(request):
    return render(request,HTML_INTEMPLATE_PATH+"zhang_simulate.html")

@check_login
def zhang_real(request):
    return render(request,HTML_INTEMPLATE_PATH+"zhang_real.html")

def lifeng(request):
    return render(request,HTML_INTEMPLATE_PATH+"lifeng.html")

def cheng(request):
    return render(request,HTML_INTEMPLATE_PATH+"cheng.html")


def lifeng_netvalue(request):
    return render(request,HTML_INTEMPLATE_PATH+"lifeng_netvalue.html")

@check_login
def research(request):
    return render(request,HTML_INTEMPLATE_PATH+"research.html")

@check_login
def netvalue(request):
    return render(request,HTML_INTEMPLATE_PATH+"netvalue.html")

@check_login
def management(request):
    return render(request,HTML_INTEMPLATE_PATH+"management.html")

def testApi(request):
    return render(request,HTML_INTEMPLATE_PATH+"testBootstrap.html")


#=================================================================================#
""" POST接口 """

def postorder(request):

    globals = {'nan': 0}
    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:
            postList = request.POST.getlist('postList',[])
            if len(postList) != 0:
                postlist_trans = []
                for i in postList:
                    postlist_trans.append(eval(i,globals))
                strategy_name = postlist_trans[0]['strategy_name']

                if strategy_name:
                    # res = add_args(position, pnl)
                    try:
                        jsonWriteOrder(strategy_name,postlist_trans)
                        return HttpResponse(strategy_name+'_order已更改')
                    except:
                        return HttpResponse(strategy_name+"请确认order文件列数据是否正确")
                else:
                    return HttpResponse('输入错误')
            else:
                return HttpResponse('无订单信息更新')
        else:
            return HttpResponse('输入为空,数据未刷新')
    else:
        return HttpResponse('方法错误')

def postpositiondetail(request):

    globals = {'nan': 0}
    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:
            postList = request.POST.getlist('postList',[])
            strategy_name = request.POST.get('strategy_name', 0)

            postlist_trans = []
            for i in postList:
                postlist_trans.append(eval(i,globals))

            if strategy_name:
                jsonWritePositionDetail(strategy_name,postlist_trans)
                return HttpResponse(strategy_name+'持仓详情已更新')
            else:
                return HttpResponse('输入错误')
        else:
            return HttpResponse('输入为空,数据未刷新')
    else:
        return HttpResponse('方法错误')

def posttotalpnl_makeup(request):

    if request.method == 'POST':  # 当提交表单时
        if request.POST:
            postList = request.POST.getlist('postList',[])
            postlist_trans = []
            for i in postList:
                postlist_trans.append(eval(i))

            if  len(postlist_trans) != 0:
                jsonWriteTotalPNL(postlist_trans)
                strategySettlement()
                productSettlement()

                return HttpResponse('策略概览PNL已更改')
            else:
                return HttpResponse('输入错误')
        else:
            return HttpResponse('输入为空,数据未刷新')
    else:
        return HttpResponse('方法错误')

def posttotalpnl(request):
    globals = {'nan': 0}

    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:

            postList = request.POST.getlist('postList',[])

            postlist_trans = []
            for i in postList:
                postlist_trans.append(eval(i,globals))

            if  len(postlist_trans) != 0:
                # res = add_args(position, pnl)
                jsonWriteTotalPNL(postlist_trans)
                return HttpResponse('策略概览PNL已更改')
            else:
                return HttpResponse('POST数据为空')
        else:
            return HttpResponse('输入为空,数据未刷新')
    else:
        return HttpResponse('方法错误')

def post_all_pos_pnl_order(request):

    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:

            positions = request.POST.getlist('positions',[])
            pnls = request.POST.getlist('pnls',[])
            orders = request.POST.getlist('orders',[])

            # postlist_trans = []
            # for i in pnls:
            #     postlist_trans.append(eval(i))

            # if  len(postlist_trans) != 0:
            #     # jsonWriteTotalPNL(postlist_trans)
            #
            #     return HttpResponse('策略概览PNL已更改')
            # else:
            #     return HttpResponse('POST数据为空')
        else:
            return HttpResponse('输入为空,数据未刷新')
    else:
        return HttpResponse('方法错误')

def postCurrentProductTs(request):
    globals = {'nan': 0}
    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:

            postList = request.POST.getlist('postList',[])
            post_type = request.POST.get('post_type', 0)
            # print("Post position detail is ready...")

            postlist_trans = []
            for i in postList:
                postlist_trans.append(eval(i,globals))

            # print("jsonWrite ready...")
            print(postlist_trans)

            if post_type:
                # res = add_args(position, pnl)
                jsonWriteCurrentProductTS(postlist_trans)
                return HttpResponse(post_type+'：今日现货价格已刷新')
            else:
                return HttpResponse('输入错误')
        else:
            return HttpResponse('输入为空,数据未刷新')
    else:
        return HttpResponse('方法错误')

def postCurrentProductReturn(request):
    globals = {'nan': 0}
    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:

            postList = request.POST.getlist('postList',[])
            post_type = request.POST.get('post_type', 0)
            # print("Post position detail is ready...")

            postlist_trans = []
            for i in postList:
                postlist_trans.append(eval(i,globals))

            # print("jsonWrite ready...")
            print(postlist_trans)

            if post_type:
                # res = add_args(position, pnl)
                jsonWriteCurrentProductReturn(post_type,postlist_trans)
                return HttpResponse(post_type+'：涨幅统计已刷新')
            else:
                return HttpResponse('输入错误')
        else:
            return HttpResponse('输入为空,数据未刷新')
    else:
        return HttpResponse('方法错误')

def netValueSettlement(request):
    """每天核算过之后上传净值"""

    if request.method == 'POST':
        if request.POST:
            refresh = request.POST.get('refresh', 0)
            if refresh == 'yes':

                strategySettlement()
                productSettlement()

                return HttpResponse('历史净值已刷新，请刷新WEB核对净值清算结果')
            else:
                return HttpResponse('输入不是yes')
        else:
            return HttpResponse('输入为空,数据未刷新')
    else:
        return HttpResponse('方法错误')

def refine_order(request):

    if request.method == 'GET':
        strategy_name = request.GET.get('strategy_name',0)
        respose = {}

        if strategy_name:

            priority = {"拒绝":5,"已成":4,"已撤单":4,"部分成交":3,"未成交":2}
            refined_data_dict = {}

            with open(TABLE_DATA_PATH+strategy_name+'_order.json',"r") as f:
                order_json = json.load(f)
                non_refine_length = len(order_json)

            for order in order_json:
                if order["entrust_status"] not in priority.keys():
                    continue
                    # 筛选掉其他杂乱的订单状态

                if (order['system_order_id'] not in refined_data_dict.keys()):
                    refined_data_dict[order['system_order_id']] = order
                else:
                    old_status = refined_data_dict[order['system_order_id']]["entrust_status"]
                    new_status = order["entrust_status"]
                    if  priority[new_status] > priority[old_status]:
                        refined_data_dict[order['system_order_id']] = order

            refined_data = list(refined_data_dict.values())

            respose['length'] = non_refine_length
            respose['data'] = refined_data

            return JsonResponse(respose)
        else:
            return JsonResponse({'status':'无输入','length':0,'data':[]})
    else:
        return JsonResponse({'status':'方法错误','length':0,'data':[]})

def get_new_order(request):
    if request.method == 'GET':  # 当提交表单时
        # 判断是否传参

        strategy_name = request.GET.get('strategy_name', 0)
        old_len = request.GET.get('old_len', 0)
        if type(old_len) != int: old_len = 99999999999

        new_order_data = {}

        if strategy_name:
            with open(TABLE_DATA_PATH+strategy_name+'_order.json',"r") as f:
                order_json = json.load(f)
                new_len = len(order_json)

                end_length = max(0,(new_len - int(old_len)))
                '''选取前10条订单记录'''

            new_order_data['new_len'] = new_len
            new_order_data['limit'] = end_length
            new_order_data['data'] = order_json[0:end_length]

            return JsonResponse(new_order_data)
        else:
            return JsonResponse({'status':'未输入策略'})
    else:
        return JsonResponse({'status':'方法错误'})

def socket(request):
    return HttpResponse("ok")


#=================================================================================#
""" 后端数据操作 """


def productSettlement():

    jsonFileRoot = ALL_STRATEGY_PNL_PATH
    product_account_path = MANAGEMENT_PATH + "product_account_manage.json"
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    with open(jsonFileRoot, 'r') as f:
        SM_TABLE_json = json.load(f)
        SM_TABLE_ALL = pd.DataFrame(SM_TABLE_json)
        SM_TABLE_ALL["PNL"] = SM_TABLE_ALL['PNL'].apply(pd.to_numeric)
        SM_TABLE_ALL["market_value"] = SM_TABLE_ALL['market_value'].apply(pd.to_numeric)

        SM_TABLE_today = SM_TABLE_ALL[SM_TABLE_ALL['trade_date'] == today]

    with open(product_account_path, 'r') as f:
        PAM_TABLE_json = json.load(f)

    product_account_dict = {}
    """存储产品账号匹配关系表"""
    for product_account_each in PAM_TABLE_json:
        if product_account_each['product_name'] in product_account_dict.keys():
            product_account_dict[product_account_each['product_name']].append(product_account_each['account_number'])
        else:
            product_account_dict[product_account_each['product_name']] = []
            product_account_dict[product_account_each['product_name']].append(product_account_each['account_number'])

    """拿到每个账号的PNL和持仓市值"""
    account_sum_pnls = dict(SM_TABLE_today.groupby(by=["account_number"])["PNL"].sum())
    account_sum_mvs = dict(SM_TABLE_today.groupby(by=["account_number"])["market_value"].sum())

    # print("\n产品对应的账号：\n", product_account_dict)
    # print("\n账号对应的PNL：\n", account_sum_pnls)

    for pro in product_account_dict.keys():
        # 产品的两个基本文件tsdata,nv_detai路径
        pro_pnl = 0
        pro_market_value = 0
        for account in product_account_dict[pro]:
            if account in account_sum_pnls.keys():
                pro_pnl += account_sum_pnls[account]
                pro_market_value += account_sum_mvs[account]
            else:
                print("账号{}属于产品{}，但是在策略管理表格中未查到。".format(account, pro))

        product_ts_Root = HISTORY_NETVALUE_PATH + pro + "_tsdata.json"
        product_NVTS_Root = HISTORY_NETVALUE_PATH + pro + "_nv_detail.json"

        try:
            with open(product_ts_Root, 'r') as f:
                load_json = json.load(f)
                ts_capital = list(load_json['ts_capital'])
                ts_data = list(load_json['ts_data'])
                ts_date = list(load_json['ts_date'])
                amount = load_json["amount"]

                CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
                if CURRENT_DATE in ts_date:

                    ts_capital[-1] = ts_capital[-2] + round(pro_pnl, 3)
                    ts_data[-1] = ts_capital[-1] / amount
                    ts_date[-1] = ts_date[-1]

                    print("{}已清算，重新刷新".format(pro))
                else:
                    ts_capital.append(ts_capital[-1] + round(pro_pnl, 3))
                    ts_data.append(ts_capital[-1] / amount)
                    ts_date.append(CURRENT_DATE)

                    print("{}今日首次清算".format(pro))

                new_json = dict(ts_capital=ts_capital, ts_data=ts_data, ts_date=ts_date, amount=amount)

                with open(product_ts_Root, 'w') as f:
                    json.dump(new_json, f)

            with open(product_NVTS_Root, 'r') as f:
                load_json = json.load(f)
                first_date = list(load_json)[0]['trade_date']

                CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
                if CURRENT_DATE == first_date:
                    load_json[0] = dict(PNL=format(round(pro_pnl, 3),','), trade_date=CURRENT_DATE, net_value=round(ts_data[-1], 6),
                                        holding_rate="%.2f%%" % (100*pro_market_value/ts_capital[-1]),
                                        capital=format(round(ts_capital[-1], 3),','), market_value=format(round(pro_market_value, 3),','))
                else:

                    new_json = dict(PNL=format(round(pro_pnl, 3),','), trade_date=CURRENT_DATE, market_value=format(round(pro_market_value, 3),','),
                                    holding_rate="%.2f%%" % (100 * pro_market_value / ts_capital[-1]),
                                    net_value=round(ts_data[-1], 6), capital=format(round(ts_capital[-1], 3),','))
                    load_json.insert(0, new_json)

                with open(product_NVTS_Root, 'w') as f:
                    json.dump(load_json, f)
        except:
            print("Warning:: ({})可能未在TABLE_DATA_PATH中添加产品文件。".format(pro))

    print("今日产品净值清算结束。")

def strategySettlement():

    jsonFileRoot = ALL_STRATEGY_PNL_PATH
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    with open(jsonFileRoot, 'r') as f:
        SM_TABLE_json = json.load(f)

    for str in SM_TABLE_json:

        str_date = str["trade_date"]
        str_ts_Root = HISTORY_NETVALUE_PATH + str["strategy_name"] + "_tsdata.json"
        str_NVTS_Root = HISTORY_NETVALUE_PATH + str["strategy_name"] + "_nv_detail.json"
        str_pnl = float(str["PNL"])
        str_market_value = float(str["market_value"])

        if str_date == today and str_pnl != 0:
            # 暂定今日盈亏为0的是未启动策略，不参与净值结算
            try:
                with open(str_ts_Root, 'r') as f:
                    load_json = json.load(f)
                    ts_capital = list(load_json['ts_capital'])
                    ts_data = list(load_json['ts_data'])
                    ts_date = list(load_json['ts_date'])
                    amount = load_json["amount"]

                    CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
                    if CURRENT_DATE in ts_date:
                        ts_capital[-1] = ts_capital[-2] + round(str_pnl, 3)
                        ts_data[-1] = ts_capital[-1] /amount
                        ts_date[-1] = ts_date[-1]

                        print('{}策略净值已清算，重新刷新'.format(str["strategy_name"]))

                    else:
                        ts_capital.append(ts_capital[-1] + round(str_pnl, 3))
                        ts_data.append(ts_capital[-1] / amount)
                        ts_date.append(CURRENT_DATE)

                        print('{}策略净值首次清算'.format(str["strategy_name"]))

                    new_json = dict(ts_capital=ts_capital, ts_data=ts_data, ts_date=ts_date,amount=amount)

                    with open(str_ts_Root, 'w') as f:
                        json.dump(new_json, f)

                with open(str_NVTS_Root, 'r') as f:
                    load_json = json.load(f)
                    first_date = list(load_json)[0]['trade_date']

                    CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
                    if CURRENT_DATE == first_date:
                        load_json[0] = dict(PNL=format(str_pnl,','), trade_date=CURRENT_DATE, net_value=round(ts_data[-1], 6),
                                            holding_rate="%.2f%%" % (100 * str_market_value / ts_capital[-1]),
                                            capital=format(round(ts_capital[-1], 3),','),market_value=format(str_market_value,','))
                    else:
                        new_json = dict(PNL=format(str_pnl,','), trade_date=CURRENT_DATE, net_value=round(ts_data[-1], 6),
                                        holding_rate="%.2f%%" % (100 * str_market_value / ts_capital[-1]),
                                        capital=format(round(ts_capital[-1], 3),','),market_value=format(str_market_value,','))
                        load_json.insert(0, new_json)

                    with open(str_NVTS_Root, 'w') as f:
                        json.dump(load_json, f)
            except:
                print("{}历史净值未写入，请核对文件是否存在或其他格式问题".format(str["strategy_name"]))
        else:
            pass

    print("今日策略净值清算结束。")

def jsonWriteOrder(strategy_name,postData):

    jsonFileRoot =TABLE_DATA_PATH+strategy_name + "_order.json"

    with open(jsonFileRoot, 'r') as f:
        load_json = json.load(f)

    for post in postData:
        load_json.insert(0,post)

    with open(jsonFileRoot, 'w') as f:
        json.dump(load_json, f)
        print(strategy_name + "_order.json已更改！")

def jsonWritePositionDetail(strategy_name,postData):

    jsonFileRoot = TABLE_DATA_PATH+ strategy_name + "_position.json"

    if len(postData) == 0:
        default_data = [ {"strategy_name": strategy_name, "trade_date":"","stock_code": " ","stock_name":" ",'long_short': 0,"signal":0,
                          "last_price": 0, "pnl": 0, "pnl_rate": "0", "current_amount": 0,"market_value":0,"AccumPNL":0,
                          "yesterday_amount": 0, "cost_price": 0} ]
        with open(jsonFileRoot, 'w') as f:
            json.dump(default_data, f)
            print(strategy_name + "_position.json覆盖（无持仓详情）")
    else:
        with open(jsonFileRoot,'w') as f:
            json.dump(postData,f)
            print(strategy_name+"_position.json已重新更改！")

def deletejson(request):
    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:
            strategy_name = request.POST.get('strategy_name',0)
            field = request.POST.get('field',0)
            if strategy_name:
                deleteJsonFile(strategy_name,field)
                return HttpResponse(strategy_name+'_'+field+'文件已删除或初始化')
            else:
                return HttpResponse('输入不正确')
        else:
            return HttpResponse('无信息')

    else:
        return HttpResponse('方法错误')

def deleteJsonFile(strategy_name,field):

    jsonFileRoot =TABLE_DATA_PATH+strategy_name + "_" + field + ".json"
    if field == "order" or field == "position":
        default_data = []
        with open(jsonFileRoot, 'w') as f:
            json.dump(default_data, f)

def jsonWriteTotalPNL(postData):

    try:
        """如果没有all_strategy_pnl，就用strategy_manage代替"""
        with open(ALL_STRATEGY_PNL_PATH,'r') as f:
            load_json = json.load(f)
    except:
        print("all_strategy_pnl有问题，将使用策略管理文件复制一份新的。")
        strategy_manage = MANAGEMENT_PATH + "strategy_manage.json"
        with open(strategy_manage, 'r') as f:
            load_json = json.load(f)

    for post in postData:
        for i  in range(len(load_json)):
            if load_json[i]['strategy_name'] == post["strategy_name"]:
                load_json[i]['PNL'] = post['PNL']
                load_json[i]['trade_date'] = post['trade_date']
                load_json[i]['market_value'] = post['market_value']
                load_json[i]['accum_pnl'] = post['accum_pnl']

    SM_TABLE_ALL = pd.DataFrame(load_json)

    with open(ALL_STRATEGY_PNL_PATH,'w') as f:
        json.dump(load_json,f)
        print("all_strategy_pnl.json已更改！")

    SM_TABLE_SHOW = SM_TABLE_ALL.loc[SM_TABLE_ALL['show']=="1"]
    SM_TABLE_SHOW = SM_TABLE_SHOW.sort_values(by=["strategy_class","account_number"],ascending=[True, True])
    SM_TABLE_SHOW = SM_TABLE_SHOW.reset_index(drop=True)
    SM_TABLE_SHOW['holding_rate'] = SM_TABLE_SHOW['market_value'].apply(float) / SM_TABLE_SHOW['total_asset'].apply(float)
    """将设置为展示的策略分发给各个分组"""

    df_group = SM_TABLE_SHOW.groupby(by=["group", "real_or_simulate"])
    for name, group in df_group:
        file_name = '_'.join(name)
        generate_group_file(file_name, group)

    df_group = SM_TABLE_SHOW.groupby(by=["real_or_simulate","strategy_type"])
    for name, group in df_group:
        file_name = '_'.join(name)
        generate_group_file(file_name, group)

    """清算各个账号的PNL"""
    SM_TABLE_SHOW["float_pnl"] = SM_TABLE_SHOW['PNL'].apply(float)
    account_pnl = dict(SM_TABLE_SHOW.groupby(["account_number"])['float_pnl'].sum())

    """根据产品-账号关系表进行产品盈亏加总"""
    product_account_dict = getProductAccountRelation()
    product_capital = getProductCapital()

    product_pnl = {}

    for account in product_account_dict.keys():
        try:
            if product_account_dict[account] == 'simulate':
                continue
            elif product_account_dict[account] not in product_pnl.keys():
                product_pnl[product_account_dict[account]] = account_pnl[account]
            else:
                product_pnl[product_account_dict[account]] += account_pnl[account]
        except:
            # print("{} 不在产品账号关系中，请核查。".format(account))
            pass
    product_temp_pnl_json = [{"product_name": key, "PNL": round(product_pnl[key], 3),"pnlRate":round((product_pnl[key]/product_capital[key]),5)} for key in product_pnl.keys()]

    with open(TABLE_DATA_PATH + 'product_temp_pnl.json', 'w') as f:
        json.dump(product_temp_pnl_json, f)

    time_now = datetime.now()
    if (time_now.hour == 15) & (time_now.minute == 15):
        strategySettlement()
        productSettlement()

def getProductAccountRelation():

    with open(MANAGEMENT_PATH + 'product_account_manage.json', "r") as f:
        product_account = json.load(f)

    product_account_dict = {}
    for each in product_account:
        product_account_dict[each["account_number"]] = each["product_name"]

    return product_account_dict

def getProductCapital():

    with open(MANAGEMENT_PATH + 'product_manage.json','r') as f:
        product_group = json.load(f)
    product_capital_dict = {}
    for each in product_group:
        product_capital_dict[each["account"]] = float(each["total_asset"])

    return product_capital_dict

def jsonWriteCurrentProductTS(postData):

    for post in postData:
        print(post)

        CURRENT_PRODUCT_TS_Root = CMMODITY_PRICE_PATH + post['current_product_type'] + '_tsdata.json'
        print(CURRENT_PRODUCT_TS_Root)
        print(post['current_product_price'])
        new_json = {}
        with open(CURRENT_PRODUCT_TS_Root, 'r') as f:
            load_json = json.load(f)
            last_date = load_json["ts_date"][-1]
            ts_data = load_json["ts_data"]
            ts_date = load_json["ts_date"]


            if last_date != post['current_datetime']:

                ts_data.append(post['current_product_price'])
                new_json["ts_data"] = ts_data
                ts_date.append(post['current_datetime'])
                new_json["ts_date"] = ts_date

                with open(CURRENT_PRODUCT_TS_Root, 'w') as wf:
                    json.dump(new_json, wf)
                    print(post['current_product_type'] + "最新现货价格已刷新(第一次)。")

            else:
                ts_data[-1] = (post['current_product_price'])
                new_json["ts_data"] = ts_data
                new_json["ts_date"] = ts_date

                with open(CURRENT_PRODUCT_TS_Root, 'w') as wf:
                    json.dump(new_json, wf)
                    print(post['current_product_type'] + "最新现货价格已刷新。")

def jsonWriteCurrentProductReturn(post_type,postData):

    jsonFileRoot =  CMMODITY_PRICE_PATH + post_type + '_current_product_return.json'

    if len(postData) == 0:
        default_data = [{"product_type": " ", "current_price": 0, "yesterday_price": 0, "_dayReturn": 0.0,
                         "_weekReturn": 0.0, "_monthReturn": 0.0}]
        with open(jsonFileRoot, 'w') as f:
            json.dump(default_data, f)
            print(post_type + "涨跌幅初始化")
    else:
        with open(jsonFileRoot,'w') as f:
            json.dump(postData,f)
            print(post_type+"涨跌幅统计已重新更改！")

#=================================================================================#
""" 其他 """
def add(req):
    strategy_name = req.GET['strategy_name']
    option = req.GET['option']
    jsonFileRoot_total_pnl = r"C:\Users\Administrator\Desktop\stopStrategy.txt"
    with open(jsonFileRoot_total_pnl, 'w') as f:
        strategy_para = dict(strategy_name=strategy_name,option=option)
        json.dump(strategy_para, f)

    return render(req,HTML_INTEMPLATE_PATH+"tanchuang.html")

def ctimes(req):
    return HttpResponse(str(datetime.now()))

def formPOST(req):
    return render(req,HTML_INTEMPLATE_PATH+"formPOST.html")

def stopStrategy(req):

    info = "Congratulations!"

    jsonFileRoot_total_pnl = r"C:\Users\Administrator\Desktop\stopStrategy.txt"
    with open(jsonFileRoot_total_pnl, 'w') as f:
        strategy_para = dict(strategy_paa=info)
        json.dump(strategy_para, f)

    return render(req,HTML_INTEMPLATE_PATH+"tanchuang.html")

def concat_us(req):
    return render(req,HTML_INTEMPLATE_PATH+"concat_us.html")

def tanchuang(req):
    return render(req,HTML_INTEMPLATE_PATH+"tanchuang.html")

def interface(req):
    return render(req,HTML_INTEMPLATE_PATH+"main.html")

def testtop(req):
    return render(req,HTML_INTEMPLATE_PATH+"testTop.html")

def postAnything(request):
    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:
            postList = request.POST.get('anything',0)
            return HttpResponse('您传输的数据为：'+str(postList))
    else:
        return HttpResponse('方法错误')
