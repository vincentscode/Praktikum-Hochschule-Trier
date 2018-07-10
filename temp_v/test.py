import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

i = "/home/student/Desktop/Labor-Robotik-Trier-2018/images/1.jpg"
img = cv2.imread(i)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
t = np.arange(0.0, 1.0, 0.001)
a0 = 5
f0 = 3
delta_f = 5.0
plt.axis([0, 1, -10, 10])

axH = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='red')
axS = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='red')
axV = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='red')


def update(val):
	h = int(sliderH.val)
	s = int(sliderS.val)
	v = int(sliderV.val)
	print(h, s, v)

	lower_red = np.array([10, 135, 30])
	upper_red = np.array([20, 250, 205])
	
	mask = cv2.inRange(hsv, lower_red, upper_red)
	res = cv2.bitwise_and(img,img, mask= mask)
	plt.subplot(121)
	plt.imshow(res,cmap='gray')
	plt.xticks([]), plt.yticks([])
	fig.canvas.draw_idle()
	cv2.imwrite("img.png", res)

sliderH = Slider(axH, 'H', 0.0, 255.0, valinit=f0, valstep=delta_f)
sliderH.on_changed(update)
sliderS = Slider(axS, 'S', 0.0, 255.0, valinit=f0, valstep=delta_f)
sliderS.on_changed(update)
sliderV = Slider(axV, 'V', 0.0, 255.0, valinit=f0, valstep=delta_f)
sliderV.on_changed(update)

plt.show()
