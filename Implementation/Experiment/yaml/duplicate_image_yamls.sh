#!/bin/bash
for p in ./ edge/
do
    for image in yolo audio
    do 
        for t in 1 2 
        do
            for i in 1 2 3 4 
            do
                ti="$((t * 4 + i))"
                #cp $p$image$i.yaml $p$image$ti.yaml
                sed -i "4c \ \ \ \ \ \ \ \ name: $image$ti-0" $p$image$ti.yaml
                sed -i "15c \ \ \ \ \ \ \ \ \ \ image: 192.168.1.100:5000/iscc19:s2-$image-$ti" $p$image$ti.yaml
            done
        done
    done
done
