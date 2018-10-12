#!/bin/bash
#
#THIS SCRIPT IS FOR AUTOMATED SCANNING, CALIBRATION, AND PLOTTING OF THRESHOLD/PETHRSCANS OF THE ARDUINO TRIGGER BOARD
#MAKE SURE THE PYTHON/GNUPLOT SCRIPTS LISTED BELOW ARE WITHIN THE SAME DIR AS THIS SCRIPT. 
#THIS SCRIPT CAN BE CALLED FROM ANYWHERE, EG. DATA/EXPERIMENT FOLDERS.
#
#
#

curdir="$( cd "$(dirname "$0")" ; pwd -P )"
testdir="${PWD##*/}"
#echo $testdir
cp -f $curdir/triggerControl.py complete.py    #PYTHON3 Script that does the actual communication, may be used independently 
cp -f $curdir/calfitplot.py calplot.py   #PYTHON3 Script that displays current calibration from cal1.dat/cal2.dat from complete.py --mode CAL
cp -f $curdir/gnup.sh plot.sh            #Gnuplot bare bones file to plot THR/PETHRSCANs
ch=1    #Default Channel for Single scan
bs='\'  #workauround special char
gf='"'  #workauround special char
on=3    

                                                                                #Mode SELECT
echo "0: THR-SCAN; 1: PE THR SCAN; 2: BOTH; 3: CALIBRATION ONLY"
read -n 1 mode
echo ""

if [ $mode -gt 0 ] && [ $mode -lt 3 ]; then
   echo "With new calibration? [y/any key]"
   read -n 1 k
   echo " "
else
    k=false
fi

                                                                                    #SINGLE SCAN
if [ $mode != 1 ] && [ $mode != 3 ]; then
  #echo " Which Channels? 1, 2; 0 = both"
  #read channels
  #echo "Channels: $channels"
   channels=0
  if [ $channels -eq 0 ]; then
    on=1
    off=2;
    echo "set xlabel 'Threshold / LSB'">>plot.sh
    echo "plot "'"'>>plot.sh
    echo "$(cat plot.sh)ch1run1"'" w errorlines lt 1 pt 3'>plot.sh
  else 
    on=channels
    off=channels 
    echo "$(cat plot.sh)ch$channels"run1'"'>plot.sh
    echo "$(cat plot.sh) w errorlines lt 1 pt 3" >plot.sh
  fi
 echo "How many THR-scans of the individual channel(s)?"
 read -n 1 n
 echo ""
 #n=1
 echo "starting $n runs @ $(date +"%T") ..."
 for ((ch=$on;ch<=$off;ch++))
  do
    for ((i=1;i<=$n;i++))
        do
         python3 complete.py --mode SSCAN --channel $ch > ch$ch"run"$i
         echo "channel $ch run $i:"
         cat ch$ch"run"$i
         echo "^This was channel $ch run $i^"
         echo "The time is: $(date +"%T")"
         if [ $i -gt 1 ] || [ $ch -gt 1 ]; then
            echo "$(cat plot.sh), $bs" >plot.sh
            echo "$gf"ch"$ch"run"$i$gf"  >> plot.sh
            echo "$(cat plot.sh) w errorlines lt $(($i+$ch-1)) pt $((2*$i+$ch))" > plot.sh
        fi
        sleep 2
    done 
 done
 cp -f ch1run1 "ch1D$testdir"
 cp -f ch2run1 "ch2D$testdir"
  ./plot.sh
  mv -f output.pdf THRSCAN.pdf
 if [ $mode -eq 2 ]; then
   cp -f plot.sh plotTHR.sh
   cp -f $curdir/gnup.sh plot.sh
 fi
fi
                                                                                    #PESCAN AND CALIBRATION
if [ $mode -gt 0 ] && [ $mode -lt 3 ]; then
    if [ $k == "y" ]; then
            python3 complete.py --mode CALPESCAN
            python3 calplot.py
    else
        python3 complete.py --mode PESCAN
        rm -f params.dat
    fi
    echo "set xlabel 'Threshold / P.E.'">>plot.sh
    echo "plot "'"'>>plot.sh
    echo "$(cat plot.sh)"pe.dat'"'>plot.sh
    echo "$(cat plot.sh) w errorlines lt 1 pt 5" >plot.sh
    ./plot.sh
    mv -f pe.dat coinc"$testdir".dat
    mv -f plot.sh plotPETHR.sh
    mv -f output.pdf PETHRSCAN.pdf  
fi

    if [ $mode -eq "3" ]; then   
        python3 complete.py --mode CAL
        python3 calplot.py
        rm -f params.dat
    fi
#Cleaning up
rm -f r*
rm -f *.py

notify-send "THE TASK WAS COMPLETED!"
xmessage "THE TASK WAS COMPLETED!" -timeout 8
echo "done! Evince plot(s)? [y/any key]"
read -n 1 h
if [ $h == "y" ]; then
    evince *.pdf &
    exit
else
 echo Goodbye!!
fi
