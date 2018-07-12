import time
import cv2
import numpy as np
from matplotlib import pyplot as plt
from operator import itemgetter
import statistics

# TIME MEASUREMENT
time0 = time.time()

# PARAMETERS
img_path = 'in.jpg'
img = cv2.imread(img_path)

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

# draw the lines
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

######################
# PART 2
######################

# PARAMETERS
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
img = l

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

min_t = 200
for i in range(len(final_lines_x)):
	x1, y1, x2, y2  = final_lines_x[i]

	if abs(min(x_points, key=lambda x:abs(x-x1))-x1) < min_t:
		x1 = min(x_points, key=lambda x:abs(x-x1))
	if abs(min(x_points, key=lambda x:abs(x-x2))-x2) < min_t:
		x2 = min(x_points, key=lambda x:abs(x-x2))

	nf_x.append((x1, y1, x2, y2))

final_lines_x = nf_x

# create nav grid - segmentate
all_lines = final_lines_x.copy() + final_lines_y.copy() + outer_lines.copy()

x_s = []
y_s = []

for line in all_lines:
	x_s.append(line[0])
	x_s.append(line[2])
	y_s.append(line[1])
	y_s.append(line[3])

x_s = sorted(list(set(x_s)))
y_s = sorted(list(set(y_s)))

lX = -2000
mX = 200
groups_lX = []
for x in x_s:
	if abs(x-lX) > mX:
		# cut
		groups_lX.append([x])
	else:
		groups_lX[-1].append(x)

	lX = x

n_xs = []
for e in groups_lX:
	if len(e) == 1:
		# add value
		n_xs.append(e[0])
	elif len(e) == 2:
		# add avg
		n_xs.append(int((e[0]+e[1])/2))
	else:
		# add mean
		n_xs.append(e[int(len(e)/2)])

x_s = n_xs


lY = -2000
mY = 200
groups_lY = []
for y in y_s:
	if abs(y-lY) > mY:
		# cut
		groups_lY.append([y])
	else:
		groups_lY[-1].append(y)

	lY = y

n_ys = []
for e in groups_lY:
	if len(e) == 1:
		# add value
		n_ys.append(e[0])
	elif len(e) == 2:
		# add avg
		n_ys.append(int((e[0]+e[1])/2))
	else:
		# add mean
		n_ys.append(e[int(len(e)/2)])

y_s = n_ys

print(str(len(x_s)-1) + "*"+ str(len(y_s)-1), "Matrix")

mid_points = []
for i in range(len(x_s)-1):
	x = int((x_s[i]+x_s[i+1])/2)
	for j in range(len(y_s)-1):
		y = int((y_s[j]+y_s[j+1])/2)
		mid_points.append((x, y))

class Node:
	def __init__(self, x, y, n, o, s, w):
		self.x = x
		self.y = y
		self.n = n
		self.o = o
		self.s = s
		self.w = w


for pt in mid_points:
	pass # check all sides and create Nodes



# draw
l = np.zeros(img.shape, dtype=np.uint8)

for pt in mid_points:
	cv2.circle(l, pt, 4, (200, 200, 0), thickness=-1)

for y in y_s:
	cv2.circle(l, (200, y), 4, (200, 200, 0), thickness=-1)
	cv2.line(l, (200, y), (2000, y), (0, 255, 255), 2)

for x in x_s:
	cv2.circle(l, (x, 20), 4, (200, 200, 0), thickness=-1)
	cv2.line(l, (x, 20), (x, 2000), (0, 255, 255), 2)

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

cv2.imwrite('lines.jpg',l)
cv2.imwrite('edges.jpg',edges)



# print timing
print("Took {} seconds.".format(time.time() - time0))