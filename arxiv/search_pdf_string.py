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
import csv
import io
import datetime

ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 200
SERCH_TYPE = 'title'  # all
COMMENTS = ['cvpr', 'iccv', 'iclr']
INVALID = False

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--query", type=str, nargs='+', help="List of keywords to search for")
    parse.add_argument("--output_dir", type=str, default="./file")
    parse.add_argument("--min_id", type=str, help="Minimum ID to download", default="")
    parse.add_argument("--blocked_keywords", type=str, nargs='*', help="List of keywords to block", default=[])
    parse.add_argument("--label", type=str, help="Filter label", default="")

    return parse.parse_args()

def RemoveTags(text):
    # 匹配尖括号内的内容
    pattern = r'<.*?>'
    # 使用 sub 函数替换匹配到的内容为空字符串
    return re.sub(pattern, '', text)

def GetPDFUrl(content, min_id):
    global INVALID
    items = []

    if INVALID:
        return items

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

            if "" != min_id:
                pdf_id = pdf_url.split('/')[-1]
                if pdf_id == min_id:
                    INVALID = True
                    return items

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

    return urls

def GetArticalUrl(page_urls, min_id):
    global INVALID
    urls = []

    base_urls = page_urls if isinstance(page_urls, list) else [page_urls, ]

    for url in base_urls:
        if INVALID:
            return urls
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            print("loading papers info from {}".format(url))
            pdf_links = GetPDFUrl(content, min_id)
            urls.extend(pdf_links)
        time.sleep(1)

    return urls


def ParseArXiv(keywords, min_id, blocked_keywords):
    all_urls = []
    for key in keywords:
        if key.split()[0].lower() in COMMENTS:
            baseurl = "https://arxiv.org/search/?query={}&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(key, "comments", ITEMS_NUM)
        else:
            if '+' in key:
                baseurl = "https://arxiv.org/search/?query={}&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(key, SERCH_TYPE, ITEMS_NUM)
            else:
                baseurl = "https://arxiv.org/search/?query=\"{}\"&searchtype={}&abstracts=show&order=-announced_date_first&size={}".format(key, SERCH_TYPE, ITEMS_NUM)
        response = requests.get(baseurl)
        if response.status_code == 200:
            content = response.text
            page_urls = GetPages(baseurl, content)
            urls = GetArticalUrl(page_urls, min_id)
            # Filter out items containing blocked keywords
            if len(blocked_keywords) == 0:
                all_urls.extend(urls)
                continue
            blocked_count = len([url for url in urls if any(blocked_keyword in url['title'] for blocked_keyword in blocked_keywords)])
            print(f"Blocked {blocked_count} records containing blocked keywords.")
            urls = [url for url in urls if not any(blocked_keyword in url['title'] for blocked_keyword in blocked_keywords)]
            all_urls.extend(urls)
        else:
            print("Response URL:", response.url)
            print("Response Status Code:", response.status_code)
            print("Response Reason:", response.reason)
            print("Response Elapsed Time:", response.elapsed)

    return all_urls

def Download(items, output: str, filter_label, usetitle=False):
    os.makedirs(output, exist_ok=True)

    if filter_label == "":
        filtered_items = items
    else:
        filter_label = filter_label if '.' in filter_label else f'{filter_label}.'
        filter_label = filter_label.lower()
        filtered_items = [item for item in items if item['label'].lower().startswith(filter_label)]
        filtered_count = len(items) - len(filtered_items)
        print(f"Filtered out {filtered_count} records not containing the label '{filter_label}'.")

    for item in tqdm(filtered_items):
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
    MkdirSimple(file)
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    for item in items:
        cleaned_values = [value.strip().replace('\n', ' ').replace('\r', ' ') for value in item.values()]
        writer.writerow(cleaned_values)

    text = output.getvalue().strip()
    WriteTxt(text, file, 'w')

def main():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    args = GetArgs()
    output_file = os.path.join(args.output_dir, "readme.csv")

    if args.min_id != "":
        date = datetime.date.today().strftime("%Y-%m-%d")
        output_file = os.path.join(args.output_dir, "readme_{}.csv".format(date))

    items = ParseArXiv(args.query, args.min_id, args.blocked_keywords)
    print("total papers: ", len(items))

    SaveCSV(items, output_file)
    Download(items, args.output_dir, args.label, False)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

if __name__ == "__main__":
    main()
