import requests
import time
import random
import string
import datetime
import sys
import argparse
from requests.adapters import HTTPAdapter


query_orgType = ""
out_date = ""
cookie = ""
return_url = ""
uuid = ""
scanid = ""

headers = {}

#查详情
#https://aiqicha.baidu.com/detail/basicAllDataAjax?pid=28680294833142
#Referer https://aiqicha.baidu.com/company_detail_28680294833142
s =requests.session()
s.mount('http://',HTTPAdapter(max_retries=5))
s.mount('https://',HTTPAdapter(max_retries=5))
def get_data(url):
    req = s.get(url,headers=headers,timeout=15)
    return req.json()
    
provinceCode_list = ["110000","120000","130000","140000","150000","210000","220000","230000","310000","320000","330000","340000","350000",
"360000","370000","410000","420000","430000","440000","450000","460000","500000","510000","520000","530000","540000","610000","620000","630000","640000","650000"]
#110000:北京，120000：天津，130000：河北，140000：山西，150000：内蒙古，210000：辽宁，"220000"：吉林,"230000"：黑龙江,
#"310000"：上海,"320000"：江苏,"330000"：浙江省,"340000"：安徽省,"350000"：福建,"360000"：江西,"370000"：山东,"410000"：河南,
#"420000"：湖北,"430000"：湖南,"440000"：广东,"450000"：广西,"460000"：海南,"500000"：重庆,"510000"：四川,"520000"：贵州,
#"530000"：云南,"540000"：西藏,"610000"：陕西,"620000"：甘肃,"630000"：青海,"640000"：宁夏,"650000"：新疆
#"recordTime":[{"start":"2022-05-31","end":"2022-05-31"}]
#2005-01-01
domain_info_list = []
def query_main():
    for provinceCode in provinceCode_list:
        time.sleep(1)
        page = 1
        url = 'https://aiqicha.baidu.com/icpsearch/sAjax?page='+str(page)+'&size=10&f={"orgType":["'+query_orgType+'"],"provinceCode":["'+provinceCode+'"],"recordTime":[{"start":"'+out_date+'","end":"'+out_date+'"}]}'

        data = get_data(url)
        #查询出错，记录一下
        if data == None:
            print("报错了")
            continue
        if not data["status"] == 0:
            print("没查到"+url+data["msg"])
            continue
        
        totalPageNum = data['data']['totalPageNum']
        if totalPageNum == 0:
            continue
        for now_page in range(1,totalPageNum+1):
            url = 'https://aiqicha.baidu.com/icpsearch/sAjax?page='+str(now_page)+'&size=10&f={"orgType":["'+query_orgType+'"],"provinceCode":["'+provinceCode+'"],"recordTime":[{"start":"'+out_date+'","end":"'+out_date+'"}]}'
            print(url)
            with open("爱企查查询url.txt",'a+',encoding="utf-8",errors="ignore") as w:
                w.write(url+"\n")
            
            data = get_data(url)
            resultList = data['data']['resultList']
            for result in resultList:
                openStatus = result['openStatus']
                if not openStatus == "开业" or openStatus == "-":
                    print("跳过此公司")
                    continue
                company_name = result['entName']
                icpNo = result['icpNo']
                orgType = result['orgType']
                pid = result['pid']
                domain_name = result['domainName'][0]
                print(openStatus+"---"+company_name+"---"+icpNo+"---"+orgType+"---"+pid+"---"+domain_name)
                domain_info_list.append({"domain_name":domain_name,"company_name":company_name,"icpNo":icpNo,"orgType":orgType,"pid":pid})
    print(domain_info_list)
    data = {"uuid":uuid,"scanid":scanid,"domain_info_list":domain_info_list}
    rep = requests.post(url=return_url,json=data)
    print(rep.text)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")
    parser.add_argument("-op", "--orgType", dest='orgType', help="组织机构类型")
    parser.add_argument("-ode", "--outdate", dest='outdate', help="日期")
    parser.add_argument("-ck", "--cookie", dest='cookie', help="cookie")
    args = parser.parse_args()
    uuid = args.uuid
    scanid = args.scanid
    query_orgType = args.orgType
    out_date = args.outdate
    cookie = args.cookie
    return_url = args.url
    #cookie = ""
    #with open('cookie.txt',encoding="utf-8",errors='ignore') as f:
    #    lines = f.readlines()
    #    cookie = lines[0]
    headers = {
    "Accept": "text/plain, */*; q=0.01",
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'cookie':cookie,
    'Referer': 'https://aiqicha.baidu.com/icpsearch?entry=21'
    }
    query_main()
    
    
