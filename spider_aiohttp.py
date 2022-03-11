import requests
import argparse
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from aiohttp import ClientSession
from aiohttp import TCPConnector
from urllib.parse import urlparse
from urllib.parse import urljoin


timeout = aiohttp.ClientTimeout(total=8)
#信号量
sem_num = 10
num = 0
total_urls=[]

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
           "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",}

def get_root_domain(url):
    # 是否应该在这里用正则判断传进来的URL是/开头，如果解析出来netloc是空，那也算是当前域名的链接
    if url is None:
        return None
    try:
        url_info=urlparse(url)
        root_domain = url_info.netloc
        return root_domain
    except:
        pass

def get_new_urls(soup, current_url):
    new_urls = []
    links = soup.find_all("a")
    for link in links:
        try:
            new_url = link.get('href')
            if new_url is not None:
                new_url = new_url.lstrip()
                
            #判断传进来的URL是/开头，如果解析出来netloc是空，那也算是当前域名的链接
            if new_url.startswith("/"):
                new_full_url = urljoin(current_url, new_url)
                new_urls.append(new_full_url)
            elif new_url.startswith("http"):
                new_url_root_domain = get_root_domain(new_url)
                if new_url_root_domain == '':
                    pass
                elif new_url_root_domain is not None:
                    if get_root_domain(current_url) != get_root_domain(new_url):
                        continue
                        
                new_full_url = urljoin(current_url, new_url)
                new_urls.append(new_full_url)
            else:
                new_full_url = urljoin(current_url, new_url)
                new_urls.append(new_full_url)
        except:
            pass

    return new_urls

def parse(html_content, current_url):
    if html_content is None:
        return
    soup = BeautifulSoup(html_content, "html.parser")
    new_urls = get_new_urls(soup, current_url)
    return new_urls

            
async def test(sem,url):
  global num
  global total_urls
  new_urls = []
  old_urls = []
  url_path = []
  #爬取深度
  deep = 2
  conn=aiohttp.TCPConnector(verify_ssl=False)
  async with sem:
      async with aiohttp.ClientSession(connector=conn) as session:
        try:
            num = num + 1
            print('>> {}'.format(num))
            new_urls.append(url)
            while len(new_urls) > 0:
                deep -= 1
                #print("deep"+str(deep))
                if deep < 0:
                    break
                temp_list = new_urls
                new_urls = []
                for x in temp_list:
                    url = x
                    if url.startswith("http"):
                        if "?" in url:
                            print(url)
                        async with session.get(url,timeout=timeout) as resp:
                            status = resp.status
                            if status == 200:
                                old_urls.append(url)
                                text = await resp.text()
                                if text:
                                    urls = parse(text,url)
                                    if urls:
                                        
                                        urls = list(set(urls))
                                        for aa in urls:
                                            flag = True
                                            for old_url in old_urls:
                                                if old_url == aa:
                                                    flag = False
                                                    #print("重复 不加")
                                                    break
                                            if flag:
                                                new_urls.append(aa)
                                        #print("-------------"+str(len(new_urls)))
                                    
            for url in old_urls:
                if "?" in url:
                    parseres = urlparse(url)
                    if parseres.path == "":
                        continue
                    elif parseres.path in url_path:
                        continue
                    else:
                        url_path.append(parseres.path)
                        total_urls.append(url)
                else:
                    continue
                
        except Exception as e:
            print(e)


def poolmana(web_url,uuid,scanid,ips):
    http_tasks = []
    loop_http = asyncio.get_event_loop()
    sem=asyncio.Semaphore(sem_num) #维持信号量
    
    
    for i in ips:
        i=i.replace('\n','')
        task = asyncio.ensure_future(test(sem,i))
        http_tasks.append(task)
        
    loop_http.run_until_complete(asyncio.wait(http_tasks))
    info_list = {"uuid":uuid,"scanid":scanid,"spider_url":total_urls}
    data = info_list
    print(data)
    rep = requests.post(url=web_url,json=data)
    print(rep.text)



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", dest='file', help="json数据")
    parser.add_argument("-u", "--url", dest='url', help="返回接口")
    parser.add_argument("-uid", "--uuid", dest='uuid', help="用户id")
    parser.add_argument("-sid", "--scanid", dest='scanid', help="任务id")
    
    args = parser.parse_args()

    poolmana(args.url,args.uuid,args.scanid,args.data)
    print("程序运行结束，查收")
