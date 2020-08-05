#!/bin/bash

for path in ./ edge/
do
    for app in audio yolo
    do
        for ver in 1 2 3 4 5
            do
            sed -i '15c \ \ \ \ \ \ \ \ \ \ image: 192.168.1.100:5000/iscc19:s2-'$app'-'$ver $path$app$ver.yaml
        done
    done
done
