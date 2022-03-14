import argparse
import requests
import json
import platform
import os
import time
from multiprocessing import Pool


total_urls=[]
target_url = []

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
           "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",}

def sqlmap(host,num):
    urlnew="http://127.0.0.1:8775/task/new"
    urlscan="http://127.0.0.1:8775/scan/"
    headers={"user-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"}
    pd=requests.get(url=urlnew,headers=headers)
    jsons=pd.json()
    id=jsons['taskid']
    scan=urlscan+id+"/start"
    print("[*]scanurl:",scan)
    data=json.dumps({"url":"{}".format(host),"smart":True,"timeout":"10","Threads":3,"keepAlive":True,"nullConnection":True})
    headerss={"Content-Type":"application/json"}
    scans=requests.post(url=scan,headers=headerss,data=data)
    swq=scans.json()
    print('--------STATUS---------')
    status="http://127.0.0.1:8775/scan/{}/status".format(id)
    print(status)
    while True:
        time.sleep(2)
        staw=requests.get(url=status,headers=headers)
        print(">>>>>>>>>>>>>>"+str(num)+":status: "+staw.json()['status'])
        if staw.json()['status'] == 'terminated':
            datas=requests.get(url='http://127.0.0.1:8775/scan/{}/data'.format(id))
            dat=datas.json()['data']
            if dat:
                print('[*]data:',dat)
                with open("sqlinj.txt",'a+',erros="ignore") as w:
                    w.write(host+"\n")
            break
        elif staw.json()['status'] == 'running':
            continue


def poolmana(web_url,uuid,scanid,target):
    open("sqlinj.txt", 'a+',errors="ignore")
    fr = open(target, 'r',errors="ignore")
    ips=fr.readlines()
    fr.close()

    for i in ips:
        i=i.replace('\n','')
        target_url.append(i)
    num = 0
    p = Pool(processes=10)
    li = []
    for targeturl in target_url:
        try:
            num += 1
            res = p.apply_async(sqlmap,args=(targeturl,num,))
            li.append(res)
        except Exception as e:
            print(e)
            pass
    p.close()
    p.join()
    f = open('sqlinj.txt','r',errors="ignore")
    aaa = f.readlines()
    for inj_url in aaa:
        inj_url = inj_url.replace("\n","")
        total_urls.append(inj_url)
    info_list = {"uuid":uuid,"scanid":scanid,"sqlinj_url":total_urls}
    data = info_list
    print(data)
    rep = requests.post(url=web_url,json=data)
    print(rep.text)



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest='target', help="json数据")
    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")
    
    args = parser.parse_args()
    for i in args.target:
        print("-----:   {}".format(i))
    poolmana(args.url,args.uuid,args.scanid,args.target)
    print("程序运行结束，查收")
