#!/usr/bin/env python3

import serial
from pymeasure.instruments.keithley import Keithley2400
from time import sleep

def sendCommand (ser, cmd, terminator=b'\r'):
	ser.write( cmd.encode('ASCII') + terminator )

def sendCommands (ser, cmds, terminator=b'\r'):
	for c in cmds:
		sendCommand(ser, c, terminator)

def getReading (ser):
	sendCommand(ser, ':READ?')
	res = ser.read()
	while res[-1] != 13:
		res += ser.read()
	return res

ser = serial.Serial(port='/dev/ttyUSB0',
					baudrate=9600,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE,
					timeout=None,
					xonxoff=False,
					rtscts=False,
					dsrdtr=False
					)

# sendCommands(ser, [
# 				'*RST', # Reset instrument to default parameters.
# 				':SYST:BEEP:STAT 0', # Disable the fricking beep
# 				':SOUR:FUNC CURR', # Select current source function.
# 				':SENS:FUNC "VOLT"', # Select volt measurement function.
# 				# ':SENS:RES:NPLC 1', # Set measurement speed to 1 PLC.
# 				# ':SENS:RES:MODE MAN', # Select manual ohms mode.
# 				# ':SOUR:CLE:AUTO ON', # Enable source auto output-off.
# 				':SOUR:CURR 1E-4', # Set source to output 10mA.
# 				':SENS:VOLT:PROT 1', # Set 1V compliance limit.
# 				':TRIG:COUN 10', # Set to perform one measurement.
# 				':FORM:ELEM VOLT', # Set to output volt reading to PC.
# 				':OUTP ON'
# 				])
# print(getReading(ser))
# sendCommand(ser, ':OUTP OFF')

sendCommands(ser, [
				'*RST', # Reset instrument to default parameters.
				':SYST:BEEP:STAT 0', # Disable the fricking beep
				':SENS:FUNC "VOLT"', # Select volt measurement function.
				':SENS:VOLT:PROT 1', # Set 1V compliance limit.
				':SOUR:FUNC CURR', # Select current source function.
				':SOUR:CURR:STAR 0.001',
				':SOUR:CURR:STOP 0.01',
				':SOUR:CURR:MODE SWE',
				':SOUR:SWE:POIN 10',
				':TRIG:COUN 10',
				':FORM:ELEM VOLT,CURR', # Set to output volt reading to PC.
 				':OUTP ON',
 				':INIT'
				])
readings = getReading(ser).decode('ASCII')[:-1].split(',')
print(len(readings), readings)
sleep(5)
sendCommand(ser, ':OUTP OFF')

ser.close()