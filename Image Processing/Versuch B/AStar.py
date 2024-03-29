import matplotlib.pyplot as plt
import math
from operator import itemgetter

show_animation = False


class Node:

    def __init__(self, x, y, cost, pind):
        self.x = x
        self.y = y
        self.cost = cost
        self.pind = pind

    def __str__(self):
        return str(self.x) + "," + str(self.y) + "," + str(self.cost) + "," + str(self.pind)


def calc_fianl_path(ngoal, closedset, reso):
    # generate final course
    rx, ry = [ngoal.x * reso], [ngoal.y * reso]
    pind = ngoal.pind
    while pind != -1:
        n = closedset[pind]
        rx.append(n.x * reso)
        ry.append(n.y * reso)
        pind = n.pind

    return rx, ry


def a_star_planning(sx, sy, gx, gy, ox, oy, reso, rr):
    """
    gx: goal x position [m]
    gx: goal x position [m]
    ox: x position list of Obstacles [m]
    oy: y position list of Obstacles [m]
    reso: grid resolution [m]
    rr: robot radius[m]
    """

    nstart = Node(round(sx / reso), round(sy / reso), 0.0, -1)
    ngoal = Node(round(gx / reso), round(gy / reso), 0.0, -1)
    ox = [iox / reso for iox in ox]
    oy = [ioy / reso for ioy in oy]

    obmap, minx, miny, maxx, maxy, xw, yw = calc_obstacle_map(ox, oy, reso, rr)

    motion = get_motion_model()

    openset, closedset = dict(), dict()
    openset[calc_index(nstart, xw, minx, miny)] = nstart
    while 1:
        c_id = min(
            openset, key=lambda o: openset[o].cost + calc_heuristic(ngoal, openset[o]))
        current = openset[c_id]

        # show graph
        if show_animation:
            plt.plot(current.x * reso, current.y * reso, "xc")
            if len(closedset.keys()) % 10 == 0:
                plt.pause(0.001)

        if current.x == ngoal.x and current.y == ngoal.y:
            print("Goal found.")
            ngoal.pind = current.pind
            ngoal.cost = current.cost
            break

        # Remove the item from the open set
        del openset[c_id]
        # Add it to the closed set
        closedset[c_id] = current

        # expand search grid based on motion model
        for i in range(len(motion)):
            node = Node(current.x + motion[i][0],
                        current.y + motion[i][1],
                        current.cost + motion[i][2], c_id)
            n_id = calc_index(node, xw, minx, miny)

            if n_id in closedset:
                continue

            if not verify_node(node, obmap, minx, miny, maxx, maxy):
                continue

            if n_id not in openset:
                openset[n_id] = node  # Discover a new node

            tcost = current.cost + calc_heuristic(current, node)

            if tcost >= node.cost:
                continue  # this is not a better path

            node.cost = tcost
            openset[n_id] = node  # This path is the best unitl now. record it!

    rx, ry = calc_fianl_path(ngoal, closedset, reso)

    return rx, ry


def calc_heuristic(n1, n2):
    w = 1.0  # weight of heuristic
    d = w * math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2)
    return d


def verify_node(node, obmap, minx, miny, maxx, maxy):

    if node.x < minx:
        return False
    elif node.y < miny:
        return False
    elif node.x >= maxx:
        return False
    elif node.y >= maxy:
        return False

    if obmap[node.x][node.y]:
        return False

    return True


def calc_obstacle_map(ox, oy, reso, vr):

    minx = round(min(ox))
    miny = round(min(oy))
    maxx = round(max(ox))
    maxy = round(max(oy))
    # print("minx:", minx)
    # print("miny:", miny)
    # print("maxx:", maxx)
    # print("maxy:", maxy)

    xwidth = round(maxx - minx)
    ywidth = round(maxy - miny)
    # print("xwidth:", xwidth)
    # print("ywidth:", ywidth)

    # obstacle map generation
    obmap = [[False for i in range(ywidth+1)] for i in range(xwidth+1)]
    for ix in range(xwidth):
        # print(ix)
        # print(xwidth)
        x = ix + minx
        for iy in range(ywidth):
            y = iy + miny
            #  print(x, y)
            for iox, ioy in zip(ox, oy):
                d = math.sqrt((iox - x)**2 + (ioy - y)**2)
                if d <= vr / reso:
                    # print(ix, iy)
                    obmap[ix][iy] = True
                    break

    return obmap, minx, miny, maxx, maxy, xwidth, ywidth


def calc_index(node, xwidth, xmin, ymin):
    return (node.y - ymin) * xwidth + (node.x - xmin)


def get_motion_model():
    # dx, dy, cost
    motion = [[1, 0, 1],
              [0, 1, 1],
              [-1, 0, 1],
              [0, -1, 1],
              [-1, -1, math.sqrt(2)],
              [-1, 1, math.sqrt(2)],
              [1, -1, math.sqrt(2)],
              [1, 1, math.sqrt(2)]]

    return motion


def run(sx, sy, gx, gy, grid_size, robot_size, lines, anim):
    global show_animation
    show_animation = anim

    ox, oy = [], []
    # divide
    n_lines = []
    for l in lines:
        x1, y1, x2, y2 = l
        f = 10
        x1 = int(x1 / f)
        y1 = int(y1 / f)
        x2 = int(x2 / f)
        y2 = int(y2 / f)
        n_lines.append((x1, y1, x2, y2))
    lines = n_lines

    # normalize
    x_min = min(lines, key=itemgetter(0))[0]
    y_min = min(lines, key=itemgetter(1))[1]
    n_lines = []
    for l in lines:
        x1, y1, x2, y2 = l
        x1 -= x_min
        y1 -= y_min
        x2 -= x_min
        y2 -= y_min
        n_lines.append((x1, y1, x2, y2))
    lines = n_lines
    
    # add lines
    for l in lines:
        x1, y1, x2, y2 = l
        if x1 == x2:
            for i in range(y1, y2):
                oy.append(i)
                ox.append(x1)
        else:
            for i in range(x1, x2):
                ox.append(i)
                oy.append(y1)

    if show_animation:
        plt.plot(ox, oy, ".k")
        plt.plot(sx, sy, "xr")
        plt.plot(gx, gy, "xb")
        plt.grid(True)
        plt.axis("equal")
    
    rx, ry = a_star_planning(sx, sy, gx, gy, ox, oy, grid_size, robot_size)

    if show_animation:
        plt.plot(rx, ry, "-r")
        plt.show()
    return rx, ry


def main():
    print(__file__ + " start!!")

    # start and goal position
    sx = 50.0  # [m]
    sy = 85.0  # [m]
    gx = 50.0  # [m]
    gy = 40.0  # [m]
    grid_size = 1.0  # [m]
    robot_size = 10.0  # [m]

    ox, oy = [], []

    lines = [
        (343, 427, 684, 427),  (1140, 402, 1429, 402),
        (737, 725, 1004, 725), (1494, 699, 1891, 699),
        (343, 427, 726, 427),  (1125, 402, 1429, 402),
        (726, 725, 1125, 725), (1494, 699, 1891, 699),
        (726, 427, 726, 699),  (1125, 402, 1125, 699),
        (343, 68, 1891, 68),   (343, 1017, 1891, 1017),
        (343, 68, 343, 1017),  (1891, 68, 1891, 1017)
    ]

    # divide
    n_lines = []
    for l in lines:
        x1, y1, x2, y2 = l
        f = 10
        x1 = int(x1 / f)
        y1 = int(y1 / f)
        x2 = int(x2 / f)
        y2 = int(y2 / f)
        n_lines.append((x1, y1, x2, y2))
    lines = n_lines

    # normalize
    x_min = min(lines, key=itemgetter(0))[0]
    y_min = min(lines, key=itemgetter(1))[1]
    n_lines = []
    for l in lines:
        x1, y1, x2, y2 = l
        x1 -= x_min
        y1 -= y_min
        x2 -= x_min
        y2 -= y_min
        n_lines.append((x1, y1, x2, y2))
    lines = n_lines
    

    print(lines)
    for l in lines:
        x1, y1, x2, y2 = l
        if x1 == x2:
            for i in range(y1, y2):
                oy.append(i)
                ox.append(x1)
        else:
            for i in range(x1, x2):
                ox.append(i)
                oy.append(y1)


    """
    # bottom
    for i in range(outer_box_h):
        ox.append(i)
        oy.append(0)

    # right
    for i in range(outer_box_h):
        ox.append(outer_box_h)
        oy.append(i)

    # top
    for i in range(outer_box_h):
        ox.append(i)
        oy.append(outer_box_h)

    # left
    for i in range(outer_box_h):
        ox.append(0)
        oy.append(i)
    """
    if show_animation:
        plt.plot(ox, oy, ".k")
        plt.plot(sx, sy, "xr")
        plt.plot(gx, gy, "xb")
        plt.grid(True)
        plt.axis("equal")
    
    rx, ry = a_star_planning(sx, sy, gx, gy, ox, oy, grid_size, robot_size)
    print("X:", rx)
    print("Y:", ry)

    if show_animation:
        plt.plot(rx, ry, "-r")
        plt.show()


if __name__ == '__main__':
    main()