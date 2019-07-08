import socket
import threading

import math
import time
from operator import itemgetter
from collections import deque

import numpy as np
import cv2
import imutils

import mss
import mss.tools

# SETTINGS
HOST = '127.0.0.1'
PORT = 1234
BUFFER_SIZE = 1024

# SOCKET
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((HOST, PORT))

def send(a):
	if a.strip() != "":
		unsendable = False
		while len(bytes(a, "utf8")) > BUFFER_SIZE:
			a += b'0x00'
		for c in a:
			if c not in [str(i) for i in range(0, 10)] + ["r", "f"]:
				print("Invalid character:", c)
				unsendable = True
				break
		if not unsendable:
			if 'r' in a:
				sock.sendall(bytes(a, "UTF-8"))
				print("rotationVelocity is now", a[1:])
			elif 'f' in a:
				sock.sendall(bytes(a, "UTF-8"))
				print("forwardVelocity is now", a[1:])
			else:
				print("Invalid format.")

def process_lines(lines_in, tresh=5):
	# get lines as arrays
	lines = [(l[0], l[1], l[2], l[3]) for l in [(l[0]) for l in lines_in]]

	# sort by direction
	lines_x = []
	lines_y = []
	for line in lines:
		x1, y1, x2, y2 = line
		if abs(x1-x2) < abs(y1-y2):
			lines_y.append(line)
		else:
			lines_x.append(line)

	# filter
	y_sorter = 0
	x_sorter = 1

	lines_y = sorted(lines_y, key=itemgetter(y_sorter))
	lines_x = sorted(lines_x, key=itemgetter(x_sorter))

	groups_y = []
	for i in range(len(lines_y)):
		if groups_y:
			x = lines_y[i][y_sorter]
			if abs(groups_y[-1][-1][y_sorter] - x) < tresh:
				groups_y[-1].append(lines_y[i])
			else:
				groups_y.append([lines_y[i]])
		else:
			groups_y.append([lines_y[i]])

	good_y = []
	for group in groups_y:
		for ln in group:
			line = (group[0][0], ln[1], group[0][0], ln[3])
			good_y.append(line)


	groups_x = []
	for i in range(len(lines_x)):
		if groups_x:
			x = lines_x[i][x_sorter]
			if abs(groups_x[-1][-1][x_sorter] - x) < tresh:
				groups_x[-1].append(lines_x[i])
			else:
				groups_x.append([lines_x[i]])
		else:
			groups_x.append([lines_x[i]])

	good_x = []
	for group in groups_x:
		for ln in group:
			line = (ln[0], group[0][1], ln[2], group[0][1])
			good_x.append(line)

	# visualize old
	LinesX_2 = np.zeros((530,550,3), np.uint8)
	LinesY_2 = np.zeros((530,550,3), np.uint8)

	for line in lines_y:
		x1, y1, x2, y2 = line
		cv2.line(LinesY_2, (x1, y1), (x2, y2), (0, 255, 0), 3)

	for line in lines_x:
		x1, y1, x2, y2 = line
		cv2.line(LinesX_2, (x1, y1), (x2, y2), (0, 255, 0), 3)

	lines_x = good_x
	lines_y = good_y

	gl = []
	for line in lines_x:
		gl.append(line)
	for line in lines_y:
		gl.append(line)

	return gl

def find_colored_object(img, lowerBound, upperBound, minRadius=10):
	center = (0, 0)
	pts = deque(maxlen=10)

	frame = img

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, lowerBound, upperBound)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
 
	if len(cnts) > 0:
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		if radius > minRadius:
			return center

def find_bot(image):
	center = (0, 0)

	lower = [0, 0, 250, 0]
	upper = [0, 0, 255, 255]

	lower = np.array(lower, dtype="uint8")
	upper = np.array(upper, dtype="uint8")

	mask = cv2.inRange(image, lower, upper)

	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	image = cv2.bitwise_and(image, image, mask = mask)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	canny = cv2.Canny(gray, 2, 200)

	lines = cv2.HoughLinesP(canny, 1, np.pi/180, 3, maxLineGap=0)

	if len(cnts) > 0:
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

	x_avg = 0
	y_avg = 0
	for line in lines:
		x1, y1, x2, y2 = line[0]
		cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
		x_avg += x1 + x2
		y_avg += y1 + y2

	x_avg /= (len(lines)*2)
	y_avg /= (len(lines)*2)

	if abs(y_avg - center[1]) < abs(x_avg - center[0]):
		if (x_avg > center[0]):
			h = 0
		else:
			h = 2
	else:
		if (y_avg > center[1]):
			h = 3
		else:
			h = 1

	return (center[0], center[1], h)

# MAIN
while True:
	time0 = time.time()
	with mss.mss() as sct:
		monitor_number = 2
		mon = sct.monitors[monitor_number]
		monitor = {
			'top': mon['top'] + 200,
			'left': mon['left'] + 1060,
			'width': 550,
			'height': 530,
			'mon': monitor_number,
		}
		
		image = np.array(sct.grab(monitor))
		image2 = image.copy()

		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		blurred = cv2.GaussianBlur(gray, (3, 3), 0)
		canny = cv2.Canny(blurred, 10, 200)

		lines = cv2.HoughLinesP(canny, 1, np.pi/180, 30, maxLineGap=0)
		 
		for line in lines:
			x1, y1, x2, y2 = line[0]
			cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)

		for line in process_lines(lines):
			x1, y1, x2, y2 = line
			cv2.line(image2, (x1, y1), (x2, y2), (255, 255, 0), 3)

		lines = process_lines(lines)

		goal = find_colored_object(image2.copy(), (29, 86, 6), (64, 255, 255))
		cv2.circle(image2, goal, 5, (255, 0, 0), -1)

		bot = find_bot(image2.copy())
		cv2.circle(image2, (bot[0], bot[1]), 5, (255, 0, 0), -1)

		# item	  |	description			  |	format
		# --------|-----------------------|-------------------
		# lines	  |	all walls			  |	x1, y1, x2, y2
		# goal	  |	location of the goal  |	x, y
		# bot	  | location of the bot   |	x, y, heading (0: right, 1: down, 2: left, 3: up)

		bot_headings = {0: "right", 1: "down", 2: "left", 3: "up"}

		print("Lines:", lines)
		print("Goal:", goal)
		print("Bot:" + "(" + str(bot[0]) + ", " + str(bot[1]) + ", facing: " + bot_headings[bot[2]] + ")")

		# get path usw.
		# TODO

		# repr
		# create image
		representation = np.zeros(image2.shape, dtype=np.uint8)
		representation.fill(255)

		# draw wall-areas
		for line in lines:
			x1, y1, x2, y2 = line
			cv2.line(representation, (x1, y1), (x2, y2), (244, 168, 234), 40)

		# draw walls
		for line in lines:
			x1, y1, x2, y2 = line
			cv2.line(representation, (x1, y1), (x2, y2), (61, 6, 54), 3)
			# cv2.circle(representation, (x1, y1), 5, (61, 6, 54), 7)
			# cv2.circle(representation, (x2, y2), 5, (61, 6, 54), 7)

		# floodfill useable area
		im_in = cv2.cvtColor(representation.copy(), cv2.COLOR_BGR2GRAY)
		th, im_th = cv2.threshold(im_in, 220, 255, cv2.THRESH_BINARY);
		im_floodfill = im_th.copy()
		h, w = im_th.shape[:2]
		mask = np.zeros((h+2, w+2), np.uint8)
		cv2.floodFill(im_floodfill, mask, (0, 0), 0);
		im_floodfill_inv = cv2.bitwise_not(im_floodfill)
		
		def create_blank(width, height, color=(0, 0, 0)):
			image = np.zeros((height, width, 4), dtype=np.uint8)
			image[:] = color
			return image

		idx = (im_floodfill!=0)
		src = create_blank(representation.shape[1], representation.shape[0], (243, 207, 249, 255))
		representation[idx] = src[idx]

		# draw goal
		cv2.circle(representation, goal, 5, (128, 0, 128), 13)

		# draw bot with facing
		bot = find_bot(image2.copy())
		x, y = (bot[0], bot[1])
		if bot[2] == 0:
			x += 9
		if bot[2] == 1:
			y -= 9
		if bot[2] == 2:
			x -= 9
		if bot[2] == 3:
			y += 9
		l2 = x, y
		x1, y1 = bot[0:2]
		x2, y2 = l2
		cv2.line(representation, (x1, y1), (x2, y2), (255, 0, 0), 2)
		cv2.circle(representation, (bot[0], bot[1]), 5, (255, 0, 0), -1)

		# cv2.imshow("Gray | Blurred | Edges", np.hstack([gray, blurred, cv2.bitwise_not(canny)]))
		# cv2.imshow("Lines (unfiltered | filtered)", np.hstack([image, image2]))
		font = cv2.FONT_HERSHEY_SIMPLEX
		fps = int(1 / (time.time() - time0))
		cv2.putText(representation,str(fps),(460,50), font, 1,(0,0,0),2,cv2.LINE_AA)
		cv2.imshow("Representation", representation)
		cv2.waitKey(1)
