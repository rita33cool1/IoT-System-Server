#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import re
import sys
import time
import pexpect
import datetime
import paramiko
import threading
import subprocess
import paho.mqtt.publish as publish
from multiprocessing import Process

#total_storage = 6
#total_storage = 5
total_storage = 3
#total_storage = 4
#total_storage = 2
logfile = ''
# YJ add
cost = {"yolo1":{"SIZE":2.15},
        "yolo2":{"SIZE":2.83},
        "yolo3":{"SIZE":3.28},
        "yolo4":{"SIZE":3.58},
        "yolo5":{"SIZE":2.15},
        "yolo6":{"SIZE":2.83},
        "yolo7":{"SIZE":3.28},
        "yolo8":{"SIZE":3.58},
        "yolo9":{"SIZE":2.15},
        "yolo10":{"SIZE":2.83},
        "yolo11":{"SIZE":3.28},
        "yolo12":{"SIZE":3.58},
        "audio1":{"SIZE":1.94},
        "audio2":{"SIZE":2.36},
        "audio3":{"SIZE":3.02},
        "audio4":{"SIZE":3.31},
        "audio5":{"SIZE":1.94},
        "audio6":{"SIZE":2.36},
        "audio7":{"SIZE":3.02},
        "audio8":{"SIZE":3.31},
        "audio9":{"SIZE":1.94},
        "audio10":{"SIZE":2.36},
        "audio11":{"SIZE":3.02},
        "audio12":{"SIZE":3.31}}
#"audio5":{"SIZE":3.67}
#"yolo5":{"SIZE":3.93}

# Extraction time (s)
Extraction = {'audio1':50,
           'audio2':53,
           'audio3':137,
           'audio4':146,
           'audio5':78,
           'audio6':82,
           'audio7':82,
           'audio8':83,
           'audio9':237,
           'audio10':217,
           'audio11':212,
           'audio12':175,
           'yolo1':25,
           'yolo2':24,
           'yolo3':28,
           'yolo4':26,
           'yolo5':25,
           'yolo6':25,
           'yolo7':25,
           'yolo8':25,
           'yolo9':25,
           'yolo10':25,
           'yolo11':25,
           'yolo12':25}

# Not work if use sudo
def ssh_command(user, host, password, command):
      ssh_newkey = 'Are you sure you want to continue connecting'
      child = pexpect.spawn('ssh -t -l %s %s %s'%(user, host, command))
      child.timeout = 300
      i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
      # if Timeout 
      if i == 0: # Timeout  
          print('ERROR!')
          print('SSH could not login. Here is what SSH said:')
          print(child.before, child.after)
          return None
      # of no public key 
      if i == 1: # SSH does not have the public key. Just accept it.  
          child.sendline ('yes')
          child.expect ('password: ')
          i = child.expect([pexpect.TIMEOUT, 'password: '])
          if i == 0: # Timeout  
            print('ERROR!')
            print('SSH could not login. Here is what SSH said:')
            print(child.before, child.after)
          return None
      # send password 
      child.sendline(password)
      return child

"""
def ssh_command_paramiko(IP, username, password, port, command, is_sudo):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP,port,username, password)
    stdin, stdout, stderr = ssh.exec_command(command)
    #sudo_pw = getpass.getpass("sudo pw for %s: " % username)
    channel = ssh.invoke_shell() 
    channel.send( command+"\n" )       
    output = ''
    if is_sudo:
        while True:
            output = str(channel.recv(1024), 'utf-8')
            #print(output)
            if re.search(".*\[sudo\].*",output): 
                break
            time.sleep(1)
        channel.send( password+"\n" )
        time.sleep(1)
        output = str(channel.recv(1024), 'utf-8')
        print(output)
        if output.find("$") == -1:
            print(command + " error")
    if not is_sudo:
        output=stdout.readlines()
        print(output)
        exit_status = stdout.channel.recv_exit_status()        
        if exit_status != 0:
            print(command + " Error", exit_status)
    channel.close()
    return output
"""
def ssh_command_paramiko(IP, username, password, port, command, is_sudo):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP,port,username, password)
    outputs = ''
    if is_sudo:
        channel = ssh.invoke_shell() 
        channel.send( command+"\n" )       
        while True:
            output = str(channel.recv(1024), 'utf-8')
            #print(output)
            if re.search(".*\[sudo\].*",output): 
                break
            time.sleep(1)
        channel.send( password+"\n" )
        time.sleep(1)
        outputs = str(channel.recv(1024), 'utf-8')
        print(outputs)
        if outputs.find("$") == -1:
            print(command + " error")
        channel.close()
    # Not is_sudo:
    else:
        print_output = False
        tmp_end_num = 0
        channel = ssh.invoke_shell()
        channel.send( command+"\n" )       
        outputs = ''
        while True:
            output = str(channel.recv(1024), 'utf-8')
            if output.find("$") != -1:
                output = ''
                tmp_end_num += 1
            if tmp_end_num == 2:
                #print(command + " finish")
                break
            if print_output:
                outputs = outputs + output
            if output.find("Last login") != -1:
                print_output = True
        channel.close()
    return outputs


def BW_restrict(uplink, downlink):
    port = 22
    user = 'minion'
    host = os.environ['MINION']
    pwd = os.environ['PASSWORD']
    cmd = f'sudo wondershaper -a enp0s25 -d {downlink} -u {uplink}'
    ssh_command_paramiko(host, user, pwd, port, cmd, True)

def pub(num):
    host = os.environ['BROKER'] 
    topic = 'gateway'
    publish.single(topic, num, qos=1, hostname=host)

def log_CPU(num):
    user = 'minion'
    host = os.environ['MINION']
    pwd = os.environ['PASSWORD']
    cmd = 'for run in {1..20};do top -bcn1 -w512 | grep %Cpu | head -1; sleep 1; done'
    result = ssh_command(user, host, pwd, cmd)
    with open(f'CPU_{logfile}.log','a') as the_file:
         the_file.write(f'time: {num}')
         result.expect(pexpect.EOF)
         result = result.before.decode().rstrip()
         the_file.write(result+'\n')

def log_bandwidth(num):
    user = 'minion'
    host = os.environ['MINION']
    pwd = os.environ['PASSWORD']
    cmd = 'timeout 58 ifstat -t -n -i enp0s25 -b 3'
    #cmd = 'timeout 20 ifstat -t -n -i enx000972836258 1'
    result = ssh_command(user, host, pwd, cmd)
    with open(f'Bandwidth_{logfile}.log','a') as the_file:
         the_file.write(f'time: {num}')
         result.expect(pexpect.EOF)
         result = result.before.decode().rstrip()
         the_file.write(result+'\n')


def deploy(analytic_name, num):
        deployfile = analytic_name
        analytic = analytic_name+'-'+str(num) 
        command = f'sed -i "4c \ \ \ \ \ \ \ \ name: {analytic}" yaml/{deployfile}.yaml'
        subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
        command = f'sed -i "6c \ \ \ \ \ \ \ \ \ \ location: cloud" yaml/{deployfile}.yaml'
        subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
        command = f'sed -i "25c \ \ \ \ \ \ \ \ \ \ \ \ value: \"cloud\"" yaml/{deployfile}.yaml'
        subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
        command = f'sed -i "29c \ \ \ \ \ \ \ \ \ \ \ \ value: \"{analytic}\"" yaml/{deployfile}.yaml'
        subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
        command = f'sed -i "32c \ \ \ \ \ \ \ \ \ \ device: master" yaml/{deployfile}.yaml'
        subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
        command = f'kubectl create -f yaml/{deployfile}.yaml'
        subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
        print("Init deployed Analytic:", analytic)

def IDA(bandwidth, storage, num, algorithm_IDA, algorithm_LRP, epsilon):
    command = f'echo "**time:"{num} >> deploy_{logfile}.log'
    subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
    #command = f'python3 ../RunDeploy/deploy.py {bandwidth} {storage} {num} >> deploy.log'
    command = f'python3 ../RunDeploy/deploy_measure.py {bandwidth} {storage} {num} {algorithm_IDA} {algorithm_LRP} {epsilon} >> deploy_{logfile}.log'
    subprocess.run(command, shell=True, stderr=subprocess.STDOUT)

def RAA(num, bandwidth, algorithm_RAA, weight_ver, step_size=0.05):
    command = f'echo "**time:" {num} >> allocation_{logfile}.log'
    subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
    command = f'python3 ../RunAllocation/run.py {bandwidth} {algorithm_RAA} {weight_ver} {step_size} >> allocation_{logfile}.log'
    subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
 
def gateway_storage():
    port = 22
    user = os.environ['GATEWAY_USER']
    host = os.environ['MINION']
    pwd = os.environ['PASSWORD']
    gateway_dir = os.environ['GATEWAY_DIR']
    cmd = f'python {gateway_dir}/Implementation/Measurement/storage_usage.py'
    results = ssh_command_paramiko(host, user, pwd, port, cmd, False)
    file_name = f'Storage_{logfile}.log'
    if not os.path.exists(file_name):
        with open(file_name,'w'): pass
    with open(file_name,'a') as the_file:
        the_file.write(f'time: {num}')
        the_file.write('\n')
        the_file.write(results)
        the_file.write('\n')

if __name__ == "__main__":
    analytics_file = sys.argv[1]
    running_time = int(sys.argv[2])
    duration = int(sys.argv[3])
    network = sys.argv[4]
    num_analytics = int(sys.argv[5])
    num_analytics = 60 if num_analytics == 0 else num_analytics
    algorithm_IDA = sys.argv[6]
    algorithm_RAA = sys.argv[7] 
    algorithm_LRP = sys.argv[8] 
    request_file = sys.argv[9] 
    #qos_logfile = algorithm_IDA + '_' + algorithm_RAA + '_' + algorithm_LRP + '_' + request_file
    #logfile = network + '_' + algorithm_IDA + '_' + algorithm_RAA + '_' + algorithm_LRP + '_' + request_file
    qos_logfile = ''
    with open('Algorithm.log', 'r') as rf:
        qos_logfile = rf.read().strip()
    if len(sys.argv) >= 11:
        epsilon = sys.argv[10]
    else: epsilon = 0.1
    if len(sys.argv) >= 12:
        step_size = sys.argv[11]
    else: step_size = 0.05
    logfile = network + '_' + algorithm_IDA + '_' + algorithm_RAA + '_' + algorithm_LRP + '_' + epsilon + '_' + step_size + '_' + request_file
        
    if network == '4G':
        #uplink = 16970
        uplink = int(16.97*1024)
        #downlink = 22750
        downlink = int(22.67*1024)
    elif network == '3G':
        uplink = 2890
        downlink = 9610
    elif network == 'optical':
        # 100Mbps/10Mbps = 100*1000Kbps/5*1000Kbps
        uplink = 5*1000
        downlink = 100*1000
    elif network == 'optical50':
        # 50Mbps/5Mbps = 50*1000Kbps/5*1000Kbps
        uplink = 5*1000
        downlink = 50*1000
    elif network == 'up10':
        # 100Mbps/5Mbps = 100*1000Kbps/10*1000Kbps
        uplink = 10*1000
        downlink = 100*1000
    elif network == 'up75':
        # 100Mbps/7.5Mbps = 100*1000Kbps/7.5*1000Kbps
        uplink = 7.5*1000
        downlink = 100*1000
    elif network == 'up25':
        # 100Mbps/2.5Mbps = 100*1000Kbps/2.5*1000Kbps
        uplink = 2.5*1000
        downlink = 100*1000

    bandwidth = uplink
    BW_restrict_thread = threading.Thread(target = BW_restrict, args=[bandwidth, downlink])
    BW_restrict_thread.start()

    # read request
    requests = []
    lines = [line.rstrip('\n') for line in open(analytics_file)]
    for line in lines:
        app = line.split(',')[0]
        arivial = int(line.split(',')[1])
        departure = int(line.split(',')[2])
        requests.append([app, arivial, departure])
    # write to log
    command = f'echo "========" >> deploy_{logfile}.log'
    subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
    command = f'echo "num: {num_analytics} running time:{running_time} bandwidth:{downlink}" >> deploy_{logfile}.log'
    subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
    command = f'echo "num: {num_analytics} running time:{running_time} bandwidth:{bandwidth}" >> allocation_{logfile}.log'
    subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
    # initialize
    num = 0
    used_storage = 0
    #total_storage = 3
    reject = 0
    # Run
    sys_analytics = []
    pub_thread = threading.Thread(target = pub, args=[running_time])
    pub_thread.start()
    deploy_threads = []
    delete_processes = []
    time_start = time.time()
    old_time_end = time_start
    removed_analytics = []
    all_departures = []
    while num <= running_time:

        CPUlog_thread = threading.Thread(target = log_CPU, args=[num])
        CPUlog_thread.start()
        BWlog_thread = threading.Thread(target = log_bandwidth, args=[num])
        BWlog_thread.start()
        print("time:", num)

        #print('requests', requests)
        #print('num_analytics', num_analytics)
        # arrival
        if len(sys_analytics) < num_analytics+1 and len(requests) > 0:
            #print('1 requests[0]', requests[0])
            while requests[0][1] == num:
                #print('Arrival: requests[0]', requests[0])
                deploy_thread = threading.Thread(target = deploy,args=[requests[0][0], num])
                deploy_thread.start()
                requests[0][1] = 0
                requests[0][0] = requests[0][0]+'-'+str(num)
                sys_analytics.append(requests[0])
                del requests[0]
                # YJ comment
                #deploy_thread.join()
                # YJ add
                deploy_threads.append(deploy_thread)
                if len(requests) == 0: break
        elif len(requests) > 0:
            #print('2 requests[0]', requests[0])
            while requests[0][1] == num:
                #print('Too many arrival: requests[0]', requests[0])
                del requests[0]
                reject += 1
                if len(requests) == 0: break

        # departure
        command = f'kubectl get pods | wc -l'
        departure = []
        line_num = subprocess.check_output([command], shell=True).decode('utf-8')
        if int(line_num) > 1:
            # Delete app which cannot be delete in time
            edge_analytics = subprocess.check_output(["kubectl","get","pods","-l","location=edge"]).splitlines()[1:]
            cloud_analytics = subprocess.check_output(["kubectl","get","pods","-l","location=cloud"]).splitlines()[1:]
            for rem_analytic in removed_analytics:
                rem_analytic = rem_analytic.split('-')[0] + '-' + rem_analytic.split('-')[-1]
                #print('Removed app: ' + rem_analytic.split('-')[0] + '-' + rem_analytic.split('-')[-1])
                for analytic in edge_analytics:
                    analytic_info = ''.join(analytic.decode("utf-8").split(' ')).split('/')[0]
                    analytic_info = analytic_info[:-1]
                    #print('Stuck edge app: ' + analytic_info.split('-')[0] + '-' + analytic_info.split('-')[-1])
                    if analytic_info.split('-')[0]+'-'+analytic_info.split('-')[-1] == rem_analytic:
                        command = f'kubectl delete pods {analytic_info}'
                        delete_processes.append(subprocess.Popen([command], shell=True))
                        print('Delete stuck app:', analytic_info)
                        all_departures.append(analytic_info)
                for analytic in cloud_analytics:
                    analytic_info = ''.join(analytic.decode("utf-8").split(' ')).split('/')[0]
                    analytic_info = analytic_info[:-1]
                    #print('Stuck cloud app: ' + analytic_info.split('-')[0] + '-' + analytic_info.split('-')[-1])
                    if analytic_info.split('-')[0]+'-'+analytic_info.split('-')[-1] == rem_analytic:
                        command = f'kubectl delete pods {analytic_info}'
                        delete_processes.append(subprocess.Popen([command], shell=True))
                        print('Delete stuck app:', analytic_info)
                        all_departures.append(analytic_info)
                    
            #departure = []
            command = f'kubectl get pods'
            app_list = subprocess.check_output([command], shell=True)
            app_ids = []
            for line in app_list.decode('utf-8').split('\n'):
                app_ids.append(line.split(' ')[0])
            for i in range(len(sys_analytics)):
                if sys_analytics[i][1] == sys_analytics[i][2]:
                    departure.append(sys_analytics[i])
                    if sys_analytics[i][0] not in app_ids:
                        sys_analytics[i][0] = sys_analytics[i][0].split('-')[0]+'-edge-'+sys_analytics[i][0].split('-')[1]
                    command = f'kubectl delete pods {sys_analytics[i][0]}'
                    print(f'init delete pods {sys_analytics[i][0]}')
                    delete_processes.append(subprocess.Popen([command], shell=True))
                    removed_analytics.append(sys_analytics[i][0])
                elif sys_analytics[i][0] not in app_ids:
                     app_name = sys_analytics[i][0].split('-')[0]
                     app_version = sys_analytics[i][0].split('-')[1]
                     if app_name+'-edge-'+app_version in app_ids:
                       sys_analytics[i][0] = app_name+'-edge-'+app_version
                       sys_analytics[i][1] += 1 
                       print(f'[Departure] {sys_analytics[i][0]}:{sys_analytics[i][1]}/{sys_analytics[i][2]}')
                elif sys_analytics[i][0] in app_ids:
                       sys_analytics[i][1] += 1 
                       print(f'[Departure] {sys_analytics[i][0]}:{sys_analytics[i][1]}/{sys_analytics[i][2]}')
            for analytic in departure:
               sys_analytics.remove(analytic)
            ''' 
            # Delete app which cannot be delete in time
            edge_analytics = subprocess.check_output(["kubectl","get","pods","-l","location=edge"]).splitlines()[1:]
            cloud_analytics = subprocess.check_output(["kubectl","get","pods","-l","location=cloud"]).splitlines()[1:]
            for rem_analytic in removed_analytics:
                rem_analytic = rem_analytic.split('-')[0] + '-' + rem_analytic.split('-')[-1]
                for analytic in edge_analytics:
                    analytic_info = ''.join(analytic.decode("utf-8").split(' ')) 
                    if analytic_info.split('-')[0]+'-'+analytic_info.split('-')[-1] == rem_analytic:
                        command = f'kubectl delete pods {analytic_info}'
                        delete_processes.append(subprocess.Popen([command], shell=True))
                for analytic in cloud_analytics:
                    analytic_info = ''.join(analytic.decode("utf-8").split(' ')) 
                    if analytic_info.split('-')[0]+'-'+analytic_info.split('-')[-1] == rem_analytic:
                        command = f'kubectl delete pods {analytic_info}'
                        delete_processes.append(subprocess.Popen([command], shell=True))
             '''      

        # Run Allocation algo
        edge_analytics = subprocess.check_output(["kubectl","get","pods","-l","location=edge"]).splitlines()[1:]

        used_bandwidth = 0
        used_storage = 0
        '''
        if "yolo" in edge_analytics:
            used_storage += 1.81
        if "audio" in edge_analytics:
            used_storage += 2.03
        '''
        counted_analytics = []
        for analytic in edge_analytics:
            analytic_info = ''.join(analytic.decode("utf-8").split(' ')) 

            analytic = analytic_info.split('-')[0]
            if analytic not in counted_analytics:
                used_storage += cost[analytic]["SIZE"]
                counted_analytics.append(analytic)

            status = analytic_info[12:19]
            if status == "Running":
                if "yolo" in analytic_info:
                    used_bandwidth = used_bandwidth + 107
                elif "audio" in analytic_info:
                    used_bandwidth = used_bandwidth + 0.0342
        print('used_storage: ',used_storage,'used bandwidth: ',used_bandwidth)
        bandwidth = bandwidth - used_bandwidth

        RAA_thread = threading.Thread(target = RAA, args=[num, bandwidth, algorithm_RAA, request_file, step_size])
        RAA_thread.start()
        with open ('qos_'+qos_logfile+'_yolo.log', 'a') as qos_wf:
            qos_wf.write('\n========== Time: ' + str(num) + ' ==========\n')
        with open ('qos_'+qos_logfile+'_audio.log', 'a') as qos_wf:
            qos_wf.write('\n========== Time: ' + str(num) + ' ==========\n')
   
        # List cloud app
        print('departure', departure)
        for d in departure:
            all_departures.append(d[0])
        with open('../RunDeploy/departure_analytics.txt', 'w') as wf:
            for d in all_departures[:-1]:
                wf.write(d)
                wf.write('\n')
            if len(all_departures) > 0:
                wf.write(all_departures[-1])
        print('all_departures', all_departures)
        cmd = f'kubectl get pods -l location=cloud> ../RunDeploy/list.txt'
        subprocess.run([cmd], shell=True)
        fr = open("../RunDeploy/list.txt","r")
        fw = open("../RunDeploy/analytics.input","w")
        for line in fr:
            app = line.split(" ")[0]
            if '-' in app and app not in all_departures:
               fw.write(app+ '\n')
        fr.close()
        fw.close()

        is_terminal = False
        # Run Deployment algo
        if num == duration:
            storage = total_storage
            # YJ comment
            IDA_thread = threading.Thread(target = IDA, args=[downlink, storage, num, algorithm_IDA, algorithm_LRP, epsilon])
            IDA_thread.start()
            with open('../RunDeploy/terminal.input', 'w') as f:
                f.write('False')
                print('write terminal.input False')
            is_terminal = False
        elif num%duration == 0 and num!= 0:
            while IDA_thread.isAlive() and not is_terminal:
                print('IDA_thread is Alive')
                is_replacing = 'True'
                replace_time = '0'
                while is_replacing != 'False':
                    with open('../RunDeploy/replace_time.input', 'r') as f:
                        replace_time = f.read().strip()
                    if replace_time != '':
                        is_replacing, replace_time = replace_time.split(',')
                    if is_replacing == 'False': break
                    time.sleep(10)
                print('Sleep replace time: ' + replace_time)
                time.sleep(int(replace_time))
    
                # Add extraction time
                # Read exist images on gateway
                images = []
                with open('../RunDeploy/exist.input', 'r') as f:
                    content = f.read().strip()
                    if ',' in content:
                        images = content.split(',')
                print('images', images)
                exist_images = []
                # E.g., 192.168.1.100:5000/iscc19:s2-audio-1 -> audio1
                for image in images:
                     exist_images.append(image.split('-', 2)[1]+image.split('-', 2)[2]) 
                print('exist_images', exist_images)
                # Read expect deploy analytics
                expect_analytics = []
                with open('../RunDeploy/expect.input', 'r') as f:
                    content = f.read().strip()
                    if ',' in content:
                        expect_analytics = content.split(',')
                print('expect_analytics', expect_analytics)
                # Add extraction time
                extract_images = []
                for analytic in expect_analytics:
                    if analytic not in exist_images and analytic not in extract_images:
                        print('Extract image: ' + analytic)
                        print('Extraction time: ' + str(Extraction[analytic]) + ' s')
                        time.sleep(Extraction[analytic]) 
                        extract_images.append(analytic)
                print('extract_images', extract_images)
                
                # Write terminal file        
                with open('../RunDeploy/terminal.input', 'w') as f:
                    f.write('True')
                    print('write terminal.input True')
                is_terminal = True
                time.sleep(5)
            while IDA_thread.isAlive():
                time.sleep(5)
            storage = total_storage
            IDA_thread = threading.Thread(target = IDA, args=[downlink, storage, num ,algorithm_IDA, algorithm_LRP, epsilon])
            IDA_thread.start()
            with open('../RunDeploy/terminal.input', 'w') as f:
                f.write('False')
                print('write terminal.input False')
            is_terminal = False

        # YJ Added
        command = f'kubectl get pods -l location=cloud'
        app_list_cloud = subprocess.check_output([command], shell=True)
        apps_cloud = []
        for line in app_list_cloud.decode('utf-8').split('\n'):
            apps_cloud.append(line.split(' ')[0])
        print('Pods in cloud: ', apps_cloud[:-1])
        command = f'kubectl get pods -l location=edge'
        app_list_edge = subprocess.check_output([command], shell=True)
        apps_edge = []
        for line in app_list_edge.decode('utf-8').split('\n'):
            apps_edge.append(line.split(' ')[0])
        print('Pods in edge: ', apps_edge[1:-1])
        
        gateway_storage()

        num = num + 1
        if time.time() - old_time_end < 60:
            time.sleep(60-(time.time() - old_time_end))
        else:
            time.sleep(1)
        time_end = time.time()
        print('The passed time: ', time_end - time_start)
        print('The time of this iteration:', time_end - old_time_end)
        old_time_end = time_end
    print("reject:", reject)
    print("=============== Time Out ===============")
    for thread in deploy_threads:
        thread.join()
    for process in delete_processes:
        process.wait()
    print('Total used time: ', time.time()-time_start)
    sys.exit(0)
