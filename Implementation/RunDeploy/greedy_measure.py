#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__author__ = YuJung Wang
"""

import os
import sys
import random
import logging
import pexpect
import subprocess
import paho.mqtt.client as mqtt

num = 0
cost={'yolo1':2.15,  'yolo2':2.83,  'yolo3':3.28,  'yolo4':3.58,  'yolo5':3.93,
      'audio1':1.94, 'audio2':2.36, 'audio3':3.02, 'audio4':3.31, 'audio5':3.67}
overall_repo = os.environ['DOCKER_PROVIDER'] + '/' + os.environ['DOCKER_REPO']

def map_index(app_image):
       if app_image == 'yolo1':
          deleted_app = 'yolo1'
          image_index = 0
       elif app_image == 'yolo2':
          deleted_app = 'yolo2'
          image_index = 1
       elif app_image == 'yolo3':
          deleted_app = 'yolo3'
          image_index = 2
       elif app_image == 'yolo4':
          deleted_app = 'yolo4'
          image_index = 3
       elif app_image == 'yolo5':
          deleted_app = 'yolo5'
          image_index = 4
       elif app_image == 'audio1':
          deleted_app = 'audio1'
          image_index = 5
       elif app_image == 'audio2':
          deleted_app = 'audio2'
          image_index = 6
       elif app_image == 'audio3':
          deleted_app = 'audio3'
          image_index = 7
       elif app_image == 'audio4':
          deleted_app = 'audio4'
          image_index = 8
       elif app_image == 'audio5':
          deleted_app = 'audio5'
          image_index = 9
       return deleted_app, image_index

def ssh_command (user, host, password, command):
    ssh_newkey = 'Are you sure you want to continue connecting'
    
    child = pexpect.spawn('ssh -l %s %s %s'%(user, host, command))
    child.timeout = 900
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

def createLogHandler(job_name,log_file):
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    logger = logging.getLogger(job_name)
    ## create a file handler ##
    handler = logging.FileHandler(log_file)
    ## create a logging format ##
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    return logger

def delete(app_id):
    cmd = f'kubectl delete pods {app_id}'
    p = subprocess.Popen([cmd], shell=True)
    return p

def deploy_measure(image_index, device_index, i):
        image_list = ["yolo1","yolo2","yolo3","yolo4","yolo5","audio1","audio2",
                "audio3","audio4","audio5"]
        device_list = ["cloud","edge"]

        image_name = image_list[image_index]

        if image_name[:4] == 'yolo': frequency = 1
        elif image_name[:5] == 'audio': frequency = 3
        frequency_str = '\\"'+str(frequency)+'\\"'

        if device_index == 1:
            app_str = '\\"'+image_name+'-edge-'+str(i)+'\\"'
        elif device_index ==0:
            app_str = '\\"'+image_name+'-'+str(i)+'\\"'

        device_str = '\\"'+device_list[device_index]+'\\"' 

        if device_index == 1:
           node_str = '\\"'+"minion-nuc-cloud"+'\\"' 
        elif device_index ==0:
           node_str = '\\"'+"master"+'\\"' 

        path = 'yaml/edge'
        # find app name
        cmd = f'grep -n "metadata" {path}/{image_name}.yaml'
        res_grep = os.popen(cmd).readlines()
        # replace specific line
        line = int(res_grep[0].split(":")[0])+1
        cmd = f'sed -i "{line}s/^.*$/        name: {image_name}-edge-{i}/g" {path}/{image_name}.yaml'
        os.system(cmd)

        # fine labels
        cmd = f'grep -n "labels" {path}/{image_name}.yaml'
        res_grep = os.popen(cmd).readlines()
        # replace location
        line = int(res_grep[0].split(":")[0])+1
        cmd = f'sed -i "{line}s/^.*$/          location: {device_list[device_index]}/g" {path}/{image_name}.yaml'
        os.system(cmd)

        # find nodeSelector
        cmd = f'grep -n "nodeSelector" {path}/{image_name}.yaml'
        res_grep = os.popen(cmd).readlines()
        # replace node
        line = int(res_grep[0].split(":")[0])+1
        cmd = f'sed -i "{line}s/^.*$/          device: {node_str}/g" {path}/{image_name}.yaml'
        os.system(cmd)

        # find DEVICE
        cmd = f'grep -n "DEVICE" {path}/{image_name}.yaml'
        res_grep = os.popen(cmd).readlines()
        # replace device
        line = int(res_grep[0].split(":")[0])+1
        cmd = f'sed -i "{line}s/^.*$/            value: {device_str}/g" {path}/{image_name}.yaml'
        os.system(cmd)

        # find APP
        cmd = f'grep -n "APP" {path}/{image_name}.yaml'
        res_grep = os.popen(cmd).readlines()
        # replace app
        line = int(res_grep[0].split(":")[0])+1
        cmd = f'sed -i "{line}s/^.*$/            value: {app_str}/g" {path}/{image_name}.yaml'
        os.system(cmd)

        # find FREQUENCY
        cmd = f'grep -n "PERIOD" {path}/{image_name}.yaml'
        res_grep = os.popen(cmd).readlines()
        # replace specific line
        line = int(res_grep[0].split(":")[0])+1
        cmd = f'sed -i "{line}s/^.*$/            value: {frequency_str}/g" {path}/{image_name}.yaml'
        os.system(cmd)

        # deploy to gateway
        user = 'minion'
        host = os.environ['MINION']
        pwd = os.environ['PASSWORD']

        app = image_name[:-1]
        version = image_name[-1]
        image_tag = f's2-{app}-{version}' 
        cmd = f'time docker pull {overall_repo}:{image_tag} '

        deploy_result = ssh_command (user, host, pwd, cmd)
        #print(deploy_result)
        deploy_result.expect(pexpect.EOF)
        deploy_info = deploy_result.before.decode().rstrip().replace(' ','')

        print(deploy_info)

        cmd = f'kubectl create -f {path}/{image_name}.yaml'
        # YJ comment
        #os.system(cmd)
        # YJ add
        #p = subprocess.Popen([cmd], stdout=PIPE, stderr=STDOUT, shell=True)
        logger.info(f'successfully deploy {image_name} with period {frequency}')
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (stdoutput,erroutput) = p.communicate()
        print('k8s create analytic stdoutput:')
        if stdoutput is not None:
            print(stdoutput)
        print('k8s create analytic erroutput:')
        if erroutput is not None:
            print(erroutput)
       
        #print(f'successfully deploy {image_name} with period {frequency}')
        #cmd = f'kubectl get pods'
        #os.system(cmd)
        
        # YJ add
        return p

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("iot/iscc19/deploy/+")

def on_message(client, userdata, msg):
    print(msg.topic+"  received")
    print(msg.topic.split('/')[3],msg.payload.decode())

    #if device == 'cloud':
    if msg.topic.split('/')[3] == 'cloud':
       device_index = 0
    else:
       device_index == 1

    if msg.payload.decode() == 'yolo':
        image_index = 0
    else:
        image_index = 1
    print("deploying...",image_index, device_index, num)
    deploy(image_index, device_index, num)
    print("deploy done")
    num = num + 1
        
if __name__ == '__main__':
    time = int(sys.argv[3])
    job_name = 'log'
    log_file = 'deploy.log'
    logger = createLogHandler(job_name ,log_file )
    logger.info("run deploy_algo.py") 

    user = os.environ['GATEWAY_USER']
    host = os.environ['MINION']
    pwd = os.environ['PASSWORD']
    gateway_dir = os.environ['GATEWAY_DIR']

    # List cloud app
    cmd = f'kubectl get pods -l location=cloud> ../RunDeploy/list.txt'
    subprocess.run([cmd], shell=True)

    app = []
    fr = open("../RunDeploy/list.txt","r")
    fw = open("../RunDeploy/analytics.input","w")
    for line in fr:
        app = line.split(" ")[0]
        if '-' in app:
           fw.write(app+ '\n')
    fr.close()
    fw.close()
    if len(app) == 0:
       sys.exit('[IDA] no analytics in system')

    # Send cloud app list to gateway
    cmd = f'sshpass -p {pwd} scp ../RunDeploy/analytics.input {user}@{host}:{gateway_dir}/Implementation/Algo/Download/'
    subprocess.run([cmd], shell=True)


    ## -----------  Replacement  ---------- ##
    total_size = float(sys.argv[2])
    high_level = 0.8 
    low_level = 0.6
    policy = 'LRU'
    analytics = f'gateway_dir}/Implementation/Algo/Download/analytics.input'
    script = f'{gateway_dir}/Implementation/Algo/Replacement/replacement_algo.py'
    print("======Replacement======")
    print('high_level:', high_level, 'low_level', low_level, 'policy:', policy)
    cmd = f'python3 {script} {total_size} {high_level} {low_level} {policy}'
    delete_result = ssh_command (user, host, pwd, cmd)
    delete_result.expect(pexpect.EOF)
    delete_info = delete_result.before.decode().rstrip().replace(' ','')
    print(delete_info)
    print("======Replacement Done======")

    ## --------------- IDA --------------- ##
    script = f'{gateway_dir}/Implementation/Algo/Download/greedy_algo.py'
    eps = '0.1'
    total_size = float(sys.argv[2])
    bw = int(float(sys.argv[1]))
    # check edge app
    cmd = f'kubectl get pods -l location=edge'
    output = os.popen(cmd).read()
    used_sz = 0
    try:
       app_ids = [line.split(' ')[0].replace(' ','') for line in output.rstrip().split('\n')[1:]]
       apps = list(dict.fromkeys([a.split('-')[0] for a in app_ids]))
       for app_id in apps:
           used_sz += cost[app_id]
    except IndexError: 
       print('no analytics in edge')
    rsize = total_size - used_sz

    print("======Deploy Algo Result======")

    if len(app_ids) >= 4:
       print("edge full")
       sys.exit(0)
    # check cloud app
    cmd = f'kubectl get pods -l location=cloud'
    output = os.popen(cmd).read()
    try:
       cloudapp_ids = [line.split(' ')[0].replace(' ','') for line in output.rstrip().split('\n')[1:]]
    except IndexError: 
       print('no analytics in cloud')

    common_app = []
    for cloudapp in cloudapp_ids:
        for app in app_ids:
            if cloudapp.split('-')[0] == app.split('-')[0]:
               common_app.append(cloudapp)
    # YJ add
    # Avoid Duplicate
    dup_apps = []
    for app in common_app:
        if app not in dup_apps:
            dup_apps.append(app)
    common_app = dup_apps 

    print('cloud apps: ', cloudapp_ids)
    print('edge apps: ', app_ids)
    print('common: ', common_app)
    
    # YJ add
    delete_processes = []
    deploy_processes = [] 
          
    analytics = f'{gateway_dir}/Implementation/Algo/Download/analytics.input'
    cmd = f'python {script} {total_size} {bw} {analytics}' 
    #cmd = f'python {script} {eps} {rsize} {bw} {analytics}' 
    download_result = ssh_command (user, host, pwd, cmd)
    download_result.expect(pexpect.EOF)
    deploy_info = download_result.before.decode().rstrip().replace(' ','')

    print(deploy_info)
    try:
      cloud = deploy_info.split(',')[0].split('>')[1].split(';')
      edge = deploy_info.split(',')[1].split('>')[1].split(';')
    except IndexError as error:
      print('No Analytics in System')
      sys.exit('no need to download (deploy)\n' + deploy_info)

    num = time
    print("Edge:",edge)
    print("Cloud:",cloud)
       
    # YJ add
    deploy_processes = []
    terminal_file = '../RunDeploy/terminal.input'
    #terminal_file = os.getcwd() + '/' + terminal_file
    index = 0

    for app in edge:
        # YJ add
        # Terminal setting
        is_terminal = False
        with open(terminal_file, 'r') as f:
            is_terminal = True if f.readline().strip() == 'True' else False
            print('terminal file content: ', f.readline().strip())
            print('is_terminal: ', is_terminal)
        if is_terminal:
            print('Terminal deploy_measure, terminal at: ' + app + ', index: ' + str(index))
            break
        index += 1


        device_index = 1
        app_image = app
        print('after IDA app: ', app_image) 
        # check if need delete
        if app_image in app_ids or app_image == '':
            print('continue app: ', app_image)
            continue

        #print("deploying...",image_index, device_index, num)
        try:
            deleted_app, image_index = map_index(app_image)
            print('app_image:', app_image)
            if app_image[0:5] == 'audio':
                for cloud_app in cloudapp_ids:
                    print('cloud_app:', cloud_app)
                    if app_image[0:6] == cloud_app[0:6]:
                        app_id = cloud_app
                        cloudapp_ids.remove(cloud_app)
                        break
            elif app_image[0:4] == 'yolo':
                for cloud_app in cloudapp_ids:
                    print('cloud_app:', cloud_app)
                    if app_image[0:5] == cloud_app[0:5]:
                        app_id = cloud_app
                        cloudapp_ids.remove(cloud_app)
                        break
            delete_processes.append(delete(app_id))
            deploy_processes.append(deploy_measure(image_index, device_index, app_id.split('-')[1]))
            print("Deploy:", app_id)
            print('try deploy app number: ', app_id.split('-')[1])
        except:
            print("Deploy:", app_id)
            print('Fail to deploy app number: ', app_id.split('-')[1])
            print('no need to download (edge), time: ', num)
            sys.exit('no need to download (edge)\n' + output)
          
    
    # YJ add
    for process in deploy_processes:
        process.wait()
    for process in delete_processes:
        process.wait()
