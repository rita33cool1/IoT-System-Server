#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/02'

import os
import sys
import subprocess

read_file = sys.argv[1]
write_file = sys.argv[2]

content = ''
with open(read_file, 'r') as rf:
    content = rf.read()
    content = content.split('**time: 0')[-1]
    content = '0**time: 0' + content
parts = content.split('**time: ')
#print('parts:', parts)
number = -1
accuracys = []
for i in range(1, len(parts)):
    number += 1
    if '========Allocate Done=============' in parts[i]:
        accuracys.append(parts[i].split('Average accuracy: ', 1)[1].split('time:', 1)[0].strip())
    else:
        accuracys.append('0')
#print('accuracys:', accuracys)
if os.path.isfile(write_file):
    with open(write_file, 'w') as wf:
        wf.write('')
with open(write_file, 'a') as wf:
    for accuracy in accuracys:
        wf.write(format(str(round(float(accuracy), 3)), ' <5') + ' ')
