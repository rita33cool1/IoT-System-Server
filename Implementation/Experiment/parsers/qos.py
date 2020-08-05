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
Gt_images = {}
WA = []
WY = []
Accuracy = []

def read_audio_qos_file(in_audio_qos_file):
    with open(in_audio_qos_file) as rf:
        parts = rf.read().split('========== Time: 0 ==========')[-1]
        parts = '0========== Time: 0 ==========' + parts
        parts = parts.split('========== Time: ')
    for part in parts[1:]:
        #print('part')
        #print(part)
        global Overall
        key, part = part.split(' ==========', 1)
        Overall[key] = {}
        #print('key')
        #print(key)
        if ', ' in part:
            audios = part.strip().split('\n')
            #print('audios')
            #print(audios)
            for audio in audios:
                name, accuracy = audio.split(', ', 1)
                Overall[key][name] = {'accuracy': float(accuracy)}

def read_yolo_qos_file(in_yolo_qos_file):
    with open(in_yolo_qos_file) as rf:
        parts = rf.read().split('========== Time: 0 ==========')[-1]
        parts = '0========== Time: 0 ==========' + parts
        parts = parts.split('========== Time: ')
    for part in parts[1:]:
        #print('part')
        #print(part)
        global Overall
        key, part = part.split(' ==========', 1)
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
                elif len(Overall[key][name]['images'].keys()) < Max_image_number:
                    Overall[key][name]['images'][iid] = result

def read_yolo_gt(yolo_gt_file):
    with open(yolo_gt_file, 'r') as rf:
        parts = rf.read().split('\n')
    global Gt_images
    for part in parts:
        if ', ' in part:
            iid, result = part.strip().split(', ')
            Gt_images[iid] = result

def yolo_accuracy():
    global Overall
    for time in range(len(Overall.keys())):
        for app in Overall[str(time)]:
            if 'yolo' in app: 
                sum_accuracy = 0
                for iid in Overall[str(time)][app]['images']:
                    if Overall[str(time)][app]['images'][iid] == Gt_images[iid]:
                        sum_accuracy += 1
                Overall[str(time)][app]['accuracy'] = float(sum_accuracy)/len(Overall[str(time)][app]['images'])

def overall_accuracy():
    global Accuracy
    for time in range(len(Overall.keys())):
        #print('time: ' + str(time))
        sum_w = 0
        sum_accuracy = 0
        for app in Overall[str(time)]:
            #print('app: ' + app)
            if 'audio' in app:
                w = WA[int(app.split('-')[0].split('audio')[-1])-1]
            elif 'yolo' in app:
                w = WY[int(app.split('-')[0].split('yolo')[-1])-1]
            #print('w: ' + str(w))
            #print('accuracy: ' + str(Overall[str(time)][app]['accuracy']))
            sum_w += w
            sum_accuracy += Overall[str(time)][app]['accuracy'] * w
        if len(Overall[str(time)].keys()) == 0:
            Accuracy.append(0)
        else:
            Accuracy.append(sum_accuracy/sum_w)
        
def write_accuracy(saved_file):
    with open(saved_file, 'w') as wf:
        for i in range(len(Accuracy)):
            if i != len(Accuracy)-1:
                wf.write(str(Accuracy[i]) + ',')
            else:
                wf.write(str(Accuracy[i]))
                                       
if __name__ == '__main__':
    weight_file = sys.argv[1]
    weight_ver = sys.argv[2]
    in_audio_qos_file = sys.argv[3]
    in_yolo_qos_file = sys.argv[4]
    yolo_gt_file = sys.argv[5]
    saved_file = sys.argv[6]
   
    # Load weights information 
    with open(weight_file, 'r') as rf: 
        # audio 1 -> 4, yolo 1 -> 4
        for line in rf.readlines():
            if line[0] == weight_ver:
                tw = line.split(': ')[1].split(', ') 
                WA = [float(tw[i]) for i in range(len(tw)/2)]
                WY = [float(tw[i]) for i in range(len(tw)/2, len(tw))]
    #print('WA', WA)
    #print('WY', WY)
    
    # Read Audio QoS files
    read_audio_qos_file(in_audio_qos_file)

    # Read Yolo QoS files
    read_yolo_qos_file(in_yolo_qos_file)

    # Debug
    #print('Overall')
    #for time in range(len(Overall.keys())):
    #    print("'"+str(time)+"':")
    #    print(Overall[str(time)]) 

    # Read groud truth results of images
    read_yolo_gt(yolo_gt_file)

    # Debug
    #print('Groud truth results')
    #print(Gt_images)

    # Calculate accuracy of yolo
    yolo_accuracy()

    # Debug
    #print('Overall')
    #for time in range(len(Overall.keys())):
    #    print("'"+str(time)+"':")
    #    print(Overall[str(time)]) 

    # Calculate overall accuracy
    overall_accuracy()

    # Debug
    #print('Overall accuracy')
    #print(Accuracy)

    # Write QoS
    write_accuracy(saved_file)
