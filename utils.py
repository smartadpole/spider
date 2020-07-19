#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: utils.py
@time: 2019/12/23 下午2:38
@desc: 
'''
import sys, os

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, './'))

def MakeDirs(dir:str):
    if not os.path.exists(dir):
        os.makedirs(dir)


def WriteTxt(txt:str, file:str, mode="w"):
    MakeDirs(os.path.dirname(file))
    with open(file, mode) as f:
        f.write(txt)