#!/usr/bin/env bash

file="myapp-simple-ht-hidden-stations.py"
# file="myapp-fifth.py"

# file="fifth-random"

lgp="python"
# lgp="c++"

cmd="true"
# cmd="false"

if [[ $lgp = "c++" ]]
then
    echo File ${file}.cc

    # Copy file to scratch
    sudo cp ../scratch/${file}.cc ../repos/ns-3-allinone/ns-3.30/scratch/

    # Set permissions to file in scratch
    sudo chmod 777 ../repos/ns-3-allinone/ns-3.30/scratch/${file}.cc
    
fi
if [[ $lgp = "python" ]]
then
    echo File ${file}

    # Copy file to scratch
    sudo cp python-examples/${file} ../repos/ns-3-allinone/ns-3.30/scratch/

    # Set permissions to file in scratch
    sudo chmod 777 ../repos/ns-3-allinone/ns-3.30/scratch/${file}
fi

    # Lendo arquivo .pcap
    cd "../"
    sudo cp WGNet/trace-files/trace1.pcap repos/ns-3-allinone/ns-3.30/
    # Tornando arquivo editável e legível
    sudo chmod 777 WGNet/trace-files/trace1.pcap
    # Atribuindo valor do tamanho do pacote em um arquivo .txt 
    sudo termshark -r WGNet/trace-files/trace1.pcap -T fields -E separator=/t  -e ip.len > repos/ns-3-allinone/ns-3.30/scratch/size.txt
    # Atribuindo valor do tempo de envio cada pacote em um arquivo .txt
    sudo termshark -r WGNet/trace-files/trace1.pcap -T fields -E separator=/t -e frame.time_delta_displayed > repos/ns-3-allinone/ns-3.30/scratch/time.txt
    # Tornando arquivos editáveis e legíveis
    sudo chmod 777 repos/ns-3-allinone/ns-3.30/scratch/size_ns3.txt
    sudo chmod 777 repos/ns-3-allinone/ns-3.30/scratch/time_ns3.txt

if [[ $cmd = "true" ]]
then
    # cd desired/directory
    cd "repos/ns-3-allinone/ns-3.30/" 
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
        cd "../repos/ns-3-allinone/ns-3.30/" 
        ./waf --run "scratch/${file}"
    fi
    if [[ $lgp = "python" ]] 
    then
        # cd desired/directory
        cd "../repos/ns-3-allinone/ns-3.30/" 
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
