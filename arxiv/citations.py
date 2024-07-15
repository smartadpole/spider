#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: citations.py
@time: 2024/7/13 下午12:12
@desc:
'''
import sys, os

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../../'))

import argparse
from util.file import MkdirSimple
from tqdm import tqdm
import urllib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from arxiv.search_pdf_string import SaveCSV


TYPE = {
    'reference': 'col-references',
    'citation': 'col-citations'
}

def GetArgs():
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--url", type=str, help="arxiv article home page")
    parser.add_argument("--type", type=str, default="all", choices=['all', 'reference', 'citation'], help="paper list type")
    parser.add_argument("--driver", type=str, help="chrome driver path")
    parser.add_argument("--output", type=str, default="", help="")

    args = parser.parse_args()
    return args

def setup_driver(chrome_driver_path):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 无头模式，不打开浏览器窗口
    return webdriver.Chrome(service=Service(chrome_driver_path), options=options)

def extract_citations(soup, type):
    results = []
    citations_div = soup.find('div', id=type)
    if citations_div:
        citations = citations_div.find_all('div', class_='bib-paper')
        citations_links = citations_div.find_all('div', class_='bib-paper-links')
        for (citation, citations_link) in zip(citations, citations_links):
            title_tag = citation.find('a', class_='notinfluential mathjax')
            if title_tag:
                title = title_tag.text.strip()
                links = citations_link.find_all('a')
                link = None
                id = ""

                for l in links:
                    href = l.get('href')
                    if 'arxiv.org' in href:
                        id = href[22:]
                        link = href.replace('abs', 'pdf')
                        break
                if not link:
                    for l in links:
                        href = l.get('href')
                        if 'doi.org' in href:
                            link = href
                            id = link[16:]
                            break
                if not link:
                    for l in links:
                        href = l.get('href')
                        if href:
                            link = href
                            break
                results.append({'title': title, 'url': link, 'id': id})
    return results

def Download(items, output: str, usetitle=False):
    os.makedirs(output, exist_ok=True)

    for item in tqdm(items):
        try:
            url = item['url']
            if usetitle:
                name = item['title']
            else:
                name = os.path.basename(url)
            file_path = os.path.join(output, name + ".pdf")
            MkdirSimple(file_path)
            urllib.request.urlretrieve(url, file_path)
        except:
            print("error download {}.".format(item))

def click_slider_and_collect_citations(driver, type):
    wait = WebDriverWait(driver, 10)
    bibex_toggle_div = wait.until(EC.presence_of_element_located((By.ID, 'bibex-toggle')))
    slider_parent = bibex_toggle_div.find_element(By.XPATH, '../../..')
    slider_button = slider_parent.find_element(By.CLASS_NAME, 'slider')
    slider_button.click()
    wait.until(EC.presence_of_element_located((By.ID, type)))

    results = []

    while True:
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        results.extend(extract_citations(soup, type))

        # 查找引用部分的下一页按钮
        citations_div = driver.find_element(By.ID, type)
        try:
            next_button = citations_div.find_element(By.XPATH, './/a[contains(@title, "Page") and contains(text(), "▶")]')
            if "disabled" in next_button.get_attribute("class"):
                break
            else:
                next_button.click()
                time.sleep(2)  # 等待新页面加载
        except:
            break

    return results

def GetArticles(driver, url, type, output):
    citations = []
    try:
        driver = setup_driver(driver)
        driver.get(url)
        citations = click_slider_and_collect_citations(driver, type)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    if not citations:
        print("No citations found.")
    else:
        citations_sort = sorted(citations, key=lambda x: x['id'])
        SaveCSV(citations_sort, os.path.join(output, "readme.csv"))
        Download(citations_sort, output)
        # for result in citations:
        #     print(f"Title: {result['title']}\nLink: {result['link']}\n")


def main():
    args = GetArgs()

    if 'all' == args.type:
        GetArticles(args.driver, args.url, TYPE['reference'], os.path.join(args.output, 'reference'))
        GetArticles(args.driver, args.url, TYPE['citation'], os.path.join(args.output, 'citation'))
    else:
        type = TYPE[args.type]
        GetArticles(args.driver, args.url, type, args.output)

if __name__ == '__main__':
    main()
