#!/bin/sh

GIT=git
ROOT=.
URL=$1
TARGET=$ROOT/$2

if [ ! -d $TARGET ]; then
    echo cloning
    $GIT clone --mirror $URL $TARGET
else
    echo fetching
    cd $TARGET && git fetch
fi
