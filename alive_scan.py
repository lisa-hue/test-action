import sys
import nmap
import argparse
import json
import requests
import time
from multiprocessing.dummy import Pool as ThreadPool


info_list = []
url_list = []
list_80 = []
list_443 = []


def action(hosts):
    global info_list
    port = "80,443"
    try:    
    #创建端口扫描对象
        nm = nmap.PortScanner() 
    except nmap.PortScannerError:
        print('Nmap not found', sys.exc_info()[0])
        sys.exit(0)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(0)

    try:
    #调用扫描方法，参数指定扫描主机hosts，nmap扫描命令行参数arguments
        nm.scan(hosts=hosts, arguments=' -v -Pn -p '+port)
    except Exception as e:
        print("Scan erro:"+str(e))
    
    #遍历扫描主机
    for host in nm.all_hosts():
        print('----------------------------------------------------')
        #输出主机及主机名
        print('Host : %s (%s)' % (host, nm[host].hostname()))
        #输出主机状态，如up、down
        print('State : %s' % nm[host].state())
        port_list = []
        for proto in nm[host].all_protocols():
            #遍历扫描协议，如tcp、udp
            print('----------')
            #输入协议名
            print('Protocol : %s' % proto)
            #获取协议的所有扫描端口
            lport = nm[host][proto].keys()
            #端口列表排序
            list(lport).sort()
            #遍历端口及输出端口与状态
            
            for port in lport:
                print('port : %s\tstate : %s\tinfo : %s' % (port, nm[host][proto][port]['state'],nm[host].tcp(port)['name']))
                port_list.append({"port":port,"state":nm[host][proto][port]['state'],"info":nm[host].tcp(port)['name']})
        #info_list = {"host":hosts,"state":nm[host].state(),"port_info":port_list}
        tmp = {"host":hosts,"state":nm[host].state(),"port_info":port_list}
        info_list.append(tmp)
        return tmp

    
    
    
if __name__ == '__main__':
    
    pool = ThreadPool(100)
    host_list = []
    with open('host.txt',errors='ignore',encoding="utf-8") as f:
        lines = f.readlines()
        for host in lines:
            host = host.replace("\n","")
            host_list.append(host)
    pool.map( action,host_list)    
    pool.close()  #关闭线程池，执行close后不会有新线程加入
    pool.join()   #等待所有子线程结束掉，后再结束。
    print(info_list)
    for host_info in info_list:
        if host_info == None:
            continue
        host = host_info["host"]
        port_list = host_info["port_info"]
        for port_info in port_list:
            port = port_info["port"]
            state = port_info["state"]
            if state == "open" and port == 80 :
                list_80.append(host)
            if state == "open" and port == 443 :
                list_443.append(host)
    
    tmp_list = []
    for host_port_443 in list_443:
        flag = False
        for host_port_80 in list_80:
            if host_port_443 == host_port_80:
                flag = True
                break
        #在80开放端口列表中，未找到重复数据，加入临时集合
        if not flag:
            tmp_list.append(host_port_443)
    list_443 = tmp_list
    for host in list_80:
        url_list.append("http://"+host)
    for host in list_443:
        url_list.append("https://"+host)
    print(url_list)
    with open('url.txt','a+',errors='ignore',encoding='utf-8') as w:
        for url in url_list:
            w.write(url+"\n")
    print("end")
