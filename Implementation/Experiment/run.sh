#!/bin/bash

#epsilon=0.3
lrp=LRU
# from time 0
#total_time=15
#total_time=25
#total_time=60
#total_time=40
total_time=30
#total_time=64
duration=5
#duration=8
#duration=10
# 100M/5M
network=optical
# 50M/5M
#network=optical50
# 100M/10M
#network=up10
# 100M/7.5M
#network=up75
# 100M/2.5M
#network=up25
#request_per_m=1
#request_per_m=2
request_per_m=3
#request_per_m=4
#request_per_m=5
#alive_time=5
#alive_time_min=0
alive_time_min=1
#alive_time_min=5
alive_time_max=10
#alive_time_max=20
request_num="$((request_per_m * alive_time_max))"
raa=RAA
#ida=DP
ida=FPTAS
#raa_step_size = 0.05
#alpha=0.05
alpha=0.1
#raa=weighted
request_input=generate_request/requests_"$request_per_m"_"$alive_time_min"_"$alive_time_max"_"$total_time" 
#request_input=generate_request/requests_"$request_per_m"_"$alive_time_min""$alive_time_max"_"$total_time" 
#request_input=generate_request/requests_"$request_per_m"_"$alive_time"_"$total_time" 
date_time=$(date +"%m%d_%H%M")
#source iscc19.config
#for i in 5
#for i in 4 5
for i in 1 2 3 4 5
do
    #for ida in DP FPTAS Greedy
    #for ida in Greedy FPTAS
    #for ida in DP
    #for ida in Greedy
    #for ida in FPTAS
    #for raa in RAA weighted unweighted
    #for raa in weighted unweighted
    #for raa in RAA
    #for raa in unweighted
    #for raa in weighted
    #for lrp in LRU MRU LFU MFU
    #for lrp in LFU
    for epsilon in 0.1 0.2 0.3 0.4 0.5
    #for alpha in 0.01 0.05 0.1 0.15
    do 
        echo +++++++++++  $ida + $raa + $lrp  ++++++++++
        result_dir="$ida"_"$raa"_"$lrp"_"$epsilon"_"$alpha"_"$i"_"$date_time"
        mkdir ../Gateway/YoloResult/$result_dir
        echo $result_dir > Algorithm.log
        kubectl delete pods --all
        echo "kubect delete all pods"
        python3 delete_all_images.py $result_dir
        echo python3 delete_all_images.py "$ida"_"$raa"_"$lrp"_"$epsilon"_"$alpha"_"$i"
        # Subscribe Yolo result sccuracy
        screen -S SubQoSYoloResult -X quit
        sleep 3
        screen -S SubQoSYoloResult -d -m bash SubQoSYoloResult.sh
        sleep 5
        echo python qos_measurement_yolo_result.py 
        # Subscribe Yolo image sccuracy
        screen -S SubQoSYoloImage -X quit
        sleep 3
        screen -S SubQoSYoloImage -d -m bash SubQoSYoloImage.sh
        sleep 5
        echo python qos_measurement_yolo_image.py 
        # Subscribe Audio result sccuracy
        screen -S SubQoSAudio -X quit
        sleep 3
        #screen -S SubQoSAudio -X stuff ^C
        #sleep 1
        #screen -S SubQoSAudio -X stuff "exit\r"
        screen -S SubQoSAudio -d -m bash SubQoSAudio.sh
        sleep 5
        echo python qos_measurement_audio.py 
        # Run experiment
        python3 poisson_run.py $request_input'_'$i'.txt' $total_time $duration $network $request_num $ida $raa $lrp $i $epsilon $alpha > "$ida"_"$raa"_"$lrp"_"$epsilon"_"$alpha"_"$i".log
        echo "poisson run finish"
        python3 delete_all_images.py END
    done
done

kubectl delete pods --all
python3 delete_all_images.py END
