import cv2
import numpy as np
import time
from matplotlib import pyplot as plt
from operator import itemgetter

time0 = time.time()


img = cv2.imread('in.jpg')
unperspective_lines = img.copy()
rows,cols,ch = unperspective_lines.shape
#					TOP-L	  TOP-R		 DOWN-R		  DOWN-L
pts1 = np.float32([[540, 0], [1500, 0], [0, 1080],   [1920, 1080]])
pts2 = np.float32([[340, 0], [1920, 0], [540, 1263], [1550, 1300]])
M = cv2.getPerspectiveTransform(pts1,pts2)
img = cv2.warpPerspective(unperspective_lines,M,(1920,1080))


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 90, 210)

lines = cv2.HoughLinesP(edges, 1, 3.141/500, 90, 120, 2)

l = np.zeros(img.shape, dtype=np.uint8)


lines_x = []
lines_y = []
for line in lines:
	for x1,y1,x2,y2 in line:
		if abs(x1-x2) > abs(y1-y2):
			cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
			cv2.line(l,(x1,y1),(x2,y2),(0,0,255),2)
			lines_x.append((x1, y1, x2, y2))
		else:
			cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
			cv2.line(l,(x1,y1),(x2,y2),(0,255,0),2)
			lines_y.append((x1, y1, x2, y2))
  

y_sorter = 0
x_sorter = 1
lines_y = sorted(lines_y, key=itemgetter(y_sorter))
lines_x = sorted(lines_x, key=itemgetter(x_sorter))
print(lines_x)



cv2.imwrite('image.jpg',img)
cv2.imwrite('lines.jpg',l)
cv2.imwrite('edges.jpg',edges)

print("Took {} seconds.".format(time.time() - time0))