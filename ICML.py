# coding:utf-8
import datetime
import re
import requests
import urllib
import os
import argparse

def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--type", choices=['ICML', 'all'], default="ICML")
    parse.add_argument("--output", type=str, default="paper")

    return parse.parse_args()

VOLUME = {"ICML": ["184","139","119","97","80","70","48","37","32","28","27"]
          , "ACML": ["189","157","129","101","95","77","63","45","39","29","25","20","13"]
          , "KDD": ["185","150","127","104","92","71","18","7"]
          }

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
        name = str(url).split('/')[-1]
        file_name = name + '.pdf'

        file_path = os.path.join(output, file_name)
        url_link = str(url).split('"')[-1]
        # download pdf files
        print('[' + str(cnt) + '/' + str(num) + "]  Downloading -> " + file_path)
        try:
            urllib.request.urlretrieve(url_link + '.pdf', file_path)
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


def GetPaper(baseurl, output):
    # get web context
    r = requests.get(baseurl)
    data = r.text
    # https://proceedings.mlr.press/v162/abbas22b.html">abs</a>][<a href="https://proceedings.mlr.press/v162/abbas22b/abbas22b
    link_list = re.findall(r"(?<=href=\").+?(?=.pdf\" target=\"_blank)", data)

    title = re.findall(r"(?<=<title>).*?(?=</title>)", data)
    name = re.findall(r"(?<=,)....", title)
    print(link_list[1])
    # name_list = re.findall(r"(?<=<span class=\"descriptor\">Title:</span>).+?(?=\n)", data)

    down_paper(link_list, output)


if __name__ == '__main__':
    arg = GetArgs()
    date = datetime.date.today().strftime("%Y-%m-%d")
    output = arg.output + "_" + date

    for id in VOLUME[arg.type]:
        url = "http://proceedings.mlr.press/v{}/".format(id)
        GetPaper(url, output)
