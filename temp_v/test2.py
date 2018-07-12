import cv2
import numpy as np
import time
from matplotlib import pyplot as plt
from operator import itemgetter
import statistics

# TIME MEASUREMENT
time0 = time.time()

# PARAMETERS
img_path = 'in.jpg'

edges_lower_thresh = 130
edges_upper_thresh = 290

lines_1 = 1
lines_2 = 3.141/300
lines_3 = 80
lines_4 = 120
lines_5 = 3

x_max_gap_x = 10
x_max_gap_y = 110

y_min_gap_y = 50

min_group_size = 7

# COLORS
colors = [(255,0,0),
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
		  (0,100,0)]


# split dict at gaps with a min size
def split_dict_at_gaps(input, min_gap_size, key):
	input = sorted(input, key=itemgetter(key))
	groups = []
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

# load/create images
img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, edges_lower_thresh, edges_upper_thresh)
lines = cv2.HoughLinesP(edges, lines_1, lines_2, lines_3, lines_4, lines_5)

# sort lines by direction
lines_x = []
lines_y = []
for line in lines:
	for x1,y1,x2,y2 in line:
		if abs(x1-x2) > abs(y1-y2):
			lines_x.append((x1, y1, x2, y2))
		else:
			lines_y.append((x1, y1, x2, y2))


# group x-lines
final_lines_x = []

# split on y-axis
grouped_x = split_dict_at_gaps(lines_x, x_max_gap_x, 1)

# remove too small groups
n_grouped_x = []
for g in grouped_x:
	if len(g) > min_group_size:
		n_grouped_x.append(g)
grouped_x = n_grouped_x

# split on x-axis
n_grouped_x = []
for group in grouped_x:
	t_group = sorted(group, key=itemgetter(0))
	n_group = []
	last0 = -x_max_gap_y*10
	for e in t_group:
		x1,y1,x2,y2 = e
		if abs(last0-x1) > x_max_gap_y:
			n_group.append([e])
		else:
			n_group[-1].append(e)
		last0 = x2
	n_grouped_x.append(n_group)
grouped_x = n_grouped_x

# remove too small groups
n_grouped_x = []
for g in grouped_x:
	for e in g:
		if len(e) > min_group_size:
			n_grouped_x.append(e)
grouped_x = n_grouped_x

# create group-lines
for i in range(len(grouped_x)):
	mipt = min(grouped_x[i], key=itemgetter(0))
	mapt = max(grouped_x[i], key=itemgetter(0))
	my = sorted(grouped_x[i], key=itemgetter(1))[int(len(grouped_x[i])/2)][1]

	l_start = mipt[0]
	l_len = abs(mipt[0]-mapt[0])

	final_lines_x.append((l_start, my, l_start+l_len, my))
	

# group y-lines
final_lines_y = []

# split on x-axis
grouped_y = split_dict_at_gaps(lines_y, y_min_gap_y, key=2)

# remove too small groups
n_grouped_y = []
for g in grouped_y:
	if len(g) > min_group_size:
		n_grouped_y.append(g)
grouped_y = n_grouped_y

# create group-lines
for i in range(len(grouped_y)):
	min_x = min(grouped_y[i], key=itemgetter(0))
	max_x = max(grouped_y[i], key=itemgetter(0))
	min_y = min(grouped_y[i], key=itemgetter(1))[1]
	max_y = max(grouped_y[i], key=itemgetter(3))[3]

	if min_x[1] > max_x[1]:
		o_min_x = min_x[0]
		min_x = max_x[0]
		max_x = o_min_x
	else:
		min_x = min_x[0]
		max_x = max_x[0]

	final_lines_y.append((min_x,min_y, max_x, max_y))

# get outer lines
line_y_min = min(final_lines_y, key=itemgetter(0))
line_y_max = max(final_lines_y, key=itemgetter(2))
line_x_min = min(final_lines_x, key=itemgetter(1))
line_x_max = max(final_lines_x, key=itemgetter(3))

# find the bot

# draw the lines
print("X-Lines:", final_lines_x)
print("Y-Lines:", final_lines_y)

l = np.zeros(img.shape, dtype=np.uint8)

for i in range(len(final_lines_x)):
	x1, y1, x2, y2 = final_lines_x[i]
	cv2.line(l, (x1,y1), (x2,y2), colors[i], 2)

for i in range(len(final_lines_y)):
	x1, y1, x2, y2 = final_lines_y[i]
	cv2.line(l, (x1,y1), (x2,y2), colors[i+len(final_lines_x)], 2)

cv2.line(l, line_y_min[:2], line_y_min[2:], (255, 255, 255), 2)
cv2.line(l, line_y_max[:2], line_y_max[2:], (255, 255, 255), 2)
cv2.line(l, line_x_min[:2], line_x_min[2:], (255, 255, 255), 2)
cv2.line(l, line_x_max[:2], line_x_max[2:], (255, 255, 255), 2)

# save the images
cv2.imwrite('image.jpg',img)
cv2.imwrite('lines.jpg',l)
cv2.imwrite('edges.jpg',edges)

# print timing
print("Took {} seconds.".format(time.time() - time0))