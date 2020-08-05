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
  
    apps_num = [] 
    with open(in_file, 'r') as rf:
       lines = rf.readlines()

    for line in lines:
        if 'num:' in line:
            apps_num = []
        if 'Edge: [' in line:
            apps = []
            if "'" in line:
                line = line.strip().split(']', 1)[0][1:-1]
                if "', '" in line:
                    apps = line.split("', '")
            apps_num.append(str(len(apps)))

    with open(outfile, 'w') as wf:
        for a in apps_num[:-2]:
            wf.write(a+' ')
        wf.write(apps_num[-2])
