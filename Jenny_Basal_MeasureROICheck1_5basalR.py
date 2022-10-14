# Segment the largest egg chamber in C1 and measure basal signal inside an inner band in C2
#
#	- by Richard Butler, Gurdon Institute Imaging Facility


import math as maths

from java.awt import Color

from ij import IJ, ImagePlus, ImageStack
from ij.plugin import RoiEnlarger
from ij.plugin.filter import ThresholdToSelection
from ij.process import ImageStatistics, Blitter, ImageProcessor, ShortProcessor, AutoThresholder, FloodFiller
from ij.measure import ResultsTable
from ij.gui import Roi, ShapeRoi, PolygonRoi, Overlay


def getEggRoi(ip):

	mask = ip.duplicate()
	mask.blurGaussian(2.5)

	stats = mask.getStatistics()
	hist = mask.getHistogram(256)
	thresh = AutoThresholder().getThreshold(AutoThresholder.Method.Otsu, hist)
	thresh = (thresh/float(255)) * (stats.max-stats.min) + stats.min
	mask.threshold( int(thresh) )
	mask = mask.convertToByte(False)
	
	fillHoles(mask)

	mask.setThreshold(255, 255, ImageProcessor.NO_LUT_UPDATE)
	composite = ThresholdToSelection().convert(mask)
	
	rois = ShapeRoi(composite).getRois()
	egg = None
	maxA = 0
	if len(rois) == 1:
		egg = composite
	else:
		egg = None
		for roi in rois:
			area = roi.getStatistics().area
			if area > maxA:
				egg = roi
				maxA = area

	hull = ShapeRoi(egg.getConvexHull())
	hullA = hull.getStatistics().area
	if maxA>0 and hullA/maxA > 2:
		egg = hull	#use the convex hull if the egg ROI area is less than half the size

	ed = 30
	egg = RoiEnlarger.enlarge(egg, -ed)
	egg = RoiEnlarger.enlarge(egg, ed)

	return egg


def fillHoles(mask):
	width = mask.getWidth()
	height = mask.getHeight()
	ff = FloodFiller(mask)
	mask.setColor(127)
	foreground = 127
	background = 0
	for y in range(height):
	    if mask.getPixel(0,y)==background:
	    	ff.fill(0, y)
	    if mask.getPixel(width-1,y)==background:
	    	ff.fill(width-1, y)
	for x in range(width):
	    if mask.getPixel(x,0)==background:
	    	ff.fill(x, 0)
	    if mask.getPixel(x,height-1)==background:
	    	ff.fill(x, height-1)
	n = width*height
	for i in range(n):
		if mask.get(i)==127:
		    mask.set(i, 0)
		else:
		    mask.set(i, 255)

imp = IJ.getImage()
cal = imp.getCalibration()
stack = imp.getStack()
ol = Overlay()
T = imp.getNFrames()
rt = ResultsTable()

basalR = 1.5 #µm
rpx = basalR/cal.pixelWidth

eggs = [None for t in range(T+1)]
t1s = 0.0
for t in range(1,T+1):
	c1ip = stack.getProcessor(imp.getStackIndex(1,1,t))
	egg = getEggRoi(c1ip)
	eggs[t] = egg

	if t>1:
		same = ShapeRoi(eggs[t-1]).and(ShapeRoi(egg))
		diff = ShapeRoi(eggs[t-1]).xor(ShapeRoi(egg))
		sameA = same.getStatistics().area
		diffA = diff.getStatistics().area
		cons = abs(sameA-diffA)/sameA
		if cons < 0.75:
			eggs[t] = eggs[t-1]
	
for t in range(1,T+1):
	c1ip = stack.getProcessor(imp.getStackIndex(1,1,t))
	c2ip = stack.getProcessor(imp.getStackIndex(2,1,t))
	egg = eggs[t]
	inner = RoiEnlarger.enlarge(egg, -rpx)
	basal = ShapeRoi(egg).not(ShapeRoi(inner))

	if basal.getLength()==0:
		continue

	c2ip.setRoi(basal)
	stats = c2ip.getStatistics()
	s = stats.mean
	if t==1:
		t1s = s
	row = rt.getCounter()
	rt.setValue("Frame", row, t)
	rt.setValue("Time ("+cal.getTimeUnit()+")", row, IJ.d2s(((t-1)*cal.frameInterval), 0))
	rt.setValue("C2 Basal Signal", row, s/t1s)
	rt.setValue("C2 Basal Mean", row, stats.mean)
	rt.setValue("C2 Basal StdDev", row, stats.stdDev)
	rt.setValue("C2 Basal Median", row, stats.median)

	basal.setPosition(-1,-1,t)
	basal.setStrokeColor(Color.MAGENTA)
	ol.add(basal)

imp.setOverlay(ol)
rt.show(imp.getTitle()+"_Basal_Measure")
