#!/usr/bin/env python
#
#   A simple program to try and measure the changes in voltage on a wire using B effect. sensor wire is taped 
#   to the measured wire so that the B effect creates current in the wire, or use a hall effect sensor
#
#   Basically its a simple program to read in data from an ADC converter..
#
#   This does not use i2c or spi interfacing. makes it simpler for beginner experimentation
#
#   it also writes the data to a text file called AD_converted_data_at_time_blah_blah
#
#
#
#
#   Created by Christopher Rehm Springe Germany. Sept 8 2015
#
#   This is licenced for use under the creative commons modified licence.
#   you may use the program for free if you do not charge for whatever you do with it.
#
#   If you charge money for something that you use this software as a part of please send 100 euros to
#
#   christopherrehm@web.de on paypal as a royalty payment.
#
#
#
 

import RPi.GPIO as GPIO
import time
import datetime
import pprint

################################################

#pi pin assignments note you can change these imputs as your design requires.
clockPin   = 37 #gpio26   CLK
dataInPin  = 38 #gpio20   Din
dataOutPin = 35 #gpio19   Dout
controlPin = 36 #gpio16   CS

timeHack = 0                   #second counter, marks time of sample
DEBUG = False           #set to true for debugging function
maxAnalogVoltage = 3.3  #change for different max analog input
sampleInterval = 1      #change for different sampling interval, currently 1 second.
################################################

#set pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
GPIO.setup(clockPin,   GPIO.OUT)
GPIO.setup(controlPin, GPIO.OUT)  
GPIO.setup(dataInPin,  GPIO.OUT)   
GPIO.setup(dataOutPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set dataOUtPin high(+3.3V) to off 

###############################################
#data stroage matrix
matrix = [0 for x in range(25)] #temp storage for raw digital data
voltages =[0 for x in range(8)] #data storage for converted values

if DEBUG == True:
    pprint.pprint(matrix)

#####################################
def setup():
    GPIO.output(controlPin, GPIO.HIGH)
    GPIO.output(clockPin,   GPIO.HIGH)
    GPIO.output(dataInPin,  GPIO.LOW)
    if DEBUG == True:
        print "expected", 1,1,0,0
        debug()
#######################################
def shortPause():
    pass
    #time.sleep(.00001) took out, dont need.
#######################################
def debug(): ###THIS DOES NOT FUNCTION CURRENTLY: NEEDS A READ VALUE OF PIN FUNCTION
              ###However it is useful for debugging as it stops the program and you can read pin values with a voltmeter
    #if controlPin  == 1:
    #    cp = 1
    #else:
    #    cp = 0
    #if clockPin == 1:
    #    clkp = 1
    #else:
    #    clkp = 0
    #if dataInPin == 1:
    #    dip = 1
    #else:
    #    dip = 0
    #if dataOutPin == 1:
    #    dop = 1
    #else:
    #    dop = 0
    #print cp,clkp,dip,dop
    print "press any key to continue"
    dummyinput =raw_input()

###########################################

def clockCycle():
    GPIO.output(clockPin, GPIO.LOW)
    if DEBUG == True:
        print "expected",0,0,"x","x"
        debug()
    shortPause()
    GPIO.output(clockPin, GPIO.HIGH)
    if DEBUG == True:
        print "expected",0,1,"x","x"
        debug()
    shortPause()

########################################

def sendControl(analogChannel):
    #set up  control signal THIS IS DESIGNED FOR SINGLE INPUT NOT DIFFERENTIAL INPUT
    GPIO.output(dataInPin, GPIO.HIGH)
    if DEBUG == True:
        print "expected", 1,1,1,0
        debug()
    #pull  control signal low
    GPIO.output(controlPin, GPIO.LOW)
    if DEBUG == True:
        print "expected", 0,1,1,0
        debug()
    shortPause()
    #send start bit
    clockCycle()
    #send sing/ diff bit 
    clockCycle()
    #set data bit to 0 for next 3 pulses, collect reading from pin 0
    #pins are numbered in binary from 0 to 7... you can expand for more signal lines. 
    if analogChannel == 0:
        GPIO.output(dataInPin, GPIO.LOW)
        #send 3 control bits
        #send 1st  bit
        clockCycle()
        #send 2nd  bit 
        clockCycle()
        #send 3rd bit
        clockCycle()
    if analogChannel == 1:
        GPIO.output(dataInPin, GPIO.LOW)
        clockCycle()
        clockCycle()
        GPIO.output(dataInPin, GPIO.HIGH)
        clockCycle()
    if analogChannel == 2:
        GPIO.output(dataInPin, GPIO.LOW)
        clockCycle()
        GPIO.output(dataInPin, GPIO.HIGH)
        clockCycle()
        GPIO.output(dataInPin, GPIO.LOW)
        clockCycle()
    if analogChannel == 3:
        GPIO.output(dataInPin, GPIO.LOW)
        clockCycle()
        GPIO.output(dataInPin, GPIO.HIGH)
        clockCycle()
        clockCycle()
    if analogChannel == 4:
        GPIO.output(dataInPin, GPIO.HIGH)
        clockCycle()
        GPIO.output(dataInPin, GPIO.LOW)
        clockCycle()
        clockCycle()
    if analogChannel == 5:
        GPIO.output(dataInPin, GPIO.HIGH)
        clockCycle()
        GPIO.output(dataInPin, GPIO.LOW)
        clockCycle()
        GPIO.output(dataInPin, GPIO.HIGH)
        clockCycle()
    if analogChannel == 6:
        GPIO.output(dataInPin, GPIO.HIGH)
        clockCycle()
        clockCycle()
        GPIO.output(dataInPin, GPIO.LOW)
        clockCycle()
    if analogChannel == 7:
        GPIO.output(dataInPin, GPIO.HIGH)
        clockCycle()
        clockCycle()
        clockCycle()

    #dummy cycles
    #clockCycle()   took out, rewrote program to compensate using the matrix as holder. 
    #clockCycle()
    #clockCycle()

################################
   
def collectOutput(analogChannel):
    for x in range (0,len(matrix)):
        matrix[x] = GPIO.input(dataOutPin)
        clockCycle()
    voltages[analogChannel] = convertToV()
    GPIO.output(controlPin,GPIO.HIGH)

################################
def convertToV ():
    decValue =matrix[11]+2*matrix[10]+4*matrix[9]+8*matrix[8]+16*matrix[7]+32*matrix[6]+64*matrix[3]+128*matrix[5]+256*matrix[4]+512*matrix[3]
    convFactor = maxAnalogVoltage/1024
    return decValue*convFactor 

################################
try:
    setup() 
    filename ="AD_Converted_Data_At_" + datetime.datetime.now().strftime("%I:%M:%S_%p_on_%B_%d_%Y")
    
    file = open(filename, 'w') 
    print("This program  takes data from an MCP3008 and outputs it to the terminal. It works on all 8 channels.")
    print("You can rewrite the program to output to a file or other location.")  
    print("Would you like to run the voltage analysis? Type y to start. Any other character ends the program")
    userInputa = raw_input()
    if userInputa ==  "y":
        while True:
            sendControl(0)
            collectOutput(0)
            sendControl(1)
            collectOutput(1)
            sendControl(2)
            collectOutput(2)
            sendControl(3)
            collectOutput(3)
            sendControl(4)
            collectOutput(4)
            sendControl(5)
            collectOutput(5)
            sendControl(6)
            collectOutput(6)
            sendControl(7)
            collectOutput(7)
            if DEBUG == True:
                pprint.pprint(matrix)
            print ("TimeHack: %1d volts: %2.3f   %2.3f   %2.3f   %2.3f   %2.3f   %2.3f   %2.3f   %2.3f   " % (timeHack,  voltages[0],voltages[1],voltages[2],voltages[3],voltages[4],voltages[5],voltages[6],voltages[7]))
            file.write("TimeHack: %1d volts: %2.3f   %2.3f   %2.3f   %2.3f   %2.3f   %2.3f   %2.3f   %2.3f  \n" % (timeHack,  voltages[0],voltages[1],voltages[2],voltages[3],voltages[4],voltages[5],voltages[6],voltages[7]))
            timeHack += 1
            time.sleep(sampleInterval)

except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the flowing code will be  executed.
    file.close()
    GPIO.cleanup()                     # Release resource

