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

import time
import argparse
import os
import re
from util.file import WriteTxt, MkdirSimple
import socket
import markdown2
from weasyprint import HTML
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

ONLY_NEW = True

NUM_FILE = "paper_number.csv"
ITEMS_NUM = 200
SERCH_TYPE = 'title'  # all
COMMENTS = ['cvpr', 'iccv', 'iclr']
INVALID = False
artical_id = 0
page_id = 0
page_count = 0

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--url", type=str)
    parse.add_argument("--output_dir", type=str, default="./file")
    parse.add_argument("--type", type=str, choices=['pdf', 'markdown'], default="pdf")

    return parse.parse_args()

def get_page_content(url):
    """Get the content of the page."""
    attempt = 0
    retries = 5
    delay = 2
    while attempt < retries:
        try:
            response = requests.get(url, verify=False, timeout=60)
            response.raise_for_status()  # 如果响应状态码不是 200，抛出异常
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < retries:
                time.sleep(delay)  # 等待一段时间后重试
            else:
                print("Max retries exceeded. Could not fetch the content.")
                raise  # 重试次数用尽后，抛出最后的异常

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

def clean_html(soup, base_url):
    # 提取目标 div 中的内容
    target = soup.find('div', class_='b_con')
    if not target:
        target = soup

    return target

def convert_html_to_markdown(soup, page_url, output_dir, output_dir_img):
    """Convert HTML content to Markdown format, preserving original whitespace and indentation."""
    markdown_content = []
    target_div = clean_html(soup, page_url)

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

    return final_content

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
    html_header = f'<h{header_level} style="text-align:center">{subtitle}</h{header_level}><hr style="border: 1px solid #eeeeee" width="">'

    return html_header

def convert_html_to_absolute_links(content, base_url):
    """Convert all relative links in HTML content to absolute links."""
    if isinstance(content, str):
        content = BeautifulSoup(content, 'html.parser')

    # Convert all <a> tags' href attributes
    for a_tag in content.find_all('a', href=True):
        a_tag['href'] = urljoin(base_url, a_tag['href'])

    # Convert all <img> tags' src attributes
    for img_tag in content.find_all('img', src=True):
        img_tag['src'] = urljoin(base_url, img_tag['src'])

        # Set max width for images
        img_tag['style'] = "max-width: 100%; height: auto;"

    return str(content)

def save_html_as_pdf(html_content, output_pdf_path):
    """Convert HTML content to PDF and save it."""
    def custom_url_fetcher(url, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                return {
                    'string': response.content,
                    'mime_type': response.headers['Content-Type'],
                }
            except requests.exceptions.RequestException as e:
                attempt += 1
                print(f"Attempt {attempt} failed: {e}")
                if attempt >= retries:
                    raise

    HTML(string=html_content, url_fetcher=custom_url_fetcher).write_pdf(output_pdf_path)

    try:
        # 尝试生成 PDF
        HTML(string=html_content, url_fetcher=custom_url_fetcher).write_pdf(output_pdf_path)

        html_filename = os.path.splitext(output_pdf_path)[0] + '.html'
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        # 如果出现异常，删除已生成的 PDF 文件（如果存在）
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)

def save(type, content, file):
    MkdirSimple(file)
    if 'pdf' == type:
        save_html_as_pdf(content, file)
    else:
        save_markdown(content, file)

def get_all_pagination_links(soup, base_url):
    """Extract all pagination links from the soup."""
    page_links = []
    pager_div = soup.find('div', class_='pager')
    if pager_div:
        links = pager_div.find_all('a', href=True)
        last_page_link = links[-1]['href']
        last_page_number = int(re.search(r'\d+', last_page_link).group())
        match = re.search(r'_(\d+)(\.\w+)$', last_page_link)
        if match:
            base_link = last_page_link[:match.start(1)]
            suffix = match.group(2)
            page_links = [(urljoin(base_url, f"{base_link}{i}{suffix}"), i) for i in range(1, last_page_number + 1)]

    return page_links

def get_filename(title, output_dir, type):
    title = title.replace('/', '_').replace(' ', '_')
    suffix = 'md' if 'markdown' == type else 'pdf'
    file = os.path.join(output_dir, f"{title}.{suffix}")

    return file

def parse_page(type, title, url, output_dir, output_dir_image):
    global artical_id, page_id, page_count

    if '' != title and os.path.exists(get_filename(title, output_dir, type)):
        print(f"ID:{artical_id} | Page {page_id}/{page_count} | parse {title} from url: {url} already exists.")
        artical_id += 1
        return False, ""

    """Parse the page and extract the nested content."""
    try:
        page_content = get_page_content(url)
    except:
        return False, ""
    soup = BeautifulSoup(page_content, 'html.parser')

    main_content = soup.find('div', class_='zjtj_list')
    if not main_content:
        print(f"Error: Failed to get main content from page {page_number}. URL: {url}")
        return

    title = extract_first_valid_text(main_content)
    file = get_filename(title, output_dir, type)

    has_toc = soup.find_all('a', class_='round_button')
    if not has_toc:
        print(f"ID:{artical_id} | Page {page_id}/{page_count} | parse {title} from url: {url}")
        artical_id += 1

    if 'pdf' == type:
        content = str(clean_html(main_content, url))
        content = convert_html_to_absolute_links(content, url)
    elif 'markdown' == type:
        content = convert_html_to_markdown(main_content, url, output_dir, output_dir_image)
    else:
        return False, ""

    if has_toc:
        if has_toc[0].text.replace(' ', '') == "目录":
            return has_toc, content

    # Recursively follow links to get the final content
    links = main_content.find_all('li')
    links = [li.find('a') for li in links if li.find('a')]
    page_content = ''

    for link in links:
        sub_output_dir = os.path.join(output_dir, title)
        sub_output_dir_image = os.path.join(output_dir_image, title)
        href = link.get('href')
        subtitle = link.text

        if href:
            full_url = urljoin(url, href)
            subpage, content = parse_page(type, subtitle, full_url, sub_output_dir, sub_output_dir_image)
            if subpage:
                if 'pdf' == type:
                    page_content += generate_html_header(subtitle)
                    page_content += content
                else:
                    # if subpage, convert the relative image path
                    content = content.replace('](../', '](')
                    page_content += '\n{}\n{}'.format(generate_markdown_header(subtitle), content)

    if len(page_content) > 0:
        save(type, page_content, file)

    return False, page_content

def parse_multi_page(type, url, output_dir, output_dir_image):
    global page_id, page_count
    page_content = get_page_content(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    page_links = get_all_pagination_links(soup, url)
    page_count = len(page_links)

    for page_link, page_id in page_links:
        parse_page(type, "", page_link, output_dir, output_dir_image)

def main():
    # 禁用 InsecureRequestWarning 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    args = GetArgs()

    socket.setdefaulttimeout(60)

    parse_multi_page(args.type, args.url, args.output_dir, os.path.join(args.output_dir, 'image'))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == "__main__":
    main()
