#!/usr/bin/env python3

from SerialSMU import SMU
from time import sleep
import numpy as np

# Initialize SMU and measure IV
def acquireIV (port, baudrate, compl, istart, istop, points):
	smu = SMU(port, baudrate)
	smu.sendCommands([	
		':DISP:TEXT:DATA "Initializing...',
		':DISP:TEXT:STAT ON',			# Set text-mode to show user defined string on display.
		'*RST',							# Reset instrument to default parameters.
		':SYST:BEEP:STAT 0',			# Disable the fricking beep
		
		':SENS:FUNC "VOLT"',			# Select volt measurement function.
		':SENS:VOLT:RANG:AUTO ON',		# Set auto-range.
		f':SENS:VOLT:PROT {compl}',		# Set 1V compliance limit.
		
		':SOUR:CLE:AUTO ON',			# Enable auto output-off.
		':SOUR:FUNC CURR',				# Select current source function.
		':SOUR:CURR:RANG:AUTO ON',		# Set auto-range.
		f':SOUR:CURR:STAR {istart}',	# Sweep starting point.
		f':SOUR:CURR:STOP {istop}',		# Sweep end point.
		f':SOUR:SWE:POIN {points}',		# Set sweep points.
		':SOUR:CURR:MODE SWE',			# Set output in sweeping mode.
		':SOUR:SWE:DIR UP',				# Set sweep direction start->stop.
		
		f':TRIG:COUN {points}',			# Set trigger count, MUST BE THE SAME AS SWEEP POINTS.
		':FORM:ELEM TIME,VOLT,CURR',	# Quantities sent to the PC.
		# ':OUTP ON',						# Enable output.
		':DISP:TEXT:DATA "Sweeping...',
		# ':INIT'							# Start measurements.
	])

	sleep(1)
	readings = smu.getReadingsArray()
	print('-= DEBUG: ', readings)
	smu.sendCommands([
		# ':OUTP OFF',
		':DISP:TEXT:DATA "Done!',
		':DISP:TEXT:STAT OFF'
	])
	smu.close()

	# Transform reading from linear array to group of quantities (time, voltage, and current)
	# e.g., [0.0, 1.0, 1.0, 0.1, 1.5, 3.0] -> [[0.0, 0.1], [1.0, 1.5], [1.0, 3.0]]
	#         t    V    I    t    V    I   ->      t           V            I
	NMEAS = 3 # Number of quantities measured (:FORM:ELEM command)
	readings = np.array(readings[:-(len(readings)%NMEAS)]) # Discarding extra ungrouped measurements
	res = readings.reshape((3, -1), order='F') # Reshaping into a matrix with NMEAS row

	return res