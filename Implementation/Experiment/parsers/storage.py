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
    total_size = float(sys.argv[3])
  
    usages = [] 
    with open(in_file, 'r') as rf:
       lines = rf.readlines()

    for line in lines:
        if 'time: 0' in line:
            usages = []
        if 'Storage usage: ' in line:
            u = float(line.strip().split('Storage usage: ')[1]) / total_size * 100
            usages.append(str(u))

    print('length: ' + str(len(usages)))

    with open(outfile, 'w') as wf:
        for u in usages[:-1]:
            wf.write(u+' ')
        wf.write(usages[-1])
