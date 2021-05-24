#!/usr/bin/env python3

# 
# Main class used to communicate with the SMU via the serial interface
# 

import serial

class SMU:
	ser = None
	dry = False

	# Initialize serial comunication with default parameters
	# port='' to test the class locally (no serial communication, commands sent to stdout, etc...)
	def __init__ (self, port, br=9600):
		self.dry = (len(port) == 0)
		if not self.dry:
			self.ser = serial.Serial(port=port,
						baudrate=br,
						bytesize=serial.EIGHTBITS,
						parity=serial.PARITY_NONE,
						stopbits=serial.STOPBITS_ONE,
						timeout=None,
						xonxoff=False,
						rtscts=False,
						dsrdtr=False
						)
		else:
			print('_Serial initialization_')

	# Send a command using the open serial communication
	# Returns False when no serial communication is active
	def sendCommand (self, cmd, terminator=b'\r'):
		# Dry run
		if self.dry:
			print(cmd)
			return True

		# Real run
		if self.ser == None:
			return False
		else:
			self.ser.write( cmd.encode('ASCII') + terminator )
			return True

	# Send a series of commands using the open serial communication
	# Returns False when no serial communication is active
	def sendCommands (self, cmds, terminator=b'\r'):
		# Dry run
		if self.dry:
			print('[\n\t', end='')
			print(',\n\t'.join(cmds))
			print(']')
			return True

		# Real run
		if self.ser == None:
			return False
		else:
			for c in cmds:
				self.sendCommand(c, terminator)
			return True

	# Send read command and get reading from the SMU
	# Returns bytes read or None in case of errors
	def getReading (self):
		res = self.sendCommand(':READ?')
		if not res:
			return None

		# Dry run
		if self.dry:
			return b'0.0,1.0,1.0,0.1,1.5,3.0,0.2,2.0,6.0\r'

		# Real run
		if self.ser == None:
			return None
		else:
			res = self.ser.read()
			while res[-1] != 13:
				res += self.ser.read()
			return res

	# Get readings as array of float numbers
	# Returns number array or None in case of errors
	def getReadingsArray (self):
		res = self.getReading()
		if res != None:
			return [float(r) for r in res.decode('ASCII')[:-1].split(',')]
		else:
			return None

	# Close the serial connection
	# Returns nothing
	def close (self):
		# Dry run
		if self.dry:
			print('_Closing serial communication_')

		# Real run
		if self.ser != None:
			self.ser.close()
			self.ser = None

# Dry run for debugging and example commands
if __name__ == '__main__':
	from time import sleep
	smu = SMU('')

	# SINGLE READING TEST
	# smu.sendCommands([
	# 					'*RST', # Reset instrument to default parameters.
	# 					':SYST:BEEP:STAT 0', # Disable the fricking beep
	# 					':SOUR:FUNC CURR', # Select current source function.
	# 					':SENS:FUNC "VOLT"', # Select volt measurement function.
	# 					# ':SENS:RES:NPLC 1', # Set measurement speed to 1 PLC.
	# 					# ':SENS:RES:MODE MAN', # Select manual ohms mode.
	# 					# ':SOUR:CLE:AUTO ON', # Enable source auto output-off.
	# 					':SOUR:CURR 1E-4', # Set source to output 10mA.
	# 					':SENS:VOLT:PROT 1', # Set 1V compliance limit.
	# 					':TRIG:COUN 10', # Set to perform one measurement.
	# 					':FORM:ELEM VOLT', # Set to output volt reading to PC.
	# 					':OUTP ON'
	# 				])

	# SWEEP TEST
	smu.sendCommands([
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

	# PRINT RESULTS
	readings = smu.getReadingsArray()
	print(readings)
	sleep(1)
	smu.sendCommand(':OUTP OFF')
	smu.close()