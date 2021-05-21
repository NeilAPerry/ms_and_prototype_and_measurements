# Need devices to have positive coordinates
class Grid:
	def __init__(self, r, side):
		self.r = r
		# number of buckets per dim
		n_steps = side // r if side % r == 0 else (side // r) + 1
		self.grid = {(i, j): set() for i in range(n_steps) for j in range(n_steps)}

	def populate(self, devices):
		for device in devices:
			self.grid[device.get_pos()].add(device.id)

	def get_neighbors(self, device):
		neighbors = []
		x, y = device.get_pos()
		x_vals = [x - 1, x, x + 1]  # neighboring buckets index
		y_vals = [y - 1, y, y + 1]  # neighboring buckets index

		# search over all 9 buckets
		for i in x_vals:
			for j in y_vals:
				if (i, j) in self.grid:
					# extend by list of ids
					neighbors.extend(self.grid[i, j])

		# remove self from list
		neighbors.remove(device.id)

		return neighbors
