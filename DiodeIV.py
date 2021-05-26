#!/usr/bin/env python3

from SerialSMU import SMU
import numpy as np

# Initialize SMU and measure IV
def acquireIV (port, baudrate, compl, istart, istop, points, source='CURR', direction='BOTH'):
	sens = 'VOLT' if source == 'CURR' else 'CURR'

	# Initialization and main settings
	NMEAS = 3 # Number of quantities measured (:FORM:ELEM command)
	smu = SMU(port, baudrate)
	smu.sendCommands([
		'*RST',							# Reset instrument to default parameters.
		':DISP:TEXT:DATA "Initializing..."',
		':DISP:TEXT:STAT ON',			# Set text-mode to show user defined string on display.
		':SYST:BEEP:STAT 0',			# Disable the fricking beep
		
		f':SENS:FUNC "{sens}"',			# Select volt measurement function.
		f':SENS:{sens}:RANG:AUTO ON',	# Set auto-range.
		f':SENS:{sens}:PROT {compl}',	# Set 1V compliance limit.
		
		':SOUR:CLE:AUTO ON',			# Enable auto output-off.
		f':SOUR:FUNC {source}',				# Select current source function.
		f':SOUR:{source}:RANG:AUTO ON',		# Set auto-range.
		f':SOUR:{source}:STAR {istart}',	# Sweep starting point.
		f':SOUR:{source}:STOP {istop}',		# Sweep end point.
		f':SOUR:SWE:POIN {points}',		# Set sweep points.
		f':SOUR:{source}:MODE SWE',			# Set output in sweeping mode.
		
		f':TRIG:COUN {points}',			# Set trigger count, MUST BE THE SAME AS SWEEP POINTS.
		':FORM:ELEM TIME,VOLT,CURR',	# Quantities sent to the PC. UPDATE "NMEAS" VARIABLE TOO.
	])

	# Sweeping up
	readingsUp = []
	if (direction == 'UP') or (direction == 'BOTH'):
		smu.sendCommands([
			':SOUR:SWE:DIR UP',				# Set sweep direction start->stop.
			':DISP:TEXT:DATA "Sweeping up..."'
		])
		readingsUp = smu.getReadingsArray()
		extra = len(readingsUp)%NMEAS
		if extra > 0:
			readingsUp = readingsUp[:-extra] # Discarding extra ungrouped measurements

	# Sweeping down
	readingsDown = []
	if (direction == 'DOWN') or (direction == 'BOTH'):
		smu.sendCommands([
			':SOUR:SWE:DIR DOWN',			# Set sweep direction stop->start.
			':DISP:TEXT:DATA "Sweeping down..."'
		])
		readingsDown = smu.getReadingsArray()
		extra = len(readingsDown)%NMEAS
		if extra > 0:
			readingsDown = readingsDown[:-extra] # Discarding extra ungrouped measurements
	
	# Print results and close serial connection
	smu.sendCommand(':DISP:TEXT:DATA "Done :)"')
	smu.close()

	# Transform reading from linear array to group of quantities (time, voltage, and current)
	# e.g., [0.0, 1.0, 1.0, 0.1, 1.5, 3.0] -> [[0.0, 0.1], [1.0, 1.5], [1.0, 3.0]]
	#         t    V    I    t    V    I   ->      t           V            I
	readings = np.array(readingsUp + readingsDown)
	res = readings.reshape((NMEAS, -1), order='F') # Reshaping into a matrix with NMEAS row

	return res

if __name__ == '__main__':
	# Function call example (on Linux)
	print(acquireIV('/dev/ttyUSB0', 9600, 3.0, 0.0/1000, 5.0/1000, 20, source='CURR', direction='BOTH'))