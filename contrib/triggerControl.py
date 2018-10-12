#!/usr/bin/env python3
import numpy as np
from numpy import loadtxt
from scipy.optimize import curve_fit
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
import serial
import sys
import time
import os

#Global variables
chan=1 #channel in use
retries=2   #Number of automatic retries for calibration
mod=None  #Mode select integer
params = []  #ARRAY of FIT-Parameters for calibration
gain,offset,intime=0,0,1000
parfile=open("params.dat", "w")
parfile.close()
h = open('pe.dat', 'w')


#Methods of Serial and Scan
def resetMode(ser):    #It may take up to 20s, but this will definitely put the controller in idle Mode    #        print("RESET START")
    ser.write(b'\n')
    ser.close()
    time.sleep(1)
    ser.open()
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.flush()
    ser.send_break()
    ser.close()
    time.sleep(1)
    ser.open()
    ser.write('SCAN THR 1\n'.encode('ascii'))
    wait_until_string(ser, '# Threshold scan for a single channel started. Please wait...\r\n')
    time.sleep(1)
    ser.write(b'\n')
    print_until_string(ser, '# Threshold scan aborted.\r\n')
    pass                #        print("RESET finished")
    
    
def wait_until_string(ser, string):                    #ALLOW SOME TIME FOR SERIAL TRANSMISSION TO COMMENCE
    tz=0
    while tz < 25:
        tz+=1
        line = ser.readline()
        if len(line) > 0 and line == string.encode('ascii'):
            break
        if tz > 24:
            resetMode(ser)
            
def wait_until_gain(ser, string):       #MAKES SURE GAIN AND OFFSET ARE TRANSMITTED SUCCESSFULLY TO CONTROLLER
    tz=0
    while tz < 25:
        tz+=1
        line = ser.readline()
        if len(line) > 0 and line.strip().split()[1] == string.encode('ascii'):
            print(line.decode('ascii'))
            break
        if tz > 24:
            print('ERROR CMD SET GAIN/OFFSET FAILED!!')
            break    
            
def print_until_string(ser, string, file=sys.stderr):       # FLUSH THE INPUT STILL COMING FROM THE CONTROLLER
    tz=0
    while tz < 25:
        tz+=1
        line = ser.readline()
        if len(line) > 0 and line == string.encode('ascii'):
            break
        if tz > 24:
            resetMode(ser)
            
def print_scan_until_string(ser, string, file=sys.stderr):      #WRITES THE INCOMING CONTROLLER DATA TO FILE AND STD.OUT
    global h
    global chan
    global mod
    xaxis = 0
    c = 0
    cutoff = 1.0
    while True:
        line = ser.readline()
        if len(line) > 0 and line == string.encode('ascii'):
            break
        if mod == "CALPESCAN" or mod == "PESCAN":
            if xaxis == 0:
                if line.decode('ascii').strip().split()[2] < line.decode('ascii').strip().split()[3]:
                    xaxis=2
                else:
                    xaxis=3            
            print(line.decode('ascii').strip().split()[xaxis], line.decode('ascii').strip().split()[4], line.decode('ascii').strip().split()[5], file=h) 
            print(line.decode('ascii').strip(), file=sys.stdout)
            if float(line.decode('ascii').strip().split()[4]) > 10 and float(line.decode('ascii').strip().split()[xaxis]) > 8:
                cutoff = 3.0
        else:
            print(line.decode('ascii').strip().split()[(chan-1)], line.decode('ascii').strip().split()[4], line.decode('ascii').strip().split()[5], file=sys.stdout)
            if float(line.decode('ascii').strip().split()[(chan-1)]) > 90:
                cutoff = 2.0
        if float(line.decode('ascii').strip().split()[4]) < cutoff:
            if int(line.decode('ascii').strip().split()[chan-1]) > 54 or mod != "SSCAN":
                c+=1
            if c > retries:
                break                
            
def thr_scan(ser, channel):         #BEGINS THE SCAN ROUTINE FOR SINGLE CHANNEL
    global retries
    ser.write('SCAN THR {}\n'.format(channel).encode('ascii'))
    wait_until_string(ser, '# Threshold scan for a single channel started. Please wait...\r\n')
    try:
        print_scan_until_string(ser, '# Threshold scan finished.\r\n')
    except KeyboardInterrupt:
        ser.write(b'\n')
        print_until_string(ser, '# Threshold scan aborted.\r\n')
        pass

def pe_thr_scan(ser):            #BEGINS THE SCAN ROUTINE FOR PE THR
    global retries
    ser.write('SCAN PE THR\n'.encode('ascii'))
    wait_until_string(ser, '# Threshold scan started. Please wait...\r\n')
    try:
        print_scan_until_string(ser, '# Threshold scan finished.\r\n')
    except KeyboardInterrupt:
        ser.write(b'\n')
        print_until_string(ser, '# Threshold scan aborted.\r\n')
        pass



#Methods of Calibration
def fitting(xdata, ydata, uplim, lolim):
    global parfile
    k=0
    xodata = []
    yodata = []
    
    def func(x, a, b, c):
        return (a / (np.exp(x-b)+1) )+ c
   
    for i in range(lolim,uplim):
        xodata.append(xdata[i])
        yodata.append(ydata[i])
   
    popt, pcov = curve_fit(func, xodata, yodata, bounds=([-np.inf, 10, 0],[np.inf, 40, 10]))
    popt
    perr = np.sqrt(np.diag(pcov))
    print(popt[0], popt[1], popt[2], perr[1], file=parfile)
    print(popt[0], popt[1], popt[2], perr[1])
    return popt[1]         
         
def prepfit(xdata, ydata, dac1, dac2):
    global gain
    global offset
    lolim=int((dac1-gain*.7))
    uplim=int((dac1+gain*.9))
    if uplim > len(xdata):
            uplim = len(xdata)
    dac1 = fitting(xdata, ydata, uplim, lolim)
    lolim=int((dac2-gain*.7))
    uplim=int((dac2+gain*.9))
    if uplim > len(xdata):
            uplim = len(xdata)
    dac2 = fitting(xdata, ydata, uplim, lolim)
    gain=(dac2-dac1) 
    offset=(2*dac1-dac2)
    print("GAIN:",gain,"| OFFSET:",offset,"| DAC1/2:",dac1,"/",dac2, file=sys.stdout)

def precalibration(ser, string, file=sys.stderr):
    global gain
    global offset
    global chan
    global parfile
    global fcal
    if chan==1:
        f = open('cal1.dat','w')
        if fcal ==1:
            r1 = open('ch1run1', 'r')
    else:
        g = open('cal2.dat','w')
        if fcal ==1:
            r2 = open('ch2run1', 'r')
    a = 0
    b = 0
    count = 0
    lastcount = 0
    slope = 0
    lastslope = 0
    maxslope = 0
    dac = 0
    dac1 = 0
    dac2 = 0
    err = 0
    xdata = []
    ydata = []          #    print("...")
    while dac < 54:
        if fcal==0:
            line = ser.readline()
            if len(line) > 0 and line == string.encode('ascii'):
                break
            dac = int(line.decode('ascii').strip().split()[(chan-1)])
            count = float(line.decode('ascii').strip().split()[4])
            err = float(line.decode('ascii').strip().split()[5])
        else:
            if chan==1:
                line = r1.readline()
            else:
                line = r2.readline()
            dac = int(line.strip().split()[0]) 
            count = float(line.strip().split()[1])
            err = float(line.strip().split()[2])
        slope = (count - lastcount)
        xdata.append(dac)
        if count != 0:
            ydata.append(np.log(count))
        else:
            ydata.append(0)
        if chan == 1:
            print(dac, count, err, file=f)
        else:
            print(dac, count, err, file=g)
        if dac > 15:                             # 
            if dac % 5 == 0 and fcal == 0:
                print(53-dac, " measurements left, DAC1/2:",dac1,dac2)
            if dac > 45 and dac2 == 0:
                break
            if slope < maxslope:
                if a == 0 and b == 0:
                     maxslope = slope
                     dac1 = dac     #                     print("^^ DAC1", file=sys.stderr)
                if a == 0 and b == 1:
                     maxslope = slope
                     dac2 = dac     #                     print("^^ DAC2", file=sys.stderr)
            if abs(slope) < 0.1*abs(maxslope) and abs(lastslope) < 0.1*abs(maxslope) and dac > 16:   
                if a == 0 and b == 0: 
                    a=1                            
                if a == 0 and b == 0 and dac > 25 and abs(slope) < 50:
                    a==1
            if a == 1 and abs(slope) > abs(lastslope)*1.5 and dac > (dac1 + 7):
                    a=0
                    b=1
                    maxslope=slope              
        lastcount=count
        lastslope=slope
    if fcal==0:
        ser.write(b'\n')
        print_until_string(ser, '# Threshold scan aborted.\r\n')
        pass
    gain=(dac2-dac1) 
    offset=(2*dac1-dac2)
    print("PRECAL CH",chan,": DAC1/2:",dac1,"/",dac2, file=sys.stdout)
    if gain > 0:
        print(chan, dac1, dac2, 0, file=parfile)
        prepfit(xdata, ydata, dac1, dac2)
    else:
        print("retrying..")
        if fcal==0:
            resetMode(ser)
    if chan==1:
        f.close()
        if fcal==1:
            r1.close()
    else:
        g.close()
        if fcal==1:
            r2.close()
            
            
def start_calib(ser, channel):
    ser.write('SCAN THR {}\n'.format(channel).encode('ascii'))
    wait_until_string(ser, '# Threshold scan for a single channel started. Please wait...\r\n')

    try:
        precalibration(ser, '# Threshold scan finished.\r\n')
    except KeyboardInterrupt:
        ser.write(b'\n')
        print_until_string(ser, '# Threshold scan aborted.\r\n')
        pass
    
def set_gain(ser):
    global gain
    ser.write('SET GAIN {},{}\n'.format(chan, gain).encode('ascii'))
    wait_until_gain(ser, 'gain_CH{}'.format(chan))
    
def set_offset(ser):
    global offset
    ser.write('SET OFFSET {},{}\n'.format(chan, offset).encode('ascii'))
    wait_until_gain(ser, 'offset_CH{}'.format(chan))
    
def set_intime(ser):
    global intime
    ser.write('SET TIME {}\n'.format(intime).encode('ascii')) 
    
def calibration(ser):
    global gain, chan, offset, parfile, retries, intime, fcal
    parfile=open("params.dat", "w")
    gain=0
    retr=0
    set_intime(ser)
    for chan in (1,2):
        print(" ")
        if os.path.exists('ch{}run1'.format(chan)):
            if os.stat('ch{}run1'.format(chan)).st_size != 0:
                fcal=1
                print('fast-calibrating CH',chan)
            else:
                fcal=0
                resetMode(ser)
                print("calibrating CH",chan, file=sys.stderr)
        else:
                fcal=0
                resetMode(ser)
                print("calibrating CH",chan, file=sys.stderr)
        while gain < 1 and retr<retries:
            retr+=1
            precalibration(ser, '# Threshold scan finished.\r\n')
        if retr > retries:
            print("ERROR, NO CALIBRATION ACHIEVED FOR CH: ",chan, file=sys.stderr)
            break
        else:
            retr = 0
            print("")
            print("awaiting controller response..")
            #resetMode(ser)
            #set_gain(ser)
            #set_offset(ser)
            gain=0
    
    
        
#ARGUMENTS        
if __name__ == '__main__':
    parser = ArgumentParser(description='Automatic SiPM Trigger Controller.\n USE: --channel $CH, --inttime $TIME \muS, --port $COMPORT, --mode $MODE\n MODEs are:\n  SSCAN  single channel THR scan\n  PESCAN is coincident PE scan \n  CAL is calibration \n  CALPESCAN ist calib. plus PE THR scan.', formatter_class=RawTextHelpFormatter)
    parser.add_argument('--port', default='/dev/ttyACM0')
    parser.add_argument('--channel', type=int, default=1)
    parser.add_argument('--mode', type=str, default=1)
    parser.add_argument('--inttime', type=int, default=1000)
    args = parser.parse_args()
    
    ser = serial.Serial(args.port,
                        9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        xonxoff=True,
                        rtscts=True)

    # Discard incomplete input lines
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    ser.open()
    ser.write('\n'.encode('ascii'))

#MODE SELECT
chan=(args.channel)
mod=(args.mode)
intime=(args.inttime)
parfile=open("params.dat", "a")

if mod == "SSCAN":                           #MODE FOR SINGEL CHANNEL SCAN
        thr_scan(ser, args.channel)

if mod == "CAL":                             #Mode for CALIBRATION
           calibration(ser)        
        
if mod == "CALPESCAN":                       #Mode for Cal and PE Scan
            calibration(ser)
            resetMode(ser)
            print(" ")
            print("Starting PE Scan", file=sys.stdout)
            pe_thr_scan(ser)
            
if mod == "PESCAN":                          #Mode for PE Scan only
            print("Starting PE Scan", file=sys.stdout)
            pe_thr_scan(ser)
            
ser.write('\n'.encode('ascii'))        
ser.close()
parfile.close()
h.close()
