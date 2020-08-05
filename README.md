# IoT-System-Server

I have built an IoT system to
- dynamically deploy IoT analytics on gateways to save upload bandwidth as much as possible.
- dynamically allocate upload bandwidth for each IoT analytic to maximize overall QoS.

Precisely, my system
+ leverages IoT devices, gateways, and cloud servers.
+ packages IoT analytics into **Docker** containers, which are easily deployed and managed.
+ manages containers and monitors resources of IoT devices with **Kubernetes**.

Tools: Python, Docker, Kubernetes, TensorFlow, MQTT, FFserver.

**This repository is the server side.**

## Environment
OS: Ubuntu 18.04.1 LTS
Docker: 18.09.7
Kubernetes: 
```
Server Version: version.Info{Major:"1", Minor:"11", GitVersion:"v1.11.0", GitCommit:"91e7b4fd31fcd3d5f436da26c980becec37ceefe", GitTreeState:"clean", BuildDate:"2018-06-27T20:08:34Z", GoVersion:"go1.10.2", Compiler:"gc", Platform:"linux/amd64"}
Client Version: version.Info{Major:"1", Minor:"11", GitVersion:"v1.11.0", GitCommit:"91e7b4fd31fcd3d5f436da26c980becec37ceefe", GitTreeState:"clean", BuildDate:"2018-06-27T20:17:28Z", GoVersion:"go1.10.2", Compiler:"gc", Platform:"linux/amd64"}
```

## Setup
### Environment Variables
Set up environment variables in `config.env`, an then `source config.env`.
### Run Local Registry
1. Go to `Implementation/`
    `cd Implementation/`
3. Copy Implementation/docker_daemon.json to /etc/docker/daemon.json
    `cp docker_daemon.json /etc/docker/daemon.json`
3. Run local registry container
    `bash registry.sh`
    
## Run Experiments
```
cd Implementation/Experiment
bash run.sh
```
