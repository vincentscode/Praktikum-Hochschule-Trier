from collections import deque
import numpy as np
import cv2
import imutils
import time

greenLower = (0, 0, 0)
greenUpper = (255, 255, 255)

frame = cv2.imread("1.jpg")

blurred = cv2.GaussianBlur(frame, (11, 11), 0)
hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

mask = cv2.inRange(hsv, greenLower, greenUpper)
mask = cv2.erode(mask, None, iterations=2)
mask = cv2.dilate(mask, None, iterations=2)

cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if imutils.is_cv2() else cnts[1]
center = None

if len(cnts) > 0:
	c = max(cnts, key=cv2.contourArea)
	((x, y), radius) = cv2.minEnclosingCircle(c)
	M = cv2.moments(c)
	center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

	if radius > 1:
		cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
		cv2.circle(frame, center, 5, (0, 0, 255), -1)

cv2.imshow("Frame.png", frame)
cv2.imwrite("Mask.png", mask)
key = cv2.waitKey(0)