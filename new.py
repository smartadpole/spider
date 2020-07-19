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

SUBJECT = {
    "cs.CV": "CV",
    "cs.AI": "AI",
    "cs.SD": "Sound",
    "stat.ML": "ML_statistics",
    "cs.LG": "ML",
    "cs.CL": "NLP",
    "cs.PL": "Programming",
    "cs.DS": "DataStructure",
}

NUM_FILE = "paper_number.csv"

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--url", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")

    return parse.parse_args()

def GetPages(content):
    content_root = "/html/body/div['content']/div/"
    if ONLY_NEW:
        content_label = content_root + "dl[1]/"
    else:
        content_label = content_root + "dl/"

    ref = content_label + "dt/span/a[1]/@href"
    items = content.xpath(ref)
    urls = ["https://arxiv.org" + i for i in items]
    date = content.xpath(content_root + "div[1]/text()")[0].split(",")[-1]
    date = "20" + DateNum(date)

    return urls, date

def ParseArXiv(driver, key:str, output_dir:str):
    baseurl = "https://arxiv.org/list/{}/new".format(key)
    driver.get(baseurl)
    time.sleep(1)

    page_content = GetContent(driver)
    urls, date = GetPages(page_content)
    file = os.path.join(output_dir, SUBJECT[key], date + ".md")

    for page in tqdm(urls):
        txt = GetXmlContent(driver, page)
        WriteTxt(txt, file, "a")
    time.sleep(0.5)
    print("{:-^30}".format(SUBJECT[key] + " done"))

    return len(urls), date

def main():
    args = GetArgs()
    driver = webdriver.Chrome()

    try:
        items_num = []
        date = ""
        for key in SUBJECT.keys():
            num, date = ParseArXiv(driver, key, args.output_dir)
            items_num.append(num)
        print(date)
        file = os.path.join(args.output_dir, NUM_FILE)
        items_num = [str(i) for i in items_num]
        txt = "\n{},".format(date) + ",".join(items_num)
        WriteTxt(txt, file, "a")
        driver.close()
    except:
        driver.close()


if __name__ == "__main__":
    main()
