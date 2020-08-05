#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

input_file = sys.argv[1]
with open(input_file, 'r') as in_f:
    parts = in_f.read().split('\ntime: ')

apps = []
cloud_apps = []
for i in range(1, len(parts)):
    #print('i: ' + str(i))
    time = parts[i].split('\n', 1)[0]
    #cloud_str = parts[i].split("Pods in cloud:  [", 1)[1]
    #print(cloud_str)
    if parts[i].split("Pods in cloud:  [", 1)[1][0] == ']':
        cloud_str = ''
    else:
        cloud_str = parts[i].split("Pods in cloud:  [", 1)[1].split("]", 1)[0]
    if cloud_str == '':
        apps.append(0)
    else:
        cloud_str = cloud_str[1:-1]
        #cloud_apps = cloud_str.split("', '")[:-1]
        cloud_apps = cloud_str.split("', '")
        if cloud_apps[0] == 'NAME': del cloud_apps[0]
        apps.append(len(cloud_apps))

#print('[', end = '')
for i in range(len(apps)):
    if i != len(apps)-1:
        print(str(apps[i])+' ', end = '')
    #if i != len(apps)-1:
    #    print(' ', end = '')    
    #if i != len(apps)-1 and i%5 == 4:
    #    print(' ', end = '')
    #elif i != len(apps)-1 and i%10 == 9:
    #    print(' ', end = '')
print(str(apps[i]))
#print('];')
