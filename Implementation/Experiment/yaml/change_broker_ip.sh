#!/bin/bash

for path in ./ edge/
do
    for app in audio1 audio2 audio3 audio4 audio5 yolo1 yolo2 yolo3 yolo4 yolo5  
    do
        sed -i '21c \ \ \ \ \ \ \ \ \ \ \ \ value: "192.168.1.102"' $path$app.yaml
        sed -i '23c \ \ \ \ \ \ \ \ \ \ \ \ value: "192.168.1.100"' $path$app.yaml
    done
done
