import requests
import json
from urllib.parse import quote
import js2py
import math
import time
import argparse
import base64

def is_chinese(string):
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
 
    return False

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'}
headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

def get_icp_domain(companyName):
    domain_list = []
    context = js2py.EvalJs()
    with open("generatetoken.js", 'r', encoding='utf8') as f:
        context.execute(f.read())
    token = context.generateWordKey(companyName)
    print(token)

    companyNameUrlEncode = quote(str(companyName))
    tokenUrlEncode = quote(str(token))
    url = 'http://icp.chinaz.com/Home/PageData'
    data = 'pageNo=1&pageSize=20&Kw=' + companyNameUrlEncode + "&token=" + tokenUrlEncode
    try:
        res = requests.post(url=url, headers=headers,data=data, allow_redirects=False, verify=False)
        json_ret = json.loads(res.text)
        #总数量
        amount = json_ret["amount"]
        pageTotal = math.ceil(amount / 20)
        print(amount)
        print(pageTotal)
        data_list = json_ret["data"]
        for domain in data_list:
            domain_list.append(domain["host"])
        for pageNo in range(1,pageTotal + 1):
            print("第{}页".format(str(pageNo + 1)))
            data = 'pageNo='+str(pageNo + 1)+'&pageSize=20&Kw=' + companyNameUrlEncode + "&token=" + tokenUrlEncode
            res = requests.post(url=url, headers=headers,data=data, allow_redirects=False, verify=False)
            json_ret = json.loads(res.text)
            data_list = json_ret["data"]
            for domain in data_list:
                tmp_domain = domain["host"]
                if is_chinese(tmp_domain):
                    continue
                domain_list.append(tmp_domain)
    except Exception as e:
        print(e)
    return domain_list
    
def poolmana(web_url,uuid,scanid,plaintext_result):
    ciphertext_str = base64.b64decode(plaintext_result)
    company_name = ciphertext_str.decode()
    company_name = company_name.replace(")","）")
    company_name = company_name.a.replace("(","（")
    domain_list = get_icp_domain(company_name)
    info_list = {"uuid":uuid,"scanid":scanid,"icp_domain_list":domain_list,"icp_company_name":company_name}
    return info_list

if __name__ == '__main__':
    result_list = []
    parser = argparse.ArgumentParser()
    parser.add_argument("-c1", "--company_name1", dest='company_name1', help="json数据")
    parser.add_argument("-c2", "--company_name2", dest='company_name2', help="json数据")
    parser.add_argument("-c3", "--company_name3", dest='company_name3', help="json数据")
    parser.add_argument("-c4", "--company_name4", dest='company_name4', help="json数据")
    parser.add_argument("-c5", "--company_name5", dest='company_name5', help="json数据")
    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")
    
    args = parser.parse_args()
    tmp = poolmana(args.url,args.uuid,args.scanid,args.company_name1)
    result_list.append(tmp)
    tmp = poolmana(args.url,args.uuid,args.scanid,args.company_name2)
    result_list.append(tmp)
    tmp = poolmana(args.url,args.uuid,args.scanid,args.company_name3)
    result_list.append(tmp)
    tmp = poolmana(args.url,args.uuid,args.scanid,args.company_name4)
    result_list.append(tmp)
    tmp = poolmana(args.url,args.uuid,args.scanid,args.company_name5)
    result_list.append(tmp)
    data = result_list
    print(data)
    web_url = args.url
    rep = requests.post(url=web_url,json=data)
    print(rep.text)
    print("程序运行结束，查收")
