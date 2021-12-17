#!/usr/bin/env python
# coding=utf-8
import _thread
import csv
import os
import re
import time
from lxml import etree
import requests
from queue import Queue
from LoggerUtil import logger
import SpiderConfig
import IPPool
from ResultProcess import resultProcess


class JobSpider:
    """
    51 job 网站爬虫类
    """

    def __init__(self):
        self.count = 1  # 记录当前爬第几条数据
        self.company = []
        self.desc_url_queue = Queue()  # 线程池队列
        self.url_list = []
        self.targetName = ""

    def job_spider(self):
        """
        爬虫入口
        """
        for b in self.url_list:
            self.desc_url_queue.put(b)
        # 打印队列长度,即多少条岗位详情 url
        logger.info("队列长度为 {} ".format(self.desc_url_queue.qsize()))

    def get_url(self):
        print(SpiderConfig.START_URL.format(self.targetName, 1))
        jobs = requests.get(
            url=SpiderConfig.START_URL.format(self.targetName, 1),
            headers=SpiderConfig.HEADERSTEST).json()
        maxPage = jobs["total_page"]
        print("一共{}页".format(maxPage))
        urls = [SpiderConfig.START_URL.format(self.targetName, p) for p in range(1, int(maxPage) + 1)]
        for url in urls:
            logger.info("爬取第 {} 页".format(urls.index(url) + 1))
            jobs = requests.get(
                url=url,
                headers=SpiderConfig.HEADERSTEST).json()
            for job in jobs["engine_jds"]:
                try:
                    href = job["job_href"]
                    with open(self.targetName + "_urls.txt", 'a', encoding='utf-8') as fi:
                        fi.write(href + '\n')
                except:
                    pass

    def post_require(self, proxies):
        """
        爬取职位描述
        """
        try:
            url = self.desc_url_queue.get(False).strip()
            if url == "":
                return
        except:
            return
        try:
            resp = requests.get(url, headers=SpiderConfig.HEADERS, timeout=60, proxies=proxies)
        except Exception as ee:
            logger.error(ee)
            logger.warning(url)
            self.log_fail_url(url)
            return
        if resp.status_code == 200:
            html = resp.content
            resp.close()
            del resp
            self.get_data(html, url)

    def get_data(self, html, url):
        try:
            # 数据分析
            data = etree.HTML(html)
            s_list = data.xpath("//div[@class='bmsg job_msg inbox']")
            s = []
            for s_ in s_list:
                s.append(s_.xpath("string(.)"))
            s = ''.join(s)
            job_info = s.replace("微信", "").replace("分享", "").replace("邮件", "").replace(
                "\t", ""
            ).strip()
            href = url
            job = ''.join(data.xpath("//div[@class='cn']/h1/text()"))
            salary = ''.join(data.xpath("//div[@class='cn']/strong/text()"))
            company_name = ''.join(data.xpath("//a[@class='catn']/text()"))
            job_cate = re.search("职能类别.*?", job_info).group().strip()
            breviary = ''.join(data.xpath("//div[@class='cn']/p[@class='msg ltype']/text()"))
            company_in = data.xpath("//div[@class='com_tag']")
            company_info = []
            for ci_ in company_in:
                company_info.append(ci_.xpath("string(.)"))
            company_info = '\n'.join(company_info)
            work_address = ''.join(data.xpath("//div[@class='bmsg inbox']/p[@class='fp']/text()"))
            item = {
                "href": href,
                "job": job,
                "salary": salary,
                "company_name": company_name,
                "job_cate": job_cate,
                "breviary": breviary,
                "job_info": job_info,
                "company_info": company_info,
                "work_address": work_address
            }
            self.company.append(item)
            logger.info("爬取第 {} 条岗位详情 - ".format(self.count) + url)
            with open(self.targetName + ".csv", 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(item.values())
            self.desc_url_queue.task_done()
            self.count += 1
        except Exception as e:
            self.log_fail_url(url)
            logger.error(e)
            logger.warning(url)

    def log_fail_url(self, url):
        with open(self.targetName + '_fail_urls.txt', 'a')as fi:
            fi.write(url + "\n")

    def set_urls(self, file_path):
        with open(file_path, 'r')as fi:
            bs = fi.readlines()
            for nn in range(len(bs)):
                bs[nn].strip()
            self.url_list = bs
        if len(self.url_list) < 1000:
            return False
        return True

    def clear_fail_urls(self):
        with open(self.targetName + '_fail_urls.txt', 'w')as fi:
            fi.write("")

    def do_more(self):
        while not self.desc_url_queue.empty():
            try:
                ips = IPPool.LiuGuan()
            except Exception as eeee:
                logger.error(eeee)
                time.sleep(10)
                continue
            for ip in ips:
                p = {
                    'http': ip,
                    'https': ip,
                }
                _thread.start_new_thread(self.post_require, (p,))
        self.desc_url_queue.join()  # 主线程阻塞,等待队列清空

    def do_fail_urls(self):
        flag = True
        while flag:
            self.url_list = []
            flag = self.set_urls(self.targetName + '_fail_urls.txt')
            self.job_spider()
            self.do_more()
            os.remove(self.targetName + '_fail_urls.txt')

    def run(self):
        """
        多线程爬取数据
        """
        self.get_url()
        self.set_urls(self.targetName + "_urls.txt")
        self.job_spider()
        self.do_more()
        self.do_fail_urls()


if __name__ == '__main__':
    spider = JobSpider()
    spider.targetName = SpiderConfig.TARGET
    spider.run()
    resultProcess(spider.targetName)
