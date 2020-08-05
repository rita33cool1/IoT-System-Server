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
        if 'num:' in line:
            usages = []
        if 'Exec Time:  ' in line:
            usages.append(str(float(line.strip().split('Exec Time:  ')[1])*1000))
        times = usages[:-1]

    with open(outfile, 'a') as wf:
        for u in times[:-1]:
            wf.write(u+' ')
        wf.write(times[-1])
