#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys 

Overall = {}
Max_image_number = 20
Images = []

def read_yolo_qos_file(in_yolo_qos_file):
    with open(in_yolo_qos_file) as rf:
        parts = rf.read().split('========== Time: ')
    for part in parts[1:]:
        #print('part')
        #print(part)
        global Overall
        key, part = part.split(' ==========', 1)
        Overall[key] = {}
        #print('key')
        #print(key)
        ex_yolos = []
        if ', ' in part:
            yolos = part.strip().split('\n')
            #print('yolos')
            #print(yolos)
            for yolo in yolos:
                name, iid, result = yolo.split(', ')
                if name not in ex_yolos:
                    Overall[key][name] = {'accuracy': '', 'images':{iid:result}}
                    ex_yolos.append(name)
                    if iid not in Images:
                        Images.append(iid)
                        print(iid)
                elif len(Overall[key][name]['images'].keys()) < Max_image_number:
                    Overall[key][name]['images'][iid] = result
                    if iid not in Images:
                        Images.append(iid)
                        print(iid)


if __name__ == '__main__':
    in_yolo_qos_file = sys.argv[1]
   
    # Read Yolo QoS files
    read_yolo_qos_file(in_yolo_qos_file)

    # Debug
    #print('Overall')
    #for time in range(len(Overall.keys())):
    #    print("'"+str(time)+"':")
    #    print(Overall[str(time)]) 
