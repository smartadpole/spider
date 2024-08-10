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
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 200
SERCH_TYPE = 'title'  # all
COMMENTS = ['cvpr', 'iccv', 'iclr']
INVALID = False

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--url", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")

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


def ParseArXiv(key, min_id):
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

        return urls
    else:
        print("Response URL:", response.url)
        print("Response Status Code:", response.status_code)
        print("Response Reason:", response.reason)
        print("Response Elapsed Time:", response.elapsed)

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
    MkdirSimple(file)
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    for item in items:
        cleaned_values = [value.strip().replace('\n', ' ').replace('\r', ' ') for value in item.values()]
        writer.writerow(cleaned_values)

    text = output.getvalue().strip()
    WriteTxt(text, file, 'w')


def get_page_content(url):
    """Get the content of the page."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def save_markdown(content, filename):
    """Save Markdown content to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def save_image(image_url, save_path):
    try:
        response = requests.get(image_url, verify=False)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
    except requests.exceptions.SSLError as e:
        print(f"SSL Error: {e}")

def convert_html_to_markdown(soup, page_url, output_dir):
    """Convert HTML content to Markdown format."""
    markdown_content = []

    for element in soup.descendants:
        if isinstance(element, str):
            markdown_content.append(element.strip())
        elif element.name == 'p':
            markdown_content.append(f"\n\n{element.get_text().strip()}\n")
        elif element.name == 'h1':
            markdown_content.append(f"# {element.get_text().strip()}\n")
        elif element.name == 'h2':
            markdown_content.append(f"## {element.get_text().strip()}\n")
        elif element.name == 'h3':
            markdown_content.append(f"### {element.get_text().strip()}\n")
        elif element.name == 'h4':
            markdown_content.append(f"#### {element.get_text().strip()}\n")
        elif element.name == 'h5':
            markdown_content.append(f"##### {element.get_text().strip()}\n")
        elif element.name == 'h6':
            markdown_content.append(f"###### {element.get_text().strip()}\n")
        elif element.name == 'img':
            img_url = element.get('src')
            if img_url:
                full_img_url = urljoin(page_url, img_url)
                img_name = os.path.basename(urlparse(full_img_url).path)
                img_save_path = os.path.join(output_dir, img_name)
                MkdirSimple(img_save_path)
                save_image(full_img_url, img_save_path)
                markdown_content.append(f"![{element.get('alt', '')}]({img_name})")
        elif element.name == 'a':
            link_text = element.get_text().strip()
            link_url = urljoin(page_url, element.get('href'))
            markdown_content.append(f"[{link_text}]({link_url})")

    return ''.join(markdown_content)


def GetArticlesUrl(soup):
    items = []
    # 查找zjtj_list类下的ul中的所有li
    zjtj_list = soup.find('div', class_='zjtj_list')
    ul = zjtj_list.find('ul')
    li_elements = ul.find_all('li')

    # 遍历所有li元素，提取主题和链接
    for li in li_elements:
        # 获取主题文本
        theme = li.get_text(strip=True)

        # 获取链接，假设链接在a标签的href属性中
        a_tag = li.find('a')
        link = a_tag['href'] if a_tag else None

        items.append({'title':theme, 'url':link})

    return items

def parse_page(url, output_dir, depth=0):
    output_dir = os.path.join(output_dir, 'depth_{}'.format(depth))
    """Parse the page and extract the nested content."""
    content = get_page_content(url)
    soup = BeautifulSoup(content, 'html.parser')
    main_content = soup.find('div', class_='zjtj_list')
    if not main_content:
        print("error get main content.")
        return
    markdown_content = convert_html_to_markdown(main_content, url, output_dir)

    has_toc = soup.find_all('a', class_='round_button')
    if has_toc:
        if has_toc[0].text.replace(' ', '') == "目录":
            return has_toc, markdown_content

    # Save the Markdown content
    markdown_filename = os.path.join(output_dir, f"page_{depth}_main.md")
    MkdirSimple(markdown_filename)
    save_markdown(markdown_content, markdown_filename)

    # Recursively follow links to get the final content
    links = main_content.find_all('li')
    links = [li.find('a') for li in links if li.find('a')]
    page_content = []
    for link in tqdm(links):
        href = link.get('href')
        if href:
            full_url = urljoin(url, href)
            subpage, content = parse_page(full_url, output_dir, depth + 1)
            if subpage:
                page_content.append(content)

    if len(page_content) > 0:
        markdown_filename = os.path.join(output_dir, f"page{depth}_content.md")
        MkdirSimple(markdown_filename)
        save_markdown('\n'.join(page_content), markdown_filename)

    return False, markdown_content

def main():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    args = GetArgs()
    output_file = os.path.join(args.output_dir, "readme.csv")

    items = parse_page(args.url, args.output_dir, 0)
    print("total papers: ", len(items))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == "__main__":
    main()
