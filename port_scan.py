import sys
import nmap
import argparse


def port_scan(hosts,port):
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
        nm.scan(hosts=hosts, arguments=' -v -sS -p '+port)
    except Exception as e:
        print("Scan erro:"+str(e))
    #遍历扫描主机
    for host in nm.all_hosts():
        print('----------------------------------------------------')
        #输出主机及主机名
        print('Host : %s (%s)' % (host, nm[host].hostname()))
        #输出主机状态，如up、down
        print('State : %s' % nm[host].state())
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest='target',help="目标")
    parser.add_argument("-p", "--port", dest='port', help="端口")

    args = parser.parse_args()

    port_scan(args.target,args.port)
