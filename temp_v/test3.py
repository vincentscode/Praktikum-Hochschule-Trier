import cv2
import numpy as np
import time
from matplotlib import pyplot as plt
from operator import itemgetter
import statistics

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

# PARAMETERS
img_path = 'lines.jpg'

edges_lower_thresh = 50
edges_upper_thresh = 0

lines_1 = 1
lines_2 = 3.141/300
lines_3 = 80
lines_4 = 120
lines_5 = 3

x_max_gap_x = 50
x_max_gap_y = 300

y_min_gap_y = 50

min_group_size = 7

# load images
img = cv2.imread(img_path)

# transform
unperspective_lines = img.copy()
rows,cols,ch = unperspective_lines.shape
#					TOP-L	  TOP-R		 DOWN-R		  DOWN-L
pts1 = np.float32([[540, 0], [1500, 0], [0, 1080],   [1920, 1080]])
pts2 = np.float32([[340, 0], [1920, 0], [540, 1263], [1550, 1300]])
M = cv2.getPerspectiveTransform(pts1,pts2)
img = cv2.warpPerspective(unperspective_lines,M,(1920,1080))

# create images
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, edges_lower_thresh, edges_upper_thresh)
lines = cv2.HoughLinesP(edges, lines_1, lines_2, lines_3, lines_4, lines_5)

# unpack lines
n_lines = []
for i in lines:
	for e in i:
		x1, y1, x2, y2 = e
		n_lines.append((x1, y1, x2, y2))
lines = n_lines

# sort lines by direction
lines_x = []
lines_y = []
for line in lines:
	x1,y1,x2,y2 = line
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

# make lines straight
n_final_lines_y = []
for i in final_lines_y:
	x1, y1, x2, y2 = i
	x2 = x1
	n_final_lines_y.append((x1, y1, x2, y2))
final_lines_y = n_final_lines_y
	

# get outer lines
t_line_y_min = min(final_lines_y, key=itemgetter(0))
t_line_y_max = max(final_lines_y, key=itemgetter(2))
final_lines_y.remove(t_line_y_min)
final_lines_y.remove(t_line_y_max)

t_line_x_min = min(final_lines_x, key=itemgetter(1))
t_line_x_max = max(final_lines_x, key=itemgetter(3))
final_lines_x.remove(t_line_x_min)
final_lines_x.remove(t_line_x_max)

line_y_min = (t_line_y_min[0], t_line_x_min[1], t_line_y_min[2], t_line_x_max[3])
line_y_max = (t_line_y_max[0], t_line_x_min[1], t_line_y_max[2], t_line_x_max[3])
line_x_min = (t_line_y_min[0], t_line_x_min[1], t_line_y_max[2], t_line_x_min[3])
line_x_max = (t_line_y_min[0], t_line_x_max[1], t_line_y_max[2], t_line_x_max[3])

outer_lines = [
	line_x_min,
	line_x_max,
	line_y_min,
	line_y_max
]

# correct inner lines
# lines close to the border (x only)
nf_x = []

min_marg = 300
for line in final_lines_x:
	x1, y1, x2, y2 = line
	if abs(x1-line_y_min[0]) < min_marg:
		x1 = line_y_min[0]
	if abs(x2-line_y_max[0]) < min_marg:
		x2 = line_y_max[0]
	nf_x.append((x1, y1, x2, y2))
final_lines_x = nf_x


# match y-lines to y-points of x-lines (y only)
y_points = []

for line in final_lines_x:
	y_points.append(line[1])

nf_y = []

for line in final_lines_y:
	x1, y1, x2, y2 = line

	y1 = min(y_points, key=lambda x:abs(x-y1))
	y2 = min(y_points, key=lambda x:abs(x-y2))

	nf_y.append((x1, y1, x2, y2))

final_lines_y = nf_y

# same for x (test)
x_points = []
x_points.append(line_y_min[0])
x_points.append(line_y_max[0])

for line in final_lines_y:
	x_points.append(line[0])

for i in range(len(final_lines_x)):
	x1, y1, x2, y2  = final_lines_x[i]

	x1 = min(x_points, key=lambda x:abs(x-x1))
	x2 = min(x_points, key=lambda x:abs(x-x2))

	nf_x.append((x1, y1, x2, y2))

final_lines_x = nf_x


# more correction
 ##########
############
### TODO ###
############
 ##########

# create nav grid - segmentate
y_parts = 0
x_parts = 0

x_s = []
y_s = []


# draw
l = np.zeros(img.shape, dtype=np.uint8)

for i in final_lines_y:
	x1, y1, x2, y2 = i
	cv2.line(l, (x1,y1), (x2,y2), (200, 0, 200), 2)

for i in final_lines_x:
	x1, y1, x2, y2 = i
	cv2.line(l, (x1,y1), (x2,y2), (200, 0, 200), 2)

cv2.line(l, line_y_min[:2], line_y_min[2:], (255, 255, 255), 2)
cv2.line(l, line_y_max[:2], line_y_max[2:], (255, 255, 255), 2)
cv2.line(l, line_x_min[:2], line_x_min[2:], (255, 255, 255), 2)
cv2.line(l, line_x_max[:2], line_x_max[2:], (255, 255, 255), 2)


cv2.imwrite('image2.jpg',img)
cv2.imwrite('lines2.jpg',l)
cv2.imwrite('edges2.jpg',edges)