#!/bin/bash

log_dir=$1
algos=$2
images_dir=$3
images_dir="$algos"_"$images_dir"
detector_dir=$4
weight=$5
BASEDIR=$(dirname $0)
total_size=3000000000
network=optical
#network=optical50
#network=up10

if [[ $log_dir == "./" ]]; then
    log_dir=.
fi
if [[ $images_dir == "./" ]]; then
    images_dir=.
fi
#if [[ $detector_dir == "./" ]]; then
#    detector_dir=.
#fi
if [[ $BASEDIR == "./" ]]; then
    BASEDIR=.
fi


# IDA running time
FILE=$log_dir/time_ida_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python $BASEDIR/time_ida.py $log_dir/deploy_"$network"_"$algos".log $FILE

# Allocation running time
FILE=$log_dir/time_allocate_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python $BASEDIR/time_allocate.py $log_dir/allocation_"$network"_$algos.log $FILE 

# Storage usage
FILE=$log_dir/storage_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python $BASEDIR/storage.py $log_dir/Storage_"$network"_$algos.log $FILE $total_size

# Request number
FILE=$log_dir/request_num_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python3 $BASEDIR/request_num.py $log_dir/$algos.log > $FILE

# Gateway number
FILE=$log_dir/gateway_num_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python3 $BASEDIR/gateway_num.py $log_dir/$algos.log > $FILE

# Deploy number
FILE=$log_dir/deploy_num_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python3 $BASEDIR/download_num.py $log_dir/$algos.log > $FILE

# Expected Deploy number
FILE=$log_dir/deploy_num_expect_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python $BASEDIR/download_num_expect.py $log_dir/deploy_"$network"_"$algos".log $FILE

# Deploy Categories
FILE=$log_dir/category_num_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python3 $BASEDIR/category.py $log_dir/$algos.log > $FILE

# Saved Bandwidth
FILE=$log_dir/saved_bw_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python3 $BASEDIR/save_bw.py $log_dir/$algos.log > $FILE

# Expect Saved Bandwidth
FILE=$log_dir/saved_bw_expect_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python3 $BASEDIR/save_bw_expect.py $log_dir/deploy_"$network"_"$algos".log $FILE

# Expected QoS
FILE=expected_qos_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python3 $BASEDIR/allocation2expectMat.py $log_dir/allocation_"$network"_$algos.log $FILE

# Up/down bw
FILE1=$log_dir/up_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
FILE2=$log_dir/down_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python $BASEDIR/bandwidth_second.py $log_dir/Bandwidth_"$network"_$algos.log $FILE1 $FILE2

# Copy ground truth images from minion to master
mkdir $log_dir/images
mkdir $log_dir/result
scp -r minion@192.168.1.102:~/YC/iscc19/Implementation/Gateway/PubImages/original/$images_dir $log_dir/images/$images_dir

# Get the images id in images_list.txt
FILE=$log_dir/"$images_dir"_images_list.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
python $BASEDIR/extract_image_num.py $log_dir/qos_"$images_dir"_yolo.log > $log_dir/"$images_dir"_images_list.txt

# Run yolo
log_dir=$PWD
cd $detector_dir
python yolo.py $log_dir/"$images_dir"_images_list.txt $log_dir/images/$images_dir $log_dir/result/$images_dir > $log_dir/"$images_dir"_result.txt

# Weighted QoS 
FILE=accuracy_$algos.txt
if [[ -f $FILE ]]; then
    rm $FILE
fi
cd $log_dir
python $BASEDIR/comp_qos.py ../../../RunAllocation/Algo/weights.txt $weight $log_dir/allocation_"$network"_$algos.log qos_"$images_dir"_audio.log qos_"$images_dir"_yolo.log "$images_dir"_result.txt $FILE
