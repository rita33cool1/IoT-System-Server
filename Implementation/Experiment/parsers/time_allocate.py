#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/05'

import os
import sys 

if __name__ == '__main__':
    in_file = sys.argv[1]
    outfile = sys.argv[2]
  
    usages = [] 
    with open(in_file, 'r') as rf:
       lines = rf.readlines()

    for line in lines:
        if '**time: 0' in line:
            usages = []
        if 'time: ' in line and '**time' not in line:
            usages.append(str(float(line.strip().split('time: ')[1])*1000))

    with open(outfile, 'a') as wf:
        for u in usages[:-1]:
            wf.write(u+' ')
        wf.write(usages[-1])
