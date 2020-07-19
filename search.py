#_*_encoding:utf-8_*_
from tqdm import tqdm
from selenium import webdriver
import time
import argparse
import  sys, os
from  utils import WriteTxt
from arxiv import *

CHROME_DRIVER = "/media/hao/DS/OTHER/TOOLS"
sys.path.append("CHROME_DRIVER")

SEARCH = "image+retrieval"
ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 200

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--query", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")

    return parse.parse_args()

def GetPages(baseurl, content):
    content_root = "/html/body/main/div[1]/div/h1/text()"[0]

    total_num = 0
    items = range(0, total_num, 200)
    urls = ["{}&start={}".format(baseurl, ITEMS_NUM*i) + i for i in items]

    return urls

def ParseArXiv(driver, key, output_dir:str):
    baseurl = "https://arxiv.org/search/cs?query={}&searchtype=all&abstracts=show&order=-announced_date_first&size={}".format(key, ITEMS_NUM)
    driver.get(baseurl)
    time.sleep(1)

    page_content = GetContent(driver)
    urls = GetPages(page_content)
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

    try:
        items_num = []
        num, date = ParseArXiv(driver, args.query, args.output_dir)
        items_num.append(num)
        print(date)
        file = os.path.join(args.output_dir, NUM_FILE)
        items_num = [str(i) for i in items_num]
        txt = "{},".format(date) + ",".join(items_num)
        WriteTxt(txt, file, "a")
        driver.close()
    except:
        driver.close()


if __name__ == "__main__":
    main()
