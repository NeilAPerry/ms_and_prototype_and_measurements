from queue import PriorityQueue
from hashlib import sha256
import sys

import constants

# Data structure to hold received messages
# Contains hash table (bit list)
# Contains timestamps for each bit
class Messages:

    EXPIRE_TIME = 5 * 60 * 1000

    # initialize empty data structure
    def __init__(self, size):
        self.bitlist = set()

        self.times = PriorityQueue()

    # add message to data structure
    def add(self, msg, time):
        h = int.from_bytes(sha256(bytes(msg, 'utf-8')).digest(), sys.byteorder)
        idx = h % constants.DS_SIZE

        # store index of bitlist
        self.bitlist.add(idx)

        # store (time, index in bitlist)
        self.times.put((time, idx))

        return idx

    # add all indices to data structure
    def update(self, indices, time):
        # can't use set.update because we don't want to overwrite times
        for idx in indices:
            if (idx not in self.bitlist):
                self.bitlist.add(idx)
                self.times.put((time, idx))

    # update timestamps and remove expired entries
    # called every round
    def clean(self, time):
        # check received messages from oldest to newest

        # if oldest item is expired
        while (not self.times.empty() and (time - self.times.queue[0][0] >= Messages.EXPIRE_TIME)):
            # remove from times and get index
            t, idx = self.times.get()
            # remove from bitlist
            self.bitlist.remove(idx)

    # compare a passed in bitlist to your bitlist
    # return a list of indices where your's is 0 but the passed in one is 1
    def compare(self, bitlist):

        return list(bitlist.difference(self.bitlist))
