#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys
import pathlib
import pexpect
import paramiko
import subprocess
from Algo import allocate_algo
from Algo import weighted_algo
from Algo import unweighted_algo

# Kbps
Yolo_MAX = 33.4854
Audio_MAX = 0.0527


if __name__ == '__main__':  
    bandwidth = sys.argv[1]
    algorithm = sys.argv[2] 
    weight_ver = sys.argv[3] 
    step_size = sys.argv[4] 

    # List app on cloud
    cmd = f'kubectl get pods -l location=cloud'
    output = subprocess.check_output([cmd],shell=True).decode('utf-8')
    lines = output.split('\n')
    apps = []
    for line in lines:
        app = line.split(" ")[0]
        if '-' in app:
            apps.append(app)
            #print(app)
    
    # Find apps on edge
    cmd = f'kubectl get pods -l location=edge'
    output = subprocess.check_output([cmd],shell=True).decode('utf-8')
    lines = output.split('\n')
    for line in lines:
        app = line.split(" ")[0]
        if '-' in app:
            apps.append(app)
    
    file_path = pathlib.Path(__file__).parent.absolute().as_posix()
    QoS_file = file_path + '/QoSknob.txt'
    # Run RAA
    if len(apps) == 0:
        print('========Allocate Done=============')
        print('There is no analytic in the cloud')
        print('Average accuracy: 0')
        print('time: 0')
    else:
        #bandwidth = int(bandwidth) - sum_edge_bw
        if algorithm == 'RAA':
            allocate_algo.main(str(bandwidth), apps, QoS_file, 'greedy', weight_ver, step_size)
        elif algorithm == 'weighted':
            weighted_algo.main(bandwidth, apps, QoS_file, weight_ver)
        else:
            unweighted_algo.main(bandwidth, apps, QoS_file, weight_ver)
    
    ## List app on edge
    #with open(QoS_file, 'a') as qf:
    #    for app in edge_apps:
    #        qf.write(f'{app}, 1.0\n')
    #

    #'''
    # Send QoS list to gateway
    user = os.environ['GATEWAY_USER']
    host = os.environ['MINION']
    pwd = os.environ['PASSWORD']
    gateway_dir = os.environ['GATEWAY_DIR']
    cmd = f'sshpass -p {pwd} scp {QoS_file} {user}@{host}:{gateway_dir}/Implementation/Gateway/'
    subprocess.run([cmd],shell=True)
    #'''
