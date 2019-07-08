surface = 	[
			["a", "a", "b", "a", "a", "b"],
			["a", "b", "b", "a", "b", "b"],
			["b", "a", "b", "a", "a", "b"],
			["b", "a", "b", "a", "b", "b"],
			["a", "a", "b", "a", "a", "a"],
			["a", "b", "b", "a", "a", "b"]
			]

def floodfill(x, y, oldColor, newColor):
	if surface[x][y] != oldColor:
		return

	surface[x][y] = newColor
	if (x+1 < len(surface)):
		floodfill(x + 1, y, oldColor, newColor)
	if (x-1 >= 0):
		floodfill(x - 1, y, oldColor, newColor)
	if (y+1 < len(surface[0])):
		floodfill(x, y + 1, oldColor, newColor)
	if (y-1 >= 0):
		floodfill(x, y - 1, oldColor, newColor)

if __name__ == '__main__':
	for f in surface:
		print(f)

	floodfill(0, 3, 'a', 'b')
	print("")

	for f in surface:
		print(f)