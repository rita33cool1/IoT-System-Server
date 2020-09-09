# IoT-System-Server (Github)

I have built an IoT system to
- dynamically deploy IoT analytics on gateways to save upload bandwidth as much as possible.
- dynamically allocate upload bandwidth for each IoT analytic to maximize overall QoS.

Precisely, my system
+ leverages IoT devices, gateways, and cloud servers.
+ packages IoT analytics into **Docker** containers, which are easily deployed and managed.
+ manages containers and monitors resources of IoT devices with **Kubernetes**.

Tools: Python, Docker, Kubernetes, TensorFlow, MQTT, FFserver.

**This repository is the server side.**

**The document is [here](https://hackmd.io/@xm_QEbubQyKiLnZco2batA/IoT-System-Server).**

## Environment
OS: Ubuntu 18.04.1 LTS
Docker: 18.09.7
Kubernetes: 
```Bash
Server Version: version.Info{Major:"1", Minor:"11", GitVersion:"v1.11.0", GitCommit:"91e7b4fd31fcd3d5f436da26c980becec37ceefe", GitTreeState:"clean", BuildDate:"2018-06-27T20:08:34Z", GoVersion:"go1.10.2", Compiler:"gc", Platform:"linux/amd64"}
Client Version: version.Info{Major:"1", Minor:"11", GitVersion:"v1.11.0", GitCommit:"91e7b4fd31fcd3d5f436da26c980becec37ceefe", GitTreeState:"clean", BuildDate:"2018-06-27T20:17:28Z", GoVersion:"go1.10.2", Compiler:"gc", Platform:"linux/amd64"}
```

## File Structure
<font color="blue">`Implementation/`</font> <br>
&nbsp;|\_\_\_\_<font color="blue">`Experiment/`</font> <br>
&nbsp;|&emsp; &emsp;|\_\_\_\_<font color="blue">`generate_request/`</font> <br>
&nbsp;| &emsp;&emsp;| &emsp; &ensp;|\_\_\_\_<font color="green">`run.py`</font> <br>
&nbsp;| &emsp;&emsp;| <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="blue">`log/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="blue">`parsers/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="blue">`yaml/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`Algorithm.log` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="green">`cplog.sh`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`delete_all_images.py` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="green">`poisson_run.py`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`qos_measurement_audio.py` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`qos_measurement_yolo_image.py` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`qos_measurement_yolo_result.py` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="green">`registry.sh`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`replace_time.input` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="green">`run.sh`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`SubQoSAudio.sh` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`SubQoSYoloImage.sh` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`SubQoSYoloResult.sh` <br>
&nbsp;| <br>
&nbsp;|\_\_\_\_<font color="blue">`Gateway/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="blue">`ObjectDector/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="blue">`ObjectDector2/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="blue">`ObjectDector3/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="blue">`ObjectDector4/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="blue">`ObjectDector5/`</font> <br>
&nbsp;|<br>
&nbsp;|\_\_\_\_<font color="blue">`RunDeploy/`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`analytics.input` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`departure_analytics.txt` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_<font color="green">`deploy_measure.py`</font> <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`exist.input` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`expect.input` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`images_download.log` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`list.txt` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`replace_time.input` <br>
&nbsp;| &emsp;&emsp;|\_\_\_\_`terminal.input` <br>
&nbsp;| <br>
&nbsp;|\_\_\_\_<font color="blue">`RunAllocation/`</font> <br>
&nbsp;|&emsp;&emsp; |\_\_\_\_<font color="blue">`Algo/`</font> <br>
&nbsp;| &emsp;&emsp;| &emsp; &ensp;|\_\_\_\_<font color="green">`allocate_algo.py`</font> <br>
&nbsp;| &emsp;&emsp;| &emsp; &ensp;|\_\_\_\_`produce_weights.py` <br>
&nbsp;| &emsp;&emsp;| &emsp; &ensp;|\_\_\_\_<font color="green">`unweighted_algo.py`</font> <br>
&nbsp;| &emsp;&emsp;| &emsp; &ensp;|\_\_\_\_<font color="green">`weighted_algo.py`</font> <br>
&nbsp;| &emsp;&emsp;| &emsp; &ensp;|\_\_\_\_`weights.txt` <br>
&nbsp;|&emsp;&emsp; | <br>
&nbsp;|&emsp;&emsp; |\_\_\_\_<font color="green">`QoSknob.txt`</font> <br>
&nbsp;|&emsp;&emsp; |\_\_\_\_<font color="green">`run.py`</font> <br>
&nbsp;| <br>
&nbsp;|\_\_\_\_<font color="green">`docker_daemon.json`</font> <br>

### Folders and Files
<font color="blue">`Experiment/`</font>: Main experiments
- <font color="blue">`generate_request/`</font>: Input requests and request generations
- <font color="blue">`log/`</font>: Log files
- <font color="blue">`parsers/`</font>: Parsers to parse raw log files
- <font color="blue">`yaml/`</font>: Analytics deployment yaml files
- <font color="green">`cplog.sh`</font>: Script to copy log files
- <font color="green">`poisson_run.py`</font>: **Main process**
- <font color="green">`registry.sh`</font>: Script to run local registry
- <font color="green">`run.sh`</font>: **Main process**

<font color="blue">`Gateway/`</font>: Including Yolo processes
- <font color="blue">`ObjectDector/`</font>~<font color="blue">`ObjectDector5/`</font>: Yolo processes

<font color="blue">`RunDeploy/`</font>: Container deployment process
- <font color="green">`deploy_measure.py`</font>: Image Download Algorithms:
    + Dynamic programming algorithm ($IDA_D$) 
    + $(1-\epsilon)$-approximation algorithm ($IDA_A$) 
    + Greedy algorithm ($IDA_G$)

<font color="blue">`RunAllocation/`</font>: Rate allocation process
- <font color="green">`run.py`</font>: Rate allocation processes
- <font color="blue">`Algo/`</font>: Rate Allocation Algorithms:
    + Our proposed algorithm (RAA)
    + Weighted allocation algorithm (WA)
    + Unweighted allocation algorithm (UA)
- <font color="green">`QoSknob.txt`</font>: QoS knobs determined by rate allocation algorithms

<font color="green">`docker_daemon.json`</font>: Local registry setup 

## Set up
### Build Local Registry
Copy `Implementation/docker_daemon.json` to `/etc/docker/daemon.json`
```Bash
cd Implementation
cp docker_daemon.json /etc/docker/daemon.json
```

## Start up
### Environment Variables
Set up environment variables in `config.env`, and then `source config.env`.
### Run Local Registry
+ Go to `Experiment/`
```Bash
cd Implementation/Experiment/
```
+ Run local registry container
```Bash 
bash registry.sh
```

## Generate Requests
+ Go to `generate_request/`
```Bash
cd generate_request/
```
+ Run the generating script `run.py`
```Bash
python3 run.py [number_of_requests_per_minute] [minimal_departure_time] [maximal_departure_time] [total_experiment_time] [output_file]
```
`output_file` is `requests_[number_of_requests_per_minute]_[minimal_departure_time]_[maximal_departure_time]_[total_experiment_time]_[version].txt`

Example.
```Bash
python3 run.py 1 1 10 20 requests_1_1_10_20_1.txt
```
    
## Set up Parameters of Experiments in `run.sh`
| **Parameters** | **Meanings** |
|:--------------:|:------------- |
| *ida* | Image download algorithm (IDA) Ex. <br> *DP*: $IDA_D$ <br> *FPTAS*: $IDA_A$ <br> *Greedy*:  $IDA_G$ |
| *raa* | Rate allocation algorithm (RAA) Ex. <br> *RAA*: RAA <br> *weighted*: WA <br> *unweighted*: UA |
| *lrp* | Layer replacement policy (LRP) Ex. *LRU*, *MRU*, *LFU*, *MFU*|
| *epsilon* | Approximation  parameter $\epsilon$ of $IDA_A$ Ex. *0.4* |
| *alpha* | Step size $\alpha$ of RAA Ex. *0.01*|
| *total_time* | Total experiment time (unit is minute). <br> Ex. *40*: for a 40-minute long experiment. |
| *duration* | Time slot duration of IDA (unit is minute) Ex. *5* |
| *network* | Download / upload bandwidth. Ex. <br> *optical*: 100Mbps / 5Mbps <br> *up10*: 100Mbps / 10Mbps <br> |
| *request_per_m* | Number of requests per minute Ex. *1* |
| *alive_time_min* | Minimal departure time (unit is minute) Ex. *1* | 
| *alive_time_max* | Maximal departure time (unit is minute) Ex. *10* |
| *i* | Requests version|
| *date_time* | Time stamp |

## Run Experiments
```Bash
screen -S run 
bash run.sh > run.log
```
### Check Screen Status
```Bash
screen -ls
```
Output should be like this:
```Bash
There are screens on:
	20519.SubQoSAudio	(08/30/2020 08:51:00 PM)	(Detached)
	20429.SubQoSYoloImage	(08/30/2020 08:50:52 PM)	(Detached)
	20348.SubQoSYoloResult	(08/30/2020 08:50:44 PM)	(Detached)
	19471.run	(08/30/2020 08:49:04 PM)	(Detached)
4 Sockets in /run/screen/S-master.
```

## Parse Log files
### Raw Log files
Here is an example
| Log files | Information of | Generated by |
| --------- | -------------- | ------------ |
| DP_RAA_LRU_0.4_0.01_1.log | Main process | Experiment/poisson_run.py
| deploy_optical_DP_RAA_LRU_0.4_0.01_1.log | IDA | RunDeploy/deploy_measure.py <br> or <br> RunDeploy/greedy_measure.py |
| allocation_optical_DP_RAA_LRU_0.4_0.01_1.log | RAA | RunAllocation/run.py
| Bandwidth_optical_DP_RAA_LRU_0.4_0.01_1.log | Experiment/Bandwidth consumption | Experiment/poisson_run.py |
| CPU_optical_DP_RAA_LRU_0.4_0.01_1.log | CPU consumption | Experiment/poisson_run.py |
| qos_DP_RAA_LRU_0.4_0.01_1_0830_2049_audio.log | Result of audio classifiers | Experiment/qos_measurement_audio.py |
| qos_DP_RAA_LRU_0.4_0.01_1_0830_2049_yolo.log | Result of object detectors | Experiment/qos_measurement_yolo_result.py |

### Copy log files to `log/`
- Edit Parameters in `cplog.sh`
    - *network*: network condition. Ex. `optical`
    - *i*: version of requests Ex. `1`
- Run `cplog.sh`
```Bash
bash cplog.sh [algorithm] [target_dir]
```
- Arguments: 
    + *algorithm*: the name of main process's log file. Ex. `DP_RAA_LRU_0.4_0.01_1`
    + *target_dir*: output directory. Ex. `log/DP_RAA_MFU_0.4_0.01_1_1_10_20_3GB_optical_Aug_31/` <br> Notice that `./` will **remove log files**
- Example.
```Bash
bash cplog.sh DP_RAA_LRU_0.4_0.01_1 log/DP_RAA_LRU_0.4_0.01_3_1_10_30_3GB_optical_Aug_7/
```
- Check log directory
```Bash
ls log/DP_RAA_LRU_0.4_0.01_3_1_10_30_3GB_optical_Aug_7
```
Output:
```Bash
...
run.log
allocation_optical_DP_RAA_LRU_0.4_0.01_1.log
Bandwidth_optical_DP_RAA_LRU_0.4_0.01_1.log
CPU_optical_DP_RAA_LRU_0.4_0.01_1.log
deploy_optical_DP_RAA_LRU_0.4_0.01_1.log
DP_RAA_LRU_0.4_0.01_1.log
qos_DP_RAA_LRU_0.4_0.01_1_0830_2049_audio.log
qos_DP_RAA_LRU_0.4_0.01_1_0830_2049_yolo.log
...
```

### Using Yolo to Calculate ground truth and Parse Log Files

```Bash
cd log/DP_RAA_LRU_0.4_0.01_3_1_10_30_3GB_optical_Aug_7
bash ../../parsers/parse.sh [log_dir] [name_of_main_process_log_file] [date_time] [yolo_dir] [request_version]
```
+ `yolo_dir`: the directory of yolo. <br>
Ex. `../../../Gateway/ObjectDector`

Example.
```Bash
bash ../../parsers/parse.sh ./ DP_RAA_LRU_0.4_0.01_1 0830_2049 ../../../Gateway/ObjectDector 1
```

### Parsed Log Files
| Log Files | Information of |
| --------- | -------------- |
| accuracy_DP_RAA_LRU_0.4_0.01_1.txt | Overall weighted QoS |
| deploy_num_DP_RAA_LRU_0.4_0.01_1.txt | Number of analytics containers on the gateway |
| deploy_num_expect_DP_RAA_LRU_0.4_0.01_1.txt | Expected number of analytics containers on the gateway |
| down_DP_RAA_LRU_0.4_0.01_1.txt | Download bandwidth consumption |
| gateway_num_DP_RAA_LRU_0.4_0.01_1.txt | Number of analytics containers on the gateway |
| request_num_DP_RAA_LRU_0.4_0.01_1.txt | Number of analytics containers on the cloud server and gateway |
| saved_bw_DP_RAA_LRU_0.4_0.01_1.txt | Saved upload bandwidth |
| saved_bw_expect_DP_RAA_LRU_0.4_0.01_1.txt | Expected saved upload bandwidth |
| time_allocate_DP_RAA_LRU_0.4_0.01_1.txt | Running time of rate alloction algorithm |
| time_ida_DP_RAA_LRU_0.4_0.01_1.txt | Running time of image download algorithm |
| up_DP_RAA_LRU_0.4_0.01_1.txt | Upload bandwidth consumption |
