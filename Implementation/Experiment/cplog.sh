algorithm=$1
target_dir=$2
#network=4G
network=optical
#network=optical50
#network=up10
#network=up75

if [ ! -d $target_dir ]; then
  mkdir $target_dir
fi

#for i in 1
#for i in 1 2 3 4
for i in 1 2 3 4 5
do
  cp run.log $target_dir
  cp $algorithm"_"$i".log" $target_dir
  cp "deploy_"$network"_"$algorithm"_"$i".log" $target_dir
  cp "allocation_"$network"_"$algorithm"_"$i".log" $target_dir
  cp "Bandwidth_"$network"_"$algorithm"_"$i".log" $target_dir
  cp "Storage_"$network"_"$algorithm"_"$i".log" $target_dir
  cp "CPU_"$network"_"$algorithm"_"$i".log" $target_dir
  cp qos_"$algorithm"_"$i"_*yolo.log $target_dir
  cp qos_"$algorithm"_"$i"_*audio.log $target_dir
  
  rm $algorithm"_"$i".log"
  rm "deploy_"$network"_"$algorithm"_"$i".log"
  rm "allocation_"$network"_"$algorithm"_"$i".log"
  rm "Bandwidth_"$network"_"$algorithm"_"$i".log"
  rm "Storage_"$network"_"$algorithm"_"$i".log"
  rm "CPU_"$network"_"$algorithm"_"$i".log" 
  rm qos_"$algorithm"_"$i"_*yolo.log
  rm qos_"$algorithm"_"$i"_*audio.log
done
