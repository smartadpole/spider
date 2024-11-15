#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: blog.py
@time: 2024/9/19 17:56
@desc: 
'''
import sys, os

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../../'))

import argparse


def GetArgs():
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--", type=str, default="", help="")
    parser.add_argument("--", type=str, default="", help="")

    args = parser.parse_args()
    return args


def main():
    args = GetArgs()


if __name__ == '__main__':
    main()
