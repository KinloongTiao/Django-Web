
import re
import os
import sys
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime,timedelta
import configparser

import warnings
warnings.filterwarnings("ignore")

ROOT_PATH = "./"
# 设置配置文件的路径
config_path = ROOT_PATH + "config_path.csv"
config_path = pd.read_csv(config_path)


# 创建配置文件对象
con = configparser.ConfigParser()
con.read('config.ini', encoding='utf-8')
# 获取所有section
sections = con.sections()

# 获取特定section
items = con.items('SERVER') 	# 返回结果为元组
items = dict(items)
print(items)

IP_ADDRESS = items["ip_address"]
Port = items["port"]

START_REAL_POST = True
# RESEND_MODE = True


def loadOrderData(str_name,root_path,date):
    str_name = str(str_name)
    data_root = root_path + '/' + date
    # date = datetime.now().strftime("%Y%m%d")
    trade_date = date
    order_root = data_root + '/' + trade_date + '_order.csv'
    if not os.path.exists(order_root):
        order_data = pd.DataFrame(columns=['order_time','trading_date','account_id','strategy_name','instrument_id','strategy_order_id',
                                           'system_order_id','entrust_no','open_close','long_short','entrust_amount','entrust_price',
                                           'business_amount','business_price','entrust_status'])
        print("  无订单信息！ ".format(str_name))
    else:
        try:
            order_data = pd.read_csv(data_root + '/' + trade_date + '_order.csv', encoding='gbk')
            order_data = order_data.fillna(" ")
            # print("  请查看order文件，数据存在缺失，可能会影响Django的展示。")
        except:
            order_data = pd.DataFrame(columns=['order_time','trading_date','account_id','strategy_name','instrument_id','strategy_order_id',
                                           'system_order_id','entrust_no','open_close','long_short','entrust_amount','entrust_price',
                                           'business_amount','business_price','entrust_status'])
            print("  订单信息为空（无表头）")

    return order_data

def loadYestPostionData(str_name, root_path, date):

    # 仅加载数据，不进行格式清理，适用于Sender5.0
    data_root = root_path + '/' + date
    # date = datetime.now().strftime("%Y%m%d")
    trade_date = date

    position_root = data_root + '/yesterday_position.csv'

    """读取昨持仓文件"""
    if not os.path.exists(position_root):
        position_data = pd.DataFrame(columns=['trading_date', 'strategy_name', 'account_id', 'stock_code', 'long_short',
                                              'volume_multiplier', 'amount', 'cost_price', 'preclose','adjust_factor'])
    else:
        try:
            position_data = pd.read_csv(data_root + '/yesterday_position.csv')

            if "volume_multiplier" not in position_data.columns:
                position_data["volume_multiplier"] = 1
                print("  {}昨持仓文件没有乘数列，按默认为1处理。".format(str_name))

            if "long_short" not in position_data.columns:
                print("  文件中没有long_short列，已默认填充为0（多头仓位）")
                position_data["long_short"] = 0

            position_data["long_short"] = position_data["long_short"].fillna(0)
            # 如果没有多空方向就默认填充多仓

            for i in position_data.index:
                # 空仓仓位为正数，改成负数，方便调用之前写过的函数计算pnl
                position_data.loc[i, "amount"] = (position_data.loc[i, "amount"] * (-1)) if position_data.loc[i, "long_short"] == 1 else \
                    position_data.loc[i, "amount"]
        except:
            position_data = pd.DataFrame(
                columns=['trading_date', 'strategy_name', 'account_id', 'stock_code', 'long_short',
                         'volume_multiplier', 'amount', 'cost_price', 'preclose']
            )
            print("  {}昨持仓为空".format(str_name))


    return position_data

def loadData_initial(str_name, root_path, date):

    # 仅加载数据，不进行格式清理，适用于Sender5.0
    data_root = root_path + '/' + date
    # date = datetime.now().strftime("%Y%m%d")
    trade_date = date

    last_price_root = data_root + '/last_price.csv'
    position_root = data_root + '/yesterday_position.csv'
    trade_root = data_root + '/' + trade_date + '_trade.csv'

    # print(os.path.exists(trade_root),trade_root)  # 调试判断是否有交易流水文件

    trade_columns_default = ["证券代码", "买卖数量", "乘数", "买卖日期", "买卖价格", "证券类型", "买卖方向", "开平方向", "策略名"]
    last_price_columns_default = ["stock_code", "lastprice", "signal"]


    """读取交易流水"""
    if not os.path.exists(trade_root):
        trade_data = pd.DataFrame(columns=trade_columns_default)
        print("  {}无交易流水！".format(str_name))
    else:
        try:
            trade_data = pd.read_csv(data_root + '/' + trade_date + '_trade.csv', encoding='gbk')

            # 如果数据中没有开平方向这一列，就自动按照买卖方向添加
            important_columns = ["证券代码", "买卖数量", "乘数", "买卖价格", "买卖方向", "开平方向"]
            for col in important_columns:
                if col not in trade_data.columns:
                    print("  交易表头缺少{}列".format(col))

        except:
            trade_data = pd.DataFrame(columns=trade_columns_default)
            print("  {}交易流水表头信息有误，请核查! ".format(str_name))


    """读取最新价文件"""
    if not os.path.exists(last_price_root):
        last_price_data = pd.DataFrame(columns=last_price_columns_default)
    else:
        try:
            last_price_data = pd.read_csv(data_root + '/last_price.csv')
            for col in last_price_columns_default:
                if col not in last_price_data.columns:
                    print("  最新价表头缺少{}列".format(col))
        except:
            last_price_data = pd.DataFrame(columns=last_price_columns_default)
            print("  {}最新价表头信息有误，请核查!".format(str_name))


    """读取昨持仓文件"""
    if not os.path.exists(position_root):
        position_data = pd.DataFrame(columns=['trading_date', 'strategy_name', 'account_id', 'stock_code', 'long_short',
                                              'volume_multiplier', 'amount', 'cost_price', 'preclose','adjust_factor'])
    else:
        try:
            position_data = pd.read_csv(data_root + '/yesterday_position.csv')

            if "volume_multiplier" not in position_data.columns:
                position_data["volume_multiplier"] = 1
                print("  {}昨持仓文件没有乘数列，按默认为1处理。".format(str_name))

            if "long_short" not in position_data.columns:
                print("  文件中没有long_short列，已默认填充为0（多头仓位）")
                position_data["long_short"] = 0

            position_data["long_short"] = position_data["long_short"].fillna(0)
            # 如果没有多空方向就默认填充多仓

            for i in position_data.index:
                # 空仓仓位为正数，改成负数，方便调用之前写过的函数计算pnl
                position_data.loc[i, "amount"] = (position_data.loc[i, "amount"] * (-1)) if position_data.loc[i, "long_short"] == 1 else \
                    position_data.loc[i, "amount"]
        except:
            position_data = pd.DataFrame(
                columns=['trading_date', 'strategy_name', 'account_id', 'stock_code', 'long_short',
                         'volume_multiplier', 'amount', 'cost_price', 'preclose']
            )
            print("  {}昨持仓为空".format(str_name))


    return last_price_data, position_data, trade_data

def getTradeFeeIndex(instrument_id):

    """
    :param instrument_id: 输入证券代码
    :return: 输出该证券代码对应instrument_fee文件中的字段名，从而获取到对应的各种手续费率
    """

    if not bool(re.search('[a-z]+|[A-Z]', (instrument_id.split('.')[0]))):
        # 如果证券代码里面不包含字母，则为股票、可转债或者期权品种

        first2_letter = str(instrument_id)[0:2]
        if first2_letter == '00' or first2_letter == '30':
            InstrumentID = 'SZSTOCK'
        elif first2_letter == '60' or first2_letter == '68':
            InstrumentID = 'SHSTOCK'
        elif first2_letter == '11' or first2_letter == '13':
            InstrumentID = 'SHDEBT'
        elif first2_letter == '12':
            InstrumentID = 'SZDEBT'
        elif first2_letter == '10':
            InstrumentID = 'SHOPTION'
        else:
            print("  ---ERROR!!  NO FOUND INSTRUMENT ID: ",instrument_id)
            InstrumentID = 'SHSTOCK'

    else:
        # 切分英文字母与数字，第一个英文字母即为
        InstrumentID = re.findall(r'[0-9]+|[a-z]+|[A-Z]+', instrument_id)[0]

    return InstrumentID

def deleteServerJson(strategy_name,field):

    if START_REAL_POST:
        deleteInfo = dict(strategy_name=strategy_name,field=field)
        try:
            res = requests.post('http://'+IP_ADDRESS+':'+Port+'/deletejson/',timeout=2, data=deleteInfo)
            print(res.text)
        except:
            print("删除失败")

def computeAndPOST(trade_date,current_order_index_dict,current_trade_index_dict,current_position):

    flag = False
    # print(current_trade_index_dict)

    print("1.发送持仓")

    post_date = datetime.strptime(trade_date, "%Y%m%d").strftime("%Y-%m-%d")

    for i in config_path.index:

        str_name, str_path = config_path.loc[i, ['strategy_name', 'strategy_path']]
        # print("------------{}--{}------------".format(str_name,'positions running'))

        last_price_data, yesterday_position, trade_data = loadData_initial(str_name,root_path=str_path, date=trade_date)

        # 如果没有最新价文件，则全部无法计算，跳过该策略
        if last_price_data.empty:
            # str_dict = {'strategy_name': str_name, 'trade_date': post_date, 'PNL': "0"}
            # pnl_list.append(str(str_dict))
            print("  {}未启动或未发生交易，{}文件有问题。".format(str_name, "last_price"))
            continue
        else:
            flag = True

        yesterday_position["stock_code"] = yesterday_position["stock_code"].apply(str)
        last_price_data["stock_code"] = last_price_data["stock_code"].apply(str)
        positions = pd.merge(yesterday_position, last_price_data, on=['stock_code'], how='left')


        """停牌情况处理"""
        for index in positions.index:
            if positions.loc[index, "lastprice"] > 0:
                continue
            else:
                lpd_index = len(last_price_data)
                last_price_data.loc[lpd_index] = [positions.loc[index,'stock_code'],positions.loc[index,'preclose'],0]
                # 如果last_price文件中没有某只股票的最新价，说明这只股票今日停牌了，在最新价文件中添加一行
                print("  {}停牌，PNL计算最新价用昨收代替。 ".format(positions.loc[index, "stock_code"]))


        end_length = len(trade_data)
        start_length = current_trade_index_dict[str_name] if str_name in current_trade_index_dict.keys() else 0


        new_trade_data = trade_data[start_length:]
        if "开平方向" not in new_trade_data.columns:
            for i in new_trade_data.index:
                new_trade_data.loc[i, "开平方向"] = "平仓" if new_trade_data.loc[i, "买卖方向"] == "卖出" else "开仓"

        for i in new_trade_data.index:
            # 对初始交易流水进行交易分类，确定交易仓位所属
            new_trade_data.loc[i, 'class'] = 0 if (
                    ((new_trade_data.loc[i, "开平方向"] == "平仓") & (new_trade_data.loc[i, "买卖方向"] == "卖出")) |
                    ((new_trade_data.loc[i, "开平方向"] == "开仓") & (new_trade_data.loc[i, "买卖方向"] == "买入"))) else 1

        current_trade_index_dict[str_name] = end_length
        # 刷新目前读取到的订单数据长度


        columns_trade = list(new_trade_data.columns)
        new_trades = [list(xi) for xi in new_trade_data.values]

        """维护持仓字典的字段顺序样例
        0: 证券代码    
        1: 证券名称    
        2: Signal    
        3: 方向    
        4: 持仓市值    
        5: 当前持仓    
        6: 昨持仓    
        7: 成本价    
        8: 最新价    
        9: 盈亏比率    
        10: 今日PNL    
        11: 累计PNL
        12: 昨日累计盈亏（用于计算今日盈亏=累计盈亏-昨日累计盈亏）    
        13: 乘数（方便后面刷新盈亏计算及最新价状态等）   
        14. 本次清仓实现盈亏

        -->>其中,方向0代表多头仓位,1表示空头仓位;昨持仓表示当前持仓中有多少份额是昨天的持仓;盈亏比率表示相对于当前持仓的保本价盈亏比率;<--
        举例:字典键值由证券ID与仓位头寸方向决定,需判断交易流水属于的仓位方向(期货多空仓位)

        current_trade_index_dict = {
        'D_30200141831':{"127009.SZ-0":["127009.SZ","东音股份",0.02,0,52161.75,2425,0,21.33,21.51,0.0083,429.225,429.225]},
        'HEDGE_simulate':{"000408.SZ-0":["000408.SZ","藏格控股",0,0,0,0,0,0,9.46,0,-1610,4830],
                                         "600657.SH-0":["600657.SH","信达地产",0,0,67980,16500,0,4.1,4.12,0.00488,330,330]
                                         }}
        """
        # total_fee = []

        """对新交易流水进行逐一计算"""
        for new_trade in new_trades:
            new_trade = dict(zip(columns_trade,new_trade))
            # 如果数据中没有开平方向这一列，就自动按照买卖方向添加
            curr_pos_key_name = new_trade["证券代码"] + '-' + str(int(new_trade["class"]))

            # 计算该笔交易的手续费，后面累计盈亏会减去手续费【编号11】
            instrument_id = getTradeFeeIndex(new_trade["证券代码"])
            trade_money = new_trade["买卖数量"] * new_trade["买卖价格"] * new_trade["乘数"]
            business_amount = new_trade["买卖数量"]

            fee = 0
            fee += trade_money * (fee_map[instrument_id]["OpenRatioByMoney"] if new_trade["开平方向"] == "开仓" else fee_map[instrument_id]["CloseRatioByMoney"])
            fee += business_amount * (fee_map[instrument_id]["OpenRatioByVolume"] if new_trade["开平方向"] == "开仓" else fee_map[instrument_id]["CloseRatioByVolume"])
            # total_fee.append(fee)

            if curr_pos_key_name in current_position[str_name].keys():

                if new_trade['买卖方向'] == "买入":

                    if new_trade["class"] == 0:
                        # 多头仓位，买入不会影响昨持仓，卖出才会降低昨持仓
                        current_position[str_name][curr_pos_key_name][6] = current_position[str_name][curr_pos_key_name][6]
                    else:
                        current_position[str_name][curr_pos_key_name][6] = current_position[str_name][curr_pos_key_name][6] - new_trade['买卖数量']

                    if current_position[str_name][curr_pos_key_name][5] + new_trade['买卖数量'] == 0:
                        """如果当前持仓为0，说明已经清仓，需要清算累计PNL以及今日PNL，后面会判断是否有仓位，若没有仓位则不计算pnlRate
                        累计盈亏 = （新交易订单成交价格 - 交易前持仓成本价）* 交易前持仓量 * 乘数
                        """
                        current_position[str_name][curr_pos_key_name][11] = current_position[str_name][curr_pos_key_name][5] * new_trade['乘数'] \
                                                                            * (new_trade['买卖价格']-current_position[str_name][curr_pos_key_name][7]) \
                                                                            + current_position[str_name][curr_pos_key_name][14] - fee

                        current_position[str_name][curr_pos_key_name][10] = current_position[str_name][curr_pos_key_name][11] - current_position[str_name][curr_pos_key_name][12]
                        current_position[str_name][curr_pos_key_name][4] = 0
                        current_position[str_name][curr_pos_key_name][9] = '0.0%'

                        # 如果该笔交易之后当前持仓为0的话，就没必要继续算成本价或者当前持仓了，直接赋值为0即可
                        current_position[str_name][curr_pos_key_name][5], current_position[str_name][curr_pos_key_name][7] = 0, 0
                        current_position[str_name][curr_pos_key_name][14] = current_position[str_name][curr_pos_key_name][11]
                        # 对于清仓的标的，记录下来本次清仓已实现盈亏，用来计算后续的累计盈亏

                    else:
                        # 如果仍有持仓，则计算最新成本价及当前持仓
                        """ 手续费对持仓成本价的影响如下：
                            若是多头仓位，不管是开仓还是平仓，都是抬高成本价；
                            若是空头仓位，不管是开仓还是平仓，都是降低成本价；
                        """

                        current_position[str_name][curr_pos_key_name][7] = (current_position[str_name][curr_pos_key_name][5] * current_position[str_name][curr_pos_key_name][7]
                                                                            + new_trade['买卖价格'] * new_trade['买卖数量'] + fee/new_trade["乘数"] * (1 if new_trade["class"] == 0 else -1)) \
                                                                           / (current_position[str_name][curr_pos_key_name][5] + new_trade['买卖数量'])

                        current_position[str_name][curr_pos_key_name][5] = current_position[str_name][curr_pos_key_name][5] + new_trade['买卖数量']
                        current_position[str_name][curr_pos_key_name][11] = current_position[str_name][curr_pos_key_name][11] -fee

                if new_trade['买卖方向'] == "卖出":

                    if new_trade["class"] == 0:
                        current_position[str_name][curr_pos_key_name][6] = current_position[str_name][curr_pos_key_name][6] - new_trade['买卖数量']
                    else:
                        current_position[str_name][curr_pos_key_name][6] = current_position[str_name][curr_pos_key_name][6]

                    if current_position[str_name][curr_pos_key_name][5] - new_trade['买卖数量'] == 0:
                        current_position[str_name][curr_pos_key_name][11] = current_position[str_name][curr_pos_key_name][5] * new_trade['乘数'] * \
                                                                            (new_trade['买卖价格']-current_position[str_name][curr_pos_key_name][7]) \
                                                                            + current_position[str_name][curr_pos_key_name][14] - fee
                        current_position[str_name][curr_pos_key_name][10] = current_position[str_name][curr_pos_key_name][11] - current_position[str_name][curr_pos_key_name][12]
                        current_position[str_name][curr_pos_key_name][4] = 0
                        current_position[str_name][curr_pos_key_name][9] = '0.0%'

                        current_position[str_name][curr_pos_key_name][5], current_position[str_name][curr_pos_key_name][7] = 0, 0
                        current_position[str_name][curr_pos_key_name][14] = current_position[str_name][curr_pos_key_name][11]


                    else:
                        current_position[str_name][curr_pos_key_name][7] = (current_position[str_name][curr_pos_key_name][5] * current_position[str_name][curr_pos_key_name][7] - new_trade['买卖价格'] * new_trade[
                            '买卖数量'] - fee/new_trade["乘数"] * (-1 if new_trade["class"] == 0 else 1)) / (current_position[str_name][curr_pos_key_name][5] - new_trade['买卖数量'])
                        current_position[str_name][curr_pos_key_name][5] = current_position[str_name][curr_pos_key_name][5] - new_trade['买卖数量']
                        current_position[str_name][curr_pos_key_name][11] = current_position[str_name][curr_pos_key_name][11] - fee

                current_position[str_name][curr_pos_key_name][6] = 0 if current_position[str_name][curr_pos_key_name][6] <= 0 else current_position[str_name][curr_pos_key_name][6]
                # 昨持仓 <= 0, 则说明当前仓位已经不包含昨天持仓了，清零

            else:
                """如果current_position本来没有当前这个头寸的键值，则需要新生成一条记录"""
                current_position[str_name][curr_pos_key_name] = [new_trade['证券代码'],
                                                                 stock_dict[new_trade['证券代码']] if new_trade['证券代码'] in stock_dict.keys() else '  ',
                                                                 0,
                                                                 new_trade["class"],
                                                                 new_trade['买卖数量'] * new_trade['买卖价格'] * new_trade['乘数'] * (1 if new_trade['class'] == 0 else -1),
                                                                 new_trade['买卖数量'] * (1 if new_trade['class'] == 0 else -1),
                                                                 0,
                                                                 new_trade['买卖价格']+fee/new_trade["买卖数量"] * (1 if new_trade["class"] == 0 else -1),
                                                                 new_trade['买卖价格'],
                                                                 "0.0%",
                                                                 0,
                                                                 0-fee,
                                                                 0,
                                                                 new_trade["乘数"],
                                                                 0
                                                                 ]



        # print("总手续费：",total_fee,sum(total_fee))

        """遍历current_position所有头寸仓位，刷新最新价，累计盈亏，持仓盈亏及盈亏比率"""
        for each_pos_key in current_position[str_name].keys():

            each_stock_code = each_pos_key.split('-')[0]
            curr_pos_key_name = each_pos_key

            try:
                new_trade_last_price = last_price_data.loc[last_price_data['stock_code'] == each_stock_code]['lastprice'].values[0]
            except:
                new_trade_last_price = 0
                print("ERROR::{}没有last_price,为了不影响Sender正常运行，用0代替，请修改后重启Sender.".format(each_stock_code))

            # print('{}最新价{}'.format(each_stock_code,new_trade_last_price))
            new_trade_signal = last_price_data.loc[last_price_data['stock_code'] == each_stock_code]['signal'].values[0]
            current_position[str_name][curr_pos_key_name][8] = new_trade_last_price
            current_position[str_name][curr_pos_key_name][2] = new_trade_signal
            # 更新最新价与Signal,用于后续PNL的计算

            if current_position[str_name][curr_pos_key_name][5] != 0:
                # 当前持仓不为0时，通过计算新交易对成本价造成的改变计算今日PNL与累计PNL

                before_acum_pnl = current_position[str_name][curr_pos_key_name][11]
                after_accum_pnl = (current_position[str_name][curr_pos_key_name][8] -
                                   current_position[str_name][curr_pos_key_name][7]) * \
                                  current_position[str_name][curr_pos_key_name][5] * current_position[str_name][curr_pos_key_name][13] \
                                  + current_position[str_name][curr_pos_key_name][14]
                # 累计盈亏计算需要单独加上清仓已实现的盈亏
                current_position[str_name][curr_pos_key_name][11] = after_accum_pnl
                current_position[str_name][curr_pos_key_name][10] = after_accum_pnl - \
                                                                    current_position[str_name][curr_pos_key_name][12]
                current_position[str_name][curr_pos_key_name][4] = current_position[str_name][curr_pos_key_name][5] * \
                                                                   current_position[str_name][curr_pos_key_name][13] * \
                                                                   current_position[str_name][curr_pos_key_name][8]

                current_position[str_name][curr_pos_key_name][9] = "%.3f%%" %  (100 * (current_position[str_name][curr_pos_key_name][11] /
                                                                               np.abs(current_position[str_name][curr_pos_key_name][4]))) \
                                                                            if np.abs(current_position[str_name][curr_pos_key_name][5]) != 0 else '0.0%'

        # print(current_position)
        # print("最终持仓===============\n")

    for strategy_name in current_position.keys():

        postPositionList = []

        for position_key in current_position[strategy_name].keys():
            pos_keys = ['stock_code','stock_name','signal','long_short','market_value','current_amount','yesterday_amount','cost_price','last_price','pnl_rate','pnl','AccumPNL','YestPnl','Multiplier']

            # 保留三位小数
            current_position[strategy_name][position_key][2] = round(current_position[strategy_name][position_key][2],3)
            current_position[strategy_name][position_key][4] = round(current_position[strategy_name][position_key][4],3)
            current_position[strategy_name][position_key][7] = round(current_position[strategy_name][position_key][7],3)
            current_position[strategy_name][position_key][10] = round(current_position[strategy_name][position_key][10],3)
            current_position[strategy_name][position_key][11] = round(current_position[strategy_name][position_key][11],3)

            each_position_dict = dict(zip(pos_keys,current_position[strategy_name][position_key]))
            each_position_str = str(dict(trade_data=post_date,**each_position_dict))
            postPositionList.append(each_position_str)

        position_data = dict(dict(strategy_name=strategy_name), postList=postPositionList)

        if START_REAL_POST:

            print("  -->{}_postion数量:{}".format(strategy_name, len(postPositionList)))
            try:
                res = requests.post('http://'+IP_ADDRESS+':'+Port+'/postpositiondetail/', timeout=5, data=position_data)
                if res.status_code == 200:
                    print("    <--{}".format(res.text))
            except:
                print("ERROR::post持仓失败，可能是网络不好")

        else:
            print("POST设置：未启动")
            print(position_data)


    print("2.发送PNL")

    pnl_list = []
    for strategy_name in current_position.keys():

        today_pnl = 0
        market_value = 0
        total_accum_profit = 0
        for each_position in current_position[strategy_name].values():
            today_pnl += each_position[10] # 累加所有仓位头寸的今日PNL
            market_value += each_position[4]
            total_accum_profit += each_position[11]

        str_dict = {'strategy_name': strategy_name, 'market_value':market_value,'accum_pnl':round(total_accum_profit,3),
                    'trade_date': post_date, 'PNL': str(round(today_pnl, 3))}
        pnl_list.append(str(str_dict))


    if START_REAL_POST:
        if len(pnl_list) != 0:
            print("  -->{}_pnl_list数量:{}".format(trade_date, len(pnl_list)))
            pnl_data = dict(postList=pnl_list)
            try:
                res = requests.post('http://' + IP_ADDRESS + ':' + Port + '/posttotalpnl/', timeout=5, data=pnl_data)
                if res.status_code == 200:
                    print("    <--{}".format(res.text))
            except:
                print("ERROR::post pnl失败，可能是网络不好")

    else:
        print(pnl_list)


    print("3.发送订单")
    #
    for i in config_path.index:

        str_name, str_path = config_path.loc[i, ['strategy_name', 'strategy_path']]

        all_order_data = loadOrderData(str_name,root_path=str_path, date=trade_date)
        if all_order_data.empty:
            print("  {}未启动或未发生交易，{}文件有问题。".format(str_name, str(trade_date) + "_order"))
            continue

        order_end_length = len(all_order_data)
        order_start_length = current_order_index_dict[str_name] if str_name in current_order_index_dict.keys() else 0
        new_order_data = all_order_data[order_start_length:order_end_length]
        new_order_data = new_order_data.fillna(' ').reset_index()
        current_order_index_dict[str_name] = order_end_length
        # 刷新目前读取到的订单数据长度

        # print("   当前Order订单发送到第{}条".format(order_end_length))

        order_list = []
        columns = list(new_order_data.columns)
        new_orders = [list(xi) for xi in new_order_data.values]

        for order in new_orders:
            if order[5] in stock_dict.keys():
                order_list.append(
                    str(dict(dict(zip(columns, order)), stock_name=stock_dict[order[5]])))
            else:
                order_list.append(str(dict(dict(zip(columns, order)), stock_name=' ')))
                # print("未查询到证券代码{}，请添加。".format(order[4]))

        order_data = dict(postList=order_list)
        print('  -->{}_order数量:{}'.format(str_name, len(order_list)))

        if START_REAL_POST:
            if len(order_list) > 1000:
                print("  订单条数过多，将分批发送")
                order_length = len(order_list)
                slice_list = []
                slice_unit = []
                for i in range(order_length):
                    slice_unit.append(order_list[i])
                    if len(slice_unit) == 1000:
                        slice_list.append(slice_unit)
                        slice_unit = []
                    if i == order_length-1:
                        slice_list.append(slice_unit)
                        slice_unit = []

                for slice_part in slice_list:
                    order_slice = dict(postList=slice_part)
                    print('  -->{}_order_slice数量:{}'.format(str_name, len(slice_part)))
                    try:
                        res = requests.post('http://'+IP_ADDRESS+':'+Port+'/postorder/', data=order_slice)
                        if res.status_code == 200:
                            print("    <--{}".format(res.text))
                        else:
                            print("    分组传送订单，Django访问状态仍然未通过。")
                    except:
                        print("ERROR::post order失败，可能是网络不好")

            else:
                print('  -->{}_order_list数量:{}'.format(str_name, len(order_list)))
                try:
                    res = requests.post('http://'+IP_ADDRESS+':'+Port+'/postorder/', data=order_data)
                    if res.status_code == 200:
                        print("    <--{}".format(res.text))
                    else:
                        print("    Django访问状态未通过。")
                except:
                    print("ERROR::post order失败，可能是网络不好")
        else:
            print("POST设置：未启动，无订单发送。")

    return flag

def init_CurrentPosition(current_position,current_date):

    """
    :param current_position: 当前持仓dict;
    :param current_date: 当前交易日期；
    :return: 早盘和夜盘开盘前均会初始化一次，返回最新的当前持仓dict
    """
    global config_path

    """根据昨持仓文件初始化持仓字典"""
    for i in config_path.index:

        str_name, str_path = config_path.loc[i, ['strategy_name', 'strategy_path']]
        yesterday_position_df = loadYestPostionData(str_name, str_path, current_date)

        current_position[str_name] = {}

        for i in yesterday_position_df.index:
            curr_pos_key_name = yesterday_position_df.loc[i, "stock_code"] + '-' + str(yesterday_position_df.loc[i, "long_short"])
            pnlRate = "%.3f%%" % ((((yesterday_position_df.loc[i, "preclose"]  - yesterday_position_df.loc[i, 'cost_price']) / yesterday_position_df.loc[i, 'cost_price']) * 100) *
                                  (1 if yesterday_position_df.loc[i, 'long_short'] == 0 else -1))

            current_position[str_name][curr_pos_key_name] = \
                [yesterday_position_df.loc[i, "stock_code"],
                 stock_dict[yesterday_position_df.loc[i, "stock_code"]] if yesterday_position_df.loc[i, "stock_code"] in stock_dict else '  ',
                 0,
                 yesterday_position_df.loc[i, 'long_short'],
                 yesterday_position_df.loc[i, 'amount'] * yesterday_position_df.loc[i, 'volume_multiplier'] *
                 yesterday_position_df.loc[i, 'preclose'],
                 yesterday_position_df.loc[i, 'amount'],
                 yesterday_position_df.loc[i, 'amount'],
                 yesterday_position_df.loc[i, 'cost_price'],
                 yesterday_position_df.loc[i, 'preclose'],
                 pnlRate,
                 0,
                 (yesterday_position_df.loc[i, 'preclose'] - yesterday_position_df.loc[i, 'cost_price']) *
                 yesterday_position_df.loc[i, 'amount'] * yesterday_position_df.loc[i, 'volume_multiplier'],
                 (yesterday_position_df.loc[i, 'preclose'] - yesterday_position_df.loc[i, 'cost_price']) *
                 yesterday_position_df.loc[i, 'amount'] * yesterday_position_df.loc[i, 'volume_multiplier'],
                 yesterday_position_df.loc[i, 'volume_multiplier'],
                 0
                 ]

            current_position[str_name][curr_pos_key_name][6] = np.abs(current_position[str_name][curr_pos_key_name][6])

    """对Django中对应策略的持仓及订单信息进行清空处理"""
    for i in config_path.index:

        str_name, str_path = config_path.loc[i, ['strategy_name', 'strategy_path']]
        deleteServerJson(str_name, "order")
        deleteServerJson(str_name, "position")

    return current_position

def locateCurrentDate(datetime_now):

    if datetime_now.hour >= 21:
        if datetime_now.weekday() == 4:
            CURRENT_DATE = (datetime_now + timedelta(days=3)).strftime("%Y%m%d")
        elif datetime_now.weekday() < 4:
            CURRENT_DATE = (datetime_now + timedelta(hours=4)).strftime("%Y%m%d")
        else:
            CURRENT_DATE = datetime_now.strftime("%Y%m%d")
    else:
        CURRENT_DATE = datetime_now.strftime("%Y%m%d")

    return CURRENT_DATE

def update():

    current_date = locateCurrentDate(datetime.now())
    current_order_index_dict = dict()
    current_trade_index_dict = dict()
    current_position = {}

    print("-->Sender重启或首次启动<--")
    print("-->初始化Django持仓及订单文件...")
    print("-->今日交易日期： ",current_date)
    time_now = datetime.now()

    if (time_now.hour >= 9) & (time_now.hour == 9 and time_now.minute <= 27):
        current_order_index_dict = dict()
        current_trade_index_dict = dict()
        current_position = {}
        print('-->早盘准备，开盘等待中...')


        time_sleep = (28 - time_now.minute) * 60
        while time_sleep > 0:
            time_sleep -= 2
            time.sleep(2)

        current_position = init_CurrentPosition(current_position, current_date)
        print('-->早盘初始化持仓已完成，实时传送等待中...')
    else:
        current_position = init_CurrentPosition(current_position,current_date)

    """维护持仓字典的字段顺序样例
    0: 证券代码    
    1: 证券名称    
    2: Signal    
    3: 方向    
    4: 持仓市值    
    5: 当前持仓    
    6: 昨持仓    
    7: 成本价    
    8: 最新价    
    9: 盈亏比率    
    10: 今日PNL    
    11: 累计PNL
    12: 昨日累计盈亏（用于计算今日盈亏=累计盈亏-昨日累计盈亏）    
    13: 乘数（方便后面刷新盈亏计算及最新价状态等）   
    14. 清仓实现盈亏

    -->>其中,方向0代表多头仓位,1表示空头仓位;昨持仓表示当前持仓中有多少份额是昨天的持仓;盈亏比率表示相对于当前持仓的保本价盈亏比率;<--
    举例:字典键值由证券ID与仓位头寸方向决定,需判断交易流水属于的仓位方向(期货多空仓位)

    current_trade_index_dict = {
    'D_30200141831':{"127009.SZ-0":["127009.SZ","东音股份",0.02,0,52161.75,2425,0,21.33,21.51,0.0083,429.225,429.225]},
    'HEDGE_simulate':{"000408.SZ-0":["000408.SZ","藏格控股",0,0,0,0,0,0,9.46,0,-1610,4830],
                                     "600657.SH-0":["600657.SH","信达地产",0,0,67980,16500,0,4.1,4.12,0.00488,330,330]
                                     }}
    """

    # time.sleep(5)

    print("  昨持仓初始化完毕：\n",current_position)

    while True:

        print("\n")
        start_time = time.time()
        time_now = datetime.now()
        current_date = locateCurrentDate(time_now)

        print("=="*10+time_now.strftime("%Y%m%d %H:%M:%S")+"=="*10)

        # 非交易日不发送数据
        if time_now.weekday() == 5 or time_now.weekday() == 6:
            time.sleep(1000)
            print('非交易日')
            continue

        # 电脑休息，期间不进行数据传输，一切收盘工作应放在下午四点之前
        if (time_now.hour >= 19 and time_now.hour <= 20) or (time_now.hour >= 3 and time_now.hour <= 8):
            print("Sender rest...")
            time.sleep(60)
            continue


        if (time_now.hour >= 9) & (time_now.hour == 9 and time_now.minute <= 26):

            current_order_index_dict = dict()
            current_trade_index_dict = dict()
            current_position = {}
            print('-->早盘准备，开盘等待中...')


            time_sleep = (28-time_now.minute) * 60
            while time_sleep > 0:
                time_sleep -= 2
                time.sleep(2)


            current_position = init_CurrentPosition(current_position, current_date)
            print('-->早盘初始化持仓已完成，实时传送等待中...')

        if (time_now.hour == 20 and time_now.minute >= 58) & (time_now.hour == 20 and time_now.minute <= 59):
            current_order_index_dict = dict()
            current_trade_index_dict = dict()
            current_position = {}
            current_position = init_CurrentPosition(current_position, current_date)
            print('-->夜盘初始化持仓已完成，实时传送等待中...')
            time.sleep(int(60*(60-time_now.minute)))

        computeAndPOST(current_date, current_order_index_dict, current_trade_index_dict, current_position)

        print("========Next Loop=========")
        end_time = time.time()
        time_consumed = (end_time-start_time)
        print("总耗时：{}".format(time_consumed))

        if RESEND_MODE:
            break

        if time_consumed < 3:
            time.sleep(int(4-time_consumed))


    print("重传结束！！请关闭本窗口。")


if __name__ == "__main__":

    if len(sys.argv)==2:
        RESEND_MODE = int(sys.argv[1])
    else:
        RESEND_MODE = False

    try:
        stock_name = pd.read_csv("stock_name.csv", encoding='gbk')
        instrument_fee_data = pd.read_csv("instrument_fee.csv")
    except:
        stock_name = pd.DataFrame(columns=["stock_code","stock_name"])
        instrument_fee_data = pd.DataFrame(columns=['InstrumentID','ExchangeID','VolumeMultiple','OpenRatioByMoney',
                                                    'OpenRatioByVolume','CloseRatioByMoney','CloseRatioByVolume',
                                                    'CloseTodayRatioByMoney','CloseTodayRatioByVolume'])

        print("请在当前路径下添加stock_name.csv文件")

    stock_dict = stock_name.set_index("stock_code")[["stock_name"]].to_dict()["stock_name"]

    """将手续费率表写入内存中，存为字典格式"""
    fee_map = {}
    for i in instrument_fee_data.index:
        instrumentID_key = instrument_fee_data.loc[i, 'InstrumentID']
        instrumentID_columns = list(instrument_fee_data.columns)
        fee_map[instrumentID_key] = dict(instrument_fee_data.loc[i, instrumentID_columns])

    update()


