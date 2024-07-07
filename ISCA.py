#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: ISCA.py
@time: 2024/7/7 下午11:52
@desc: 
'''
import sys, os

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../../'))

import datetime
import re
import requests
import urllib
import os
import argparse
from util.file import MkdirSimple
from tqdm import tqdm
from bs4 import BeautifulSoup

FIRST_YEAR = 1987
LAST_YEAR = 2024

def GetArgs():
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--year", type=str, required=True, help="year of conference [2024, 2023, ...]")
    parser.add_argument("--output", type=str, default="", help="output dir name")

    args = parser.parse_args()
    return args



def down_paper(link_list, output):
    if len(link_list) == 0:
        return False

    cnt = 0
    num = len(link_list)
    progress_bar = tqdm(total=num, leave=False)

    err_cnt = 0
    while cnt < num:
        category, url, file_name = link_list[cnt]
        file = os.path.join(output, category, file_name)
        MkdirSimple(file)

        # download pdf files
        try:
            urllib.request.urlretrieve(url, file)
            err_cnt = 0
        except Exception as err:
            err_cnt += 1
            if err_cnt < 3:
                continue
            print(err, " ", url)
        cnt = cnt + 1
        progress_bar.update(1)

    progress_bar.close()

    return True


def GetPaper(baseurl, output, y):
    # get web context
    print("url: {}".format(baseurl))
    r = requests.get(baseurl)
    soup = BeautifulSoup(r.text, 'html.parser')

    link_list = []
    prefix = os.path.dirname(baseurl)

    for div in soup.find_all("div", class_="w3-card w3-round w3-white w3-padding"):
        category = div.find("h4", class_="w3-center").text.strip()
        for a in div.find_all("a", class_="w3-text"):
            paper_url = prefix + '/' + a['href'].replace('html', 'pdf')
            paper_title = a.find("p").text.strip().split("\n")[0]
            link_list.append((category, paper_url,  "{}_{}.pdf".format(paper_title, y)))

    if not link_list:
        print("No papers found.")
        return

    print(f"Found {len(link_list)} papers.")
    down_paper(link_list, output)


def main():
    arg = GetArgs()
    date = datetime.date.today().strftime("%Y-%m-%d")
    output = os.path.join("{}_{}".format(arg.output, date))

    baseurl = "https://www.isca-archive.org/"
    r = requests.get(baseurl)
    soup = BeautifulSoup(r.text, 'html.parser')
    container = soup.find("div", class_="w3-container w3-padding")
    links = container.find_all("a", class_="w3-text-blue w3-margin")
    years_link = {link.text: f"{baseurl}/{link['href']}" for link in links}

    if 'all' != arg.year:
        years_link = {arg.year: years_link[arg.year]}

    for year, url in years_link.items():
        GetPaper(url, output, year)



if __name__ == '__main__':
    main()
