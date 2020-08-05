#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import random
import sys

#apps_name = ['yolo1','yolo2','yolo3','audio1','audio2','audio3','audio4','audio5']
#apps_name = ['yolo1','yolo2','yolo3','yolo4','yolo5','audio1','audio2','audio3','audio4','audio5']
#apps_name = ['yolo1','yolo2','yolo3','yolo4','audio1','audio2','audio3','audio4']
apps_name = [
    'yolo1', 'yolo2', 'yolo3', 'yolo4', 'yolo5', 'yolo6', 'yolo7', 'yolo8',
    'yolo9', 'yolo10', 'yolo11', 'yolo12', 'audio1', 'audio2', 'audio3', 'audio4',
    'audio5', 'audio6', 'audio7', 'audio8', 'audio9', 'audio10', 'audio11', 'audio12'
]


try:
    a = int(sys.argv[1])
    dmin = int(sys.argv[2])
    dmax = int(sys.argv[3])
    time = int(sys.argv[4])
    file_name = sys.argv[5]
except:
    print('python3 run.py {arrival} {departure} {total time} {file name}')

# Poisson
is_rep = True
while True:
    is_next = True
    # a requests per minute
    arrival_nums = np.random.poisson(a, time)
    arrivals = []
    zero_arrs = []
    apps_index = []
    gap = 0
    for i in range(time):
        #print('i: ' + str(i))
        #print('arrival_nums['+str(i)+']: ' + str(arrival_nums[i]))
        if arrival_nums[i] == 0:
            gap += 1
            continue
        elif i == 0: 
            tmp_gap = 0
        else: 
            tmp_gap = gap + 1
            gap = 0
        #for j in range(arrival_nums[i]):
        j = 0
        while j < arrival_nums[i]:
            #print('j: ' + str(j))
            if j == 0:
                arrivals.append(tmp_gap)
            else:
                arrivals.append(0)
            # Randomly choose an app
            app_index = (random.randint(0,23))
            # Randomly choose an app with probabilities
            #app_index = np.random.choice(np.arange(0, 8), p=[0.03, 0.04, 0.05, 0.06, 0.19, 0.20, 0.21, 0.22])
            #print('app_index: ' + str(app_index))
            #print('arrivals: ' + str(arrivals[len(arrivals)-1]))
            #print('zero_arrs', zero_arrs)
            if app_index not in zero_arrs: 
                # Check the previous request
                if (i != 0 or j != 0) and arrivals[len(arrivals)-2] != 0 and arrivals[len(arrivals)-1] != 0:
                    zero_arrs = []
                    #print('zero_arrs = []')
                zero_arrs.append(app_index)
                #print('zero_arrs append')
            elif (i != 0 or j != 0) and arrivals[len(arrivals)-1] == 0:
                #print('break')
                #is_next = False
                arrivals.pop()
                continue
                #break
            else:
                zero_arrs = []
                #print('zero_arrs = []')
                zero_arrs.append(app_index)
                #print('zero_arrs append')
            apps_index.append(app_index)
            #print('apps_index: '  + str(apps_index[len(apps_index)-1]))
            j += 1
        # last
        if not is_next: break
        if i == time-1: 
            is_rep = False
    if not is_rep: break

#print('arrivals', arrivals)
#print('len(arrivals)', len(arrivals))
#print('apps_index', apps_index)
#print('len(apps_index)', len(apps_index))

tmp = 0
# A request exists b minutes
#departures = np.random.poisson(d, len(arrivals))
departures = np.random.random_integers(dmin,dmax, len(arrivals))
#print('departures', departures)
#print('len(departures)', len(departures))
with open(file_name, 'w') as the_file:
    for i in range(len(arrivals)):
        #print('wi: ' + str(i))
        #print('apps_index: ' + str(apps_index[i]))
        #print('arrivals: ' + str(arrivals[i]))
        #print('departures: ' + str(departures[i]))
        tmp = tmp + arrivals[i]
        the_file.write(f'{apps_name[apps_index[i]]}, {tmp}, {departures[i]}\n')
