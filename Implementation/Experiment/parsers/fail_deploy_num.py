#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/05'

import os
import sys 

if __name__ == '__main__':
    in_file = sys.argv[1]
    outfile = sys.argv[2]
  
    overall_deploy_nums = [] 
    with open(in_file, 'r') as rf:
       lines = rf.readlines()
    
    is_start = False
    is_deploy = False
    deploy_nums = [] 
    deploy_app = ''
    for line in lines:
        if 'num:' in line:
            overall_deploy_nums = []
            deploy_nums = []
            is_start = False
        elif '**time:10' in line:
            is_start = True
        elif '======Deploy Algo Result======' in line and is_start:
            overall_deploy_nums.append(deploy_nums)
            deploy_nums = []
        elif 'Deploy: ' in line and not is_deploy:
            is_deploy = True
            deploy_app = line.strip().split('Deploy: ', 1)[1]
        elif 'try deploy app number:  ' in line and is_deploy :
            try_deploy = line.strip().split('try deploy app number:  ', 1)[1]
            if try_deploy == deploy_app.split('-')[-1]:
                deploy_nums.append(deploy_app)
                is_deploy = False
            else:
                print(f'Deploy: {deploy_app} and try deploy: {try_deploy} not match')
                deploy_nums.append(deploy_app)
                is_deploy = False
        elif 'Fail to deploy app number:  ' in line and is_deploy:
            fail_deploy = line.strip().split('Fail to deploy app number:  ', 1)[1] 
            if fail_deploy == deploy_app:
                is_deploy = False
            else: 
                print(f'Deploy: {deploy_app} and Fail to deploy: {fail_deploy} not match')
                is_deploy = False
     
    # Debug
    print('overall_deploy_nums', overall_deploy_nums)

    with open(outfile, 'w') as wf:
        for apps in overall_deploy_nums[:-1]:
            wf.write(f'{len(apps)} ')
        wf.write(f'{len(overall_deploy_nums[-1])}')
