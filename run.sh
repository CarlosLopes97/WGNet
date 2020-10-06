#!/usr/bin/env bash

file="myapp-fifth.py"

# file="fifth-random"

lgp="python"
# lgp="c++"

cmd="true"
# cmd="false"

if [[ $lgp = "c++" ]]
then
    echo File ${file}.cc

    # Copy file to scratch
    sudo cp ../../scratch/${file}.cc ../../../../repos/ns-3-allinone/ns-3.30/scratch/

    # Set permissions to file in scratch
    sudo chmod 777 ../../../../repos/ns-3-allinone/ns-3.30/scratch/${file}.cc
    
fi
if [[ $lgp = "python" ]]
then
    echo File ${file}

    # Copy file to scratch
    sudo cp ns-3-python-examples/${file} ../../../../repos/ns-3-allinone/ns-3.30/scratch/

    # Set permissions to file in scratch
    sudo chmod 777 ../../../../repos/ns-3-allinone/ns-3.30/scratch/${file}
fi


if [[ $cmd = "true" ]]
then
    # cd desired/directory
    cd "../../../../repos/ns-3-allinone/ns-3.30/" 
    sizeFile=$(wc -l < scratch/time.txt)
    lastTime=$(tail -n 1 scratch/time.txt)

    echo Size File $sizeFile
    echo Last Time $lastTime

    if [[ $lgp = "c++" ]] 
    then
        ./waf --run "scratch/${file} --nPackets=$sizeFile --timeStopSimulation=$lastTime"
    fi
    if [[ $lgp = "python" ]] 
    then
        ./waf --pyrun "scratch/${file} --nPackets=$sizeFile --timeStopSimulation=$lastTime"
    fi

fi
if [[ $cmd = "false" ]]
then
    if [[ $lgp = "c++" ]] 
    then
        # cd desired/directory
        cd "../../../../repos/ns-3-allinone/ns-3.30/" 
        ./waf --run "scratch/${file}"
    fi
    if [[ $lgp = "python" ]] 
    then
        # cd desired/directory
        cd "../../../../repos/ns-3-allinone/ns-3.30/" 
        ./waf --pyrun "scratch/${file}"
    fi
fi

if [[ $lgp = "python" ]]
then
    sudo rm scratch/$file


if [[ $lgp = "c++" ]]
then
    sudo rm scratch/$file.cc
fi
