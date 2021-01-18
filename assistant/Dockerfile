FROM debian:stretch
RUN apt-get update
RUN apt update && apt upgrade -y && apt install -y python3-git
RUN apt install -y python3-pip
RUN pip3 install GitPython git-utils git-wrapper flask
