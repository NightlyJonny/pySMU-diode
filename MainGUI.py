#!/usr/bin/env python3

import tkinter as tk
import tkinter.scrolledtext as tkscrolled
from PIL import Image, ImageTk
from itertools import cycle
import matplotlib.pyplot as plt
import numpy as np
import sys
import glob
import serial
from DiodeIV import acquireIV

def start(Compliance, SweepStart, SweepFinish, Points, baudrate, port):
	global Results
	# text = tkscrolled.ScrolledText(UserLabx).grid(row=9, column=17, rowspan = 5,columnspan= 16, sticky= "WE", pady=5, padx=5)
	readings = np.array(acquireIV(port, baudrate, Compliance, SweepStart, SweepFinish, Points))
	# text.insert(tk.END, readings)
	# text.grid(row=6, column=1, columnspan= 1, sticky= "WE")
	Results = np.append(Results, readings)
	show_plot()

def show_plot():
	global Results
	# DO STUFF WITH THE RESULTS!
	
	plt.cla()
	plt.plot(Results)
	plt.show()
	
def export_csv():
	global Results
	np.savetxt("results.csv", Results, delimiter = ";")
	
def progress(iterator):
	cycling = cycle("⡇⣆⣤⣰⢸⠹⠛⠏")
	for element in iterator:
		print(next(cycling), end="\r")
		yield element
	print(" \r", end='')

def init_func():
	warn = tk.Toplevel()
	warn.title("Abandon the current session?")
	label = tk.Label(warn, textvariable=tk.StringVar(value="Are you you to want to leave the current session?\nThe data not saved will be lost!!!!!")).pack()
	ok = tk.Button(warn, text="Ok", command = lambda: initializer() or warn.destroy()).pack()
	null = tk.Button(warn, text="Cancel", command = warn.destroy).pack()

def initializer():
	global Results    
	Compliance.set(1.0)
	SweepStart.set(0.1)
	SweepFinish.set(10.0)
	Points.set(10)
	Baudrate.set(9600)
	Port.set('')
	Results = np.array([], dtype=np.float64)

def serial_ports():
	if sys.platform.startswith('win'):
		ports = ['COM%s' % (i + 1) for i in range(10)]
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		ports = glob.glob('/dev/tty[A-Za-z]*')
	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/tty.*')
	else:
		raise EnvironmentError('Unsupported platform')
	return ports

# for idx in progress(range(10000)):
# 	sleep(0.5)
# print("finished!")
UserLabx = tk.Tk()
UserLabx.title("SMU Interface")

SMUimage= Image.open("SMU.jpg")
SMUimage = SMUimage.resize((480, 350), Image.ANTIALIAS)
SMUimage = ImageTk.PhotoImage(SMUimage)
#SMUimage = tk.Label(image=SMUimage).grid(row=0, column=3, columnspan =1, rowspan = 1)

#Variable Initialization
Compliance = tk.DoubleVar(value=1.0)
SweepStart = tk.DoubleVar(value=0.1)
SweepFinish = tk.DoubleVar(value=10.0)
Points = tk.IntVar(value=10)
Baudrate = tk.IntVar(value=9600)
baudrate = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 , 256000]
Port = tk.StringVar()
port = [''] + serial_ports()
Results = np.array([], dtype=np.float64)

#let's make the window responsive
n_rows =8
n_columns =32
for i in range(n_rows):
	UserLabx.grid_rowconfigure(i,  weight =1)
for i in range(n_columns):
	UserLabx.grid_columnconfigure(i,  weight =1)

smuimage = tk.Label(UserLabx,image=SMUimage).grid(row=0, column=16, columnspan =16, rowspan = 10)

sep = tk.Frame(UserLabx, height=3, width=450, bd=1, relief="sunken").grid(row=0, column=1, columnspan = 15, pady=1)
init = tk.Label(UserLabx, text = "Intializing setup", font=("Courier", 7)).grid(row=0, column=0,sticky = "WE", columnspan = 1)

baudLab = tk.Label(UserLabx, text = "Baudrate").grid(row=1, column=0,sticky = "WE", padx=5)
baud = tk.OptionMenu(UserLabx, Baudrate, *baudrate)
baud.config(width=10)
baud.grid(row=1, column = 1, sticky = "W")

portLab = tk.Label(UserLabx, text = "Port", height =5, width=5).grid(row=1, column=2,sticky = "WE", padx=5)
port = tk.OptionMenu(UserLabx, Port, *port)
port.config(width=1)
port.grid(row=1, column = 3, sticky = "W")

sep = tk.Frame(UserLabx, height=3, width=450, bd=1, relief="sunken").grid(row=2, column=1, columnspan = 15, padx=5, pady=2)
init = tk.Label(UserLabx, text = "Measure setup", font=("Courier", 7)).grid(row=2, column=0,sticky = "WE", columnspan = 1,padx=2)

compl = tk.Label(UserLabx, text = "Compliance (V)").grid(row=3, column=0,sticky = "WE", columnspan=1, padx=2)
complValue = tk.Entry(UserLabx, textvariable=Compliance).grid(row=3, column=1,sticky = "WE",columnspan=1, padx=2)
	
sweep = tk.Label(UserLabx, text = "Sweep start (mA)").grid(row=4, column=0,sticky = "WE",columnspan=1, padx=2)
sweepValue = tk.Entry(UserLabx, textvariable=SweepStart).grid(row=4, column=1,sticky = "WE",columnspan=1, padx=2)
 
finish = tk.Label(UserLabx, text = "Sweep end (mA)").grid(row=5, column=0,sticky = "WE",columnspan=1, padx=2)
finishValue = tk.Entry(UserLabx, textvariable=SweepFinish).grid(row=5, column=1,sticky = "WE",columnspan=1, padx=2)

points = tk.Label(UserLabx, text = "Sweep points").grid(row=6, column=0,sticky = "WE",columnspan=1, padx=2)
pointsValue = tk.Entry(UserLabx, textvariable=Points).grid(row=6, column=1,sticky = "WE",columnspan=1, padx=2)

tk.Button(UserLabx, text = "Start serial comunication", command =lambda: start(Compliance.get(), SweepStart.get()/1000.0, SweepFinish.get()/1000.0, Points.get(), Baudrate.get(), Port.get())).grid(row=7,column=0, columnspan = 16,sticky = "WE", padx=10, pady = 10)

menu = tk.Menu(UserLabx)
UserLabx.config(menu=menu)
fileMenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label = "Reset all data" ,command = init_func)
fileMenu.add_command(label = "Export data", command = export_csv) 
   
editMenu = tk.Menu(menu)
menu.add_cascade(label="Measure", menu=editMenu)
editMenu.add_command(label="Choose X-Y measure")
editMenu.add_command(label="Show plot", command = show_plot)
UserLabx.mainloop()