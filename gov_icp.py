# -*- coding: utf-8 -*-
import requests
import hashlib
import time
import base64
import cv2
import os
import random
from fake_useragent import UserAgent
import argparse


def gov_main(company_name):
    info = company_name
    cookie = ""
    get_token = ""
    p_uuid = ""
    mouse_length = ""
    info_data = {
        'pageNum':'',
        'pageSize':'',
        'unitName':info
    }

    ua = UserAgent()
    user_agent = ua.random
    os.environ['no_proxy'] = '*' #避免因系统代理设置导致请求失败

    #提前获取要查询的对象信息，以免Token失效（Token有效时间为3分钟）
    ip = str(random.randint(1,255))+"."+str(random.randint(1,255))+"."+str(random.randint(1,255))+"."+str(random.randint(1,255))
    ip = str(ip)
    #构造AuthKey
    timeStamp = int(round(time.time()*1000))
    authSecret = "testtest" + str(timeStamp)
    authKey = hashlib.md5(authSecret.encode(encoding='UTF-8')).hexdigest()
    #获取Cookie
    cookie_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'user-agent': user_agent
    }
    try:
        cookie = requests.utils.dict_from_cookiejar(requests.get('https://beian.miit.gov.cn/',headers=cookie_headers).cookies)['__jsluid_s']
    except Exception as e:
        print(e)
        
    #请求获取Token
    t_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/auth'
    t_headers = {
        'Host': 'hlwicpfwc.miit.gov.cn',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
        'Accept': '*/*',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': user_agent,
        'Origin': 'https://beian.miit.gov.cn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://beian.miit.gov.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '__jsluid_s=' + cookie,
        "CLIENT-IP": ip,
        "X-FORWARDED-FOR": ip
    }
    data = {
        'authKey': authKey,
        'timeStamp': timeStamp
    }

    try:
        t_response = requests.post(t_url,data=data,headers=t_headers)
        print(t_response.text)
        get_token = t_response.json()['params']['bussiness']
    except:
        print('\n'"获取token失败请求被禁止，请稍后或更换头部与IP后再试，状态码：",t_response.status_code)
    #获取验证图像、UUID
    p_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImage'
    p_headers = {
        'Host': 'hlwicpfwc.miit.gov.cn',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
        'Accept': 'application/json, text/plain, */*',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': user_agent,
        'token': get_token,
        'Origin': 'https://beian.miit.gov.cn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://beian.miit.gov.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '__jsluid_s=' + cookie
    }

    try:
        p_request = requests.post(p_url,data='',headers=p_headers)
        p_uuid = p_request.json()['params']['uuid']
        big_image = p_request.json()['params']['bigImage']
        small_image = p_request.json()['params']['smallImage']
    except KeyError:
        print("请重试，请求状态码：",p_request.status_code)

    #解码图片，写入并计算图片缺口位置
    try:
        with open('bigImage.jpg','wb') as f:
            f.write(base64.b64decode(big_image))
            f.close()
        with open('smallImage.jpg','wb') as f:
            f.write(base64.b64decode(small_image))
            f.close()
        background_image = cv2.imread('bigImage.jpg',cv2.COLOR_GRAY2RGB)
        fill_image = cv2.imread('smallImage.jpg',cv2.COLOR_GRAY2RGB)
        background_image_canny = cv2.Canny(background_image, 100, 200)
        fill_image_canny = cv2.Canny(fill_image, 100, 300)
        position_match = cv2.matchTemplate(background_image, fill_image, cv2.TM_CCOEFF_NORMED)
        min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(position_match)
        position = max_loc
        mouse_length = position[0]+1
        os.remove('bigImage.jpg')
        os.remove('smallImage.jpg')
    except Exception as e:
        print(e)
        
    #通过拼图验证，获取sign
    check_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/checkImage'
    check_headers = {
        'Host': 'hlwicpfwc.miit.gov.cn',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Content-Length': '60',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.42',
        'User-Agent': user_agent,
        'token': get_token,
        'Content-Type': 'application/json',
        'Origin': 'https://beian.miit.gov.cn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://beian.miit.gov.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '__jsluid_s=' + cookie
    }
    check_data = {
        'key':p_uuid,
        'value':mouse_length
    }

    try:
        check_request = requests.post(check_url,json=check_data,headers=check_headers)
        sign = check_request.json()['params']
    except Exception:
        print('\n'"请求被禁止，请稍后或更换头部与IP后再试，状态码：",check_request.status_code)
    #获取备案信息
    info_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/icpAbbreviateInfo/queryByCondition'
    info_headers = {
        'Host': 'hlwicpfwc.miit.gov.cn',
        'Connection': 'keep-alive',
        'Content-Length': '78',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'uuid': p_uuid,
        'token': get_token,
        'sign': sign,
        'Origin': 'https://beian.miit.gov.cn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://beian.miit.gov.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '__jsluid_s=' + cookie
    }

    info_request = None
    domain_total = 0
    page_total = 0
    page_size = 0
    start_row = 0
    end_row = 0
    try:
        info_request = requests.post(info_url,json=info_data,headers=info_headers)
        domain_total = info_request.json()['params']['total']
        page_total = info_request.json()['params']['lastPage']
        page_size = info_request.json()['params']['pageSize']
        start_row = info_request.json()['params']['startRow']
        end_row = info_request.json()['params']['endRow']
    except Exception as e:
        print(e)
    print("\n查询对象",info,"共有",domain_total,"个备案域名",'\n')
    print("域名具体信息如下：")
    domain_list = []
    for i in range(1,page_total+1):
        print("第"+str(i)+"页")
        for k in range(start_row,end_row+1):
            info_base = info_request.json()['params']['list'][k]
            domain_name = info_base['domain']
            print("域名：",domain_name,'\n')
            domain_list.append(domain_name)
        info_data_page = {
            'pageNum':i+1,
            'pageSize':'10',
            'unitName':info
        }
        if info_data_page['pageNum'] > page_total:
            print("查询完毕",'\n')
            print(str(len(domain_list)))
            break
        else:
            try:
                info_request = requests.post(info_url,json=info_data_page,headers=info_headers)
                start_row = info_request.json()['params']['startRow']
                end_row = info_request.json()['params']['endRow']
                time.sleep(3)
            except Exception as e:
                print("报错了{}".format(e))
                continue

    print("查询完毕",'\n')
    print(str(len(domain_list)))
    return domain_list

def poolmana(web_url,uuid,scanid,company_name):
    domain_list = gov_main(company_name)
    info_list = {"uuid":uuid,"scanid":scanid,"icp_domain_list":domain_list,"icp_company_name":company_name}
    data = info_list
    print(data)
    rep = requests.post(url=web_url,json=data)
    print(rep.text)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--company_name", dest='company_name', help="json数据")
    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")
    
    args = parser.parse_args()
    poolmana(args.url,args.uuid,args.scanid,args.company_name)
    print("程序运行结束，查收")
