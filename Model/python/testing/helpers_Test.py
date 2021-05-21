import constants
import helpers


def compress_in_out():
    bandwidths = [{'incoming': 1, 'outgoing': 2}, {
        'incoming': 3, 'outgoing': 4},
        {'incoming': 5, 'outgoing': 6}]
    assert(helpers.compress_in_out(bandwidths) == [3, 7, 11])


def get_random_string():
    rand1 = helpers.get_random_string(300)
    rand2 = helpers.get_random_string(300)

    # check lengths
    assert(len(rand1) == 300)
    assert(len(rand2) == 300)

    # probability that they are the same is neglibable
    assert(rand1 != rand2)


def chunk_measurements():
    chunks = helpers.chunk_measurements(list(range(30)))

    assert(len(chunks) == 3)

    assert(chunks[0] == list(range(10)))
    assert(chunks[1] == list(range(10, 20)))
    assert(chunks[2] == list(range(20, 30)))


def sum_chunks():
    chunks = [[1, 2], [3, 4, 5], [6], [7, 8, 9, 10]]
    summed_chunks = helpers.sum_chunks(chunks)

    assert(summed_chunks == [3, 12, 6, 34])


def average_list():
    l = [1, 2, 3, 4, 5]
    avg = helpers.average_list(l)

    assert(avg == 3)


def calc_num_bitlist_packets():
    assert(helpers.calc_num_bitlist_packets(100, 50, 10) == 3)
    assert(helpers.calc_num_bitlist_packets(100, 100, 10) == 2)
    assert(helpers.calc_num_bitlist_packets(100, 110, 10) == 1)


def calc_request_size():
    assert(helpers.calc_request_size(
        [1, 2, 3]) == constants.BLE_ADVERTISEMENT_HEADER_SIZE + constants.ID_SIZE + 3)

    body_size = (constants.MAX_TOTAL_SIZE -
                 constants.BLE_ADVERTISEMENT_HEADER_SIZE - constants.ID_SIZE)
    assert(helpers.calc_request_size(list(range(constants.MAX_TOTAL_SIZE + 1))) ==
           constants.MAX_TOTAL_SIZE + constants.BLE_ADVERTISEMENT_HEADER_SIZE + constants.ID_SIZE +
           (constants.MAX_TOTAL_SIZE + 1 - body_size))


def calc_response_size():
    assert(helpers.calc_response_size(set(list(range(300))))
           == 300 * constants.TOTAL_MESSAGE_SIZE)


def get_experiments_csv_header():
    assert(helpers.get_experiments_csv_header() == 'sim_id,num_rounds,num_devices,x,y,move,uniform\n')

def build_experiments_log_line():
    assert(helpers.build_experiments_log_line(0, 0, 0, 0, 0,
                                              False, False) == '0,0,0,0,0,False,False\n')

def get_messages_csv_header():
    assert(helpers.get_messages_csv_header() ==
           'sender,receiver,type,msg_id,transimission_id,size,time,sim_id\n')

def build_messages_log_line():
    assert(helpers.build_messages_log_line('s', 'r', 'msg', 0, 0, 0, 0, 0) == 's,r,msg,0,0,0,0,0\n')
