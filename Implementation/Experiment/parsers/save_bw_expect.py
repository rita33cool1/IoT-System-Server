#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/05'

import os
import sys 

audio_saved_bw = 688 
yolo_saved_bw = 23

if __name__ == '__main__':
    in_file = sys.argv[1]
    outfile = sys.argv[2]
  
    save_bws = [] 
    with open(in_file, 'r') as rf:
       lines = rf.readlines()

    for line in lines:
        if 'num:' in line:
            apps_num = []
        if 'Edge: [' in line:
            apps = []
            sum_bw = 0 
            if "'" in line:
                line = line.strip().split(']', 1)[0][1:-1]
                if "', '" in line:
                    apps = line.split("', '")
                    for app in apps:
                        if 'audio' in app:
                            sum_bw += audio_saved_bw
                        elif 'yolo' in app:
                            sum_bw += yolo_saved_bw
                        else:
                            print('Cannot recognize: ' + app)
            save_bws.append(str(sum_bw))

    with open(outfile, 'w') as wf:
        for a in save_bws[:-2]:
            wf.write(a+' ')
        wf.write(save_bws[-2])
