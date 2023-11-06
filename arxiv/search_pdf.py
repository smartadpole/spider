#_*_encoding:utf-8_*_
from tqdm import tqdm
from selenium import webdriver
import time
import argparse
import  sys, os
import urllib
from arxiv import *
import re

CHROME_DRIVER = "/home/hao/Software"
sys.path.append("CHROME_DRIVER")

SEARCH = "image+retrieval"
ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 50
SERCH_TYPE = 'title' # all

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--query", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")

    return parse.parse_args()

def GetPDFUrl(content):
    content_root = "/html/body/main/div['content']/ol"
    re_url = content_root + "/li/div/p/span/a[1]/@href"

    content_urls = content.xpath(re_url)

    # re_label = content_root + "/li/p[1]"
    # content_label = content.xpath(re_label)
    # names = [name.strip() for name in content_label if name.strip() != ""]
    urls = [i for i in content_urls]

    return urls

def GetPages(baseurl, content):
    content_root = "/html/body/main/div[1]/div/h1/text()"
    num = content.xpath(content_root)[0]
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
    baseurl = "https://arxiv.org/search/cs?query={}&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(key, SERCH_TYPE, ITEMS_NUM)
    driver.get(baseurl)
    time.sleep(1)

    page_content = GetContent(driver)
    page_urls = GetPages(baseurl, page_content)
    urls = GetArticalUrl(driver, page_urls)

    return urls

def Download(urls, output:str):
    os.makedirs(output, exist_ok=True)

    for url in tqdm(urls):
        try:
            name = os.path.basename(url)
            file_path = os.path.join(output, name + ".pdf")
            urllib.request.urlretrieve(url, file_path)
        except:
            print("error download {}.".format(url))

def main():
    args = GetArgs()
    sev = webdriver.chrome.service.Service()
    sev.path = os.path.join(CHROME_DRIVER, "chromedriver")
    driver = webdriver.Chrome(service=sev)

    urls = ParseArXiv(driver, args.query)
    print("num: ", len(urls))
    driver.close()

    Download(urls, args.output_dir)


if __name__ == "__main__":
    main()
