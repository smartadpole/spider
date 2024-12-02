#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: title.py
@time: 2024/12/2 10:53
@desc: 
'''
import sys, os
import argparse
from bs4 import BeautifulSoup

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../'))

def GetArgs():
    parser = argparse.ArgumentParser(description="Process a file name",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", type=str, required=True, help="Name of the file to process")

    args = parser.parse_args()
    return args

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    items = soup.find_all('li', id=lambda x: x and x.startswith('item_'))
    results = []
    for item in items:
        if item.find('h2') and not item.find('h1'):
            title = item.find('h2').text
        else:
            continue
        date_element = item.find('th', text='Date')
        date = date_element.find_next_sibling('td').text if date_element else ""
        date = date.strip()

        tags = item.find('ul', class_='tags').find_all('li')
        tags = [tag.text.strip('#')  for tag in tags if tag.text.strip('#') in {'CVPR', 'ICCV', 'ECCV', 'WACV', 'AAAI', 'ACCV', 'ICLR', 'ICML', 'ICRA', 'NIPS'}]
        results.append((title, date, tags))

        print(f"【】{title} ({', '.join(tags)}{f' {date}' if tags else date})")
    print("total items: ", len(results))
    return results

def main():
    args = GetArgs()
    file_path = args.file

    if not os.path.isfile(file_path):
        print(f"File {file_path} does not exist.")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    title = parse_html(html_content)


if __name__ == '__main__':
    main()