from payjs import payjs  # 也可根据个人习惯选择使用 Payjs/PAYJS/payjs
from payjs import PayJSNotify  # 也可根据个人习惯选择使用 PayjsNotify/PAYJSNotify

MCHID = '1525004441'
KEY = 'FEHhbkIGzkqbIdSg'

# 初始化
p = payjs(MCHID, KEY)

# 扫码支付
OUT_TRADE_NO = '2017TEST'  # 外部订单号（自己的支付系统的订单号，请保证唯一）
TOTAL_FEE = 1  # 支付金额，单位为分，金额最低 0.01 元最多 10000 元
BODY = '测试支付'  # 订单标题
# NOTIFY_URL = 'https://pay.singee.site/empty/' # Notify 网址
ATTACH = 'info'  # Notify 内容
