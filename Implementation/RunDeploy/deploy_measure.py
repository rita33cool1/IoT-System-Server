#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/02'

import os
import re
import sys
import time
import random
import logging
import pexpect
import paramiko
import subprocess
import paho.mqtt.client as mqtt

num = 0
BW_ratio = 1
cost={'yolo1':2.15,  'yolo2':2.83,  'yolo3':3.28,  'yolo4':3.58,  'yolo5':3.93,
      'audio1':1.94, 'audio2':2.36, 'audio3':3.02, 'audio4':3.31, 'audio5':3.67}
MAX_EDGE_APPS=8
overall_repo = os.environ['DOCKER_PROVIDER'] + '/' + os.environ['DOCKER_REPO']
image_list = [
    "yolo1","yolo2","yolo3","yolo4","yolo5","yolo6","yolo7","yolo8",
    "yolo9","yolo10","yolo11","yolo12","audio1","audio2","audio3","audio4",
    "audio5","audio6","audio7","audio8","audio9","audio10","audio11","audio12"
]
deploy_analytics = []

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
       elif app_image == 'yolo6':
          deleted_app = 'yolo6'
          image_index = 5
       elif app_image == 'yolo7':
          deleted_app = 'yolo7'
          image_index = 6
       elif app_image == 'yolo8':
          deleted_app = 'yolo8'
          image_index = 7
       elif app_image == 'yolo9':
          deleted_app = 'yolo9'
          image_index = 8
       elif app_image == 'yolo10':
          deleted_app = 'yolo10'
          image_index = 9
       elif app_image == 'yolo11':
          deleted_app = 'yolo11'
          image_index = 10
       elif app_image == 'yolo12':
          deleted_app = 'yolo12'
          image_index = 11
       elif app_image == 'audio1':
          deleted_app = 'audio1'
          image_index = 12
       elif app_image == 'audio2':
          deleted_app = 'audio2'
          image_index = 13
       elif app_image == 'audio3':
          deleted_app = 'audio3'
          image_index = 14
       elif app_image == 'audio4':
          deleted_app = 'audio4'
          image_index = 15
       elif app_image == 'audio5':
          deleted_app = 'audio5'
          image_index = 16
       elif app_image == 'audio6':
          deleted_app = 'audio6'
          image_index = 17
       elif app_image == 'audio7':
          deleted_app = 'audio7'
          image_index = 18
       elif app_image == 'audio8':
          deleted_app = 'audio8'
          image_index = 19
       elif app_image == 'audio9':
          deleted_app = 'audio9'
          image_index = 20
       elif app_image == 'audio10':
          deleted_app = 'audio10'
          image_index = 21
       elif app_image == 'audio11':
          deleted_app = 'audio11'
          image_index = 22
       elif app_image == 'audio12':
          deleted_app = 'audio12'
          image_index = 23
       return deleted_app, image_index

def ssh_command(user, host, password, command):
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

def ssh_command_paramiko(IP, username, password, port, command, is_sudo):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP,port,username, password)
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
        output = str(channel.recv(1024), 'utf-8')
        print(output)
        if output.find("$") == -1:
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
    #cmd = f'kubectl get pods -l location=cloud | grep "{app}"'
    #output = os.popen(cmd).read()
    #output = subprocess.check_output(["kubectl","get","pods","-l","location=cloud","|","grep",f'"{app}"'], shell=True)
    #app_id = output.rstrip().split(' ')[0].replace(' ','')
    cmd = f'kubectl delete pods {app_id}'
    # YJ comment
    #subprocess.run([cmd], shell=True)
    # YJ add
    p = subprocess.Popen([cmd], shell=True)
    return p

def deploy_measure(image_index, device_index, i):
    #image_list = ["yolo1","yolo2","yolo3","yolo4","yolo5","audio1","audio2",
    #        "audio3","audio4","audio5"]
    #frequency_list = [1,2,3]
    device_list = ["cloud","edge"]

    image_name = image_list[image_index]

    #frequency_index = random.randint(0,2)
    #frequency = frequency_list[frequency_index]
    if image_name[:4] == 'yolo': frequency = 2
    elif image_name[:5] == 'audio': frequency = 3
    frequency_str = '\\"'+str(frequency)+'\\"'

    if device_index == 1:
        app_str = '\\"'+image_name+'-edge-'+str(i)+'\\"'
    elif device_index ==0:
        app_str = '\\"'+image_name+'-'+str(i)+'\\"'

    #device_index = random.randint(0,1)
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
    port = 22
    app = image_name[:-1]
    version = image_name[-1]
    if 'yolo' in image_name:
        app = 'yolo'
        version = image_name.split('yolo')[-1]
    elif 'audio' in image_name:
        app = 'audio'
        version = image_name.split('audio')[-1]
    image_tag = f's2-{app}-{version}' 
    cmd = f'time docker pull {overall_repo}:{image_tag} '
    deploy_start = float(time.time())
    deploy_result = ssh_command (user, host, pwd, cmd)
    #print(deploy_result)
    deploy_result.expect(pexpect.EOF)
    deploy_info = deploy_result.before.decode().rstrip().replace(' ','')
    print(deploy_info)
    # Check download or not
    is_download = False
    if time.time() - deploy_start > 15:
        is_download = True
        print('is_download: True')
    else: 
        print('is_download: False')

    departures = []
    is_deploy = True
    with open('../RunDeploy/departure_analytics.txt', 'r') as rf:
        for line in rf.readlines():
            if '-' in line.strip():
                departures.append(line.strip())
    for analytic in departures:
        if analytic.split('-',1)[0] == image_name and analytic.split('-')[-1] == str(i):
            is_deploy = False
    global deploy_analytics
    if is_deploy:
        cmd = f'kubectl create -f {path}/{image_name}.yaml'
        logger.info(f'successfully deploy {image_name} with period {frequency}')
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (stdoutput,erroutput) = p.communicate()
        print('k8s create analytic stdoutput:')
        if stdoutput is not None:
            print(stdoutput)
        print('k8s create analytic erroutput:')
        if erroutput is not None:
            print(erroutput)
        deploy_analytics.append(overall_repo+':'+image_tag)
    else:
        logger.info(f'fail to deploy {image_name} with period {frequency} since {image_name} has departured')
        print(f'fail to deploy {image_name} with period {frequency} since {image_name} has departured')       
        if is_download:
            deploy_analytics.append(overall_repo+':'+image_tag)

    #print(f'successfully deploy {image_name} with period {frequency}')
    #cmd = f'kubectl get pods'
    #os.system(cmd)
    
    # YJ add
    return p

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("iot/iscc19/deploy/+")

def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
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
    sys_time = int(sys.argv[3])
    algorithm_IDA = sys.argv[4]
    algorithm_LRP = sys.argv[5]
    alpha = sys.argv[6]
    job_name = 'log'
    log_file = 'deploy.log'
    logger = createLogHandler(job_name ,log_file )
    logger.info("run deploy_algo.py") 

    user = os.environ['GATEWAY_USER']
    host = os.environ['MINION']
    pwd = os.environ['PASSWORD']
    gateway_dir = os.environ['GATEWAY_DIR']
    port = 22

    app = []
    fr = open("../RunDeploy/analytics.input","r")
    for line in fr.readlines():
        a = line.strip()
        if '-' in a:
           app.append(a)
    fr.close()
    if len(app) == 0:
       sys.exit('[IDA] no analytics in system')

    # Send cloud app list to gateway
    cmd = f'sshpass -p {pwd} scp ../RunDeploy/analytics.input {user}@{host}:{gateway_dir}/Implementation/Algo/Download/'
    subprocess.run([cmd], shell=True)


    ## -----------  Replacement  ---------- ##
    print("======Replacement======")
    replace_time_file = '../RunDeploy/replace_time.input'
    print('Start replacing and Lock replace_time.input')
    with open(replace_time_file, 'w') as f:
        f.write('True,0')
    #if rsize/total_size < 0.2:      
    total_size = float(sys.argv[2])
    #delee_size = 0.2*total_size 
    high_level = 0.8
    low_level = 0.6
    #policy = 'LRU'
    policy = algorithm_LRP
    analytics = f'{gateway_dir}/Implementation/Algo/Download/analytics.input'
    script = f'{gateway_dir}/Implementation/Algo/Replacement/replacement_algo.py'
    print('high_level:', high_level, 'low_level', low_level, 'policy:', policy)
    cmd = f'python3 {script} {total_size} {high_level} {low_level} {policy}' 

    delete_info = ssh_command_paramiko(host, user, pwd, port, cmd, False)
    print(delete_info)
    # Replace time
    replace_time = float(delete_info.split('\ntime: ')[-1].split('\n')[0].strip())
    print('Replace time: ' + str(int(round(replace_time))))
    with open(replace_time_file, 'w') as f:
        f.write('False,' + str(int(round(replace_time))))

    # Exist images
    content =  delete_info.split("exist_images: [", 1)[1].split("]", 1)[0]
    exist_images = []
    print('content', content)
    if content != '':
        exist_images = content[1:-1].split("', '")
    exist_file = '../RunDeploy/exist.input'
    with open(exist_file, 'w') as f:
        for img in exist_images[:-1]:
            f.write(img + ',')
        if len(exist_images) > 0:
            f.write(exist_images[-1])

    print("======Replacement Done======")

    ## --------------- IDA --------------- ##
    script = f'{gateway_dir}/Implementation/Algo/Download/download_algo.py'
    #eps = '0.1'
    total_size = float(sys.argv[2])
    bw = int(float(sys.argv[1]))
    # check edge app
    cmd = f'kubectl get pods -l location=edge'
    output = os.popen(cmd).read()
    #used_sz = 0
    try:
       app_ids = [line.split(' ')[0].replace(' ','') for line in output.rstrip().split('\n')[1:]]
       apps = list(dict.fromkeys([a.split('-')[0] for a in app_ids]))
       #for app_id in apps:
       #    used_sz += cost[app_id]
    except IndexError: 
       print('no analytics in edge')
    #rsize = total_size - used_sz

    print("======Deploy Algo Result======")

    #if len(app_ids) >= MAX_EDGE_APPS:
    #   print("edge full")
    #   sys.exit(0)
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
    cmd = f'python {script} {total_size} {int(bw*BW_ratio)} {analytics} {algorithm_IDA} {alpha}' 

    deploy_info = ssh_command_paramiko(host, user, pwd, port, cmd, False).strip()
    try:
      cloud = deploy_info.split(',')[0].split('> ')[1].split(' ')[0].split(';')
      edge = deploy_info.split(',')[1].split('> ')[1].split(';')
      edge[-1], exec_time = edge[-1].split('\r\ntime:')
    except IndexError as error:
      print('No Analytics in System')
      sys.exit('no need to download (deploy)\n' + deploy_info)

    num = sys_time
    print("Edge:",edge)
    print("Cloud:",cloud)
    print("Exec Time:",exec_time)

    # Write expected deployed containers
    expect_file = '../RunDeploy/expect.input'
    with open(expect_file, 'w') as wf:
        for app in edge[:-1]:
            wf.write(app+',')
        if len(edge) > 0:
            wf.write(edge[-1])
       
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
                    if app_image == cloud_app.split('-',1)[0]:
                        app_id = cloud_app
                        cloudapp_ids.remove(cloud_app)
                        break
            elif app_image[0:4] == 'yolo':
                for cloud_app in cloudapp_ids:
                    if app_image == cloud_app.split('-',1)[0]:
                        app_id = cloud_app
                        cloudapp_ids.remove(cloud_app)
                        break
            #print('app_id: ' + app_id)
            delete_processes.append(delete(app_id))
            print('delete app:' + app_id)
            deploy_processes.append(deploy_measure(image_index, device_index, app_id.split('-')[1]))
            print("Deploy:", app_id)
            print('try deploy app number: ', app_id.split('-')[1])
        except:
            print("Deploy:", app_image)
            #print('Fail to deploy app number: ', app_image.split('-')[1])
            print('Fail to deploy app number: ', app_image)
            print('no need to download (edge), time: ', num)
            #sys.exit('no need to download (edge)\n' + output)
            #sys.exit('no need to download (edge)\n')
        #print("deploy done")
        #num = num + 1
        #break
    
    # Write deploy logs
    images_download = {}
    with open('../RunDeploy/images_download.log', 'r') as rf: 
        for line in rf.readlines():
            image, down_time, down_num = line.split(',')
            images_download[image] = {'time':float(down_time), 'num':int(down_num)}
    for analytic in deploy_analytics:
        images_download[analytic]['time'] = time.time()
        images_download[analytic]['num'] = images_download[analytic]['num'] + 1
    with open('../RunDeploy/images_download.log', 'w') as wf: 
        #print('Write ../RunDeploy/images_download.log')
        i = 1
        for image in images_download.keys():
            if i < len(images_download):
                wf.write(f'{image},{images_download[image]["time"]},{images_download[image]["num"]}\n')
                #print(f'{image},{images_download[image]["time"]},{images_download[image]["num"]}\n')
            else:
                wf.write(f'{image},{images_download[image]["time"]},{images_download[image]["num"]}')
                #print(f'{image},{images_download[image]["time"]},{images_download[image]["num"]}')
            i += 1
    # Send deploy logs to gateway
    cmd = f'sshpass -p {pwd} scp ../RunDeploy/images_download.log {user}@{host}:{gateway_dir}/Implementation/Algo/Replacement/'
    subprocess.run([cmd], shell=True)
    #print('images_download', images_download)

    
    # YJ add
    for process in deploy_processes:
        process.wait()
    for process in delete_processes:
        process.wait()
