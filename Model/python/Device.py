import random
import math
from collections import deque

import constants
from Messages import Messages

class Device:

    NEIGHBOR_PENALTY = 0.03

    """
    x: spatial x coordinate
    y: spatial y coordinate
    id_num: id of device
    num_rounds: number of rounds in simulation
                -> Need to store results for each round
    join_time: time that you joined the network mod 1 minute
               -> need to do something every 30 seconds
                  relative to this
    """

    def __init__(self, x, y, id_num, num_rounds, join_time, message_interval, bitlist_interval):
        self.x = x
        self.y = y
        # periodicially a new random direction could be chosen (but it would be the same for several rounds at a time)
        self.direction = None
        self.id = id_num
        self.neighbors = []  # store list of ids

        # probability of successfully delivering a message
        self.deliver_prob = 1  # calc_deliver_prob() would be used if this was not set to 100%
        self.range = constants.DEVICE_RANGE # connectivity range in feet
        self.join_time = join_time % (60 * 1000)
        self.message_interval = message_interval
        self.bitlist_interval = bitlist_interval

        self.messages = Messages(constants.DS_SIZE)
        self.missing = {}
        self.requests = {}

        # for simple broadcast
        self.curr_queue = deque() # messages to send this round
        self.next_queue = deque() # messages to send next round
        self.seen = set()

        self.round = 0
        self.round_states = [{'incoming': 0, 'outgoing': 0}
                             for _ in range(num_rounds)]

    # add a new neighbor
    def add_neighbor(self, neighbor):
        self.neighbors += [neighbor]

    # remove an existing neighbor
    def remove_neighbor(self, neighbor):
        self.neighbors.remove(neighbor)

    # remove all neighbors
    def clear_neighbors(self):
        self.neighbors = []

    # check if 2 devices are within range of each other
    def in_range(self, other_id):
        other = constants.device_mappings[other_id]
        distance = (self.x - other.x) ** 2 + (self.y - other.y) ** 2
        return distance < self.range ** 2

    # return probability of message being delivered
    def calc_deliver_prob(self):
        self.deliver_prob = max(
            0.1, 1 - len(self.neighbors) * Device.NEIGHBOR_PENALTY)

    # choose a random neighbor
    # used to choose who to send the message list to
    # throws 'No Neighbors' Exception when the device has no neighbors
    def choose_random_neighbor(self):
        if (len(self.neighbors) > 0):
            return random.choice(self.neighbors)
        else:
            raise Exception('No Neighbors')

    # update state for a round
    def update_round(self, round_num, incoming, outgoing):
        self.round_states[round_num]['incoming'] += incoming
        self.round_states[round_num]['outgoing'] += outgoing

    # check if device should send a message
    def should_send_msg(self, time):
        # send message at join_time or join_time + 30s
        diff = (time - self.join_time) % self.message_interval
        return diff == 0

    # check if device should send its bitlist
    # (send bitlist to 1 neighbor every BITLIST_INTERVAL ms)
    def should_send_bitlist(self, time):
        diff = (time - self.join_time) % (60 * 1000)
        return diff % self.bitlist_interval == 0

    # record what messages another device has that this device
    # does not have and the id of the other device
    def update_missing(self, id_num, bitlist):
        # check which ones are missing
        missing = self.messages.compare(bitlist)

        # save who has them
        self.missing[id_num] = missing

    # clear all missing lists
    def clear_missing(self):
        self.missing = {}

    # add a new request to list of request
    def update_requests(self, id_num, requests):
        self.requests[id_num] = requests

    # clear all request lists
    def clear_requests(self):
        self.requests = {}

    # add a message
    def add_message(self, msg, time):
        idx = self.messages.add(msg, time)
        return idx

    # update data structure with received messages
    # response is a list of indices
    def store_messages(self, response, time):
        self.messages.update(response, time)

    # TODO write test
    def simple_add(self, msg):
        if msg not in self.seen:
            self.next_queue.append(msg)
            self.seen.add(msg)

    # TODO write test
    def simple_next_round(self):
        self.curr_queue = self.next_queue
        self.next_queue = deque()

    # TODO make more realistic and use self.direction
    # move device by updating its location
    def move(self):
        self.x += random.randint(-4, 4)
        self.y += random.randint(-4, 4)

        if (self.x < 0):
            self.x = 0
        if (self.y < 0):
            self.y = 0

    def get_pos(self):  # get the bucket index for this device
        return int(self.x // self.range), int(self.y // self.range)
