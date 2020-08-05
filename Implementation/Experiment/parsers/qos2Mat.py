#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys
import subprocess

def readAppFile(read_file):
    content = ''
    with open(read_file, 'r') as rf:
        content = rf.read()
    parts = content.split('**time: ')
    #print('parts:', parts)
    number = -1
    all_apps = {}
    for part in parts[1:]:
        number += 1
        apps = {}
        if '========Allocate Done=============' in part:
            #print('part', part)
            #part_1 = part.split('========Allocate Done=============\n', 1)[1]
            #print('part_1', part_1)
            #part_2 = part_1.split('\nSum of bandwidth:', 1)[0]
            #print('part_2', part_2)
            #lines = part.split('========Allocate Done=============\r\n', 1)[1].split('\r\nSum of bandwidth:', 1)[0]
            lines = part.split('========Allocate Done=============\n', 1)[1].split('\nSum of bandwidth:', 1)[0]
            #if '\r\n' in lines:
            if '\n' in lines:
                #lines = lines.split('\r\n')
                lines = lines.split('\n')
                for line in lines:
                    segs = line.split(' ')
                    if segs[0] not in apps.keys():
                        apps[segs[0]] = [float(segs[-1])]
                    else:
                        apps[segs[0]].append(float(segs[-1]))
            elif 'audio' in lines or 'yolo' in lines:
                segs = lines.split(' ')
                apps[segs[0]] = [float(segs[-1])]
        all_apps[number] = apps 
    #print('all_apps\n', all_apps)

    return all_apps

if __name__ == '__main__':
    read_app_file = sys.argv[1]
    read_qos_file = sys.argv[2]
    write_file = sys.argv[3]

    all_apps = readAppFile(read_app_file)

    wy = [1, 0.8, 0.6, 0.4, 0.2]
    wa = [0.9, 0.7, 0.5, 0.3, 0.1]

    content = ''
    with open(read_qos_file, 'r') as rf:
        content = rf.read()
    try:
        parts = content.split('========== Time: 0 ==========\n')
    except:
        sys.exit('Not From Time 0')
    parts = parts[1].split(' ==========\n')
    #print('parts:', parts)
    number = -1
    accuracys = []
    for part in parts:
        yolo_apps = {}
        audio_apps = {}
        number += 1
        weights = 0
        sum_w_a = 0
        #print('number:', number)
        if ', ' in part:
            #print('part', part)
            lines = part.split('\n')
            #print('lines', lines)
            for line in lines[:-2]:
                #print('line:\n' + line)
                if line[:5] == 'audio':
                    app, accuracy = line.split(', ', 1)
                elif line[:4] == 'yolo':
                    app, img_number, result = line.split(', ', 2)

                if app in all_apps[number].keys():
                    if app[:5] == 'audio' and app not in audio_apps:
                        audio_apps[app] = [float(accuracy)]
                    elif app[:5] == 'audio':
                        apps[app].append(float(accuracy))
                    elif app[:4] == 'yolo' and app not in yolo_apps:
                        yolo_apps[app] = {}
                        yolo_apps[app][img_number] = result
                    elif app[:4] == 'yolo':
                        yolo_apps[app][img_number] = result
            
            # Debug
            print('audio_apps')
            for app in audio_apps:
                print('app: '+app)   
                print('accuracy: ' + str(audio_apps[app])) 
            print('yolo_apps')
            for app in yolo_apps:
                print('app: '+app)   
                for numb in yolo_apps[app]:
                    print('img_number: ' + numb)
                    print('result: ' + yolo_apps[app][numb])       

            for app in apps:
                apps_number = len(all_apps[number][app])
                if app[:4] == 'yolo':
                    weight = wy[int(app[4])-1]
                if app[:5] == 'audio':
                    weight = wa[int(app[5])-1]
                if len(apps[app]) >= apps_number:
                    max_apps = sorted(apps[app], reverse=True)
                    #print('max_apps', max_apps)
                    for i in range(apps_number):
                        sum_w_a += max_apps[i]*weight
                        weights += weight
                else:
                    max_apps = sorted(apps[app], reverse=True)
                    for qos in apps[app]:
                        sum_w_a += qos*weight
                        weights += weight
                    for i in range(apps_number-len(apps[app])):
                        i %= len(max_apps)
                        sum_w_a += max_apps[i]*weight
                        weights += weight
            remaining_apps = [app for app in all_apps[number] if app not in apps.keys()]
            for app in remaining_apps:
                apps_number = len(all_apps[number][app])
                if app[:4] == 'yolo':
                    weight = wy[int(app[4])-1]
                if app[:5] == 'audio':
                    weight = wa[int(app[5])-1]
                sum_w_a += 0
                weights += weight*apps_number
                
            #print('sum_w_a:', sum_w_a)
            #print('weights:', weights)
            if weights == 0:
                accuracys.append(0)
            else:
                accuracys.append(sum_w_a/weights)
        else:
            accuracys.append(0)
    #print('accuracys:', accuracys)
    if os.path.isfile(write_file):
        with open(write_file, 'w') as wf:
            wf.write('')
    with open(write_file, 'a') as wf:
        for accuracy in accuracys:
            wf.write(format(str(round(float(accuracy), 3)), ' <5') + ' ')
