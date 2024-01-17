#@ Dataset ds

import math as maths

from net.imglib2.view import Views
from net.imagej.axis import Axes

from ij import IJ
from ij.measure import ResultsTable

from javax.swing import JOptionPane


title = ds.getName()
width = ds.getWidth()
height = ds.getHeight()
channels = ds.getChannels()
depth = ds.getDepth()
frames = ds.getFrames()

if channels != 2 or depth > 1 or frames == 1:
	JOptionPane.showMessageDialog(None, "2 channel 2D time series required", "Wrong Dimensions", JOptionPane.ERROR_MESSAGE)
	exit(1)

timeAxis = ds.axis(Axes.TIME).get()
frameInterval = timeAxis.calibratedValue(1)
timeUnit = timeAxis.unit()

table = ResultsTable()
table.showRowNumbers(False)
table.setPrecision(3)

for t in range(frames):
	IJ.showStatus("Pearson Correlation: frame "+str(t)+"/"+str(frames))
	viewcursorC0 = Views.interval(ds, [0,0,0,t], [width-1,height-1,0,t])
	viewcursorC1 = Views.interval(ds, [0,0,1,t], [width-1,height-1,1,t])
	cursorC0 = viewcursorC0.cursor()
	cursorC1 = viewcursorC1.cursor()
	C0 = []
	C1 = []
	while cursorC0.hasNext():
		cursorC0.fwd()
		cursorC1.fwd()
		C0.append(cursorC0.get().get())
		C1.append(cursorC1.get().get())
	
	cursorC0.reset()
	cursorC1.reset()
	
	meancursorC0 = sum(C0)/len(C0)
	meancursorC1 = sum(C1)/len(C1)
	covar = 0
	varC0 = 0
	varC1 = 0
	for i in range(len(C0)):
		covar += (C0[i]-meancursorC0)*(C1[i]-meancursorC1)
		varC0 += (C0[i]-meancursorC0)*(C0[i]-meancursorC0)
		varC1 += (C1[i]-meancursorC1)*(C1[i]-meancursorC1)
	r = covar/maths.sqrt(varC0*varC1)
	table.setValue("Time ("+timeUnit+")", t, maths.ceil(t*frameInterval)) # ceil to get int seconds
	table.setValue("Pearson\'s r", t, r)
	
	table.show("Correlation "+title)
	