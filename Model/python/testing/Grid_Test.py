from Grid import Grid
from Device import Device

def populate():
	devices = []
	for i in range(15):
		for j in range(15):
			devices += [Device(i * 30, j * 30, i * 100 + j, 1, 0)]
	
	grid = Grid(30, 15 * 30)
	grid.populate(devices)

	for dev in devices:
		assert(dev.id in grid.grid[dev.get_pos()])

def get_neighbors():
	devices = []
	for i in range(15):
		for j in range(15):
			devices += [Device(i * 30, j * 30, i * 100 + j, 1, 0)]

	grid = Grid(30, 15 * 30)
	grid.populate(devices)

	# devices[22] has coords (30, 210) which places it at (1, 7)
	# (1, 7)'s neighboring squares are:
	# (0, 6), (0, 7), (0, 8), (1, 6), (1, 8), (2, 6), (2, 7), (2, 8)
	# => neighbors: [6, 7, 8, 106, 108, 206, 207, 208]
	# for dev in devices:
	# 	if (dev.x == 0 and dev.y == 180) or (dev.x == 0 and dev.y == 210) or (dev.x == 0 and dev.y == 240) \
	# 		or (dev.x == 30 and dev.y == 180) or (dev.x == 30 and dev.y == 240) \
	# 		or (dev.x == 60 and dev.y == 180) or (dev.x == 60 and dev.y == 210) or (dev.x == 60 and dev.y == 240):
	# 		print(dev.id)

	assert(grid.get_neighbors(devices[22]) == [6, 7, 8, 106, 108, 206, 207, 208])
