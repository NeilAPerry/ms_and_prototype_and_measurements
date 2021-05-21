import random
import math
import sys
from collections import defaultdict

import constants
import helpers

from Device import Device
from Grid import Grid


class Simulator:

    """
    num_rounds: number of rounds to run in simulation
    num_devices: number of devices in simulation
    x: mean x coordinate for starting position of devices in simulation
    y: mean y coordinate for starting position of devices in simulation
    move: boolean of if devices should move during simulation
    uniform: boolean of if devices's starting position should be
             a uniform grid with 5 ft between each device
    """

    def __init__(self, num_rounds, num_devices, x, y, bitlist_interval, move=True, uniform=False, broadcastType='smart', uniform_spacing=constants.UNIFORM_SPACING, send_rate=constants.SEC_30, messages_file=None, experiments_file=None, delivery_file=None):
        if (messages_file == None):
            messages_file = open('/dev/null', 'w')

        if (experiments_file == None):
            experiments_file = open('/dev/null', 'w')

        print('Initializing simulation state...')

        self.messages_file = messages_file
        self.experiments_file = experiments_file

        self.logDelivery = delivery_file != None
        self.delivery_file = delivery_file
        # keep track of which messages have been delivered
        self.deliveries = defaultdict(set)
        self.origin_times = {}
        self.finished_thresholds = defaultdict(set)
        # holds stats on messages for each second of the simulation
        # self.delivery_stats = [None] * (num_rounds // (1000 // constants.TIME_STEP))
        # for idx in range(len(self.delivery_stats)):
        #     self.delivery_stats[idx] = {}

        self.id = random.randint(0, 10000000)
        self.experiments_file.write(helpers.build_experiments_log_line(
            self.id, num_rounds, num_devices, x, y, bitlist_interval, move, uniform, broadcastType))

        self.num_rounds = num_rounds
        self.round = 0  # initialize with starting round
        self.move = move
        self.x = x
        self.y = y
        self.num_devices = num_devices
        self.bitlist_interval = bitlist_interval
        self.uniform = uniform
        self.broadcastType = broadcastType
        self.uniform_spacing = uniform_spacing
        self.send_rate = send_rate
        self.degree = 0
        self.transimission_count = 0

        # use helper to initialize rest of state
        self.setup()

        # file headers
        self.messages_file.write(helpers.get_messages_csv_header())
        if self.logDelivery:
            self.delivery_file.write(helpers.get_delivery_csv_header())

    def setup(self):

        # TIME_STEP sized intervals uniformly distributed for 1 minute
        possible_start_times = list(range(0, 60 * 1000, constants.TIME_STEP))

        # create devices
        # uniform square with everyone 5 ft apart (assumes 10,000 devices)
        if (self.uniform):
            wrap_around = math.sqrt(self.num_devices)
            self.devices = [Device((idx % wrap_around) * self.uniform_spacing,
                                   (idx // wrap_around) *
                                   self.uniform_spacing,
                                   idx,
                                   self.num_rounds,
                                   random.choice(possible_start_times),
                                   self.send_rate,
                                   self.bitlist_interval
                                   ) for idx in range(self.num_devices)]
        # default is normal distribution
        else:
            self.devices = [Device(random.gauss(self.x, 1),
                                   random.gauss(self.y, 1),
                                   idx,
                                   self.num_rounds,
                                   random.choice(possible_start_times),
                                   self.send_rate,
                                   self.bitlist_interval
                                   ) for idx in range(self.num_devices)]

        # add devices to global mapping
        for dev in self.devices:
            constants.device_mappings[dev.id] = dev

        self.connect_devices()

    # send a message if your device is eligible to send
    # update device and neighboring devices' bandwidths
    def process_send(self, dev):
        # check if device should send
        if (not dev.should_send_msg(self.round * constants.TIME_STEP)):
            return

        # have the device generate a random message to send
        msg = helpers.get_random_string(300)  # change 300 to constant

        # add message to dev
        msg_id = dev.add_message(msg, self.round * constants.TIME_STEP)
        # update sender's outgoing bandwidth
        dev.update_round(self.round, 0, constants.TOTAL_MESSAGE_SIZE)

        # update that sender has their own message
        if (self.logDelivery):
            self.origin_times[msg_id] = (
                self.round * constants.TIME_STEP) // 1000
            self.update_deliveries(dev.id, msg_id)

        # add message to neighbors' DS and update incoming bandwidth
        for neighbor_id in dev.neighbors:
            neighbor = constants.device_mappings[neighbor_id]
            if (self.broadcastType == 'smart'):
                neighbor.add_message(msg, self.round * constants.TIME_STEP)
            else:
                neighbor.simple_add(msg_id)
            neighbor.update_round(self.round, constants.TOTAL_MESSAGE_SIZE, 0)
            # log message
            log_line = helpers.build_messages_log_line(dev.id, neighbor_id, 'msg', msg_id, self.transimission_count,
                                                       constants.TOTAL_MESSAGE_SIZE, self.round * constants.TIME_STEP, self.id)
            self.messages_file.write(log_line)
            if (self.logDelivery):
                self.update_deliveries(neighbor_id, msg_id)

        # broadcast so only 1 message sent
        self.transimission_count += 1

    # send device's bitlist to neighbors
    # TODO look at bandwidth numbers of only 1 neighbor running update_missing vs all of them doing it.
    # could also have only 1 request it but when you give your answer everyone updates their DS
    def process_bitlist(self, dev):
        # check if device should send
        if (not dev.should_send_bitlist(self.round * constants.TIME_STEP)):
            return

        # update sender's outgoing bandwidth
        dev.update_round(self.round, 0, constants.TOTAL_BITLIST_MESSAGE_SIZE)

        # each neighbor receives bitlist broadcast
        for neighbor_id in dev.neighbors:

            neighbor = constants.device_mappings[neighbor_id]

            # update neighbor's incoming bandwidth
            neighbor.update_round(
                self.round, constants.TOTAL_BITLIST_MESSAGE_SIZE, 0)

            # update neighbor's missing info so they know what to request
            neighbor.update_missing(dev.id, dev.messages.bitlist)

            # log bitlist
            log_line = helpers.build_messages_log_line(dev.id, neighbor_id, 'bitlist', None, self.transimission_count,
                                                       constants.TOTAL_BITLIST_MESSAGE_SIZE, self.round * constants.TIME_STEP,
                                                       self.id)
            self.messages_file.write(log_line)

        # broadcast so only 1 message sent (for the purpose of processing logs - its actually many packets)
        self.transimission_count += 1

    # look at all of the messages that a device knows its missing
    # make a request to each neighbor who has messages you are missing
    def process_request(self, dev):
        # if nothing to process
        if (len(dev.missing.keys()) == 0):
            return

        # keep track of which messages have been requested to avoid repeats
        requests = set()

        # request missing messages
        for neighbor_id, missing in dev.missing.items():
            neighbor = constants.device_mappings[neighbor_id]
            curr_request = []  # list to send to neighbor
            for msg_idx in missing:
                if (msg_idx not in requests):
                    curr_request += [msg_idx]
                requests.add(msg_idx)

            # don't need to send empty requests
            if (len(curr_request) == 0):
                continue

            # update neighbor state
            neighbor.update_requests(dev.id, curr_request)
            # update sender's outgoing bandwidth
            dev.update_round(
                self.round, 0, helpers.calc_request_size(curr_request))

            # all neighbors hear broadcast
            for n_id in dev.neighbors:
                n = constants.device_mappings[n_id]
                # update neighbor's incoming bandwidth
                n.update_round(
                    self.round, helpers.calc_request_size(curr_request), 0)
                # log request
                log_line = helpers.build_messages_log_line(dev.id, n_id, 'request', None, self.transimission_count,
                                                           helpers.calc_request_size(
                                                               curr_request), self.round * constants.TIME_STEP,
                                                           self.id)
                self.messages_file.write(log_line)
            # broadcast so only 1 message sent (but in loop since this happens for each request)
            self.transimission_count += 1

        # clear requests
        dev.clear_missing()

    # go through a devices requests (what neighbors requested from it) and respond to each one
    def process_response(self, dev):
        # if nothing to process
        if (len(dev.requests.keys()) == 0):
            return

        response = set()  # union of all requested messages

        # union all requests
        for neighbor_id, request in dev.requests.items():
            response.update(request)

        response_size = helpers.calc_response_size(response)

        # update sender's outgoing bandwidth
        dev.update_round(self.round, 0, response_size)

        # update neighbors' incoming bandwidth and data structures
        for neighbor_id in dev.neighbors:
            neighbor = constants.device_mappings[neighbor_id]
            neighbor.update_round(self.round, response_size, 0)
            neighbor.store_messages(response, self.round * constants.TIME_STEP)
        # log response
        for msg_id in response:
            for neighbor_id in dev.neighbors:
                log_line = helpers.build_messages_log_line(dev.id, neighbor_id, 'response', msg_id, self.transimission_count,
                                                           constants.TOTAL_MESSAGE_SIZE, self.round * constants.TIME_STEP, self.id)
                self.messages_file.write(log_line)
                if (self.logDelivery):
                    self.update_deliveries(neighbor_id, msg_id)
            # broadcast (union of all requests) so only 1 message sent
            self.transimission_count += 1

        # clear requests (all of them have been responded to)
        dev.clear_requests()

    # TODO write test
    def process_simple_forward(self, dev):
        while (dev.curr_queue):
            msg_id = dev.curr_queue.popleft()
            # send message to all neighbors
            for neighbor_id in dev.neighbors:
                neighbor = constants.device_mappings[neighbor_id]
                neighbor.simple_add(msg_id)
                neighbor.update_round(self.round, constants.TOTAL_MESSAGE_SIZE, 0)
                # log message
                log_line = helpers.build_messages_log_line(dev.id, neighbor_id, 'msg', msg_id, self.transimission_count,
                                                        constants.TOTAL_MESSAGE_SIZE, self.round * constants.TIME_STEP, self.id)
                self.messages_file.write(log_line)
                if (self.logDelivery):
                    self.update_deliveries(neighbor_id, msg_id)

            # broadcast so only 1 message sent
            self.transimission_count += 1

    # connect all devices that are within range of each other
    # (add them to each other's neighbor lists)

    def connect_devices(self):

        # keep track of degree
        degree = 0

        # clear neighbors
        for dev in self.devices:
            dev.clear_neighbors()

        # reset grid
        self.grid = Grid(constants.DEVICE_RANGE, 2000)
        self.grid.populate(self.devices)

        for dev in self.devices:
            degree = 0
            neighbors = self.grid.get_neighbors(dev)

            for neighbor_id in neighbors:
                if dev.in_range(neighbor_id):
                    dev.add_neighbor(neighbor_id)
                    degree += 1

            # store the maximum degree seen
            if (degree > self.degree):
                self.degree = degree

    def update_deliveries(self, node_id, msg_id):

        self.deliveries[msg_id].add(node_id)
        size = len(self.deliveries[msg_id])

        threshold = helpers.get_threshold(size, self.num_devices)
        
        # already recorded threshold level of message (don't record 0%)
        if threshold == 0 or msg_id in self.finished_thresholds[threshold]:
            return

        self.finished_thresholds[threshold].add(msg_id)
        log_line = helpers.build_delivery_log_line(
            msg_id,
            ((self.round * constants.TIME_STEP) // 1000) - self.origin_times[msg_id],
            threshold)
        self.delivery_file.write(log_line)
        

    # def update_delivery_stats(self):
    #     idx = self.round // (1000 // constants.TIME_STEP)

    #     # add length of sets to delivery_stats
    #     for msg_id, nodes in self.deliveries.items():
    #         self.delivery_stats[idx][msg_id] = len(nodes)

    # process 1 round of the simulation

    def process_round(self):
        # have each device check if it should send and send to neighbors if yes
        for dev in self.devices:
            self.process_send(dev)

        if (self.broadcastType == 'smart'):
            # have each device check if it should send its bitlist
            for dev in self.devices:
                self.process_bitlist(dev)

            # have each device make request for missing messages
            for dev in self.devices:
                self.process_request(dev)

            # have each device respond to any missing message requests
            for dev in self.devices:
                self.process_response(dev)

            # everyone updates messages data structure
            for dev in self.devices:
                dev.messages.clean(self.round * constants.TIME_STEP)

        else:
            # devices check their queues and forward messages
            for dev in self.devices:
                self.process_simple_forward(dev)
            
            # swap queues for next round
            for dev in self.devices:
                dev.simple_next_round()


        # everyone moves each second (if move=True)
        if (self.move and (self.round * constants.TIME_STEP % 1000 == 0)):
            for dev in self.devices:
                dev.move()
            # rebuild topology
            self.connect_devices()

        # update delivery info if logging
        # if (self.logDelivery and (self.round % (1000 // constants.TIME_STEP) == 0)):
        #     self.update_delivery_stats()

        # increment round number
        self.round += 1

    # run num_rounds of the simulation
    def run(self):
        for _ in range(self.num_rounds):
            # progress bar
            sys.stdout.write(
                '\rround: {0} / {1}          '.format(self.round + 1, self.num_rounds))
            sys.stdout.flush()

            # run 1 round
            self.process_round()

    # calculate stats on how much bandwidth devices used
    def bandwidth_results(self):
        round_states = [dev.round_states for dev in self.devices]
        total_round_states = [
            helpers.compress_in_out(rs) for rs in round_states]

        device_summaries = [helpers.average_list(helpers.sum_chunks(
            helpers.chunk_measurements(trs))) for trs in total_round_states]

        avg_device_bandwidth = helpers.average_list(
            device_summaries) / constants.BYTES_IN_MB
        max_device_bandwidth = max(device_summaries) / constants.BYTES_IN_MB
        min_device_bandwidth = min(device_summaries) / constants.BYTES_IN_MB

        return avg_device_bandwidth, max_device_bandwidth, min_device_bandwidth
