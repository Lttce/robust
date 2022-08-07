#!/bin/sh
mkdir -p data/send data/receive
rm data/send/*
rm data/receive/*
rm data/check.md5
for i in `seq 0 99`
do
    cat /dev/urandom | head -c 102400 > data/send/data$i
done
cd data/send
md5sum $(find . -type f) | tee ../check.md5
cd ../../
