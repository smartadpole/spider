#!/usr/bin/python3
# encoding: utf-8
'''
@author: sunhao
@contact: smartadpole@163.com
@file: __init__.py.py
@time: 2025/7/18 10:40
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
