#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: search_pdf_no_driver.py
@time: 2024/5/12 上午10:51
@desc: 
'''
import requests
from lxml import html
import time
import argparse
import sys
import os
import urllib
import re
from tqdm import tqdm
from util.file import WriteTxt, MkdirSimple

CHROME_DRIVER = "/home/hao/Software"
sys.path.append("CHROME_DRIVER")

SEARCH = "image+retrieval"
ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 200
SERCH_TYPE = 'title'  # all


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
    total_pages = int((num[2] + num[1] - 1) / num[1])

    urls = [baseurl, ]
    if total_pages > 1:
        items = list(range(0, total_pages))
        urls = ["{}&start={}".format(baseurl, str(ITEMS_NUM * i)) for i in items]

    print("pages: ", "\n".join(urls))
    return urls


def GetArticalUrl(page_urls):
    print('parse pdf links')
    urls = []
    for url in page_urls:
        response = requests.get(url)
        if response.status_code == 200:
            content = html.fromstring(response.text)
            pdf_links = GetPDFUrl(content)
            urls.extend(pdf_links)
        time.sleep(1)

    return urls


def ParseArXiv(key):
    baseurl = "https://arxiv.org/search/?query={}&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(
        key, SERCH_TYPE, ITEMS_NUM)
    response = requests.get(baseurl)
    if response.status_code == 200:
        content = html.fromstring(response.text)
        page_urls = GetPages(baseurl, content)
        urls = GetArticalUrl(page_urls)

        return urls

    return []


def Download(items, output: str):
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

    items = ParseArXiv(args.query)
    print("total papers: ", len(items))

    SaveCSV(items, os.path.join(args.output_dir, "readme.csv"))
    Download(items, args.output_dir)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == "__main__":
    main()
