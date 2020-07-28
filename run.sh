#!/usr/bin/env bash

file="fifth"
echo File ${file}.cc

# Copy file to scratch
sudo cp ${file}.cc ../../repos/ns-3-allinone/ns-3.30/scratch/

# Set permissions to file in scratch
sudo chmod 777 ../../repos/ns-3-allinone/ns-3.30/scratch/${file}.cc

sizeFile=$(wc -l < Parameters/Times.txt)
lastTime=$(tail -n 1 Parameters/Times.txt)

echo Size File $sizeFile
echo Last Time $lastTime
# scriptdir="$(../../repos/ns-3-allinone/ns-3.30 "$0")"

# cd desired/directory
cd "../../repos/ns-3-allinone/ns-3.30/" 
./waf --run "scratch/${file} --nPackets=$sizeFile --timeStopSimulation=$lastTime"


sudo rm scratch/$file.cc