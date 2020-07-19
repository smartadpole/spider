#_*_encoding:utf-8_*_
import urllib
from lxml.html import etree
import time
import  sys, os
import re

CHROME_DRIVER = "/media/hao/DS/OTHER/TOOLS"
sys.path.append("CHROME_DRIVER")

__all__ = ["page", "GetContent", "ParseUrls",
           "DateNum", "DateFormat", "FindYear",
           "GetXmlContent", "save", "GenUrls",
           "InConference"]

DATE = {
    "Jan": 1
    , "Feb": 2
    , "Mar": 3
    , "Apr": 4
    , "May": 5
    , "Jun": 6
    , "Jul": 7
    , "Aug": 8
    , "Sep": 9
    , "Oct": 10
    , "Nov": 11
    , "Dec": 12
}
CONFERENCE = ['CVPR', 'ICLR', 'ICCV', 'ECCV', 'IJCAI', 'AAAI', 'ICML', 'ECAI',
              'ICRA', 'ICAPS', 'AAMAS', 'ICME', 'ACCV', 'NIPS', 'IJCV', 'ICME', 'IMVIP',
              'Conference'
              ]

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

def ParseUrls(content):
    urls = []
    #找到大标签
    content_label = "/html/body/div[5]/div/"
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

def  DateNum(date:str):
    sub_date = date.strip(" ").split(' ')
    return  "{}-{:0>2}-{:0>2}".format(sub_date[2], DATE[sub_date[1]], sub_date[0])

def DateFormat(date:str):
    prefix = "Submitted on "
    submit = date[date.find(prefix) + len(prefix):date.find(")")]

    return DateNum(submit)

def FindYear(data):
    year = re.findall("20[0-9][0-9]", data)
    if  0 ==len(year):
        return ""
    else:
        return year[0]

def InConference(data):
    for c in CONFERENCE:
        if c.lower() in data.lower():
            return c
    return ""

def GetXmlContent(driver, url):
    txt = ""
    try:
        driver.get(url)
        # time.sleep(2)
        content = GetContent(driver)
        root = "/html/body/div/main/div/div/div/div['content']/div['abs']/"
        title = content.xpath(root + "h1/text()")[0]
        date = content.xpath(root + "div[2]/text()")
        if [] == date or ',' in str(date[0]).strip():
            date = content.xpath(root + "div[1]/text()")[0].strip().strip('\n')
        else:
            date = date[0]
        date = DateFormat(date)
        abstract = content.xpath(root + "blockquote/text()")[0].strip(" ").strip('\n')
        if '' != abstract:
            abstract += ' '
        abstract_other = content.xpath(root + "blockquote/*")
        for a in abstract_other:
            if None != a.text and 'Abstract:' != a.text:
                abstract += a.text.strip()
            if None != a.tail and 'Abstract:' != a.tail:
                abstract += a.tail.strip()
        abstract = abstract.replace("\n", " ")
        tag = content.xpath(root + "div['metatable']/table/tbody/tr[1]/td[2]/text()")[0].strip("\n").strip(" ")
        if "" == tag:
            tag = content.xpath(root + "div['metatable']/table/tbody/tr[1]/td[2]/span/text()")[0].strip("\n").strip(" ")
        year = FindYear(tag)
        tag = InConference(tag)
        if "" != tag:
            tag += " " + year

        txt = "1. [{}]({})  \n".format(title, url.replace("https://arxiv", "http://cn.arxiv"))
        txt += "{} *{}* [paper]({}) ".format(tag, date, url)
        try:
            code = content.xpath(root + "blockquote/a/@href")[0].strip(" ").replace("\n", " ")
            txt += "| [code]({})-official    \n".format(code)
        except:
            txt += "    \n"
        txt += "{}  \n\n".format(abstract)
    except:
        print("error: ", url)

    return txt

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
            urls.append(main_page.replace("&q=", "&p={}&q=".format(i+1)))

    return urls