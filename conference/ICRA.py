#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: ICRA.py
@time: 2024/5/20 上午1:56
@desc: 
'''
import sys, os

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../'))

import argparse
import time
from tqdm import tqdm
from arxiv import GetPages, SaveCSV, Download, RemoveTags
import requests
import re

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--url", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")

    return parse.parse_args()

def GetPDFUrl(content):
    print("loading papers info...")
    items = []

    year_match = re.search(r'<h2>(\d{4})\b.*?</h2>', content)
    year = year_match.group(1) if year_match else "0000"

    patch_matches = re.finditer(r'<div class="article compact">.*?(?=<div class="article compact">|</div></div>)', content, re.DOTALL)
    i = 0
    for pm in patch_matches:
        i += 1
        if i == 56:
            i = 56
        patch = pm.group()
        # label = re.findall(r'">([^<]+)</span>', patch)
        pdf_match = re.search(r'<a href="([^"]+)">Download fulltext</a>', patch)
        title_match = re.search(r'<a href="[^"]+">([^<]+)</a>', patch, re.DOTALL)
        if pdf_match and title_match:
            # label = "cs.CV" if "cs.CV" in label else label[0]
            pdf_url = pdf_match.group(1)
            pdf_url = pdf_url.replace(' ', '%20') # fix for space
            title = RemoveTags(title_match.group(1))
            items.append({"url": "https://www.iaarc.org/publications/" + pdf_url, "label": "pdf", "title": title})

    return year, items


def GetArticalUrl(page_urls, output_dir):
    base_urls = page_urls if isinstance(page_urls, list) else [page_urls, ]

    for url in base_urls:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            year, pdf_links = GetPDFUrl(content)

            dir_name = os.path.join(output_dir, year)
            print("writing in {}, total papers: {}".format(dir_name, len(pdf_links)))
            SaveCSV(pdf_links, os.path.join(dir_name, "readme.csv"))
            Download(pdf_links, dir_name, True)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def ParseUrls():
    urls = []
    baseurl = "https://www.iaarc.org/publications/search.php?series=1&query=&publication=0"

    response = requests.get(baseurl)
    if response.status_code == 200:
        content = response.text
        urls = re.findall( r'<a\s+href="(/pub[^"]+)"', content)
        urls = ["https://www.iaarc.org" +  u.replace('&amp;', '&') for u in urls]

    return urls

def main():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    args = GetArgs()

    url_list = ParseUrls() if args.url == '' or args.url is None else [args.url, ]
    print("conference numbers: ", len(url_list))

    for url in url_list:
        GetArticalUrl(url, args.output_dir)


if __name__ == '__main__':
    main()
