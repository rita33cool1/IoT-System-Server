#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

audio_saved_bw = 688
yolo_saved_bw = 23

input_file = sys.argv[1]
with open(input_file, 'r') as in_f:
    parts = in_f.read().split('\ntime: ')

apps = []
edge_apps = []
old_edge_apps = []
for i in range(1, len(parts)):
    #print(parts[i])
    time = parts[i].split('\n', 1)[0]
    #print(parts[i])
    #edge_str = parts[i].split("Pods in edge:  [", 1)[1]
    #print(edge_str)
    if parts[i].split("Pods in edge:  [", 1)[1][0] == ']':
        edge_str = ''
    else:
        edge_str = parts[i].split("Pods in edge:  [", 1)[1].split("]", 1)[0]
    if edge_str == '':
        apps.append(0)
        old_edge_apps = []
    else:
        old_edge_apps = edge_apps
        edge_str = edge_str[1:-1]
        #edge_apps = edge_str.split("', '")[:-1]
        edge_apps = edge_str.split("', '")
        new_apps = [app for app in edge_apps if app not in old_edge_apps]
        sum_bw = 0
        for app in new_apps:
            if 'audio' in app:
                sum_bw += audio_saved_bw
            elif 'yolo' in app:
                sum_bw += yolo_saved_bw
            else:
                print(f'Cannot recognize: {app}')
        apps.append(sum_bw)

for i in range(len(apps)):
    if i != len(apps)-1:
        print(str(apps[i])+' ', end = '')
print(str(apps[i]))
