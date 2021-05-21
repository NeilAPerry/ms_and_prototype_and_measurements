import random
import string

import constants


def compress_in_out(bandwidths):
    return [bandwidth['incoming'] + bandwidth['outgoing'] for bandwidth in bandwidths]


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# list of compressed bandwidths -> average bandwidths for each second
# len of rounds -> len of total seconds


def chunk_measurements(measurements):
    chunk_length = 1000 // constants.TIME_STEP

    chunked_measurements = [measurements[i * chunk_length:(i + 1) * chunk_length] for i in range(
        (len(measurements) + chunk_length - 1) // chunk_length)]

    return chunked_measurements


def sum_chunks(chunked_measurements):
    return [sum(chunk) for chunk in chunked_measurements]


def average_list(measurements):
    return sum(measurements) / len(measurements)


# returns number of messages needed to send a bitlist
def calc_num_bitlist_packets(ds_size, max_packet_size, header_size):
    res = ds_size // (max_packet_size - header_size)
    return res if ds_size % (max_packet_size - header_size) == 0 else res + 1

# take in list of bitlist indices to request and return size of combined messages


def calc_request_size(request):
    if (len(request) == 0):
        return 0

    # requester id + 1 byte per idx number
    body_size = (constants.MAX_TOTAL_SIZE -
                 constants.BLE_ADVERTISEMENT_HEADER_SIZE - constants.ID_SIZE)
    num_packets = len(request) // body_size
    num_packets = num_packets if len(
        request) % body_size == 0 else num_packets + 1

    last_packet_size = constants.BLE_ADVERTISEMENT_HEADER_SIZE + \
        constants.ID_SIZE + (len(request) % body_size)
    result = (num_packets - 1) * constants.MAX_TOTAL_SIZE + last_packet_size
    if (result < 0):
        print(request)
    return result

# response is set of messages indices


def calc_response_size(response):
    # num messages * size of message
    return len(response) * constants.TOTAL_MESSAGE_SIZE


def get_experiments_csv_header():
    header_fields = ['sim_id', 'num_rounds',
                     'num_devices', 'x', 'y', 'bitlist_interval', 'move', 'uniform', 'broadcastType']
    return ','.join(header_fields) + '\n'


def build_experiments_log_line(sim_id, num_rounds, num_devices, x, y, bitlist_interval, move, uniform, broadcastType):
    inputs = [sim_id, num_rounds, num_devices, x, y, bitlist_interval, move, uniform, broadcastType]
    inputs = [str(i) for i in inputs]
    return ','.join(inputs) + '\n'


def get_messages_csv_header():
    header_fields = ['sender', 'receiver', 'type', 'msg_id',
                     'transimission_id', 'size', 'time', 'sim_id']
    return ','.join(header_fields) + '\n'


# SCHEMA: sender, receiver, type (message, bitlist, request), message id, size, time,
# num_rounds, num_devices, x, y, move, uniform, sim_id


def build_messages_log_line(sender, receiver, typ, msg_id, transimission_id, size, time, sim_id):
    inputs = [sender, receiver, typ, msg_id,
              transimission_id, size, time, sim_id]
    inputs = [str(i) for i in inputs]
    return ','.join(inputs) + '\n'


# TODO write unit test
def get_delivery_csv_header():
    header_fields = ['msg_id', 'seconds', 'threshold']
    return ','.join(header_fields) + '\n'

# TODO write unit test
def build_delivery_log_line(msg_id, second, threshold):
    inputs = [msg_id, second, threshold]
    inputs = [str(i) for i in inputs]
    return ','.join(inputs) + '\n'

# TODO write unit test
def get_threshold(size, num_devices):
    return (size // (num_devices // 10)) * 10
