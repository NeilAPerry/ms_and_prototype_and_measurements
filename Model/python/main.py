import constants
from Simulator import Simulator

import argparse
import sys
import traceback
import json


def start(minutes, num_devices, bitlist_interval, move, uniform, broadcastType, uniform_spacing, send_rate, messages_file, experiments_file, delivery_file):
    sim = Simulator(minutes * 10 * 60,
                    num_devices,
                    5280/4,
                    5280/4,
                    bitlist_interval,
                    move=move,
                    uniform=uniform,
                    broadcastType=broadcastType,
                    uniform_spacing=uniform_spacing,
                    send_rate=send_rate,
                    messages_file=messages_file,
                    experiments_file=experiments_file,
                    delivery_file=delivery_file)

    sim.run()
    print(sim.degree)

    # if (delivery_file != None):
    #     # print(sim.delivery_stats)
    #     json.dump(sim.delivery_stats, delivery_file)

# TODO change gen scripts for -c broadcastType
def main():

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--Spacing", type=int, help="Spacing of devices")
    parser.add_argument("-d", "--Devices", type=int, help="Number of devices")
    parser.add_argument("-m", "--Minutes", type=int,
                        help="Minutes that the simulation ran for")
    parser.add_argument("-b", "--BitListInterval",
                        type=int, help="BitList Interval (ms")
    parser.add_argument("-v", "--Move", type=str,
                        help="If people were moving (boolean)")
    parser.add_argument("-u", "--Uniform", type=str,
                        help="If uniform (boolean)")
    parser.add_argument("-c", "--BroadcastType", type=str,
                        help="simple or smart")
    parser.add_argument("-r", "--Rate", type=int,
                        help="Send rate of new messages (ms)")
    parser.add_argument("-l", "--LogDelivery", type=str,
                        help="Write message delivery stats to file")
    args = parser.parse_args()

    # files
    experiments_file_name = 'experiments.csv'
    experiments_file_path = 'processing/logs/{file_name}'.format(
        file_name=experiments_file_name)
    experiments_file = open(experiments_file_path, 'a')

    # set params
    minutes = args.Minutes
    bitlist_interval = args.BitListInterval
    uniform_spacing = args.Spacing
    send_rate = args.Rate
    move = True if args.Move == "True" else False
    uniform = True if args.Uniform == "True" else False
    if (args.BroadcastType != 'simple') and (args.BroadcastType != 'smart'):
        exit(1)
    broadcastType = args.BroadcastType
    num_devices = args.Devices
    logDelivery = True if args.LogDelivery == "True" else False

    try:
        messages_file_name = 'minutes_{minutes}_numDevices_{num_devices}_bitListInterval_{bitlist_interval}_move_{move}_uniform_{uniform}_broadcastType_{broadcastType}_uniformSpacing_{uniform_spacing}_sendRate_{send_rate}.csv'.format(
            minutes=minutes, num_devices=num_devices, bitlist_interval=bitlist_interval, move=move, uniform=uniform,
            broadcastType=broadcastType, uniform_spacing=uniform_spacing, send_rate=send_rate)
        messages_file_path = 'processing/logs/{file_name}'.format(
            file_name=messages_file_name)

        messages_file = open(messages_file_path, 'w')
        delivery_file = None

        if (logDelivery):
            delivery_file_path = 'processing/delivery/{file_name}'.format(
                file_name=messages_file_name)
            delivery_file = open(delivery_file_path, 'w')

        start(minutes, num_devices, bitlist_interval, move, uniform, broadcastType, uniform_spacing=uniform_spacing, send_rate=send_rate,
              messages_file=messages_file, experiments_file=experiments_file, delivery_file=delivery_file)
    except Exception as e:
        print(e)
        traceback.print_exception(type(e), e, e.__traceback__)
        print('Failed to run simulation')
    finally:
        messages_file.close()
        if (logDelivery):
            delivery_file.close()


if __name__ == "__main__":
    main()
