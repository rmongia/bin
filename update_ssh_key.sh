#!/bin/bash -x

NAME=$1
IP=`host $NAME | cut -d' ' -f4`
ssh-keygen -f "$HOME/.ssh/known_hosts" -R $NAME
ssh-keygen -f "$HOME/.ssh/known_hosts" -R $IP
ssh-keygen -f "$HOME/.ssh/known_hosts" -R $NAME,$IP
ssh-keyscan -H $NAME >> $HOME/.ssh/known_hosts
ssh-keyscan -H $IP >> $HOME/.ssh/known_hosts
ssh-keyscan -H $NAME,$IP >> $HOME/.ssh/known_hosts
ssh-keyscan $NAME >> $HOME/.ssh/known_hosts
