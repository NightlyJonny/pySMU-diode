#!/usr/bin/env python3

from SerialSMU import SMU
import numpy as np

# Initialize SMU and measure IV
def acquireIV (port, baudrate, compl, istart, istop, points, direction='BOTH'):
	# Initialization and main settings
	NMEAS = 3 # Number of quantities measured (:FORM:ELEM command)
	smu = SMU(port, baudrate)
	smu.sendCommands([
		'*RST',							# Reset instrument to default parameters.
		':DISP:TEXT:DATA "Initializing..."',
		':DISP:TEXT:STAT ON',			# Set text-mode to show user defined string on display.
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
		
		f':TRIG:COUN {points}',			# Set trigger count, MUST BE THE SAME AS SWEEP POINTS.
		':FORM:ELEM TIME,VOLT,CURR',	# Quantities sent to the PC. UPDATE "NMEAS" VARIABLE TOO.
		# ':OUTP ON',					# Enable output.
		# ':INIT'						# Start measurements.
	])

	# Sweeping up
	readingsUp = []
	if (direction == 'UP') or (direction == 'BOTH'):
		smu.sendCommands([
			':SOUR:SWE:DIR UP',				# Set sweep direction start->stop.
			':DISP:TEXT:DATA "Sweeping up..."'
		])
		readingsUp = smu.getReadingsArray()
		readingsUp = readingsUp[:-(len(readingsUp)%NMEAS)] # Discarding extra ungrouped measurements

	# Sweeping down
	readingsDown = []
	if (direction == 'DOWN') or (direction == 'BOTH'):
		smu.sendCommands([
			':SOUR:SWE:DIR DOWN',			# Set sweep direction stop->start.
			':DISP:TEXT:DATA "Sweeping down..."'
		])
		readingsDown = smu.getReadingsArray()
		readingsDown = readingsDown[:-(len(readingsDown)%NMEAS)] # Discarding extra ungrouped measurements
	
	# Print results and close serial connection
	print('-= DEBUG: ', readingsUp + readingsDown, '=-')
	smu.sendCommands([
		# ':OUTP OFF',
		':DISP:TEXT:DATA "Done!"',
		':DISP:TEXT:STAT OFF'
	])
	smu.close()

	# Transform reading from linear array to group of quantities (time, voltage, and current)
	# e.g., [0.0, 1.0, 1.0, 0.1, 1.5, 3.0] -> [[0.0, 0.1], [1.0, 1.5], [1.0, 3.0]]
	#         t    V    I    t    V    I   ->      t           V            I
	readings = np.array(readingsUp + readingsDown)
	res = readings.reshape((3, -1), order='F') # Reshaping into a matrix with NMEAS row

	return res