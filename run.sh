#!/usr/bin/env bash

file="myapp-simple-ht-hidden-stations.py"
# file="myapp-fifth.py"

# file="fifth-random"

lgp="python"
# lgp="c++"

rd="pcap"
# rd="xml"

cmd="true"
# cmd="false"

# app_protocol="tcp"
app_protocol="udp"

# Definindo diretório do arquivo trace a ser utilizado pela simulação
dir_tr_file="WGNet/trace-files/Case-Studies/Case-Study-2/UDP-files/vlc-udp.${rd}"

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
if [[ $rd = "pcap" ]]
then
    # Lendo arquivo .pcap
    cd "../"
    
    sudo cp ${dir_tr_file} repos/ns-3-allinone/ns-3.30/
    # Tornando arquivo editável e legível
    sudo chmod 777 ${dir_tr_file}
    # Atribuindo valor do tamanho do pacote em um arquivo .txt 
    sudo termshark -r ${dir_tr_file} -T fields -E separator=/t  -e ip.len > repos/ns-3-allinone/ns-3.30/scratch/size.txt
    # Atribuindo valor do tempo de envio cada pacote em um arquivo .txt
    sudo termshark -r ${dir_tr_file} -T fields -E separator=/t -e frame.time_relative > repos/ns-3-allinone/ns-3.30/scratch/time.txt
    # Tornando arquivos editáveis e legíveis
    sudo chmod 777 repos/ns-3-allinone/ns-3.30/scratch/size.txt
    sudo chmod 777 repos/ns-3-allinone/ns-3.30/scratch/time.txt
    sed -i 's/,/./g' repos/ns-3-allinone/ns-3.30/scratch/size.txt
fi

if [[ $rd = "xml" ]]
then
    cd "../"
    sudo cp apache-jmeter-5.3/bin/results-http-docker.pdml repos/ns-3-allinone/ns-3.30/scratch/
fi

if [[ $cmd = "true" ]] && [[ $rd = "pcap" ]]
then
    # cd desired/directory
    cd "repos/ns-3-allinone/ns-3.30/" 
    sizeFile=$(wc -l < scratch/time.txt)
    lastTime=$(tail -n 1 scratch/time.txt)

    echo Size File $sizeFile
    echo Last Time $lastTime

    if [[ $lgp = "c++" ]] 
    then
        ./waf --run "scratch/${file} --nPackets=$sizeFile --timeStopSimulation=$lastTime --app_protocol=$app_protocol"
    fi
    if [[ $lgp = "python" ]] 
    then
        ./waf --pyrun "scratch/${file} --nPackets=$sizeFile --timeStopSimulation=$lastTime --app_protocol=$app_protocol"
    fi

fi

if [[ $cmd = "true" ]] && [[ $rd = "xml" ]]
then
    # cd desired/directory
    cd "repos/ns-3-allinone/ns-3.30/" 

    sizeFile=$(grep -ow 'by=' scratch/results-http-docker.pdml | wc -l)
    
    # grep -zo '.*" s="' results-http-docker.pdml
    # grep -o 'ts="[0-9]*\.[0-9]*' | cut -d ' ' -f 2
    
    # lastTime=$(tac scratch/results-http-docker.pdml | grep -m1 -oP '(?=" ts=").*(?=" s=")')
    date_end=$(tac scratch/results-http-docker.pdml | awk '/ s=/ {p=1; split($0, a, " s="); $0=a[1]}; /ts=/ {p=0; split($0, a, "ts="); $0=a[2]; print; exit}; p' | tac | tr -d '"')
    # date_ini=$(tac scratch/results-http-docker.pdml | awk '/ s=/ {f=1; split($0, a, " s="); $0=a[1]}; /ts=/ {f=0; split($0, a, "ts="); $0=a[2]; print; exit}; pf' | tac | tr -d '"')
    
    echo Data end $date_end
    # echo Data ini $date_ini
    
    # diff=$($date2 - $date1)
    # echo Diff $diff
    # date_end=$($date_end -du @$date_end +"%T")
    date_end=$(date $data_end +%s | bc)
    # echo $date
    echo DATE $date_end
    # $date_end | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }'   
    # SavedIFS="$IFS"
    # IFS=":."
    # Time=($date1)
    # Seconds=$(${Time[0]}*3600 + ${Time[1]}*60 + ${Time[2]}).${Time[3]}
    # IFS="$SavedIFS"

    # # diff=$(date diff +%s | bc)
    # echo "Time Taken - $(($date /60/60)) hours and $(($date % 60)) minutes and $(($date % 60)) seconds elapsed."
    # echo DIFF $diff

    # lastTime=$Seconds
    string1="+10 days 11:33:56.5400022"
    string2="+15 days 10:36:10.8800056"
    StartDate=$(date -u -d "2000/1/1 $string1" +"%s.%N")
    FinalDate=$(date -u -d "2000/1/1 $string2" +"%s.%N")
    date -u -d "2000/1/1 $FinalDate sec - $StartDate sec" +"%j days %H:%M:%S.%N"

    datetime1=$date_end
    datetime2=20160312000101

    seconds1=$(date --date "$(echo "$datetime1" | sed -nr 's/(....)(..)(..)(..)(..)(..)/\1-\2-\3 \4:\5:\6/p')" +%s)
    seconds2=$(date --date "$(echo "$datetime2" | sed -nr 's/(....)(..)(..)(..)(..)(..)/\1-\2-\3 \4:\5:\6/p')" +%s)

    delta=$((seconds1 - seconds2))
    # echo "$delta seconds"
    diff1 = $(datediff -i '%Y%m%d%H%M%S.%N' 20160312000101 20160312000101)
    echo $diff1 seconds
    # echo date $date
    # a=( $(date -u -d "2000/1/1 $FinalDate sec - $StartDate sec" +"%j days %H:%M:%S.%N") )
    # a[0]=$((10#${a[0]}-1)); echo "${a[@]}"  
    # echo a $a

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
        cd "repos/ns-3-allinone/ns-3.30/" 
        ./waf --run "scratch/${file}"
    fi
    if [[ $lgp = "python" ]] 
    then
        # cd desired/directory
        cd "repos/ns-3-allinone/ns-3.30/" 
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

echo "End of Simulation"