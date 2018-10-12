#!/usr/bin/env python3
#                   THIS PROGRAM USES THE cal1.dat cal2.dat and params.dat file created by the triggerControl.py --mode CAL script execution and visualizes
##                  the gain and offset evaluating functions and parameters. Run simply from the dir of those mentioned files with python3 calfitplot.py
#######
########
#########
#########
import numpy as np
from numpy import loadtxt
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



###  INITIALISATION ###
params = open("params.dat", "r")
cal1 = open("cal1.dat", "r")
cal2 = open("cal2.dat", "r")
xdata =  loadtxt("cal1.dat", comments="#", dtype=float, usecols = (0,), unpack=False)
ydata1 =  np.log(loadtxt("cal1.dat", comments="#", dtype=float, usecols = (1,), unpack=False))
ydata2 =  np.log(loadtxt("cal2.dat", comments="#", dtype=float, usecols = (1,), unpack=False))
pop = loadtxt("params.dat", unpack=False, comments='#')
cal1.close()
cal2.close()
params.close()

fp1a= [pop[1][0], pop[1][1], pop[1][2]]
fp1b= [pop[2][0], pop[2][1], pop[2][2]]
fp2a= [pop[4][0], pop[4][1], pop[4][2]]
fp2b= [pop[5][0], pop[5][1], pop[5][2]]
label1=['Spektrum CH1', 'predac1:', pop[0][1], 'predac2:', pop[0][2]]
label2=['Spektrum CH2', 'predac1:', pop[3][1], 'predac2:', pop[3][2]]
lab1a=[fp1a[1],pop[1][3]]
lab1b=[fp1b[1],pop[2][3]]
lab2a=[fp2a[1],pop[4][3]]
lab2b=[fp2b[1],pop[5][3]]
labdat1=[pop[0][0],pop[0][1],pop[0][2]]
labdat2=[pop[3][0],pop[3][1],pop[3][2]]
def func(x, a, b, c):
   return (a / (np.exp(x-b)+1) )+ c

def plot1():
    fig, ax = plt.subplots(1,1)
    plt.title('Darstellung der Kalibrierung durch die Software')
    ax.plot(xdata, ydata1, 'b-', label='Spektrum CH%1d, dac1/2: %2.1d/%2.1d' % tuple(labdat1))
    ax.axvline(x=pop[0][1], color='r', linestyle='solid')
    ax.axvline(x=pop[0][2], color='r', linestyle='solid')
    ax.axvline(x=pop[1][1], color='y', linestyle='solid')
    ax.axvline(x=pop[2][1], color='g', linestyle='solid')

    ax.plot(xdata, func(xdata, *fp1a), 'g--', color='y',
       label='dac1fit: %2.2f$\pm$%0.2f' % tuple(lab1a))
    ax.plot(xdata, func(xdata, *fp1b), 'g--', color='g',
       label='dac2fit: %2.2f$\pm$%0.2f' % tuple(lab1b))
    ax.set_xlabel('Diskriminatorschwelle / DAC')
    ax.set_xlim(10,45)
    ax.set_ylabel('LOG( Rate / Hz )')
    ax.set_ylim(0,11)
    ax.set_yticks(np.arange(0,12,1))
    ax.set_yticks(np.arange(0,12,0.2), minor = True)
    ax.grid(which='minor', color='lightgray')
    ax.grid(which='major', color='black')
    ax.legend(fancybox=True, framealpha=1)
    fig.savefig("calFIT1.pdf", bbox_inches='tight')

def plot2():
    fig, ax = plt.subplots(1,1)
    plt.title('Darstellung der Kalibrierung durch die Software')
    ax.plot(xdata, ydata2, 'b-', label='Spektrum CH%1d, dac1/2: %2.1d/%2.1d' % tuple(labdat2)) 
    ax.axvline(x=pop[3][1], color='r', linestyle='solid')
    ax.axvline(x=pop[3][2], color='r', linestyle='solid')
    ax.axvline(x=pop[4][1], color='y', linestyle='solid')
    ax.axvline(x=pop[5][1], color='g', linestyle='solid')

    ax.plot(xdata, func(xdata, *fp2a), 'g--', color='y',
       label='dac1fit: %2.2f$\pm$%0.2f' % tuple(lab2a))
    ax.plot(xdata, func(xdata, *fp2b), 'g--', color='g',
       label='dac2fit: %2.2f$\pm$%0.2f' % tuple(lab2b))
    ax.set_xlabel('Diskriminatorschwelle / DAC')
    ax.set_xlim(10,45)
    ax.set_ylabel('LOG( Rate / Hz )')
    ax.set_ylim(0,11)
    ax.set_yticks(np.arange(0,12,1))
    ax.set_yticks(np.arange(0,12,0.2), minor = True)
    ax.grid(which='minor', color='lightgray')
    ax.grid(which='major', color='black')
    ax.legend(fancybox=True, framealpha=1)
    fig.savefig("calFIT2.pdf", bbox_inches='tight')



plot1()
plt.clf()
plot2()
#plt.show()
