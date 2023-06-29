# coding:utf-8
import datetime
import re
import requests
import urllib
import os
import argparse
from util.file import MkdirSimple
from tqdm import tqdm


def GetArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument("--type", choices=['ICML', 'ACML', 'KDD'], default="ICML")
    parse.add_argument("--output", type=str, default="paper")

    return parse.parse_args()


VOLUME = {"ICML": ["184", "162", "139", "119", "97", "80", "70", "48", "37", "32", "28", "27"]
    , "ACML": ["189", "157", "129", "101", "95", "77", "63", "45", "39", "29", "25", "20", "13"]
    , "KDD": ["185", "150", "127", "104", "92", "71", "18", "7"]
          }


def down_paper(link_list, output):
    if len(link_list) == 0:
        return False

    cnt = 0
    num = len(link_list)
    progress_bar = tqdm(total=num, leave=False)

    err_cnt = 0
    while cnt < num:
        url = link_list[cnt]
        # file_name = link_list[cnt].split('/')[-1] + '.pdf'
        name = str(url).split('/')[-1]
        file_name = name + '.pdf'

        file = os.path.join(output, file_name)
        MkdirSimple(file)
        url_link = str(url).split('"')[-1]
        # download pdf files
        try:
            urllib.request.urlretrieve(url_link + '.pdf', file)
            err_cnt = 0
        except Exception as err:
            err_cnt += 1
            if err_cnt < 3:
                continue
            print(err, " ", url_link)
        cnt = cnt + 1
        progress_bar.update(1)

    progress_bar.close()

    return True


def GetPaper(baseurl, output):
    # get web context
    print("url: {}".format(baseurl))
    r = requests.get(baseurl)
    data = r.text
    # https://proceedings.mlr.press/v162/abbas22b.html">abs</a>][<a href="https://proceedings.mlr.press/v162/abbas22b/abbas22b
    link_list = re.findall(r"(?<=href=\").+?(?=.pdf\" target=\"_blank)", data)

    title = re.findall(r"(?<=<title>).*?(?=</title>)", data)[0]
    year = re.findall(r"\b\d{4}\b", title)
    # name = re.findall(r"\b[A-Z]{2}\w{2}.\d{4}\b", title)
    output = output + "_" + year[0]

    print("write to {}, count: {}".format(output, len(link_list)))
    down_paper(link_list, output)


if __name__ == '__main__':
    arg = GetArgs()
    date = datetime.date.today().strftime("%Y-%m-%d")

    for id in VOLUME[arg.type]:
        output = os.path.join("{}_{}_{}".format(arg.output, date, id), arg.type)
        url = "http://proceedings.mlr.press/v{}/".format(id)
        GetPaper(url, output)
