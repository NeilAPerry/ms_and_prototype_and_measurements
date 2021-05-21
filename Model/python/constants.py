import helpers

SEC_30 = 30 * 1000 # 30 seconds

TIME_STEP = 100  # 100 ms
BITLIST_INTERVAL = 10 * 1000  # 10s

DS_SIZE = 50584  # (2 * num_nodes * rate * min_to_keep)

DEVICE_RANGE = 30  # range of device

BYTES_IN_MB = 1000000  # number of bytes in 1 megabyte

UNIFORM_SPACING = 15  # space between devices when uniform=True in Simulator()

# Message Size
TAG_SIZE = 16  # 16 bytes for tag
PT_SIZE = 288  # bytes of message
E_SYM_KEY = 64  # 64 bytes(enc sym key, 2x size of key, one group element)
# OPTIONAL_TAG = 16  # maybe mac tag of 16 bytes if shared extra mac tag
ID_SIZE = 32  # size of public key

BLE_ADVERTISEMENT_HEADER_SIZE = 16
MAX_TOTAL_SIZE = 255 #384  # max size of BLE Advertisement

TOTAL_MESSAGE_SIZE = 255 #BLE_ADVERTISEMENT_HEADER_SIZE + TAG_SIZE + PT_SIZE + E_SYM_KEY  # size of 1 message

# BITLIST message size
DS_SIZE_BYTES = DS_SIZE // 8 if DS_SIZE % 8 == 0 else (DS_SIZE // 8) + 1
NUM_BITLIST_PACKETS = helpers.calc_num_bitlist_packets(
    DS_SIZE_BYTES, MAX_TOTAL_SIZE, BLE_ADVERTISEMENT_HEADER_SIZE)
TOTAL_BITLIST_MESSAGE_SIZE = NUM_BITLIST_PACKETS * MAX_TOTAL_SIZE  # overestimate (last body might not be full)

# keep mapping of ids to devices
# id -> device object
device_mappings = {}
