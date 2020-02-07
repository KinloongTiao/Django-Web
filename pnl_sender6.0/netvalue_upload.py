import requests
import configparser
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

def handRefreshNetValue(refresh_or_not):

    post_data = dict(refresh=refresh_or_not)
    res = requests.post('http://'+IP_ADDRESS +':'+Port+'/settle_net_value/', data=post_data)
    print(res.text)

handRefreshNetValue("yes")





