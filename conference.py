#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: conference.py
@time: 2023/1/28 下午3:54
@desc: 
'''
import sys, os

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../../'))

import argparse


def GetArgs():
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--type", type=str, default="CVPR", help="")
    parser.add_argument("--year", type=str, default="2022", help="")
    parser.add_argument("--output", type=str, default="./", help="")

    args = parser.parse_args()
    return args


# coding:utf-8
import re
import requests
import urllib
import os
import threading
import pdb
import os


def getIJCAIPapers(ctype, year, minnum, maxnum):
    url = 'https://www.ijcai.org/proceedings/2018/%04d.pdf'
    # maxnum = 870
    localDir = 'E:\\' + ctype + year + '\\'
    for i in range(minnum, maxnum + 1):
        urlpath = url % (i)
        file_path = localDir + '%04d.pdf' % (i)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        print('[' + str(i) + '/' + str(maxnum) + "]  Downloading -> " + file_path)
        try:
            urllib.request.urlretrieve(urlpath, file_path)
        except Exception as err:
            print(urlpath, ' error :', err)
            continue
    print("all download finished")


def get_CVPR_ICCV_Papers(ctype, year, output):
    # get web context
    baseurl = 'http://openaccess.thecvf.com/' + ctype + year + '?day=all'
    r = requests.get(baseurl)
    data = r.text
    # find all pdf links
    link_list = re.findall(r"(?<=href=\").+?pdf(?=\">pdf)|(?<=href=\').+?pdf(?=\">pdf)", data)
    name_list = re.findall(r"(?<=href=\").+?'+year+'_paper.html\">.+?</a>", data)
    cnt = 98
    num = len(link_list)
    # your local path to download pdf files
    localDir = os.path.join(output, ctype, year)
    if not os.path.exists(localDir):
        os.makedirs(localDir)

    err_cnt = 0
    while cnt < num:
        url = link_list[cnt]
        # seperate file name from url links
        file_name = link_list[cnt].split('/')[-1]
        # 以下是解析文件名即文章名称的部分，不想搞这命名工程了，所以直接没用了
        # to avoid some illegal punctuation in file name
        # file_name = file_name.replace(':','_')
        # file_name = file_name.replace('\"','_')
        # file_name = file_name.replace('?','_')
        # file_name = file_name.replace('/','_')
        file_path = os.path.join(localDir, file_name)
        # download pdf files
        print('[' + str(cnt) + '/' + str(num) + "]  Downloading -> " + file_path)
        try:
            urllib.request.urlretrieve('http://openaccess.thecvf.com/' + url, file_path)
            err_cnt = 0
        except Exception as err:
            print(err)
            err_cnt += 1
            if err_cnt < 3:
                continue
        cnt = cnt + 1
    print("all download finished")


if __name__ == '__main__':
    args = GetArgs()

    ctype = args.type  # 修改成对应的会议类型（限：ICCV,CVPR,IJCAI，其余的需要自己修改网站链接）
    year = args.year  # 论文发表的年份
    # 注意这里由于ICCV,CVPR下载很快，所以没有加入多线程机制，如果有需要可以参考IJCAI的下载方法

    if ctype.lower() == 'cvpr' or ctype.lower() == 'iccv':
        get_CVPR_ICCV_Papers(ctype,year, args.output)
    else:
        threads = []
        t1 = threading.Thread(target=getIJCAIPapers, args=(1, 400,))
        threads.append(t1)
        t2 = threading.Thread(target=getIJCAIPapers, args=(401, 870,))
        threads.append(t2)
        for t in threads:
            t.start()
