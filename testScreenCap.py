import time

import cv2
import mss
import numpy


with mss.mss() as sct:
	monitor = {'top': 150, 'left': 60, 'width': 830, 'height': 350}

	while 'Screen capturing':
		last_time = time.time()
		img = numpy.array(sct.grab(monitor))


		cv2.imshow('n.jpg', img)
		cv2.waitKey(1)