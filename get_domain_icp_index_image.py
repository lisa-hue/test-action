from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import difflib
import base64
import argparse
import requests

def get_chrome_driver():
    from selenium import webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)


def get_icp_image(company_name,domain_name):
    try:
        #driver = webdriver.Chrome()
        driver = get_chrome_driver()
        driver.maximize_window()
        driver.get('https://icp.chinaz.com/'+domain_name)
        icp_company_name_element=WebDriverWait(driver,50,0.5).until(EC.presence_of_element_located((By.XPATH,'//*[@id="first"]/li[1]/p/a')))
        icp_company_name = icp_company_name_element.text
        #公司名称模糊匹配
        dif_result = difflib.get_close_matches(icp_company_name, [company_name])
        #匹配成功，截图返回
        if dif_result:
            icp_image_base64 = driver.get_screenshot_as_base64()
            return icp_image_base64
            """
            imgdata = base64.b64decode(icp_image_base64)
            #将图片保存为文件
            with open("temp.jpg",'wb') as f:
                f.write(imgdata)
            """
    except Exception as e:
        print(e)
        return ""
        
def get_index_image(index_url):
    try:
        #driver = webdriver.Chrome()
        driver = get_chrome_driver()
        driver.maximize_window()
        driver.get(index_url)
        index_image_base64 = driver.get_screenshot_as_base64()
        return index_image_base64
    except Exception as e:
        print(e)
        return ""

    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", dest='url', help="返回接口")
    parser.add_argument("--uuid", dest='uuid', help="用户id")
    parser.add_argument("--scanid", dest='scanid', help="任务id")
    parser.add_argument("--company_name", dest='company_name', help="company_name")
    parser.add_argument("--domain_name", dest='domain_name', help="domain_name")
    parser.add_argument("--index_url", dest='index_url', help="index_url")
    parser.add_argument("--vul_id", dest='vul_id', help="vul_id")
    
    args = parser.parse_args()
    flag = True
    icp_image_base64 = get_icp_image(args.company_name,args.domain_name)
    #没获取到beian截图，GG
    if icp_image_base64 == "":
        index_image_base64 = ""
        flag = False
    else:
        index_image_base64 = get_index_image(args.index_url)
        if index_image_base64 == "":
            flag = False
        
    info_list = {"uuid":args.uuid,"scanid":args.scanid,"vul_id":args.vul_id,"icp_image_base64":icp_image_base64,"index_image_base64":index_image_base64,"flag":flag}
    print(info_list)
    rep = requests.post(url=args.url,json=info_list)
    #print(rep.text)
