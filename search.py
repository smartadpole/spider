#_*_encoding:utf-8_*_
from tqdm import tqdm
from selenium import webdriver
import time
import argparse
import  sys, os
from  utils import WriteTxt
from arxiv import *
import re

CHROME_DRIVER = "/media/hao/DS/OTHER/TOOLS"
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

def GetPages(baseurl, content):
    content_root = "/html/body/main/div[1]/div/h1/text()"
    num = content.xpath(content_root)[0]
    num = re.findall(r"\d+\.?\d*", num)
    num = [int(n) for n in num]
    total_num = int((num[2]+num[1]-1) / num[1])

    urls = [baseurl, ]
    if total_num > 1:
        items = range(0, total_num, num[1])
        urls = ["{}&start={}".format(baseurl, ITEMS_NUM*i) + i for i in items]

    return urls

def GetArticalUrl(driver, page_urls):
    urls = []
    for url in page_urls:
        driver.get(url)
        page_content = GetContent(driver)
        artical = ''
        urls.append(artical)

    return  urls


def ParseArXiv(driver, key, output_dir:str):
    baseurl = "https://arxiv.org/search/cs?query={}&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(key, SERCH_TYPE, ITEMS_NUM)
    driver.get(baseurl)
    time.sleep(1)

    page_content = GetContent(driver)
    page_urls = GetPages(baseurl, page_content)
    urls = GetArticalUrl(driver, page_urls)
    file = os.path.join(output_dir, "{}.md".format(key))

    for page in tqdm(urls):
        txt = GetXmlContent(driver, page)
        WriteTxt(txt, file, "a")
    time.sleep(0.5)
    print("{:-^30}".format("search " + key + " done"))

    return len(urls)

def main():
    args = GetArgs()
    driver = webdriver.Chrome()

    items_num = []
    num = ParseArXiv(driver, args.query, args.output_dir)
    print("num: ", num)
    driver.close()


if __name__ == "__main__":
    main()
