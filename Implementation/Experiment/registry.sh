#!/bin/bash

docker ps -a -f name=registry | cut -d $'\n' -f 2 | cut -d ' ' -f 1 | xargs docker rm
docker run -d -p 5000:5000 -v /home/user1/storage:/var/lib/registry --name registry registry:2
