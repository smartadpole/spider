#_*_encoding:utf-8_*_
import urllib
from urllib import request
import requests
from lxml.html import etree
from selenium import webdriver
import time
import argparse
import  sys, os

CHROME_DRIVER = "/media/hao/DS/OTHER/TOOLS"
sys.path.append("CHROME_DRIVER")

USER_NAME = "smartadpole@gmail.com"
PASSWORD = "********"
SEARCH = "image+retrieval"

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--url", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")

    return parse.parse_args()

def page(number):
    data =  {}
#Language
    data['l'] = 'c++'
#page    
    data['p'] = number    
#添加搜索关键词    
    data['q'] = 'image retrieval'
    data['type'] = 'Repositories'
    url_values = urllib.parse.urlencode(data)
    url = 'https://github.com/search?'
    full_url = url + url_values
    full_url = urllib.parse.unquote(full_url)
    full_url = "https://github.com/search?l=C%2B%2B&q=image+retrieval&type=Repositories"
    # "https://github.com/search?l=C%2B%2B&p=2&q=image+retrieval&type=Repositories"
    print(full_url)
    return full_url 

#获取url页面
def GetContent(driver):
    content = driver.page_source
    try :
        content = content.decode('UTF-8')
    except:
        inf = "爬取成功"
    else:
        print("解码...")

    #构造一个XPath解析对象并对HTML文本进行自动修正
    content = etree.HTML(content)
    return content

def GetPageNum(content):
    content_label = "/html/body/div[4]/main/div/div[3]/div"
    page_num = content.xpath(content_label + "/div/div/a[last() - 1]/text()")

    if 0 == len(page_num):
        page_num = [1,]

    return int(page_num[0])

def ParseUrls(content):
    urls = []
    #找到大标签
    content_label = "/html/body/div[4]/main/div/div[3]/div"
    codelist = content.xpath(content_label + "/ul[1]/*") # /div[2]/div[1]/*

    #大标签内有10个链接
    for l in codelist:
        # url = l.xpath("./div[2]/div/a/@href")
        url = l.xpath("./div/h3/a/@href")
        if 0 == len(url):
            url = l.xpath("./div[2]/div/a/@href")
        url = url[0]

        # if url.endswith("xml"):
        urls.append(url)

    return  urls

def GetXmlContent(driver, url):
    driver.get(url)
    time.sleep(2)
    print(url)
    content = driver.page_source
    try :
        content = content.decode('UTF-8')
    except:
        print("爬取成功")
    else:
        print("继续...")
    content = etree.HTML(content)
    #找到大标签
    xmlcontent = content.xpath("/html/body/div[4]/div/main/div[3]/div/div[3]/div[2]/table/tbody/*")     
    #存储xml文件
    xmlcontentss = [] 
    #逐行提取
    for c in xmlcontent:
        xmlcontents = ''.join(c.xpath(".//td[2]//text()"))
        xmlcontentss.append(xmlcontents+"\r\n")
    #转化为字符串
    xmlcontentss = ''.join(xmlcontentss)      
    return xmlcontentss

#将爬取的数据写入文件
def save(path, xmlcontents):
    filename = time.strftime('%Y%m%d-%H%M%S ',time.localtime(time.time()))
    filename = str(filename)                        
    file = os.path.join(path, filename+ ".xml")
    f = open(file,'a+')
    f.write(xmlcontents)
    f.close()

def GenUrls(main_page:str, page_num):
    urls = []
    if page_num == 1:
        urls = [main_page,]
    else:
        for i in range(page_num):
            if "&q=" in main_page:
                urls.append(main_page.replace("&q=", "&p={}&q=".format(i+1)))
            else:
                urls.append(main_page.replace("?q=", "?p={}&q=".format(i+1)))


    return urls

def main():
    args = GetArgs()

    if (not os.path.exists(args.output_dir)):
        os.makedirs(args.output_dir)

    baseurl = "https://github.com/login"
    # baseurl = "https://github.com"
    driver = webdriver.Chrome()
    driver.get(baseurl)
    # driver.find_element_by_id("login_field").send_keys(USER_NAME)
    # driver.find_element_by_id("password").send_keys(PASSWORD)
    # driver.find_element_by_name("commit").click()
    time.sleep(2)

    try:
        main_page = args.url # page(1+i)
        driver.get(main_page)
        time.sleep(2)
        page_content = GetContent(driver)
        page_num = GetPageNum(page_content)
        pages = GenUrls(main_page, page_num)
        print("pages num: ", len(pages))
        cd_dir = "cd {}".format(args.output_dir)

        for i, page in enumerate(pages):
            driver.get(page)
            time.sleep(2) # wait for printing info from last `os.system`
            print("page {}: ".format(i + 1))
            urls = []

            for i in range(50):
                page_content = GetContent(driver)
                urls = ParseUrls(page_content)
                if 0 != len(urls):
                    break
                else:
                    print("\r{}".format("."*(i+1)), end="")

                driver.refresh()
                driver.refresh()
                time.sleep(2)
            print("item num: ", len(urls))

            for url in urls:
                name = url.split("/")
                name = "{}_{}".format(name[2], name[1])
                url = "https://github.com" + url
                os.system("{} && git clone --recursive {} {}&".format(cd_dir, url, name))
        print("-----------------此次数据爬取已完成！--------------")
        driver.close()
    except:
        driver.close()


if __name__ == "__main__":
    main()

'''
i = i + 1
try:
    xmlcontents = GetXmlContent(driver, url)
    if xmlcontents:
        s = s + 1
        save(args.output_dir, xmlcontents)
    else:
        k = k + 1
        print("file empty!")
except:
    print("fail to write!")
else:
    print("next...")
print("page %d item %d done %s empty file %d " % (i + 1), i, s, k)
'''