#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: search_pdf_string.py
@time: 2024/5/12 上午11:42
@desc: 
'''
import sys, os

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../'))

import math
import requests
import time
from tqdm import tqdm
import argparse
import sys
import os
import urllib
import re
from util.file import WriteTxt, MkdirSimple

ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 200
SERCH_TYPE = 'title'  # all
COMMENTS = ['cvpr', 'iccv', 'iclr']

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--query", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")

    return parse.parse_args()

def RemoveTags(text):
    # 匹配尖括号内的内容
    pattern = r'<.*?>'
    # 使用 sub 函数替换匹配到的内容为空字符串
    return re.sub(pattern, '', text)

def GetPDFUrl(content):
    print("loading papers info...")
    items = []
    li_matches = re.finditer(r'<li class="arxiv-result">.*?</li>', content, re.DOTALL)
    for li_match in li_matches:
        li_content = li_match.group()
        label = re.findall(r'">([^<]+)</span>', li_content)
        pdf_match = re.search(r'<a href="([^"]+)">pdf</a>', li_content)
        title_match = re.search(r'<p class="title is-5 mathjax">\s*(.*?)\s*</p>', li_content, re.DOTALL)
        if len(label) > 0 and pdf_match and title_match:
            label = "cs.CV" if "cs.CV" in label else label[0]
            pdf_url = pdf_match.group(1)
            title = title_match.group(1)
            title = RemoveTags(title)
            items.append({"url": pdf_url, "label": label, "title": title})

    return items


def GetPages(baseurl, content):
    urls = [baseurl, ]

    total_num = re.search(r'of (\d{1,3}(,\d{3})*(\.\d+)?)', content)

    if total_num:
        total_num = int(total_num.group(1).replace(',', ''))
        total_pages = math.ceil(total_num / ITEMS_NUM)

        if total_pages > 1:
            items = list(range(0, total_pages))
            urls = ["{}&start={}".format(baseurl, str(ITEMS_NUM * i)) for i in items]

    print("pages: ", "\n".join(urls))

    return urls


def GetArticalUrl(page_urls):
    urls = []

    base_urls = page_urls if isinstance(page_urls, list) else [page_urls, ]

    for url in base_urls:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            pdf_links = GetPDFUrl(content)
            urls.extend(pdf_links)
        time.sleep(1)

    return urls


def ParseArXiv(key):
    if key.split()[0].lower() in COMMENTS:
        baseurl = "https://arxiv.org/search/?query={}&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(key, "comments", ITEMS_NUM)
    else:
        baseurl = "https://arxiv.org/search/?query={}&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(key, SERCH_TYPE, ITEMS_NUM)
    response = requests.get(baseurl)
    if response.status_code == 200:
        content = response.text
        page_urls = GetPages(baseurl, content)
        urls = GetArticalUrl(page_urls)

        return urls

    return []


def Download(items, output: str, usetitle=False):
    os.makedirs(output, exist_ok=True)

    for item in tqdm(items):
        try:
            url = item['url']
            if usetitle:
                name = item['title']
            else:
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
