import constants
import helpers
from Device import Device
from Simulator import Simulator


def setup():
    rounds = 10
    num_devices = 4
    possible_start_times = list(range(0, 60 * 1000, constants.TIME_STEP))

    # clear device_mappings
    constants.device_mappings = {}

    # create placeholder simulator with 3 rounds
    sim = Simulator(rounds * constants.TIME_STEP, num_devices,
                    0, 0, move=False, uniform=True)

    # check for correct number of devices
    assert(len(sim.devices) == num_devices)

    # check that all devices added to mapping
    assert(len(constants.device_mappings) == num_devices)

    # check that join times are valid
    for dev in sim.devices:
        assert(dev.join_time in possible_start_times)


def process_send():
    sim = Simulator(1, 1, 0, 0, move=False, uniform=True)

    # create device
    dev = Device(0, 0, 0, 1, 0)  # will send this time interval

    # create neighbors
    neighbors = [Device(0, 0, i + 1, 1, 0) for i in range(3)]

    # link dev to neighbors
    for i in range(3):
        dev.add_neighbor(i + 1)

    # add to mapping
    constants.device_mappings[0] = dev
    for i in range(3):
        constants.device_mappings[i + 1] = neighbors[i]

    # run the function being tested
    sim.process_send(dev)  # self.round is the only thing from sim used

    # check state of dev
    assert(len(dev.messages.bitlist) == 1)
    assert(len(dev.messages.times.queue) == 1)
    assert(dev.round_states[0]['incoming'] ==
           0 and dev.round_states[0]['outgoing'] == constants.TOTAL_MESSAGE_SIZE)

    # check state of neighbors
    for neighbor in neighbors:
        assert(len(neighbor.messages.bitlist) == 1)
        assert(len(neighbor.messages.times.queue) == 1)
        assert(neighbor.round_states[0]['incoming'] ==
               constants.TOTAL_MESSAGE_SIZE and neighbor.round_states[0]['outgoing'] == 0)


def process_bitlist():
    sim = Simulator(1, 1, 0, 0, move=False, uniform=True)

    # create device
    dev = Device(0, 0, 0, 1, 0)  # will send this time interval

    # create neighbors
    neighbors = [Device(0, 0, i + 1, 1, 0) for i in range(3)]

    # link dev to neighbors
    for i in range(3):
        dev.add_neighbor(i + 1)

    # add to mapping
    constants.device_mappings[0] = dev
    for i in range(3):
        constants.device_mappings[i + 1] = neighbors[i]

    # add message to dev so that the bitlist is not empty
    dev.add_message(helpers.get_random_string(300), 0)

    # run the function being tested
    sim.process_bitlist(dev)  # self.round is the only thing from sim used

    # check state of dev
    assert(dev.round_states[0]['incoming'] ==
           0 and dev.round_states[0]['outgoing'] == constants.TOTAL_BITLIST_MESSAGE_SIZE)

    # check state of neighbors
    for neighbor in neighbors:
        # check round state
        assert(neighbor.round_states[0]['incoming'] == constants.TOTAL_BITLIST_MESSAGE_SIZE
               and neighbor.round_states[0]['outgoing'] == 0)
        # check missing
        assert(len(neighbor.missing[0]) != 0)


def process_request():
    sim = Simulator(1, 1, 0, 0, move=False, uniform=True)

    # create device
    dev = Device(0, 0, 0, 1, 0)  # will send this time interval

    # create neighbors
    neighbors = [Device(0, 0, i + 1, 1, 0) for i in range(3)]

    # link dev to neighbors
    for i in range(3):
        dev.add_neighbor(i + 1)

    # add to mapping
    constants.device_mappings[0] = dev
    for i in range(3):
        constants.device_mappings[i + 1] = neighbors[i]

    # give neighbors preset messages
    neighbors[0].store_messages([1, 2], 0)
    neighbors[1].store_messages([3], 0)
    neighbors[2].store_messages([4], 0)

    # give dev missing list
    dev.missing = {1: [1, 2], 2: [3], 3: [4]}

    # run the function being tested
    sim.process_request(dev)  # self.round is the only thing from sim used

    # check neighbors' requests
    assert(neighbors[0].requests[0] == [1, 2])
    assert(neighbors[1].requests[0] == [3])
    assert(neighbors[2].requests[0] == [4])

    req_size = helpers.calc_request_size([1, 2]) + helpers.calc_request_size([3]) + helpers.calc_request_size([4])

    # check device round states
    assert(dev.round_states[0]['incoming'] == 0 and dev.round_states[0]['outgoing'] == req_size)

    # check neighbors' round states
    for neighbor in neighbors:
        assert(neighbor.round_states[0]['incoming'] == req_size and neighbor.round_states[0]['outgoing'] == 0)

    # check that dev cleared missing
    assert(len(dev.missing) == 0)


def process_response():
    sim = Simulator(1, 1, 0, 0, move=False, uniform=True)

    # create device
    dev = Device(0, 0, 0, 1, 0)  # will send this time interval

    # create neighbors
    neighbors = [Device(0, 0, i + 1, 1, 0) for i in range(3)]

    # link dev to neighbors
    for i in range(3):
        dev.add_neighbor(i + 1)

    # add to mapping
    constants.device_mappings[0] = dev
    for i in range(3):
        constants.device_mappings[i + 1] = neighbors[i]

    # add requests to dev
    dev.requests = {1: [1, 2], 2: [2, 3], 3: [4]}

    # run the function being tested
    sim.process_response(dev)  # self.round is the only thing from sim used

    # check dev round states
    assert(dev.round_states[0]['incoming'] == 0 and dev.round_states[0]
           ['outgoing'] == 4 * constants.TOTAL_MESSAGE_SIZE)

    # check neighbors' round states
    for neighbor in neighbors:
        assert(neighbor.round_states[0]['incoming'] == 4 * constants.TOTAL_MESSAGE_SIZE
               and neighbor.round_states[0]['outgoing'] == 0)

    # check neighbors' Messages DS
    for neighbor in neighbors:
        assert(len(neighbor.messages.bitlist) == 4)
        assert(len(neighbor.messages.times.queue) == 4)

    # check that dev cleared requests
    assert(len(dev.requests) == 0)


def _connect_devices_helper(topo):
    if (topo == 'line'):
        # create placeholder simulator
        sim = Simulator(1, 4, 0, 0, move=False, uniform=True)

        # line
        line = [Device(i * (constants.DEVICE_RANGE - 1), 0, i, 1, 0)
                for i in range(4)]

        # reset device_mappings
        constants.device_mappings = {}
        for dev in line:
            constants.device_mappings[dev.id] = dev

        # insert line into sim
        sim.devices = line
        sim.connect_devices()

        # check connection
        assert(line[0].neighbors == [1])
        assert(line[1].neighbors == [0, 2])
        assert(line[2].neighbors == [1, 3])
        assert(line[3].neighbors == [2])

        return

    if (topo == 'square'):
        # create placeholder simulator
        sim = Simulator(1, 4, 0, 0, move=False, uniform=True)

        # square
        square = [Device(0, 0, 0, 1, 0),
                  Device((constants.DEVICE_RANGE - 1), 0, 1, 1, 0),
                  Device(0, (constants.DEVICE_RANGE - 1), 2, 1, 0),
                  Device((constants.DEVICE_RANGE - 1), (constants.DEVICE_RANGE - 1), 3, 1, 0)]

        # reset device_mappings
        constants.device_mappings = {}
        for dev in square:
            constants.device_mappings[dev.id] = dev

        # insert square into sim
        sim.devices = square
        sim.connect_devices()

        # check connection
        assert(square[0].neighbors == [1, 2])
        assert(square[1].neighbors == [0, 3])
        assert(square[2].neighbors == [0, 3])
        assert(square[3].neighbors == [1, 2])

        return

    if (topo == 'Y'):
        # create placeholder simulator
        sim = Simulator(1, 4, 0, 0, move=False, uniform=True)

        # Y
        y = [Device((constants.DEVICE_RANGE - 1), 0, 0, 1, 0),
             Device((constants.DEVICE_RANGE - 1),
                    (constants.DEVICE_RANGE - 1), 1, 1, 0),
             Device(0, (constants.DEVICE_RANGE - 1), 2, 1, 0),
             Device(2 * (constants.DEVICE_RANGE - 1), (constants.DEVICE_RANGE - 1), 3, 1, 0)]

        # reset device_mappings
        constants.device_mappings = {}
        for dev in y:
            constants.device_mappings[dev.id] = dev

        # insert y into sim
        sim.devices = y
        sim.connect_devices()

        # check connection
        assert(y[0].neighbors == [1])
        assert(y[1].neighbors == [0, 2, 3])
        assert(y[2].neighbors == [1])
        assert(y[3].neighbors == [1])

        return

    if (topo == 'K4'):
        # create placeholder simulator
        sim = Simulator(1, 4, 0, 0, move=False, uniform=True)

        # k4
        k4 = [Device(0, 0, 0, 1, 0),
              Device(1, 0, 1, 1, 0),
              Device(0, 1, 2, 1, 0),
              Device(1, 1, 3, 1, 0)]

        # reset device_mappings
        constants.device_mappings = {}
        for dev in k4:
            constants.device_mappings[dev.id] = dev

        # insert k4 into sim
        sim.devices = k4
        sim.connect_devices()

        # check connection
        assert(k4[0].neighbors == [1, 2, 3])
        assert(k4[1].neighbors == [0, 2, 3])
        assert(k4[2].neighbors == [0, 1, 3])
        assert(k4[3].neighbors == [0, 1, 2])

        return


def connect_devices():
    # line
    _connect_devices_helper('line')

    # square
    _connect_devices_helper('square')

    # Y
    _connect_devices_helper('Y')

    # K4
    _connect_devices_helper('K4')


def update_deliveries():
    # create placeholder simulator
    sim = Simulator(60, 4, 0, 0, 10000, move=False, uniform=True)

    # device 0 sends message 10
    # device 1 receives message 10
    # device 2 sends message 5
    # device 3 receives message 5
    sim.update_deliveries(0, 10)
    sim.update_deliveries(1, 10)
    sim.update_deliveries(2, 5)
    sim.update_deliveries(3, 5)

    assert(len(sim.deliveries[10]) == 2 and len(sim.deliveries[5]) == 2)


def update_delivery_stats():
    # create placeholder simulator
    sim = Simulator(60, 4, 0, 0, 10000, move=False, uniform=True)

    # device 0 sends message 10
    # device 1 receives message 10
    # device 2 sends message 5
    # device 3 receives message 5
    sim.update_deliveries(0, 10)
    sim.update_deliveries(1, 10)
    sim.update_deliveries(2, 5)
    sim.update_deliveries(3, 5)

    sim.update_delivery_stats()
    assert(sim.delivery_stats[0][10] == 2 and sim.delivery_stats[0][5] == 2)
    
    sim.round += 10

    sim.update_deliveries(2, 10)

    sim.update_delivery_stats()
    assert(sim.delivery_stats[1][10] == 3 and sim.delivery_stats[1][5] == 2)



# def bandwidth_results():
#     rounds = 10
#     num_devices = 4

#     # create placeholder simulator with 3 rounds
#     sim = Simulator(rounds * constants.TIME_STEP, num_devices,
#                     0, 0, move=False, uniform=True)

#     # create devices
#     devices = [Device(0, 0, i, rounds, 0) for i in range(num_devices)]

#     # set round states
#     for dev in devices:
#         dev.round_states = [{'incoming': x * dev.id,
#                              'outgoing': 2 * x * dev.id} for x in range(rounds)]

#     sim.devices = devices

#     print(sim.bandwidth_results())
#     # might have to change to np.close()
#     # assert(sim.bandwidth_results() == (0.45, 0.9, 0.0))

#     return
