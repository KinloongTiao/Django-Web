from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from interface.datapath import *
import pandas as pd
import json
import shutil
from datetime import datetime,timedelta
import os


#=================================================================================#
"""初始化策略配置表"""
try:
    # 实例化调度器
    scheduler = BackgroundScheduler()
    # 调度器使用DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # 设置定时任务，选择方式为interval，时间间隔为10s
    # 另一种方式为周一到周五固定时间执行任务，对应代码为：
    # @register_job(scheduler,"interval", seconds=10)
    # day_of_week='mon-fri',
    @register_job(scheduler, 'cron', hour='20', minute='58', second='5',id='initStrategyTotal')
    # @register_job(scheduler,"interval", seconds=10)
    def initStrategyTotal():
        # 这里写你要执行的任务
        import os
        import zipfile

        def zip_ya(start_dir,zip_dir):

            start_dir = start_dir  # 要压缩的文件夹路径
            file_news = zip_dir    # 压缩后文件夹的名字

            z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)
            for dir_path, dir_names, file_names in os.walk(start_dir):
                f_path = dir_path.replace(start_dir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
                f_path = f_path and f_path + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
                for filename in file_names:
                    z.write(os.path.join(dir_path, filename), f_path + filename)
            z.close()
            return file_news

        today = datetime.now().strftime("%Y%m%d")
        post_date = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
        # post_date = (datetime.now()).strftime("%Y-%m-%d")

        strTotRoot = ALL_STRATEGY_PNL_PATH
        # product_capital_root = MANAGEMENT_PATH + 'product_group_pnl.json'

        start_dir = ROOT_PATH + 'static/tableData'
        zip_dir = BACKUP_DATA_PATH + today + '.zip'

        zip_ya(start_dir,zip_dir)

        def generate_group_file(file_name, file_content_df):
            file_content = file_content_df
            group_json = [dict(file_content.loc[i]) for i in file_content.index]
            with open(TABLE_DATA_PATH + file_name + "_group_pnl.json", "w") as f:
                json.dump(group_json, f)

        with open(strTotRoot,"r" ) as f:
            SM_TABLE_json = json.load(f)
            for i,strategy in enumerate(SM_TABLE_json):
                try:
                    this_strategy_ts_path = HISTORY_NETVALUE_PATH + strategy["strategy_name"] + '_tsdata.json'
                    with open(this_strategy_ts_path,'r') as g:
                        this_strategy_ts_data = json.load(g)["ts_capital"]
                        capital = round(float(this_strategy_ts_data[-1]),3)
                except:
                    capital = 10000.00
                    print('--->>> ',SM_TABLE_json[i])
                    """如果某策略文件不存在或打不开，则突出错误。方便找到并修改"""

                strategy["total_asset"] = capital
                SM_TABLE_json[i] = strategy


            SM_TABLE = pd.DataFrame(SM_TABLE_json)
            SM_TABLE["PNL"] = "0"
            SM_TABLE["trade_date"] = post_date
            SM_TABLE["accum_pnl"] = "0"
            SM_TABLE["market_value"] = "0"
            # SM_TABLE['holding_rate'] = SM_TABLE['market_value'].apply(float) / SM_TABLE['total_asset'].apply(float)

        SM_TABLE_NEW_ALL = SM_TABLE.drop_duplicates(subset='strategy_name', keep='last')

        SM_TABLE_SHOW = SM_TABLE_NEW_ALL.loc[SM_TABLE_NEW_ALL['show'] == "1"]
        SM_TABLE_SHOW = SM_TABLE_SHOW.sort_values(by=["strategy_name", "show"])

        df_group = SM_TABLE_SHOW.groupby(by=["group", "real_or_simulate"])
        for name, group in df_group:
            file_name = '_'.join(name)
            generate_group_file(file_name, group)
            print("{} group done!".format(file_name))

        df_group = SM_TABLE_SHOW.groupby(by=["real_or_simulate", "strategy_type"])
        for name, group in df_group:
            file_name = '_'.join(name)
            generate_group_file(file_name, group)
            print("{} group done!".format(file_name))

        # 生成添加了新策略之后的json文件
        total_group_json = [dict(SM_TABLE_NEW_ALL.loc[i]) for i in SM_TABLE_NEW_ALL.index]
        with open(MANAGEMENT_PATH + "strategy_manage.json", "w") as f:
            json.dump(total_group_json, f)

    register_events(scheduler)
    scheduler.start()
except Exception as e:
    print(e)

#=================================================================================#
"""收盘更新上证指数"""
try:
    scheduler2 = BackgroundScheduler()
    scheduler2.add_jobstore(DjangoJobStore(), "default")

    @register_job(scheduler2, 'cron', day_of_week='mon-fri', hour='15', minute='2', second='50', id='getShanghaiInsex')
    def getShanghaiInsex():

        """更新上证指数"""
        shanghaiRoot = HISTORY_NETVALUE_PATH + 'shanghai_tsdata.json'
        with open(shanghaiRoot, 'r') as f:

            load_json = json.load(f)
            index_data = list(load_json['ts_index'])
            index_date = list(load_json['ts_date'])

            now_date = datetime.strftime(datetime.now(),"%Y-%m-%d")

            if now_date in index_date:
                print(now_date)
                print('今日上证指数已经更新1。',now_date)
            else:
                import requests
                # 从新浪拿到今日收盘价
                data = requests.get('http://hq.sinajs.cn/list=s_sh000001')
                today_index = data.text.split(',')[1]

                index_data.append(float(today_index))
                index_date.append(now_date)

                new_json = dict(ts_index=index_data, ts_date=index_date)

                with open(shanghaiRoot, 'w') as f:
                    json.dump(new_json, f)
                    print("今天上证指数已更新（第一次）。")

    register_events(scheduler2)
    scheduler2.start()
except Exception as e:
    print(e)


"""收盘更沪深300指数"""
try:
    scheduler5 = BackgroundScheduler()
    scheduler5.add_jobstore(DjangoJobStore(), "default")

    @register_job(scheduler5, 'cron', day_of_week='mon-fri', hour='15', minute='1', second='10', id='getHushen300Index')
    def getHushen300Index():

        """更新上证指数"""
        shanghaiRoot = HISTORY_NETVALUE_PATH + 'hushen300_tsdata.json'
        with open(shanghaiRoot, 'r') as f:

            load_json = json.load(f)
            index_data = list(load_json['ts_index'])
            index_date = list(load_json['ts_date'])

            now_date = datetime.strftime(datetime.now(),"%Y-%m-%d")

            if now_date in index_date:
                print('今日上证指数已经更新。')
            else:
                import requests
                # 从新浪拿到今日收盘价
                data = requests.get('http://hq.sinajs.cn/list=s_sh000300')
                today_index = data.text.split(',')[1]

                index_data.append(float(today_index))
                index_date.append(now_date)

                new_json = dict(ts_index=index_data, ts_date=index_date)

                with open(shanghaiRoot, 'w') as f:
                    json.dump(new_json, f)
                    print("今天上证指数已更新（第一次）。")

    register_events(scheduler5)
    scheduler5.start()
except Exception as e:
    print(e)

#=================================================================================#
# """收盘产品清算"""
# try:
#     scheduler3 = BackgroundScheduler()
#     scheduler3.add_jobstore(DjangoJobStore(), "default")
#
#     @register_job(scheduler3, 'cron', day_of_week='mon-fri', hour='15', minute='59', second='10', id='productClear')
#     def productClear():
#
#         jsonFileRoot = MANAGEMENT_PATH + "strategy_pnl_total.json"
#         product_account_path = MANAGEMENT_PATH + "0product_account_manage.json"
#         from datetime import datetime
#         today = datetime.now().strftime("%Y-%m-%d")
#
#         with open(jsonFileRoot, 'r') as f:
#             SM_TABLE_json = json.load(f)
#             SM_TABLE_ALL = pd.DataFrame(SM_TABLE_json)
#             SM_TABLE_ALL["PNL"] = SM_TABLE_ALL['PNL'].apply(pd.to_numeric)
#             SM_TABLE_ALL["market_value"] = SM_TABLE_ALL['market_value'].apply(pd.to_numeric)
#
#             SM_TABLE_today = SM_TABLE_ALL[SM_TABLE_ALL['trade_date'] == today]
#
#         with open(product_account_path, 'r') as f:
#             PAM_TABLE_json = json.load(f)
#
#         product_account_dict = {}
#         """存储产品账号匹配关系表"""
#         for product_account_each in PAM_TABLE_json:
#             if product_account_each['product_name'] in product_account_dict.keys():
#                 product_account_dict[product_account_each['product_name']].append(product_account_each['account_number'])
#             else:
#                 product_account_dict[product_account_each['product_name']] = []
#                 product_account_dict[product_account_each['product_name']].append(product_account_each['account_number'])
#
#         """拿到每个账号的PNL和持仓市值"""
#         account_sum_pnls = dict(SM_TABLE_today.groupby(by=["account_number"])["PNL"].sum())
#         account_sum_mvs = dict(SM_TABLE_today.groupby(by=["account_number"])["market_value"].sum())
#
#         # print("\n产品对应的账号：\n", product_account_dict)
#         # print("\n账号对应的PNL：\n", account_sum_pnls)
#
#         for pro in product_account_dict.keys():
#             # 产品的两个基本文件tsdata,nv_detai路径
#             pro_pnl = 0
#             pro_market_value = 0
#             for account in product_account_dict[pro]:
#                 if account in account_sum_pnls.keys():
#                     pro_pnl += account_sum_pnls[account]
#                     pro_market_value += account_sum_mvs[account]
#                 else:
#                     print("账号{}属于产品{}，但是在策略管理表格中未查到。".format(account, pro))
#
#             product_ts_Root = HISTORY_NETVALUE_PATH + pro + "_tsdata.json"
#             product_NVTS_Root = HISTORY_NETVALUE_PATH + pro + "_nv_detail.json"
#
#             try:
#                 with open(product_ts_Root, 'r') as f:
#                     load_json = json.load(f)
#                     ts_capital = list(load_json['ts_capital'])
#                     ts_data = list(load_json['ts_data'])
#                     ts_date = list(load_json['ts_date'])
#                     amount = load_json["amount"]
#
#                     CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
#                     if CURRENT_DATE in ts_date:
#
#                         ts_capital[-1] = ts_capital[-2] + round(pro_pnl, 3)
#                         ts_data[-1] = ts_capital[-1] / amount
#                         ts_date[-1] = ts_date[-1]
#
#                         print("{}已清算，重新刷新".format(pro))
#                     else:
#                         ts_capital.append(ts_capital[-1] + round(pro_pnl, 3))
#                         ts_data.append(ts_capital[-1] / amount)
#                         ts_date.append(CURRENT_DATE)
#
#                         print("{}今日首次清算".format(pro))
#
#                     new_json = dict(ts_capital=ts_capital, ts_data=ts_data, ts_date=ts_date,amount=amount)
#
#                     with open(product_ts_Root, 'w') as f:
#                         json.dump(new_json, f)
#
#                 with open(product_NVTS_Root, 'r') as f:
#                     load_json = json.load(f)
#                     first_date = list(load_json)[0]['trade_date']
#
#                     CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
#                     if CURRENT_DATE == first_date:
#                         load_json[0] = dict(PNL=round(pro_pnl,3), trade_date=CURRENT_DATE, net_value=round(ts_data[-1], 6), capital=round(ts_capital[-1], 3), market_value=round(pro_market_value,3))
#                     else:
#
#                         new_json = dict(PNL=round(pro_pnl,3), trade_date=CURRENT_DATE, market_value=round(pro_market_value,3), net_value=round(ts_data[-1], 6), capital=round(ts_capital[-1], 3))
#                         load_json.insert(0, new_json)
#
#                     with open(product_NVTS_Root, 'w') as f:
#                         json.dump(load_json, f)
#             except:
#                 print("Warning:: ({})可能未在HISTORY_NETVALUE_PATH中添加产品文件。".format(pro))
#
#         print("今日产品净值清算结束。")
#
#     register_events(scheduler3)
#     scheduler3.start()
# except Exception as e:
#     print(e)
#
# #=================================================================================#
#
# """收盘策略清算"""
# try:
#     scheduler4 = BackgroundScheduler()
#     scheduler4.add_jobstore(DjangoJobStore(), "default")
#
#     @register_job(scheduler4, 'cron', day_of_week='mon-fri', hour='15', minute='59', second='20', id='strategyClear')
#     def strategyNetValueClear():
#
#         jsonFileRoot = MANAGEMENT_PATH + "strategy_pnl_total.json"
#         from datetime import datetime
#         today = datetime.now().strftime("%Y-%m-%d")
#
#         with open(jsonFileRoot, 'r') as f:
#             SM_TABLE_json = json.load(f)
#
#         for str in SM_TABLE_json:
#
#             str_date = str["trade_date"]
#             str_ts_Root = HISTORY_NETVALUE_PATH + str["strategy_name"] + "_tsdata.json"
#             str_NVTS_Root = HISTORY_NETVALUE_PATH + str["strategy_name"] + "_nv_detail.json"
#             str_pnl = float(str["PNL"])
#             str_market_value = float(str["market_value"])
#
#             if str_date == today and str_pnl != 0:
#                 # 暂定今日盈亏为0的是未启动策略，不参与净值结算
#                 try:
#                     with open(str_ts_Root, 'r') as f:
#                         load_json = json.load(f)
#                         ts_capital = list(load_json['ts_capital'])
#                         ts_data = list(load_json['ts_data'])
#                         ts_date = list(load_json['ts_date'])
#                         amount = load_json["amount"]
#
#                         CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
#                         if CURRENT_DATE in ts_date:
#                             ts_capital[-1] = ts_capital[-2] + round(str_pnl, 3)
#                             ts_data[-1] = ts_capital[-1] /amount
#                             ts_date[-1] = ts_date[-1]
#
#                             print('{}策略净值已清算，重新刷新'.format(str["strategy_name"]))
#
#                         else:
#                             ts_capital.append(ts_capital[-1] + round(str_pnl, 3))
#                             ts_data.append(ts_capital[-1] / amount)
#                             ts_date.append(CURRENT_DATE)
#
#                             print('{}策略净值首次清算'.format(str["strategy_name"]))
#
#                         new_json = dict(ts_capital=ts_capital, ts_data=ts_data, ts_date=ts_date,amount=amount)
#
#                         with open(str_ts_Root, 'w') as f:
#                             json.dump(new_json, f)
#
#                     with open(str_NVTS_Root, 'r') as f:
#                         load_json = json.load(f)
#                         first_date = list(load_json)[0]['trade_date']
#
#                         CURRENT_DATE = (datetime.now()).strftime("%Y-%m-%d")
#                         if CURRENT_DATE == first_date:
#                             load_json[0] = dict(PNL=str_pnl, trade_date=CURRENT_DATE, net_value=round(ts_data[-1], 6), capital=round(ts_capital[-1], 3),market_value=str_market_value)
#                         else:
#                             new_json = dict(PNL=str_pnl, trade_date=CURRENT_DATE, net_value=round(ts_data[-1], 6), capital=round(ts_capital[-1], 3),market_value=str_market_value)
#                             load_json.insert(0, new_json)
#
#                         with open(str_NVTS_Root, 'w') as f:
#                             json.dump(load_json, f)
#                 except:
#                     print("Not well!!")
#             else:
#                 pass
#
#         print("今日策略净值清算结束。")
#
#     register_events(scheduler4)
#     scheduler4.start()
# except Exception as e:
#     print(e)


#=================================================================================#
"""收盘更新创业板指数"""
try:
    scheduler6 = BackgroundScheduler()
    scheduler6.add_jobstore(DjangoJobStore(), "default")

    @register_job(scheduler6, 'cron', day_of_week='mon-fri', hour='15', minute='1', second='15', id='getCYBIndex')
    def getCYBIndex():

        """更新上证指数"""
        cybRoot = HISTORY_NETVALUE_PATH + 'cyb_tsdata.json'
        with open(cybRoot, 'r') as f:

            load_json = json.load(f)
            index_data = list(load_json['ts_index'])
            index_date = list(load_json['ts_date'])

            now_date = datetime.strftime(datetime.now(),"%Y-%m-%d")

            if now_date in index_date:
                print('今日上证指数已经更新。')
            else:
                import requests
                # 从新浪拿到今日收盘价
                data = requests.get('http://hq.sinajs.cn/list=s_sz399006')
                today_index = data.text.split(',')[1]

                index_data.append(float(today_index))
                index_date.append(now_date)

                new_json = dict(ts_index=index_data, ts_date=index_date)

                with open(cybRoot, 'w') as f:
                    json.dump(new_json, f)
                    print("今天上证指数已更新（第一次）。")

    register_events(scheduler6)
    scheduler6.start()
except Exception as e:
    print(e)