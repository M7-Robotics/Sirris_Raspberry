#!/usr/bin/env python
#
# GrovePi Python library
# v1.2.2
#
# This file provides the basic functions for using the GrovePi
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi
#
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/grovepi
#
'''
## License

The MIT License (MIT)

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2017  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''
# Initial Date: 13 Feb 2014
# Last Updated: 11 Nov 2016
# http://www.dexterindustries.com/
# Author	Date      		Comments
# Karan		13 Feb 2014  	Initial Authoring
# 			11 Nov 2016		I2C retries added for faster IO
#							DHT function updated to look for nan's

import sys
import time
import math
import struct
import numpy

debug = 0

if sys.version_info<(3,0):
	p_version=2
else:
	p_version=3

if sys.platform == 'uwp':
	import winrt_smbus as smbus
	bus = smbus.SMBus(1)
else:
	import smbus
	import RPi.GPIO as GPIO
	rev = GPIO.RPI_REVISION
	if rev == 2 or rev == 3:
		bus = smbus.SMBus(1)
	else:
		bus = smbus.SMBus(0)

# I2C Address of Arduino
address = 0x04

# Command Format
# digitalRead() command format header
dRead_cmd = [1]
# digitalWrite() command format header
dWrite_cmd = [2]
# analogRead() command format header
aRead_cmd = [3]
# analogWrite() command format header
aWrite_cmd = [4]
# pinMode() command format header
pMode_cmd = [5]
# Ultrasonic read
uRead_cmd = [7]
# Get firmware version
version_cmd = [8]
# Accelerometer (+/- 1.5g) read
acc_xyz_cmd = [20]
# RTC get time
rtc_getTime_cmd = [30]
# DHT Pro sensor temperature
dht_temp_cmd = [40]

# Grove LED Bar commands
# Initialise
ledBarInit_cmd = [50]
# Set orientation
ledBarOrient_cmd = [51]
# Set level
ledBarLevel_cmd = [52]
# Set single LED
ledBarSetOne_cmd = [53]
# Toggle single LED
ledBarToggleOne_cmd = [54]
# Set all LEDs
ledBarSet_cmd = [55]
# Get current state
ledBarGet_cmd = [56]

# Grove 4 Digit Display commands
# Initialise
fourDigitInit_cmd = [70]
# Set brightness, not visible until next cmd
fourDigitBrightness_cmd = [71]
# Set numeric value without leading zeros
fourDigitValue_cmd = [72]
# Set numeric value with leading zeros
fourDigitValueZeros_cmd = [73]
# Set individual digit
fourDigitIndividualDigit_cmd = [74]
# Set individual leds of a segment
fourDigitIndividualLeds_cmd = [75]
# Set left and right values with colon
fourDigitScore_cmd = [76]
# Analog read for n seconds
fourDigitAnalogRead_cmd = [77]
# Entire display on
fourDigitAllOn_cmd = [78]
# Entire display off
fourDigitAllOff_cmd = [79]

# Grove Chainable RGB LED commands
# Store color for later use
storeColor_cmd = [90]
# Initialise
chainableRgbLedInit_cmd = [91]
# Initialise and test with a simple color
chainableRgbLedTest_cmd = [92]
# Set one or more leds to the stored color by pattern
chainableRgbLedSetPattern_cmd = [93]
# set one or more leds to the stored color by modulo
chainableRgbLedSetModulo_cmd = [94]
# sets leds similar to a bar graph, reversible
chainableRgbLedSetLevel_cmd = [95]

# Read the button from IR sensor
ir_read_cmd=[21]
# Set pin for the IR reciever
ir_recv_pin_cmd=[22]

dus_sensor_read_cmd=[10]
dust_sensor_en_cmd=[14]
dust_sensor_dis_cmd=[15]
encoder_read_cmd=[11]
encoder_en_cmd=[16]
encoder_dis_cmd=[17]
flow_read_cmd=[12]
flow_disable_cmd=[13]
flow_en_cmd=[18]
# This allows us to be more specific about which commands contain unused bytes
unused = 0
retries = 10
# Function declarations of the various functions used for encoding and sending
# data from RPi to Arduino


# Write I2C block
def write_i2c_block(address, block):
	for i in range(retries):
		try:
			return bus.write_i2c_block_data(address, 1, block)
		except IOError:
			if debug:
				print ("IOError")
	return -1

# Read I2C byte
def read_i2c_byte(address):
	for i in range(retries):
		try:
			return bus.read_byte(address)
		except IOError:
			if debug:
				print ("IOError")
	return -1


# Read I2C block
def read_i2c_block(address):
	for i in range(retries):
		try:
			return bus.read_i2c_block_data(address, 1)
		except IOError:
			if debug:
				print ("IOError")
	return -1

# Arduino Digital Read
def digitalRead(pin):
	write_i2c_block(address, dRead_cmd + [pin, unused, unused])
	# time.sleep(.1)
	n = read_i2c_byte(address)
	return n

# Arduino Digital Write
def digitalWrite(pin, value):
	write_i2c_block(address, dWrite_cmd + [pin, value, unused])
	return 1


# Setting Up Pin mode on Arduino
def pinMode(pin, mode):
	if mode == "OUTPUT":
		write_i2c_block(address, pMode_cmd + [pin, 1, unused])
	elif mode == "INPUT":
		write_i2c_block(address, pMode_cmd + [pin, 0, unused])
	return 1


# Read analog value from Pin
def analogRead(pin):
	write_i2c_block(address, aRead_cmd + [pin, unused, unused])
	read_i2c_byte(address)
	number = read_i2c_block(address)
	return number[1] * 256 + number[2]


# Write PWM
def analogWrite(pin, value):
	write_i2c_block(address, aWrite_cmd + [pin, value, unused])
	return 1

# Read the firmware version
def version():
	write_i2c_block(address, version_cmd + [unused, unused, unused])
	time.sleep(.1)
	read_i2c_byte(address)
	number = read_i2c_block(address)
	return "%s.%s.%s" % (number[1], number[2], number[3])


# after a list of numerical values is provided
# the function returns a list with the outlier(or extreme) values removed
# make the std_factor_threshold bigger so that filtering becomes less strict
# and make the std_factor_threshold smaller to get the opposite
def statisticalNoiseReduction(values, std_factor_threshold = 2):
	if len(values) == 0:
		return []
		
	mean = numpy.mean(values)
	standard_deviation = numpy.std(values)

	if standard_deviation == 0:
		return values

	filtered_values = [element for element in values if element > mean - std_factor_threshold * standard_deviation]
	filtered_values = [element for element in filtered_values if element < mean + std_factor_threshold * standard_deviation]

	return filtered_values