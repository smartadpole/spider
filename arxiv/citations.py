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

import requests
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


def GetArgs():
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--url", type=str, default="", help="")
    parser.add_argument("--output", type=str, default="", help="")

    args = parser.parse_args()
    return args

def setup_driver(chrome_driver_path):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 无头模式，不打开浏览器窗口
    return webdriver.Chrome(service=Service(chrome_driver_path), options=options)

def extract_citations(soup):
    results = []
    citations_div = soup.find('div', id='col-citations')
    if citations_div:
        citations = citations_div.find_all('div', class_='bib-paper')
        for citation in citations:
            title_tag = citation.find('a', class_='notinfluential mathjax')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                if not link.startswith('http'):
                    link = 'https://www.semanticscholar.org' + link
                results.append({'title': title, 'link': link})
    return results

def click_slider_and_collect_citations(driver):
    wait = WebDriverWait(driver, 10)
    bibex_toggle_div = wait.until(EC.presence_of_element_located((By.ID, 'bibex-toggle')))
    slider_parent = bibex_toggle_div.find_element(By.XPATH, '../../..')
    slider_button = slider_parent.find_element(By.CLASS_NAME, 'slider')
    slider_button.click()
    wait.until(EC.presence_of_element_located((By.ID, 'col-citations')))

    results = []

    while True:
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        results.extend(extract_citations(soup))

        # 检查是否有下一页按钮
        try:
            next_button = driver.find_element(By.XPATH, '//a[contains(@title, "Page") and contains(text(), "▶")]')
            if "disabled" in next_button.get_attribute("class"):
                break
            else:
                next_button.click()
                time.sleep(2)  # 等待新页面加载
        except:
            break

    return results

def main():
    args = GetArgs()

    # 设置Chrome浏览器驱动路径
    chrome_driver_path = '/home/hao/Software/chromedriver-126/chromedriver'  # 请根据实际情况修改

    citations = []
    try:
        driver = setup_driver(chrome_driver_path)
        driver.get(args.url)
        citations = click_slider_and_collect_citations(driver)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    if not citations:
        print("No citations found.")
    else:
        for result in citations:
            print(f"Title: {result['title']}\nLink: {result['link']}\n")




if __name__ == '__main__':
    main()
