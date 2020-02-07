import requests
import sys

def deleteServerJson(strategy_name,field):

    deleteInfo = dict(strategy_name=strategy_name,field=field)
    res = requests.post('http://47.100.210.243:50100/deletejson/', data=deleteInfo)
    print(res.text)


if __name__ == "__main__":

    # 示例：若要删除服务器文件，只需传入要删除的策略及其对应的json文件field包括order，ts_data,positions,nv_detail
    """目前只支持order文件的一键删除"""

    group = {
        "debt_simulate": ["D_simulate", 'lpp_simulate', 'tft_simulate', 'ihif_simulate'],
        "debt_real": ['D_30200141831', 'D_880004110681'],
        "zhang_simulate": ['SLD_simulate', 'N1_simulate', 'N2_simulate', 'N3A_simulate', 'N3B_simulate', 'N3C_simulate',
                           'N4_simulate', 'N5_simulate', 'N6_simulate', 'N7_simulate'],
        "zhang_real": ['SLD_30200141831', 'SLD_8009191223', 'N1_8009191223', 'N2_8009191223', 'N3A_8009191223',
                       'N3B_8009191223', 'N3C_8009191223', 'N4_8009191223', 'N5_8009191223', 'N6_8009191223',
                       'N7_8009191223']
    }
    if sys.argv[1] == 'all':
        for strategy_group in group.keys():
            for strategy in group[strategy_group]:
                deleteServerJson(strategy, "order")
    else:
        deleteServerJson(sys.argv[1], "order")



