import sys
import nmap
import argparse
import json
import requests

info_list = {}

def port_scan(url,uuid,taskid,scanid,hosts,port):
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
        nm.scan(hosts=hosts, arguments=' -v -T4 -p '+port)
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
        info_list = {"uuid":uuid,"scanid":scanid,"taskid":taskid,"host":hosts,"state":nm[host].state(),"port_info":port_list}
        data = json.dumps(info_list)
    print(data)
    rep = requests.post(url=url,json=data)
    print(rep.text)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest='target',help="目标")
    parser.add_argument("-p", "--port", dest='port', help="端口")
    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")
    parser.add_argument("-tid", "--taskid", dest='taskid', help="线程id")

    args = parser.parse_args()

    port_scan(args.url,args.uuid,args.taskid,args.scanid,args.target,args.port)
