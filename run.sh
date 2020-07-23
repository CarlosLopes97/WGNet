#!/bin/sh
sizeFile=$(wc -l < scratch/Times.txt)
echo $sizeFile

./waf --run "scratch/fifth --nPackets=$sizeFile"