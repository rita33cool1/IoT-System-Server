#!/usr/bin/env python3

__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import re
import sys
import time
import paramiko
import subprocess

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
        while True:
            output = str(channel.recv(1024), 'utf-8')
            if output.find("$") != -1:
                output = ''
                tmp_end_num += 1
            if tmp_end_num == 2:
                #print(command + " finish")
                break
            if print_output:
                print(output)
            if output.find("Last login") != -1:
                print_output = True
        channel.close()
        """
        stdin, stdout, stderr = ssh.exec_command(command)
        output=stdout.readlines()
        print(output)
        exit_status = stdout.channel.recv_exit_status()        
        if exit_status != 0:
            print(command + " Error", exit_status)
        #else:
        #    print (command + ' Comoplete')

        #print('========== stdout ==========\n')
        #print(stdout.readlines())
        """

def clean_download_logs():
    image_num = 12
    provider = os.environ['DOCKER_PROVIDER'] + '/'
    repo = os.environ['DOCKER_REPO']
    with open('../RunDeploy/images_download.log', 'w') as wf:
        for i in range(image_num):
            wf.write(f'{provider}{repo}:s2-yolo-{i+1},0,0\n')
        for i in range(image_num-1):
            wf.write(f'{provider}{repo}:s2-audio-{i+1},0,0\n')
        wf.write(f'{provider}{repo}:s2-audio-{image_num},0,0')

def clean_image_exist_expect_input():
    with open('../RunDeploy/exist.input', 'w') as wf:
        wf.write('')
    with open('../RunDeploy/expect.input', 'w') as wf:
        wf.write('')

if __name__ == '__main__':
    user = 'minion'
    host = os.environ['MINION']
    pwd = os.environ['PASSWORD']
    port = 22
    print('========== ssh ==========\n')
    cmd = 'sudo -S wondershaper -ca enp0s25'
    #cmd = 'sudo -S wondershaper -ca enx000972836258'
    ssh_command_paramiko(host, user, pwd, port, cmd, True)
    print('========== minion delete containers ==========\n')
    cmd = 'docker ps -a | grep Exit | cut -d " " -f 1 | xargs  docker rm'
    ssh_command_paramiko(host, user, pwd, port, cmd, False)
    print('========== cloud delete containers ==========\n')
    subprocess.run([cmd], shell=True)
    print('========== cloud clean download image logs ==========\n')
    clean_download_logs()
    clean_image_exist_expect_input()
    print('========== minion delete images ==========\n')
    gateway_dir = os.environ['GATEWAY_DIR']
    cmd = f'python3 {gateway_dir}/delete_all_images.py {sys.argv[1]}'
    ssh_command_paramiko(host, user, pwd, port, cmd, False)
