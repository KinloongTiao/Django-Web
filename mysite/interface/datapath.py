
"""数据路径统一管理"""

from mysite.settings import ROOT_PATH

HTML_INTEMPLATE_PATH = ROOT_PATH  + 'interface/templates/interface/'
# HTML模板路径
TABLE_DATA_PATH =ROOT_PATH  +  'static/tableData/TempData/'
# json数据路径
CMMODITY_PRICE_PATH =ROOT_PATH  +  'static/tableData/CommodityPriceData/'
# 现货数据路径
MANAGEMENT_PATH =ROOT_PATH  +  'static/tableData/Manage/'
# Django账号，策略管理路径
HISTORY_NETVALUE_PATH = ROOT_PATH  +  'static/tableData/HistoryNetValue/'
# 备份文件路径
BACKUP_DATA_PATH = ROOT_PATH + 'static/BackUpData/'
# 所有策略配置表的路径
ALL_STRATEGY_PNL_PATH = ROOT_PATH + 'static/tableData/all_strategy_pnl.json'

