import cv2
import numpy as np
import time
from matplotlib import pyplot as plt
from operator import itemgetter
import statistics

time0 = time.time()


def split_dict_at_gaps(input, min_gap_size=5, key=0):
	input = sorted(input, key=itemgetter(key))
	groups = [] # arr = [[(30, 30, 30, 30), (...), (...)][(...), (...)]]
	for i in range(len(input)):
		if groups:
			x = input[i][key]
			if abs(groups[-1][-1][key] - x) < min_gap_size:
				groups[-1].append(input[i])
			else:
				groups.append([input[i]])
		else:
			groups.append([input[i]])
	return groups


img = cv2.imread('in.jpg')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 130, 290)

lines = cv2.HoughLinesP(edges, 1, 3.141/300, 80, 120, 3)

l = np.zeros(img.shape, dtype=np.uint8)


lines_x = []
lines_y = []
for line in lines:
	for x1,y1,x2,y2 in line:
		if abs(x1-x2) > abs(y1-y2):
			cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
			# cv2.line(l,(x1,y1),(x2,y2),(0,0,255),2)
			lines_x.append((x1, y1, x2, y2))
		else:
			cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
			# cv2.line(l,(x1,y1),(x2,y2),(0,255,0),2)
			lines_y.append((x1, y1, x2, y2))


# X
x_sorter = 1

grouped_x = split_dict_at_gaps(lines_x, 10, x_sorter)
n_grouped_x = []
for g in grouped_x:
	if len(g) > 10:
		n_grouped_x.append(g)
grouped_x = n_grouped_x

colors = [
			(255,0,0),
			(0,255,0),
			(0,0,255),
			(255,255,0),
			(0,255,255),
			(255,0,255),
			(192,192,192),
			(128,128,128),
			(128,0,0),
			(128,128,0),
			(0,128,0),
			(128,0,128),
			(0,128,128),
			(0,0,128)
		]

for i in range(len(grouped_x)):
	mipt = min(grouped_x[i], key=itemgetter(0))
	mapt = max(grouped_x[i], key=itemgetter(0))
	my = sorted(grouped_x[i], key=itemgetter(1))[int(len(grouped_x[i])/2)][1]

	l_start = mipt[0]
	l_len = abs(mipt[0]-mapt[0])
	l_hei = my

	cv2.line(l,(l_start,l_hei),(l_start+l_len,l_hei),colors[i],2)
	

# Y
y_sorter = 1

grouped_y = split_dict_at_gaps(lines_y, 50, key=2)
n_grouped_y = []
for g in grouped_y:
	if len(g) > 5:
		n_grouped_y.append(g)
grouped_y = n_grouped_y

colors = [
			(255,0,0),
			(0,255,0),
			(0,0,255),
			(255,255,0),
			(0,255,255),
			(255,0,255),
			(192,192,192),
			(128,128,128),
			(128,0,0),
			(128,128,0),
			(0,128,0),
			(128,0,128),
			(0,128,128),
			(0,0,128),
			(139,0,0),
			(220,20,60),
			(255,69,0),
			(0,100,0)
		]

for i in range(len(grouped_y)):
	for e in grouped_y[i]:
		x1, y1, x2, y2 = e
		cv2.line(l,(x1,y1),(x2,y2),colors[i + len(grouped_x)+2],2)
	



cv2.imwrite('image.jpg',img)
cv2.imwrite('lines.jpg',l)
cv2.imwrite('edges.jpg',edges)

print("Took {} seconds.".format(time.time() - time0))