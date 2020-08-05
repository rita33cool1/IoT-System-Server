#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Subscribe the result accuracy from applocations
"""
__author__ = 'YuJung Wang'
__date__ = '2020/02'

import os
import sys
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

algorithm = ''
result_image_dir = '../Gateway/YoloResult/'

def on_message(client, userdata, msg):
    app = msg.topic.split("image/", 1)[1]
    # Save images
    f = open(result_image_dir+algorithm+'/result_'+app+'.jpg','wb')
    f.write(msg.payload)
    f.close()
    #print ('img received')

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
        client.on_message = on_message
        client.subscribe("iot/iscc19/result/image/#")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")

if __name__ == '__main__':
    with open('Algorithm.log', 'r') as rf: 
        algorithm = rf.read().strip()

    client = mqtt.Client()
    client.connect(os.environ['BROKER'], 1883, 60)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.loop_forever() 

