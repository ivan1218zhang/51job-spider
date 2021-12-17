import time

import requests


# 流冠
def LiuGuan():
    time.sleep(10)
    ips = requests.get(
        "购买代理ip 获得到的接口 用文本形式返回 ip之间用换行连接").text.strip().split("\n")
    return ips
