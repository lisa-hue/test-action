import requests
import argparse
import json
from urllib.parse import urlparse

total_urls=[]

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
           "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",}


def poolmana(web_url,uuid,scanid):
    vul_info = []
    with open("rs.json",errors="ignore") as f:
        lines = f.readlines()
        for a in lines:
            line = json.loads(a)
            name = line["info"]["name"]
            severity = line["info"]["severity"]
            matched_at = line["matched-at"]
            url_info=urlparse(matched_at)
            vul_host = url_info.netloc
            vul_info.append({"vul_name":name,"vul_level":severity,"vul_url":matched_at,"vul_host":vul_host})
    info_list = {"uuid":uuid,"scanid":scanid,"vul_info":vul_info}
    print(info_list)
    #rep = requests.post(url=web_url,json=info_list)
    #print(rep.text)



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")
    
    args = parser.parse_args()
    poolmana(args.url,args.uuid,args.scanid)
    print("程序运行结束，查收")
