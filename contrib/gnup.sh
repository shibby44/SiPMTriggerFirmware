#!/usr/bin/gnuplot

set term pdf color size 15cm, 10cm 
set output 'output.pdf'
set mxtics
set mytics 10
set bars 0.5 
set logscale y
#set grid


#set xrange [0:64]
#set yrange [0.1:25000]
set logscale y
set key top right
set key box opaque height 0 width 0
set key title "Spectrum"
#set xlabel 'Threshold / p.e.'
set ylabel 'Rate / Hz'
set bars 0.5 	

set title 'Title'
#set ylabel 'Rate / Hz'
#set xlabel 'Threshold / LSB'

set style line 1 pt 7 ps 0.2 lt 1 lw 0.8 lc rgb '#FF8C00' #darkorange
set style line 4 pt 7 ps 0.2 lt 1 lw 0.8 lc rgb '#0000CD' #mediumblue
set style line 2 pt 7 ps 0.2 lt 1 lw 0.8 lc rgb '#DC143C' #crimson
set style line 5 pt 7 ps 0.2 lt 1 lw 0.8 lc rgb '#32CD32' #limegreen
set style line 3 pt 7 ps 0.2 lt 1 lw 0.8 lc rgb '#DA70D6' #orchid	
set style line 6 pt 7 ps 0.2 lt 1 lw 1 lc -1
set style line 7 lt 0 lw 1 lc rgb "#A9A9A9" #darkgray
set style line 8 lt 0 lw 1.7 lc rgb "#696969" #dimgray
set style line 9 pt 7 ps 0.2 lt 1 lw 1.5 lc rgb '#A0522D' #sienna
set style line 10 pt 7 ps 0.2 lt 1 lw 1 lc rgb '#DEB887' #burlywood
set style line 11 pt 7 ps 0.2 lt 1 lw 1 lc rgb '#FFDAB9' #peachpuff
set style line 12 pt 7 ps 0.2 lt 1 lw 0 lc rgb '#FFDAB9' #peachpuff

set grid xtics ytics  mxtics mytics ls 8, ls 7

