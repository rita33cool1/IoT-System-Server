#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
When this file is using in the Gateway, 
put the file under Algo/Allocate and directly using it.
E.g. 
python3 unweighted_algo.py 16970 analytics.input.

When this file is using in the cloud server, 
put the file under RunAllocation/Algo, import it, and use its main().                                    
E.g. 
from Algo import allocate_algo
unweighted_algo.main(bandwidth, apps, QoS_file)
"""

__author__ = 'YuJung Wang'
__data__ = '2020/04'

import os
import sys
import time
import math
import random
import pathlib
import logging
import functools
import subprocess
from scipy.optimize import fsolve

# weights
# [yolo audio]
#w = [1, 0.8, 0.6, 0.4, 0.2, 0.9, 0.7, 0.5, 0.3, 0.1]
# [audio yolo]
w = []
#ry = [3062, 0.01702, -3057] 
#ra = [687.5604, 1.011] 
#py = [2846, 0.01086, -2842]
#pa = [0.0527] 
ry = [52.52, 5.449]
ra = [687.5604, 1.011]
py = [30.01, 4.17]
pa = [0.0527]


def calculatebw(knob, is_edge, YorA, const):
    if YorA and is_edge:
        return (py[0]*knob + py[1])- const
    elif not YorA and is_edge:
        return (pa[0]) - const
    elif YorA and not is_edge:
        return (ry[0]*knob + ry[1]) - const
    elif not YorA and not is_edge:
        return (ra[0]*knob + ra[1]) - const


def cal_accuracy(app, QoS):
    if "audio" in app:
        if QoS <= 0.38:
            return 0.2
        elif QoS <= 0.45:
            return 0.25
        elif QoS <= 0.5:
            return 0.27
        elif QoS <= 0.54:
            return 0.30
        elif QoS <= 0.59:
            return 0.31
        elif QoS <= 0.63:
            return 0.32
        elif QoS <= 0.68:
            return 0.34
        elif QoS <= 0.72:
            return 0.36
        elif QoS <= 0.77:
            return 0.42
        elif QoS <= 0.81:
            return 0.57
        elif QoS <= 0.86:
            return 0.67
        elif QoS <= 0.9:
            return 0.74
        elif QoS <= 0.95:
            return 0.84
        else:
            return 0.9
    elif "yolo" in app:
        if QoS <= 0.2:
            return 0.525
        elif QoS <=0.3:
            return 0.64
        elif QoS <=0.4:
            return 0.685
        elif QoS <=0.5:
            return 0.82
        elif QoS <=0.6:
            return 0.88
        elif QoS <=0.7:
            return 0.93
        elif QoS <=0.8:
            return 0.955
        elif QoS <=0.9:
            return 0.99
        else:
            return 0.99


def QoS(num, apps_array, bandwidths_array):
    QoS_array = [1]*num
    for i in range(num):
        is_edge = False
        if 'edge' in apps_array[i]:
            is_edge = True
        if 'yolo' in apps_array[i]:
            YorA = True
        elif 'audio' in apps_array[i]:
            YorA = False
        partial_func = functools.partial(calculatebw, is_edge=is_edge, YorA=YorA, const=bandwidths_array[i])
        QoS_knobs = fsolve(partial_func,1) 
        QoS_array[i] = QoS_knobs[0]
    return QoS_array, bandwidths_array


def allocate_algo(bandwidth, num, analytics_array, QoS_file, weight_ver):
    print('Allocate Bandwidth:', bandwidth)
    bandwidth_tag = False
    qos = []
    bandwidths_array = []
    apps_array = []
    num = len(analytics_array)
    allocate_bandwidth = float(bandwidth)/num
    for i in range(num):
        #apps_array.append(analytics_array[i].split('-')[0])
        apps_array.append(analytics_array[i])
        bandwidths_array.append(allocate_bandwidth)

    print("========Allocate Done=============")

    # Load weights info
    global w
    file_path = pathlib.Path(__file__).parent.absolute().as_posix()
    with open(file_path+'/weights.txt', 'r') as rf:
        # audio 1 -> 4, yolo 1 -> 4
        for line in rf.readlines():
            if line[0] == weight_ver:
                tw = line.split(': ')[1].split(', ') 
                w = [float(wi) for wi in tw]

    # QoS Knob
    QoS_array, bandwidths_array = QoS(num, apps_array, bandwidths_array)
    with open(QoS_file,'w+') as the_file:
        sum_bandwidth = 0
        sum_accuracy = 0
        sum_weights = 0
        accuracy = [0] * num
        for i in range(num):
            sum_bandwidth += bandwidths_array[i]
            accuracy[i] = cal_accuracy(apps_array[i],QoS_array[i])
            print(apps_array[i],QoS_array[i],bandwidths_array[i], accuracy[i])
            the_file.write(f'{apps_array[i]}, {QoS_array[i]}\n')
            # Average
            #sum_accuracy += accuracy[i]
            # Weighted Average
            weight = 0
            if apps_array[i][:4] == 'yolo':
                weight = w[int(apps_array[i][4])+3]
            else:
                weight = w[int(apps_array[i][5])-1]
            sum_weights += weight
            sum_accuracy += accuracy[i]*weight
    #print("average QoS:", sum(accuracy)/pre_weights)
    print('Sum of bandwidth:', sum_bandwidth)
    # Average
    #print('Average accuracy:', sum_accuracy/num)
    # Weighted Average
    #print('Sum weights:', sum_weights)
    print('Average accuracy:', sum_accuracy/sum_weights)
    return QoS_array, apps_array


def read(filename):
    num=0
    with open(filename) as f:
         analytics = f.readlines()
    num = len(analytics)
    return num, analytics


def main(bandwidth, analytics, QoS_file, weight_ver):
    start_time = time.time()
    bandwidth = float(bandwidth)
    num = len(analytics)
    result, apps_array = allocate_algo(bandwidth, num, analytics, QoS_file, weight_ver)
    print('time: ' + str(time.time()-start_time))


if __name__ == '__main__':

    try:
        bandwidth = float(sys.argv[1])
    except IndexError:
        #bandwidth = 1000 # 1000Kbps
        bandwidth = 16970 # 16970Kbps
    try:
        analytics_file = sys.argv[2]
    except IndexError:
        analytics_file = 'analytics.input'

    start_time = time.time()

    gateway_dir = os.environ['GATEWAY_DIR']
    QoS_file = f'{gateway_dir}/Implementation/Gateway/QoSknob.txt'
    num, analytics = read(analytics_file)
    result, apps_array = allocate_algo(bandwidth, num, analytics, QoS_file)

    print('time: ' + str(time.time()-start_time)) 
