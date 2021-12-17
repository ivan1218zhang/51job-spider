# 最重要的事

> 此程序只作为学习和研究使用，严禁用于商业用途，切勿占用对方服务器过多资源，使用前默认已经读过本文件，若违反相关法律，开发者本人概不负责，如果有相关法律问题，请及时联系我。





# 环境

> Python版本

+ Python 3.6.8

> 用到的库

+ requests
+ lxml





# 程序使用说明



## 相关需要修改的代码或参数说明

> IPPool.py 中需要自己写好获取代理IP的方法，网上购买或者自己的IP池随意，只要是以list形式返回就行，如果是只有一个也要用list。

```python
# 流冠（流冠记得打钱！！）
def LiuGuan():
    time.sleep(10)
    ips = requests.get(
        "购买代理ip 获得到的接口 用文本形式返回 ip之间用换行连接").text.strip().split(
        "\n")
    return ips
```

> 如果需要调整地区或者其它参数，SpiderConfig.py中的START_URL需要相应调整（默认全国）。

```python
START_URL = "https://search.51job.com/list/000000,000000,0000,00,9,99,{},2,{}.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare="
# 第一个空是关键词 第二个空是用来翻页的页数
```

> SpiderConfig.py中TARGET可以修改为自己需要搜索的关键词，作为测试用的是“JAVA工程师”。

```python
TARGET = "JAVA工程师"
```

## 程序入口

> spider.py

