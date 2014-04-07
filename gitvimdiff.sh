#!/bin/bash

GIT_ROOT=`git rev-parse --show-toplevel`
git diff --no-ext-diff $GIT_ROOT/$1

read -n 1 -p "Do you want to open file in Vimdiff [y/n]? " REPLY
if [ "$REPLY" = "y" ]; then
  vimdiff "$2" "$5"
fi
echo ''
