import cv2
import numpy as np

import time


time0 = time.time()


img = cv2.imread('8.jpg')
img = cv2.imread('10.jpg')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 0, 255)
minLineLength = 0
maxLineGap = 7
lines = cv2.HoughLinesP(edges, 1, 3.141/300, 100, minLineLength, maxLineGap)

print(len(lines))

l = np.zeros(img.shape, dtype=np.uint8)
l[:] = (255)


for line in lines:
	for x1,y1,x2,y2 in line:
		cv2.line(l,(x1,y1),(x2,y2),(0,255,0),2)

 
for line in lines:
	for x1,y1,x2,y2 in line:
		if abs(x1-x2) < abs(y1-y2):
			cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
		else:
			cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)



cv2.imwrite('image.jpg',img)
cv2.imwrite('lines.jpg',l)
cv2.imwrite('edges.jpg',edges)

print("Took {} seconds.".format(time.time() - time0))