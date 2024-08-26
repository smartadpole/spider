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
import markdown2
from weasyprint import HTML, CSS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 200
SERCH_TYPE = 'title'  # all
COMMENTS = ['cvpr', 'iccv', 'iclr']
INVALID = False
PAGE_COUNT = 0

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

    # markdown_to_pdf(content, filename.replace('.md', '.pdf'))

def save_image(image_url, save_path):
    try:
        response = requests.get(image_url, verify=False)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
    except requests.exceptions.SSLError as e:
        print(f"SSL: Error downloading {image_url}: {e} path: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {image_url}: {e} path: {save_path}")


def extract_first_valid_text(soup):
    """Extract the first valid non-empty text from the HTML soup."""
    for element in soup.stripped_strings:
        return element  # 返回第一个有效字符串
    return "Untitled"  # 如果没有有效字符串，使用默认标题

def markdown_to_pdf(markdown_string, output_pdf_path):
    html_content = markdown2.markdown(markdown_string, extras=["break-on-newline"])
    html_content = html_content.replace('src="', f'src="{os.path.dirname(output_pdf_path)}/')
    HTML(string=html_content).write_pdf(output_pdf_path)

def convert_html_to_markdown(soup, page_url, output_dir, output_dir_img):
    """Convert HTML content to Markdown format, preserving original whitespace and indentation."""
    markdown_content = []
    html_content = ""

    # 提取目标 div 中的内容
    target_div = soup.find('div', class_='b_con')
    if not target_div:
        target_div = soup


    # 提前提取标题
    title = extract_first_valid_text(target_div)
    html_content += str(target_div)

    def clean_content(content):
        content = re.sub(r'[ \t]+', ' ', content)  # 替换空格和制表符为单个空格
        return content

    def process_element(element):
        """Recursive function to process HTML elements into Markdown, preserving whitespace."""
        if isinstance(element, str):
            return clean_content(element)
        elif element.name == 'br':
            return '\n'
        elif element.name == 'div':
            inner_content = ''.join(process_element(e) for e in element.contents)
            return f"\n{inner_content}\n"  # 在 </div> 结束时加换行
        elif element.name in ['p', 'span', 'sup', 'sub']:
            # 处理 p, span, sup, sub 标签，不换行处理
            content = clean_content(''.join(process_element(e) for e in element.contents))
            if element.name == 'sup':
                return f"^{content}^"  # 上标的 Markdown 语法
            elif element.name == 'sub':
                return f"~{content}~"  # 下标的 Markdown 语法
            else:
                return content
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:  # 确保处理的只是合法的标题标签
            level = element.name[1]  # h1 -> 1, h2 -> 2, etc.
            return f"{'#' * int(level)} {clean_content(element.get_text().strip())}\n"
        elif element.name == 'img':
            img_url = element.get('src')
            if img_url:
                full_img_url = urljoin(page_url, img_url)
                img_name = os.path.basename(urlparse(full_img_url).path)
                img_save_path = os.path.join(output_dir_img, img_name)
                MkdirSimple(img_save_path)
                save_image(full_img_url, img_save_path)

                # 生成相对路径
                relative_img_path = os.path.relpath(img_save_path, start=output_dir)
                return f"![{element.get('alt', '')}]({relative_img_path})"
            else:
                return ''
        elif element.name == 'a':
            link_text = clean_content(''.join(process_element(e) for e in element.contents))
            link_url = urljoin(page_url, element.get('href'))
            return f"[{link_text}]({link_url})"
        elif element.name == 'li':
            return f"* {clean_content(''.join(process_element(e) for e in element.contents))}\n"
        elif element.name == 'ul':
            return '\n'.join(f"* {process_element(li)}" for li in element.find_all('li')) + '\n'
        elif element.name == 'ol':
            return '\n'.join(f"{i+1}. {process_element(li)}" for i, li in enumerate(element.find_all('li'))) + '\n'
        else:
            return clean_content(''.join(process_element(e) for e in element.contents))

    for element in target_div.children:
        content = process_element(element)
        markdown_content.append(content)

    # 合并连续的换行符并保留单个换行符
    final_content = '\n'.join(line for line in ''.join(markdown_content).splitlines() if line.strip())

    return title, final_content, html_content

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

def generate_markdown_header(subtitle):
    """Generate a markdown header based on the number of dots in the subtitle."""

    dot_count = subtitle.count('.')
    header_level = '#' * (dot_count + 1)

    # 生成最终的 Markdown 标题
    return f"{header_level} {subtitle}"

def generate_html_header(subtitle):
    header_level = subtitle.count('.') + 1
    html_header = f'<div style="margin-bottom:40px;"><h{header_level} style="text-align:center;>{subtitle}</h{header_level}><hr style="border: 1px solid #eeeeee" width=""></div>'

    return html_header

def convert_html_to_absolute_links(html_content, base_url):
    """Convert all relative links in HTML content to absolute links."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Convert all <a> tags' href attributes
    for a_tag in soup.find_all('a', href=True):
        a_tag['href'] = urljoin(base_url, a_tag['href'])

    # Convert all <img> tags' src attributes
    for img_tag in soup.find_all('img', src=True):
        img_tag['src'] = urljoin(base_url, img_tag['src'])

        # Set max width for images
        img_tag['style'] = "max-width: 100%; height: auto;"

    return str(soup)

def save_html_as_pdf(html_content, output_pdf_path, base_url):
    """Convert HTML content to PDF and save it."""
    html_content_with_absolute_links = convert_html_to_absolute_links(html_content, base_url)
    HTML(string=html_content_with_absolute_links, base_url=base_url).write_pdf(output_pdf_path)

    html_filename = os.path.splitext(output_pdf_path)[0] + '.html'
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def parse_page(url, output_dir, output_dir_image):
    global PAGE_COUNT
    """Parse the page and extract the nested content."""
    content = get_page_content(url)
    soup = BeautifulSoup(content, 'html.parser')
    main_content = soup.find('div', class_='zjtj_list')
    if not main_content:
        print("error get main content.")
        return

    title, markdown_content, html_content = convert_html_to_markdown(main_content, url, output_dir, output_dir_image)
    title = title.replace('/', '_').replace(' ', '_')

    global flag
    if '600问' in title:
        flag = True

    has_toc = soup.find_all('a', class_='round_button')
    if has_toc:
        if has_toc[0].text.replace(' ', '') == "目录":
            return has_toc, markdown_content, html_content
    else:
        print(f"ID:{PAGE_COUNT} | parse {title} from url: {url}")
        PAGE_COUNT += 1

# Save the Markdown content
    markdown_filename = os.path.join(output_dir, f"{title}_TOC.md")
    MkdirSimple(markdown_filename)
    save_markdown(''.join(markdown_content), markdown_filename)
    save_html_as_pdf(html_content, markdown_filename.replace('.md',".pdf"), url)

    # Recursively follow links to get the final content
    links = main_content.find_all('li')
    links = [li.find('a') for li in links if li.find('a')]
    page_content = []
    page_html = ""

    for link in links:
        sub_output_dir = os.path.join(output_dir, title)
        sub_output_dir_image = os.path.join(output_dir_image, title)
        href = link.get('href')
        subtitle = link.text
        if href:
            full_url = urljoin(url, href)
            subpage, content, html_content = parse_page(full_url, sub_output_dir, sub_output_dir_image)
            if subpage:
                page_content.append(generate_markdown_header(subtitle))
                # if subpage, convert the relative image path
                content = content.replace('](../', '](')
                page_content.append(''.join(content))
                page_html += generate_html_header(subtitle)
                page_html += html_content

    if len(page_content) > 0:
        markdown_filename = os.path.join(output_dir, f"{title}.md")
        MkdirSimple(markdown_filename)
        save_markdown('\n'.join(page_content), markdown_filename)
        save_html_as_pdf(page_html, markdown_filename.replace('.md',".pdf"), url)

    return False, page_content, page_html

def main():
    # 禁用 InsecureRequestWarning 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    args = GetArgs()
    output_file = os.path.join(args.output_dir, "readme.csv")

    items = parse_page(args.url, args.output_dir, os.path.join(args.output_dir, 'image'))
    print("total papers: ", len(items))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == "__main__":
    main()
