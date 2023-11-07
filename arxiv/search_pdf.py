#_*_encoding:utf-8_*_
from tqdm import tqdm
from selenium import webdriver
import time
import argparse
import  sys, os
import urllib
from arxiv import *
import re
from util.file import WriteTxt, MkdirSimple

CHROME_DRIVER = "/home/hao/Software"
sys.path.append("CHROME_DRIVER")

SEARCH = "image+retrieval"
ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 200
SERCH_TYPE = 'title' # all

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--query", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")

    return parse.parse_args()

def GetPDFUrl(content):
    re_root = "/html/body/main/div['content']/ol"
    re_item = re_root + "/li"
    content_item = content.xpath(re_item)

    re_url = "div/p/span/a[1]/@href"
    re_label = "div/div/span[1]/text()"
    re_title = "p[1]/text()"
    items = []

    for c in content_item:
        url = c.xpath(re_url)
        label = c.xpath(re_label)
        label = "cs.CV" if "cs.CV" in label else label[0]
        title = c.xpath(re_title)
        title = "".join(title)
        title = re.sub('[^a-zA-Z0-9#$%&()]', " ", title)
        title = " ".join(title.split())
        if len(url) == 0:
            continue
        items.append({"url": url[0], "label": label, "title": title})

    return items

def GetPages(baseurl, content):
    content_root = "/html/body/main/div[1]/div/h1/text()"
    num = content.xpath(content_root)[0]
    num = num.replace(',', '')
    num = re.findall(r"\d+\.?\d*", num)
    num = [int(n) for n in num]
    total_pages = int((num[2]+num[1]-1) / num[1])

    urls = [baseurl, ]
    if total_pages > 1:
        items = list(range(0, total_pages))
        urls = ["{}&start={}".format(baseurl, str(ITEMS_NUM*i + i)) for i in items]

    return urls

def GetArticalUrl(driver, page_urls):
    urls = []
    for url in page_urls:
        driver.get(url)
        page_content = GetContent(driver)
        pdf_links = GetPDFUrl(page_content)
        urls.extend(pdf_links)

    return  urls


def ParseArXiv(driver, key):
    baseurl = "https://arxiv.org/search/?query={}&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(key, SERCH_TYPE, ITEMS_NUM)
    driver.get(baseurl)
    time.sleep(1)

    page_content = GetContent(driver)
    page_urls = GetPages(baseurl, page_content)
    urls = GetArticalUrl(driver, page_urls)

    return urls

def Download(items, output:str):
    os.makedirs(output, exist_ok=True)

    for item in tqdm(items):
        try:
            url = item['url']
            name = os.path.basename(url)
            label = item['label']
            file_path = os.path.join(output, label, name + ".pdf")
            MkdirSimple(file_path)
            urllib.request.urlretrieve(url, file_path)
        except:
            print("error download {}.".format(item))

def SaveCSV(items, file):
    text = []
    for item in items:
        txt = ','.join(item.values())
        text.append(txt)
    text = "\n".join(text)
    WriteTxt(text, file, 'w')


def main():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    args = GetArgs()
    sev = webdriver.chrome.service.Service()
    sev.path = os.path.join(CHROME_DRIVER, "chromedriver")
    driver = webdriver.Chrome(service=sev)

    items = ParseArXiv(driver, args.query)
    print("num: ", len(items))
    driver.close()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    SaveCSV(items, os.path.join(args.output_dir, "readme.csv"))
    Download(items, args.output_dir)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == "__main__":
    main()
