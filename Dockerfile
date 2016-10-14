from ubuntu:14.04

maintainer AdamJFurbee

#run echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
run apt-get update
run apt-get install -y build-essential git
run apt-get install -y python3 python3-dev python3-setuptools python3-pip
## run apt-get install -y supervisor

## # install our code
add . /home/docker/code/

## # run pip install
run pip3 install -r /home/docker/code/requirements.txt
## 
## # run flask app
run python3 /home/docker/code/main.py
## 
# expose 80
# cmd ["supervisord", "-n"]
