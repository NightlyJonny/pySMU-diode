#!/usr/bin/env python3

from SerialSMU import SMU
from time import sleep

# Initialize SMU and measure IV
def acquireIV (port, baudrate, compl, istart, istop, points=10):
	smu = SMU(port, baudrate)
	smu.sendCommands([	
		':DISP:TEXT:DATA "Initializing...',
		':DISP:TEXT:STAT ON',			# Set text-mode to show user defined string on display.
		'*RST',							# Reset instrument to default parameters.
		':SYST:BEEP:STAT 0',			# Disable the fricking beep
		
		':SENS:FUNC "VOLT"',			# Select volt measurement function.
		':SENS:VOLT:RANG:AUTO ON',		# Set auto-range.
		f':SENS:VOLT:PROT {compl}',			# Set 1V compliance limit.
		
		':SOUR:FUNC CURR',				# Select current source function.
		':SOUR:CURR:RANG:AUTO ON',		# Set auto-range.
		f':SOUR:CURR:STAR {istart}',	# Sweep starting point.
		f':SOUR:CURR:STOP {istop}',		# Sweep end point.
		':SOUR:CURR:MODE SWE',			# Set output in sweeping mode.
		f':SOUR:SWE:POIN {points}',		# Set sweep points.
		':SOUR:SWE:DIR UP',				# Set sweep direction start->stop.
		
		f':TRIG:COUN {points}',			# Set trigger count, MUST BE THE SAME AS SWEEP POINTS.
		':FORM:ELEM TIME,VOLT,CURR',	# Quantities sent to the PC.
		':OUTP ON',						# Enable output.
		':DISP:TEXT:DATA "Sweeping...',
		':INIT'							# Start measurements.
	])

	sleep(1)
	readings = smu.getReadingsArray()
	smu.sendCommands([
		':OUTP OFF',
		':DISP:TEXT:DATA "Done!'
	])
	smu.sendCommand(':DISP:TEXT:STAT OFF')
	smu.close()

	return readings