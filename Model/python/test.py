from testing.Messages_Test import *
from testing.Device_Test import *
from testing.Simulator_Test import *
from testing.Grid_Test import *
from testing.helpers_Test import *

def test_Messages():
	add()
	update()
	clean()
	compare()

def test_Devices():
	add_neighbor()
	remove_neighbor()
	clear_neighbors()
	in_range()
	calc_deliver_prob()
	choose_random_neighbor()
	update_round()
	should_send_msg()
	should_send_bitlist()
	update_missing()
	clear_missing()
	update_requests()
	clear_requests()
	add_message()
	store_messages()
	move()
	get_pos()

def test_Simulator():
	# setup()
	# process_send()
	# process_bitlist()
	# process_request()
	# process_response()
	# connect_devices()
	update_deliveries()
	update_delivery_stats()
	# bandwidth_results()

def test_Grid():
	populate()
	get_neighbors()

def test_Helpers():
	compress_in_out()
	get_random_string()
	chunk_measurements()
	sum_chunks()
	average_list()
	calc_num_bitlist_packets()
	calc_request_size()
	calc_response_size()
	get_experiments_csv_header()
	build_experiments_log_line()
	get_messages_csv_header()
	build_messages_log_line()


# test_Messages()
# test_Devices()
test_Simulator()
# test_Grid()
# test_Helpers()
