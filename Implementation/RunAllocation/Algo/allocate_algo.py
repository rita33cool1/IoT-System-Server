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
from Algo import unweighted_algo
allocate_algo.main(bandwidth, apps, QoS_file)
"""
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys
import copy
import math
import time
import docker
import random
import logging
import pathlib
import warnings
import functools
import subprocess
import numpy as np
from scipy.optimize import fsolve

'''
const_overall_maxbw = { 
    "yolo1":259.6,
    "yolo2":259.6,
    "yolo3":259.6,
    "yolo4":259.6,
    "yolo5":259.6,
    "audio1":3497.6,
    "audio2":3497.6,
    "audio3":3497.6,
    "audio4":3497.6,
    "audio5":3497.6
}
overall_maxbw = copy.deepcopy(const_overall_maxbw)
'''

class Analytics():
    # QoS coefficient
    #qy = [-0.5928, 1.015, 0.5533]
    qy = [0.1632, 494]
    #qa = [2.211, -1.966, 0.6833]
    #qa = [0.06484, 2.647]
    qa = [0.01465, 3.992, 0.1575]
    # weight
    #wy = [1, 0.8, 0.6, 0.4, 0.2]
    #wa = [0.9, 0.7, 0.5, 0.3, 0.1]
    # Raw BW coefficient
    #ry = [-9.488, 62.96, 3.362] 
    #ry = [3062, 0.01702, -3057] 
    ry = [52.52, 5.449] 
    ra = [687.5604, 1.011] 
    # Processed BW coefficient
    pa = [0.0527] 
    #py = [2846, 0.01086, -2842]
    py = [30.01, 4.17]
    # analytic versions
    # lambda
    _lambda = 0
    
    def __init__(self, analytic_name, number, weights):
        self.number = number
        self.name = analytic_name
        self.is_edge = False
        if 'edge' in self.name:
            self.is_edge = True
        if 'yolo' in self.name:
            self.YorA = True
            self.order = int(self.name[4]) - 1 
            #self.knob = 0.1
            #self.knob = 0
            # math.log(x), x must > 0
            self.knob = 0.01
            self.weight = weights[self.order+12]
            # Plus 1 is to make the priority of yolo lower than audio
            self.w = self.weight + 1
            #self.minKnob = 0
            self.minKnob = 0.01
            #self.maxKnob = 0.844
            self.maxKnob = 1
            self.singleMinBw = self.RawBw(self.minKnob)
        elif 'audio' in self.name:        
            self.YorA = False
            self.order = int(self.name[5]) - 1
            #self.knob = 0.4
            self.knob = 0
            self.weight = weights[self.order]
            self.w = self.weight
            self.minKnob = 0.4
            self.maxKnob = 1
            self.singleMinBw = self.RawBw(self.minKnob)
        else: 
            print ('analytic is neither "yolo" nor "audio"')
        self.minBw = self.RawBw(self.knob)

    def QoS(self, knob):
        """
        QoS of yolo: Qa(Ka) = Pa,1*log(Pa,2*Ka) + Pa,3
        QoS of audio: Qa(Ka) = Pa,1*exp(Pa,2*Ka)
        """        
        # log(x), x should larger than zero
        if self.YorA and self.qy[1]*knob <= 0:
            return 0
        elif self.YorA and self.qy[0]*math.log(self.qy[1]*knob)+self.qa[2] < 0:
            return 0
        elif self.YorA:
            return (self.qy[0]*math.log(self.qy[1]*knob)) * self.number * 1000
        else:
            #return (self.qa[0]*math.exp(self.qa[1]*knob)) * self.number * 1000
            return (self.qa[0]*math.exp(self.qa[1]*knob) + self.qa[2]) * self.number * 1000
        
    def RawBw(self, knob):
        """
        Raw bandwidth of yolo: Ra(Ka) = Pa,1*exp(Pa,2*Ka) + Pa,3
        Raw bandwidth of audio: Ra(Ka) = Pa,1*Ka + Pa,2
        """
        if self.YorA:
            #return (self.ry[0]*math.exp(self.ry[1]*knob) + self.ry[2]) * self.number
            return (self.ry[0]*knob + self.ry[1]) * self.number
        else:
            return (self.ra[0]*knob + self.ra[1]) * self.number
    
    def SolveRawBw(self, knob, const):
        """
        Raw bandwidth of yolo: Ra(Ka) = Pa,1*exp(Pa,2*Ka) + Pa,3
        Raw bandwidth of audio: Ra(Ka) = Pa,1*Ka + Pa,2
        """
        if self.YorA:
            #return (self.ry[0]*math.exp(self.ry[1]*knob) + self.ry[2]) * self.number - const
            return (self.ry[0]*knob + self.ry[1]) * self.number - const
        else:
            return (self.ra[0]*knob + self.ra[1]) * self.number - const
    
    def ProcessBw(self, knob):
        """
        Processed bandwidth of yolo: Pa(Ka) = Pa,1*exp(Pa,2*Ka) + Pa,3
        Processed bandwidth of audio: Pa(Ka) = Pa,1
        """
        if self.YorA:
            #return (self.py[0]*math.exp(self.py[1]*knob) + self.py[2])
            return (self.py[0]*knob + self.py[1])
        else:
            return (self.pa[0])
    
    def SolveProcessBw(self, knob, const):
        """
        Processed bandwidth of yolo: Pa(Ka) = Pa,1*exp(Pa,2*Ka) + Pa,3
        Processed bandwidth of audio: Pa(Ka) = Pa,1
        """
        if self.YorA:
            #return (self.py[0]*math.exp(self.py[1]*knob) + self.py[2]) - const
            return (self.py[0]*knob + self.py[1]) - const
        else:
            return (self.pa[0]) - const
    
    def Lagrangian(self, knob):
        """
        Lagrangian: WaQa(Ka) - lambda*Ra(Ka)
        """
        if self.YorA:
            return self.weight*self.QoS(knob) - self._lambda*self.RawBw(knob)
        else:
            return self.weight.order*self.QoS(knob) - self._lambda*self.RawBw(knob)
    
    def ArgMaxKa(self, _lambda):
        """
        The dual decomposed result in each container:
        Ka* = argmax WaQa(Ka) - lambda*Ra(Ka) 
        """
        x = np.linspace(self.minKnob, self.maxKnob)
        self._lambda = _lambda
        max_knob = max(x, key=self.Lagrangian) 
        #print('max_knob: ' + str(max_knob))
        return max_knob

    def GofKnob(self, knob):
        """ 
        (QoS in Accurace/bandwidth): WaQa(Ka)/Ra(Ka) 
        """
        #print('weight: ' + str(self.weight))
        #print('QoS: ' + str(self.QoS(knob)))
        #print('RawBw: ' + str(self.RawBw(knob)))
        return self.weight*self.QoS(knob) / self.RawBw(knob)


def process_bandwidth(weights):
    #run_analytics = get_images(get_containers())
    # List app on edge
    cmd = f'kubectl get pods -l location=edge'
    output = subprocess.check_output([cmd],shell=True).decode('utf-8')
    lines = output.split('\n')
    run_analytics = []
    for line in lines:
        app = line.split(" ")[0]
        if '-' in app:
            #print(app)
            run_analytics.append(app)
    #print('running containers', run_analytics)
    # Sum Processed bandwidth
    sum_bandwidth = 0
    for analytic in run_analytics:
        sum_bandwidth += Analytics(analytic, 1, weights).ProcessBw()
    return sum_bandwidth 


def cal_accuracy(app, QoS):
    if "audio" in app:
        if QoS == 0:
            return 0
        elif QoS <= 0.38:
            return 0.2
        elif QoS < 0.45:
            return 0.25
        elif QoS < 0.5:
            return 0.27
        elif QoS < 0.54:
            return 0.30
        elif QoS < 0.59:
            return 0.31
        elif QoS < 0.63:
            return 0.32
        elif QoS < 0.68:
            return 0.34
        elif QoS < 0.72:
            return 0.36
        elif QoS < 0.77:
            return 0.42
        elif QoS < 0.81:
            return 0.57
        elif QoS < 0.86:
            return 0.67
        elif QoS < 0.9:
            return 0.74
        elif QoS < 0.95:
            return 0.84
        else:
            return 0.9
    elif "yolo" in app:
        if QoS == 0:
            return 0
        elif QoS <= 0.2:
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


def lagrange(analytics, bandwidth):
    #print('bandwidth: ' + str(bandwidth))
    t = 0
    _lambda = 1
    alpha = 0.00001
    old_old_min_sum_value = 0
    old_min_sum_value = 0
    min_sum_value = 0
    value = 0
    old_value = value 
    old_old_knobs = []
    old_knobs = []
    knobs = []
    old_old_min_t = t
    old_min_t = t
    min_t = t
    old_old_min_sum_bw = 0
    old_min_sum_bw = 0
    min_sum_bw = 0
    result_knobs = []
    while _lambda > 0 and (value <= old_value):
        #print('\niteration: ' + str(t))
        max_knobs = []
        sum_value = 0
        sum_bw = 0
        for analytic in analytics:
            #print(analytic.name)
            max_knob = analytic.ArgMaxKa(_lambda) 
            max_knobs.append(max_knob)  
            sum_value += analytic.Lagrangian(max_knob)
            sum_bw += analytic.RawBw(max_knob)
            #print('qos: ' + str(analytic.QoS(max_knob)))
            #print('bw: ' + str(analytic.RawBw(max_knob)))
            #print('value: ' + str(analytic.Lagrangian(max_knob)))
        old_lambda = _lambda
        #print('_lambda: ' + str(old_lambda))
        _lambda -= alpha * (sum_bw)
        old_value = value
        value = sum_value + _lambda*bandwidth
        #print('sum_value: ' + str(sum_value))
        #print('value: ' + str(value))
        #print('sum_bw: ' + str(sum_bw))
        #print('max_knobs: ', max_knobs)
        if _lambda < 0: _lambda = 0
        if len(knobs)==0:
            old_value = value
        if min_sum_value > value or len(knobs)==0:
            old_old_min_sum_value = old_min_sum_value
            old_old_min_t = old_min_t
            old_old_knobs = old_knobs
            old_old_min_sum_bw = old_min_sum_bw
            old_min_sum_value = min_sum_value
            old_min_t = min_t
            old_knobs = knobs
            old_min_sum_bw = min_sum_bw
            min_sum_value = value
            min_t = t
            knobs = max_knobs
            min_sum_bw = sum_bw
        t += 1
    if min_sum_bw <= bandwidth:
        result_min_t = min_t
        result_min_sum_value = min_sum_value
        result_knobs = knobs
        result_min_sum_bw = min_sum_bw
    elif old_min_sum_bw <= bandwidth:
        result_min_t = old_min_t
        result_min_sum_value = old_min_sum_value
        result_knobs = old_knobs
        result_min_sum_bw = old_min_sum_bw
    else:
        result_min_t = old_old_min_t
        result_min_sum_value = old_old_min_sum_value
        result_knobs = old_old_knobs
        result_min_sum_bw = old_old_min_sum_bw
    # Update analytics' knobs
    try: 
        for i in range(len(analytics)):
            analytics[i].knob = result_knobs[i]
    except:
        warnings.warn('analytics and result_knobs IndexError: list index out of range\n' + 'len(analytics): ' + str(len(analytics)) + '\nlen(result_knobs): ' + str(len(result_knobs))) 

    # If there is remaining bandwidth, 
    # allocate the remaining bandwidth to the high-weight analytics
    weight_analytics = analytics.copy()
    remaining_bw = bandwidth - result_min_sum_bw
    while remaining_bw > 1 and len(weight_analytics) > 0:
        max_w_analytic = max(weight_analytics, key = lambda a: a.w)
        #print('max_w_analytic: ' + max_w_analytic.name + ', w: ' + str(max_w_analytic.w))
        #print('remaining_bw:', remaining_bw)
        if max_w_analytic.knob >= max_w_analytic.maxKnob:            
            weight_analytics.remove(max_w_analytic)
        else:
            analytic = analytics[analytics.index(max_w_analytic)]
            original_bw = analytic.RawBw(analytic.knob)
            max_bw = analytic.RawBw(analytic.maxKnob)
            if remaining_bw > max_bw-original_bw:
                analytic.knob = analytic.maxKnob
                remaining_bw -= (max_bw - original_bw)
                weight_analytics.remove(max_w_analytic)
            else:
                func = lambda knob: analytic.RawBw(knob) - remaining_bw - original_bw
                analytic.knob = fsolve(func, analytic.knob)[0]
                remaining_bw -= (analytic.RawBw(analytic.knob) - original_bw)
    # Update result_knobs
    result_knobs = []
    for analytic in analytics:
        result_knobs.append(analytic.knob)

    '''
    # Debug Message
    print('analytics and accuracies')
    for analytic in analytics:
        print(analytic.name)
        print(analytic.knob)
        print(cal_accuracy(analytic.name, analytic.knob))
    print('Result min iteration: ' + str(result_min_t))
    print('Result min_sum_value: ' + str(result_min_sum_value))
    print('Result knobs: ', result_knobs)
    '''
    
    return result_knobs     


def greedy(analytics, bandwidth, step_size):
    # Only consider the analytic whose knob hasn't reached 1
    tmp_analytics = []
    for analytic in analytics:
        if analytic.knob < 1:
            tmp_analytics.append(analytic)
    # Repeatedly select the analytic which has maximal qos/bw
    while bandwidth > 0 and len(tmp_analytics) > 0:
        # Build a list to record qos/bw of each analytic
        analytic_qb = []
        for analytic in tmp_analytics:
            #print('analytic: ' + analytic.name)
            #print('analytic.knob: ' + str(analytic.knob))
            #print('GofKnob: ' + str(analytic.GofKnob(analytic.knob)))
            analytic_qb.append([analytic, analytic.GofKnob(analytic.knob)])
        # Find the analytic which has maximal qos/bw
        max_analytic = max(analytic_qb, key = lambda a_qb: a_qb[1])[0]
        tmp_knob = max_analytic.knob + step_size
        if max_analytic.is_edge:
            if max_analytic.knob < max_analytic.minKnob:
                tmp_knob = max_analytic.minKnob
                tmp_bandwidth = bandwidth - max_analytic.ProcessBw(tmp_knob)
                tmp_1_bandwidth = bandwidth - max_analytic.ProcessBw(1)
            else:
                tmp_bandwidth = bandwidth + max_analytic.ProcessBw(max_analytic.knob) - max_analytic.ProcessBw(tmp_knob)
                tmp_1_bandwidth = bandwidth + max_analytic.ProcessBw(max_analytic.knob) - max_analytic.ProcessBw(1)
        else:
            if max_analytic.knob < max_analytic.minKnob:
                tmp_knob = max_analytic.minKnob
                tmp_bandwidth = bandwidth - max_analytic.RawBw(tmp_knob)
                tmp_1_bandwidth = bandwidth - max_analytic.RawBw(1)
            else:
                tmp_bandwidth = bandwidth + max_analytic.RawBw(max_analytic.knob) - max_analytic.RawBw(max_analytic.knob+step_size)
                tmp_1_bandwidth = bandwidth + max_analytic.RawBw(max_analytic.knob) - max_analytic.RawBw(1)
        #print('max_analytic: ' + str(max_analytic.name))
        #print('knob: ' + str(max_analytic.knob))
        #print('tmp_knob: ' + str(tmp_knob))
        #print('bandwidth: ' + str(bandwidth))
        #print('tmp_bandwidth: ' + str(tmp_bandwidth))
        #print('tmp_1_bandwidth: ' + str(tmp_1_bandwidth))
        # Max analytic's knob add step_size
        if tmp_knob <= 1 and tmp_bandwidth >= 0:
            max_analytic.knob = tmp_knob
            bandwidth = tmp_bandwidth
            #print('Add step size')
            #print('After knob: ' + str(max_analytic.knob))
            #print('After bandwidth: ' + str(bandwidth))
            # Max knob reaches 1 
            if max_analytic.knob == 1:
                #print('Remove max_analytic: ' + str(max_analytic.name))
                tmp_analytics.remove(max_analytic)
        # Max knob reaches 1 
        elif tmp_knob > 1 and tmp_1_bandwidth >= 0:
            max_analytic.knob = 1
            tmp_analytics.remove(max_analytic)
            bandwidth = tmp_1_bandwidth
            #print('Knob is 1')
            #print('After knob: ' + str(max_analytic.knob))
            #print('After bandwidth: ' + str(bandwidth))
            #print('Remove max_analytic: ' + str(max_analytic.name))
        # Bandwidth reaches max 
        elif tmp_knob >= max_analytic.minKnob:
            if max_analytic.is_edge:
                remaining_bw = bandwidth + max_analytic.ProcessBw(max_analytic.knob)
                func = functools.partial(max_analytic.SolveProcessBw, const=remaining_bw)
            else:
                remaining_bw = bandwidth + max_analytic.RawBw(max_analytic.knob)
                func = functools.partial(max_analytic.SolveRawBw, const=remaining_bw)
            max_analytic.knob = fsolve(func, max_analytic.knob)[0]
            bandwidth = 0
            #print('Bandwidth used up')
            #print('After knob: ' + str(max_analytic.knob))
            #print('After bandwidth: ' + str(bandwidth))
        # Bandwidth reaches max and max_analytic's knob cannot reach min knob
        # Choose another analytic
        else:
            tmp_analytics.remove(max_analytic)
            #print('Bandwidth is about used up and the knob of max_analytic cannot reach min knob')


def allocate_algo(bandwidth, num, analytics_array, QoS_file, method, weight_ver, step_size):
    ## Initial analytics_array
    #print('Initial analytics_array:', analytics_array)

    ## ---------- Initialization ---------- ##
    # Combine Analytics
    """ 
    # Remove Duplicate
    duplic_analytics = []
    counted_analytics = []
    duplic_num = []
    times = {}
    #input_analytics = []
    #global overall_maxbw
    for analytic_name in analytics_array:
        ana_name = analytic_name.split('\n', 1)[0]
        #input_analytics.append(ana_name)
        name, time = ana_name.split('-', 1)
        # Preserve time information
        if name not in times.keys():
            times[name] = [time]
        else:
            times[name].append(time)
 
        if name not in counted_analytics:
            counted_analytics.append(name)
        elif name not in duplic_analytics:
            duplic_analytics.append(name)
            duplic_num.append(2)
            #overall_maxbw[name] += const_overall_maxbw[name]
        else:
            duplic_num[duplic_analytics.index(name)] += 1
            #overall_maxbw[name] += const_overall_maxbw[name]
    ## Reorder list
    ##counted_analytics.sort(key=lambda a: overall_maxbw[a], reverse=True)
    #counted_analytics.sort(key=lambda a: overall_maxbw[a])
    #print('Reorder counted_analytics')
    #for analy in counted_analytics:
    #    print(analy, overall_maxbw[analy])
    """
    # Do Not Combine Analytics
    duplic_analytics = []
    counted_analytics = []
    times = {}
    for analytic in analytics_array:
        parts = analytic.split('-')
        # Edge
        if len(parts) > 2:
            name = parts[0] + '-' + parts[1]
        else:
            name = parts[0]
        time = parts[-1]
        if name not in times.keys():
            times[name] = [time]
        else:
            times[name].append(time)
        counted_analytics.append(name)
    

    # Load weights information
    tmp_weights = []
    file_path = pathlib.Path(__file__).parent.absolute().as_posix()
    with open(file_path+'/weights.txt', 'r') as rf:
        # audio 1 -> 12, yolo 13 -> 24
        for line in rf.readlines():
            if line[0] == weight_ver:
                tw = line.split(': ')[1].split(', ') 
                tmp_weights = [float(w) for w in tw]
    #print('tmp_weights', tmp_weights)
            
    ## Upload bandwidth - bandwidth of containers running in the gateway
    #process_bw = process_bandwidth(tmp_weights)
    #bandwidth -= process_bw

    # Create analytic object
    # result: apps' name
    apps_array = []
    # result: apps' knobs
    QoS_array = []
    qos_array = []
    # result: apps' accuracy
    accuracy = [] 
    # result: apps' bandwidth
    bandwidths_array = []
    analytics = []
    is_stop = False
    for analytic_name in counted_analytics:
        if analytic_name in duplic_analytics:
            obj = Analytics(analytic_name, duplic_num[duplic_analytics.index(analytic_name)], tmp_weights)
        else:
            obj = Analytics(analytic_name, 1, tmp_weights)
        analytics.append(obj)
    # Debug Message: weights
    #print('weights')
    #print('len(analytics): ' + str(len(analytics)))
    #for analytic in analytics:
    #    print(analytic.name + ': ' + str(analytic.weight))

    # If the sum of all the minmun bw more than the total bw
    # Set some knobs zero. (The priority depends on their weights)
    # Fisrtly set audio analytics zero, then yolo
    zero_analytics = []
    zero_num = []
    sum_bw = sum([a.minBw for a in analytics])
    while sum_bw > bandwidth:
        # Select analytic by its weight
        min_w_app = min(analytics, key=lambda a: a.w)
        if min_w_app.name in duplic_analytics:
            min_w_index = duplic_analytics.index(min_w_app.name)
            duplic_num[min_w_index] -= 1
            if duplic_num[min_w_index] == 1:
                del duplic_analytics[min_w_index]
                del duplic_num[min_w_index]
                min_w_app.number = 1
            else:
                min_w_app.number = duplic_num[min_w_index]
        else:
            analytics.remove(min_w_app)
            min_w_app.number = 0
        if min_w_app.name not in zero_analytics:
            zero_analytics.append(min_w_app.name)
            zero_num.append(1)
        else:
            zero_num[zero_analytics.index(min_w_app)] += 1
        sum_bw -= min_w_app.singleMinBw
            
    ## ---------- Lagrange Relaxtion ---------- ##
    if method == 'lagrange':
        qos_array = lagrange(analytics, bandwidth)
    ## ---------- Greedy ---------- ##
    elif method == 'greedy':
        greedy(analytics, bandwidth, step_size)
            
    ## ---------- Collect Result ---------- ##
    # Insert back duplicate analytics
    # Insert back some of the zero-knob analytics
    #index = 0
    weights = []
    for analytic in analytics:
        #print('index:', index)
        apps_array.append(analytic.name)
        #QoS_array.append(qos_array[index])
        QoS_array.append(analytic.knob)
        #bandwidths_array.append(analytic.RawBw(qos_array[index])/analytic.number)
        if analytic.is_edge:
            bandwidths_array.append(analytic.ProcessBw(analytic.knob))
        else:
            bandwidths_array.append(analytic.RawBw(analytic.knob)/analytic.number)
        #accuracy.append(cal_accuracy(analytic.name, qos_array[index]))
        accuracy.append(cal_accuracy(analytic.name, analytic.knob))
        # Weighted average
        weights.append(analytic.weight)
        if analytic.name in duplic_analytics:
            number = duplic_num[duplic_analytics.index(analytic.name)]
            for i in range(number-1):
                apps_array.append(analytic.name)
                #QoS_array.append(qos_array[index])
                QoS_array.append(analytic.knob)
                #bandwidths_array.append(analytic.RawBw(qos_array[index])/analytic.number)
                if analytic.is_edge:
                    bandwidths_array.append(analytic.ProcessBw(analytic.knob))
                else:
                    bandwidths_array.append(analytic.RawBw(analytic.knob)/analytic.number)
                #accuracy.append(cal_accuracy(analytic.name, qos_array[index]))
                accuracy.append(cal_accuracy(analytic.name, analytic.knob))
                # Weighted average
                weights.append(analytic.weight)
        if analytic.name in zero_analytics:
            zero_index = zero_analytics.index(analytic.name)
            number = zero_num[zero_index]
            for i in range(number):
                apps_array.append(analytic.name)
                QoS_array.append(0)
                bandwidths_array.append(0)
                accuracy.append(cal_accuracy(analytic.name, 0))
                # Weighted average
                weights.append(analytic.weight)
            del zero_analytics[zero_index]
            del zero_num[zero_index]
        #index += 1

    # Insert back the remaining zero-knob analytics
    # That is the analytic not in analytics
    for i in range(len(zero_analytics)):
        for j in range(zero_num[i]):
            apps_array.append(zero_analytics[i])
            QoS_array.append(0)
            bandwidths_array.append(0)
            #accuracy.append(cal_accuracy(zero_analytics[i].name, 0))
            accuracy.append(cal_accuracy(zero_analytics[i], 0))
            # Weighted average
            tmp_app = Analytics(zero_analytics[i], 1)
            weights.append(tmp_app.weight)
            del tmp_app
    
    # Insert back time information for each analytic
    new_apps_array = []    
    for app in apps_array:
        new_apps_array.append(app+'-'+times[app][0])
        del times[app][0]
    apps_array = new_apps_array.copy()

    ## Debug message
    #print('Debug')
    #for i in range(len(apps_array)):
    #    print("app name: " + apps_array[i])
    #    print("qos: " + str(QoS_array[i]))


    ## ---------- Writting Result ---------- ##    
    # Write the Result
    print("========Allocate Done=============")
    # QoS Knob
    with open(QoS_file, 'w+') as the_file:
        sum_bandwidth = 0
        sum_accuracy = 0
        for i in range(len(apps_array)):
            sum_bandwidth += bandwidths_array[i]
            sum_accuracy += accuracy[i]*weights[i]
            print(apps_array[i],QoS_array[i],bandwidths_array[i], accuracy[i])
            the_file.write(f'{apps_array[i]}, {QoS_array[i]}\n')
    #print("average QoS:", sum(accuracy)/pre_weights) 
    #print('Sum of bandwidth:', sum_bandwidth+process_bw)
    print('Sum of bandwidth:', sum_bandwidth)
    print('Sum of weights:', sum(weights))
    # Average
    #print('Average accuracy:', sum_accuracy/len(apps_array))
    # Weighted average
    print('Average accuracy:', sum_accuracy/sum(weights))
    return QoS_array, apps_array


def read(filename):
    num=0
    with open(filename) as f:
         analytics = f.readlines()
    num = len(analytics)
    return num, analytics


def main(bandwidth, analytics, QoS_file, method, weight_ver, step_size):
    start_time = time.time()
    bandwidth = float(bandwidth)

    num = len(analytics)
    # Step size is only needed for greedy
    result, apps_array = allocate_algo(bandwidth, num, analytics, QoS_file, method, weight_ver, float(step_size))

    print('time: ' + str(time.time()-start_time))


if __name__ == '__main__':

    try:
        bandwidth = float(sys.argv[1])
    except IndexError:
        bandwidth = 16970 # 16970Kbps
    try:
        analytics_file = sys.argv[2]
    except IndexError:
        analytics_file = 'analytics.input'

    start_time = time.time()

    gateway_dir = os.environ['GATEWAY_DIR']
    QoS_file = f'{gateway_dir}/Implementation/Gateway/QoSknob.txt'
    method = 'greedy'
    weight_ver = '1'
    # Step size is only needed for greedy
    step_size = 0.05
    num, analytics = read(analytics_file)
    result, apps_array = allocate_algo(bandwidth, num, analytics, QoS_file, method, weight_ver, float(step_size))

    print('time: ' + str(time.time()-start_time))
