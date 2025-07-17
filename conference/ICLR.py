# coding:utf-8
import re
import requests
import urllib
import os
import threading
import pdb
import os
from lxml import etree


def down_paper(link_list, output):
    # todo : what
    # name_list = re.findall(r"(?<=href=\").+?'+year+'_paper.html\">.+?</a>", data)
    #

    if len(link_list) == 0:
        return False

    cnt = 0
    num = len(link_list)

    err_cnt = 0
    while cnt < num:
        url = link_list[cnt]
        # file_name = link_list[cnt].split('/')[-1] + '.pdf'
        name = str(url).split('=')[-1]
        file_name = name + '.pdf'

        file_path = os.path.join(output, file_name)
        # url_link = str(url).split('"')[-1]
        # download pdf files
        print('[' + str(cnt) + '/' + str(num) + "]  Downloading -> " + file_path)

        try:
            print("https://openreview.net/pdf/" + url + '.pdf')
            urllib.request.urlretrieve("https://openreview.net/pdf" + url, file_path)
            print(url + '.pdf')
            err_cnt = 0
        except Exception as err:
            print(err)
            err_cnt += 1
            if err_cnt < 3:
                continue
        cnt = cnt + 1
    print("all download finished")

    return True


def get_CVPR_ICCV_Papers(output):
    # get web context
    # baseurl = 'https://openreview.net/group?id=ICLR.cc/2022/Conference#oral-submissions/'
    # # print('baseurl', baseurl)
    # r = requests.get(baseurl)
    # data = r.text
    data = open('html.txt', 'r').read()
    # print(txt)
    # print(data)
    # https://proceedings.mlr.press/v162/abbas22b.html">abs</a>][<a href="https://proceedings.mlr.press/v162/abbas22b/abbas22b
    link_list = re.findall(r"(?<=href=\"/pdf).+?(?=\" class=\"pdf-link)", data)
    # link_list = re.findall("pdf", data)
    print(link_list)
    # name_list = re.findall(r"(?<=<span class=\"descriptor\">Title:</span>).+?(?=\n)", data)

    # href = "/pdf?id=FPCMqjI0jXN"

    # class ="pdf-link" title="Download PDF" target="_blank" > < img src="/images/pdf_icon_blue.svg" > < / a >
    down_paper(link_list, output)


if __name__ == '__main__':
    output = '/data/WorkMind/data/datum/ICLR'
    # https://openreview.net/pdf?id=FPCMqjI0jXN
    get_CVPR_ICCV_Papers(output)
