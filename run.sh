#!/bin/sh
sizeFile=$(wc -l < scratch/Times.txt)

lastTime=$(tail -n 1 scratch/Times.txt )

# lastTime=${lastLine%}

echo $sizeFile
echo $lastTime

./waf --run "scratch/fifth --nPackets=$sizeFile --timeStopSimulation=$lastTime+1"
# --timeStopSimulation=$lastTime