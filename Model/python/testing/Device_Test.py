import constants
from Device import Device

def add_neighbor():
	# create device and neighbor
	dev = Device(0, 0, 0, 1, 0)
	neighbor = Device(1, 1, 1, 1, 0)

	# add neighbor
	dev.add_neighbor(neighbor.id)

	assert(len(dev.neighbors) == 1 and dev.neighbors[0] == 1)

def remove_neighbor():
	# create device and neighbor
	dev = Device(0, 0, 0, 1, 0)
	neighbor = Device(1, 1, 1, 1, 0)

	# add neighbor
	dev.add_neighbor(neighbor.id)

	# remove neighbor
	dev.remove_neighbor(1)

	assert(len(dev.neighbors) == 0)

def clear_neighbors():
	# create device
	dev = Device(0, 0, 0, 1, 0)
	# add many neighbors
	for i in range(10):
		dev.add_neighbor(i)
	
	dev.clear_neighbors()

	assert(len(dev.neighbors) == 0)

def in_range():
	# create devices
	dev0 = Device(0, 0, 0, 1, 0) # (0,0)
	dev1 = Device(5, 5, 1, 1, 0) # (5, 5) - in range
	dev2 = Device(25, 25, 2, 1, 0) # (25, 25) - out of range

	# add mappings
	constants.device_mappings[1] = dev1
	constants.device_mappings[2] = dev2

	assert(dev0.in_range(1))
	assert(not dev0.in_range(2))

def calc_deliver_prob():
	# create device
	dev = Device(0, 0, 0, 1, 0)
	# add many neighbors
	for i in range(10):
		dev.add_neighbor(i)

	dev.calc_deliver_prob()

	assert(dev.deliver_prob == 1 - Device.NEIGHBOR_PENALTY * len(dev.neighbors))

def choose_random_neighbor():
	# create device
	dev = Device(0, 0, 0, 1, 0)
	# add many neighbors
	for i in range(10):
		dev.add_neighbor(i)
	
	# get random neighbor
	rand_neighbor_id = dev.choose_random_neighbor()

	assert(rand_neighbor_id in list(range(10)))

def update_round():
	# create device
	dev = Device(0, 0, 0, 3, 0) # 3 rounds

	dev.update_round(0, 100, 50)
	dev.update_round(1, 100, 100)
	dev.update_round(1, 100, 100)
	dev.update_round(2, 100, 100)

	# should be [(100, 50), (200, 200), (100, 100)] but objects, not tuples
	assert(dev.round_states[0]['incoming'] == 100 and dev.round_states[0]['outgoing'] == 50)
	assert(dev.round_states[1]['incoming'] == 200 and dev.round_states[1]['outgoing'] == 200)
	assert(dev.round_states[2]['incoming'] == 100 and dev.round_states[2]['outgoing'] == 100)

def should_send_msg():
	join_time = 300
	# create device
	dev = Device(0, 0, 0, 1, join_time)

	assert(not dev.should_send_msg(0))
	assert(dev.should_send_msg(300))
	assert(dev.should_send_msg(300 + 60 * 1000))
	assert(dev.should_send_msg(300 + 30 * 1000))
	assert(not dev.should_send_msg(300 + 30 * 1000 + 1000))

def should_send_bitlist():
	join_time = 300
	# create device
	dev = Device(0, 0, 0, 1, join_time)

	assert(dev.should_send_bitlist(join_time + constants.BITLIST_INTERVAL * 9))
	assert(not dev.should_send_bitlist(join_time + constants.BITLIST_INTERVAL * 9 + 100))

def update_missing():
	# create devices
	dev0 = Device(0, 0, 0, 1, 0)
	dev1 = Device(0, 0, 1, 1, 0)

	# store messages
	dev0.store_messages([1, 2, 3], 0)
	dev1.store_messages([3, 4, 5], 0)

	# update missing for dev0
	dev0.update_missing(1, dev1.messages.bitlist)

	# dev0 should have 1 -> [4, 5]
	assert(dev0.missing[1] == [4, 5])

def clear_missing():
	# create devices
	dev0 = Device(0, 0, 0, 1, 0)
	dev1 = Device(0, 0, 1, 1, 0)

	# store messages
	dev1.store_messages([1, 2, 3], 0)

	# update missing for dev0
	dev0.update_missing(1, dev1.messages.bitlist)
	dev0.clear_missing()
	assert(len(dev0.missing) == 0)

def update_requests():
	# create device
	dev = Device(0, 0, 0, 1, 0)
	dev.update_requests(5, [1, 2, 3])
	
	assert(dev.requests[5] == [1, 2, 3])

def clear_requests():
	# create device
	dev = Device(0, 0, 0, 1, 0)
	dev.update_requests(5, [1, 2, 3])
	dev.clear_requests()

	assert(len(dev.requests) == 0)


def add_message():
	dev = Device(0, 0, 0, 1, 0)

	assert(len(dev.messages.bitlist) == 0)
	assert(len(dev.messages.times.queue) == 0)

	dev.add_message("1", 0)

	assert(len(dev.messages.bitlist) == 1)
	assert(len(dev.messages.times.queue) == 1)
	

def store_messages():
	dev = Device(0, 0, 0, 1, 0)
	dev.store_messages([1, 2], 0)

	assert(1 in dev.messages.bitlist and 2 in dev.messages.bitlist)
	assert((0, 1) in dev.messages.times.queue and (0, 1) in dev.messages.times.queue)

def move():
	dev = Device(0, 0, 0, 1, 0)
	dev.move()

	assert(dev.x >= -4 and dev.x <= 4)
	assert(dev.y >= -4 and dev.y <= 4)

def get_pos():
	for i in range(15):
		for j in range(15):
			assert(Device(i * 30, j * 30, 0, 1, 0).get_pos() == (i, j))
