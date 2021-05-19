#!/usr/bin/env python3

from SerialSMU import SMU
from time import sleep

# Current sweep parameters
ISTART = 0.001
ISTOP  = 0.01
POINTS = 10

# Initialize SMU and measure IV
smu = SMU('')
smu.sendCommands([	
	':DISP:TEXT:DATA "Initializing...',
	':DISP:TEXT:STAT ON',			# Set text-mode to show user defined string on display.
	'*RST',							# Reset instrument to default parameters.
	':SYST:BEEP:STAT 0',			# Disable the fricking beep
	
	':SENS:FUNC "VOLT"',			# Select volt measurement function.
	':SENS:VOLT:RANG:AUTO ON',		# Set auto-range.
	':SENS:VOLT:PROT 1',			# Set 1V compliance limit.
	
	':SOUR:FUNC CURR',				# Select current source function.
	':SOUR:CURR:RANG:AUTO ON',		# Set auto-range.
	f':SOUR:CURR:STAR {ISTART}',	# Sweep starting point.
	f':SOUR:CURR:STOP {ISTOP}',		# Sweep end point.
	':SOUR:CURR:MODE SWE',			# Set output in sweeping mode.
	f':SOUR:SWE:POIN {POINTS}',		# Set sweep points.
	':SOUR:SWE:DIR UP',				# Set sweep direction start->stop.
	
	f':TRIG:COUN {POINTS}',			# Set trigger count, MUST BE THE SAME AS SWEEP POINTS.
	':FORM:ELEM TIME,VOLT,CURR',	# Quantities sent to the PC.
	':OUTP ON',						# Enable output.
	':DISP:TEXT:DATA "Sweeping...',
	':INIT'							# Start measurements.
])

readings = smu.getReadingsArray()
print(readings)

sleep(1)
smu.sendCommands([
	':OUTP OFF',
	':DISP:TEXT:DATA "Done!'
])

sleep(5)
smu.sendCommand(':DISP:TEXT:STAT OFF')

smu.close()