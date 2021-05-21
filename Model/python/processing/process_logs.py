import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import random
import os
import sys
import argparse

NUM_DEVICES = 100
NUM_ROUNDS = 3000
BITLIST_INTERVAL = 10000
MINUTES = 5
MOVE = False
UNIFORM = True
UNIFORM_SPACING = 15
SEND_RATE = 30000

FILE_PATH = './logs/minutes_{minutes}_numDevices_{num_devices}_bitListInterval_{bitlist_interval}_move_{move}_uniform_{uniform}_uniformSpacing_{uniform_spacing}_sendRate_{send_rate}.csv'.format(
    minutes=MINUTES,
    num_devices=NUM_DEVICES,
    bitlist_interval=BITLIST_INTERVAL,
    move=MOVE,
    uniform=UNIFORM,
    uniform_spacing=UNIFORM_SPACING,
    send_rate=SEND_RATE)

FIGURES_PATH = './Figures/minutes_{minutes}_numDevices_{num_devices}_bitListInterval_{bitlist_interval}_move_{move}_uniform_{uniform}_uniformSpacing_{uniform_spacing}_sendRate_{send_rate}/'.format(
    minutes=MINUTES,
    num_devices=NUM_DEVICES,
    bitlist_interval=BITLIST_INTERVAL,
    move=MOVE,
    uniform=UNIFORM,
    uniform_spacing=UNIFORM_SPACING,
    send_rate=SEND_RATE)

def read_messages(file, usecols=[]):
    types = {'sender': 'Int64',
             'receiver': 'Int64',
             'type': 'str',
             'msg_id': 'Int64',
             'transmission_id': 'Int64',
             'size': 'Int64',
             'time': 'Int64',
             'sim_id': 'Int64'}

    if (len(usecols) == 0):
        df = pd.read_csv(file, na_values=['None'], dtype=types, low_memory=False)
    else:
        df = pd.read_csv(file, na_values=[
                         'None'], dtype=types, low_memory=False, usecols=usecols)

    return df


def get_outgoing_bandwidth(df):
    tmp = df[['sender', 'time', 'transimission_id', 'size']]
    tmp = tmp.groupby(['sender', 'time', 'transimission_id'],
                      as_index=False).min()
    # if this doesn't round down do .apply(np.floor)
    tmp['seconds'] = tmp['time'] // 1000
    tmp = tmp.groupby(['sender', 'seconds']).sum()
    tmp = tmp.reset_index()
    result = tmp[['sender', 'seconds', 'size']].copy()
    result.columns = ['Device', 'Seconds', 'Bytes']
    result['MB'] = result['Bytes'] / 1000000
    return result


# TODO make less copies
def get_incoming_bandwidth(df):
    tmp = df[['receiver', 'time', 'size']].copy()
    tmp['seconds'] = tmp['time'] // 1000
    tmp = tmp.groupby(['receiver', 'seconds']).sum()
    tmp = tmp.reset_index()
    result = tmp[['receiver', 'seconds', 'size']].copy()
    result.columns = ['Device', 'Seconds', 'Bytes']
    result['MB'] = result['Bytes'] / 1000000
    return result


def read_incoming_bandwidth(file_path):
    df = read_messages(file_path, usecols=['receiver', 'time', 'size'])

    df.loc[:, 'time'] = df['time'] // 1000
    df = df.groupby(['receiver', 'time']).sum()
    df = df.reset_index()
    df.loc[:, 'size'] = df['size'] / 1000000
    df.columns = ['Device', 'Seconds', 'MB']
    return df


def process_incoming_chunk(df):
    df.loc[:, 'time'] = df['time'] // 1000
    df = df.groupby(['receiver', 'time']).sum()
    df = df.reset_index()
    df.columns = ['Device', 'Seconds', 'Bytes']
    return df


def read_incoming_bandwidth_chunked(file_path):
    types = {'sender': 'Int64',
             'receiver': 'Int64',
             'type': 'str',
             'msg_id': 'Int64',
             'transmission_id': 'Int64',
             'size': 'Int64',
             'time': 'Int64',
             'sim_id': 'Int64'}

    dfs = []
    chunksize = 10 ** 6
    with pd.read_csv(file_path, chunksize=chunksize, usecols=['receiver', 'time', 'size'], dtype=types) as reader:
        for chunk in reader:
            dfs += [process_incoming_chunk(chunk)]

    # To handle duplicate (Device, Seconds) key pairs in two dfs (msg split across chunks), sum them.
    # i.e. for stitching, just concat them all together, do another identical groupby and sum.
    # Do this on Bytes and then convert to MB to avoid floating point problems.
    df = pd.concat(dfs)
    df = df.groupby(['Device', 'Seconds']).sum()
    df = df.reset_index()
    df.loc[:, 'Bytes'] = df['Bytes'] / 1000000
    df.rename(columns={'Bytes': 'MB'}, inplace=True)
    return df


def process_outgoing_chunk(df):
    df = df.groupby(['sender', 'time', 'transimission_id'],
                    as_index=False).min()
    df.loc[:, 'time'] = df['time'] // 1000
    df = df.groupby(['sender', 'time']).sum()
    df = df.reset_index()
    df.drop(['transimission_id'], axis=1, inplace=True)
    df.columns = ['Device', 'Seconds', 'Bytes']
    return df


def read_outgoing_bandwidth_chunked(file_path):
    types = {'sender': 'Int64',
             'receiver': 'Int64',
             'type': 'str',
             'msg_id': 'Int64',
             'transmission_id': 'Int64',
             'size': 'Int64',
             'time': 'Int64',
             'sim_id': 'Int64'}

    dfs = []
    chunksize = 10 ** 6
    with pd.read_csv(file_path, chunksize=chunksize, usecols=['sender', 'time', 'transimission_id', 'size'], dtype=types) as reader:
        prev = pd.DataFrame()
        for chunk in reader:
            # problems happen if a transmission id is split across chunks
            if (prev.empty):
                prev = chunk
                continue
            else:
                # check if a transmission is split across 2 chunks
                last_prev_id = prev.iloc[-1]['transimission_id']
                first_chunk_id = chunk.iloc[0]['transimission_id']

                if (last_prev_id == first_chunk_id):

                    chunk = pd.concat(
                        [prev[prev['transimission_id'] == last_prev_id], chunk])
                    prev = prev[prev['transimission_id'] != last_prev_id]
                    dfs += [process_outgoing_chunk(prev)]
                    prev = chunk

                else:
                    dfs += [process_outgoing_chunk(prev)]
                    prev = chunk

        dfs += [process_outgoing_chunk(chunk)]

    # To handle duplicate (Device, Seconds) key pairs in two dfs (msg split across chunks), sum them.
    # i.e. for stitching, just concat them all together, do another identical groupby and sum.
    # Do this on Bytes and then convert to MB to avoid floating point problems.
    df = pd.concat(dfs)
    df = df.groupby(['Device', 'Seconds']).sum()
    df = df.reset_index()
    df.loc[:, 'Bytes'] = df['Bytes'] / 1000000
    df.rename(columns={'Bytes': 'MB'}, inplace=True)

    return df


def combine_in_out(in_df, out_df):
    combined = pd.concat([in_df, out_df])
    combined = combined.groupby(['Device', 'Seconds']).sum()
    combined = combined.reset_index()
    return combined


def print_statistics(bandwidths):
    avg_bandwidth = bandwidths['MB'].mean()
    min_bandwidth = bandwidths['MB'].min()
    max_bandwidth = bandwidths['MB'].max()

    print('Average MB/sec: {b}'.format(b=avg_bandwidth))
    print('Min MB/sec: {b}'.format(b=min_bandwidth))
    print('Max MB/sec: {b}'.format(b=max_bandwidth))


def plot_bandwidth_pdf(df, col, bins, direction):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel(col)
    ax.set_ylabel('% Data')
    ax.set_title('{direction} PDF'.format(direction=direction))

    ys, xs = np.histogram(df[col], bins=bins)
    ys = np.array(ys) / sum(ys) * 100

    plt.plot(xs[:-1], ys)  # ignore end of last bucket

    plt.savefig(FIGURES_PATH +
                '{direction}_bandwidth_pdf.png'.format(direction=direction))


def plot_bandwidth_cdf(df, col, direction):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel(col)
    ax.set_ylabel('% Data')
    ax.set_title('{direction} CDF'.format(direction=direction))

    sorted_data = np.sort(df[col])
    sorted_data_cdf = np.arange(len(sorted_data))/float(len(sorted_data)) * 100
    plt.plot(sorted_data, sorted_data_cdf)

    plt.savefig(FIGURES_PATH +
                '{direction}_bandwidth_cdf.png'.format(direction=direction))


def message_delivery_percentage(df):
    devices = set(np.array(df['sender']))
    msg_ids = set(np.array(df['msg_id']))
    msg_ids.remove(pd.NA)

    missing = {}
    num_missing = 0
    for msg_id in msg_ids:
        for receiver in devices:
            entries = df[(df['receiver'] == receiver)
                         & (df['msg_id'] == msg_id)]
            if (len(entries) == 0):
                if (msg_id in missing):
                    missing[msg_id] += [receiver]
                else:
                    missing[msg_id] = [receiver]

    print('{num_missing} / {total} messages were not delivered to all nodes'.format(
        num_missing=len(missing), total=len(msg_ids)))
    print(missing)


def cdf_received_points(df, sender_id, msg_id):

    received = set()
    received.add(sender_id)

    time_series = df[df['msg_id'] == msg_id][['receiver', 'time']]

    start_time = time_series['time'].iloc[0]

    points = {}
    count = 1  # sender already added

    for receiver, time in time_series.values:
        time -= start_time
        # not already received
        if (receiver not in received):
            received.add(receiver)
            count += 1
        points[time] = count

    points_list = [(k, points[k])
                   for k in sorted(points, key=points.get, reverse=False)]
    xs, ys = zip(*points_list)

    xs = [x / 1000 for x in xs]
    ys = [100 * y / NUM_DEVICES for y in ys]

    return xs, ys


def plot_group_received_points(df, sender_message_pairs, start, end):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('seconds')
    ax.set_ylabel('% devices')
    ax.set_title('Message Delivery CDF')

    cmap = plt.cm.get_cmap('hsv', end - start)
    for idx in range(start, end):
        xs, ys = cdf_received_points(
            df, sender_message_pairs[idx][0], sender_message_pairs[idx][1])
        ax.step(xs, ys, color=cmap(idx))
    plt.savefig(FIGURES_PATH + 'message_deliver_cdf.png')


def spacing_scaling_percentile(quantile):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('devices')
    ax.set_ylabel('MB/s')
    ax.set_title('Scaling {percentile}th Percentile'.format(
        percentile=int(quantile * 100)))

    people = [100, 200, 300, 400]  # [100, 200, 300, 400, 500, 600, 700]
    spacing = [2, 5, 15]  # [2, 10, 15]  # [3, 5, 10, 15]
    colors = ['red', 'blue', 'purple']  # ['red', 'blue', 'purple', 'green']

    data = None
    results = {}

    for space, color in zip(spacing, colors):
        print('spacing: {space}'.format(space=space))
        results[space] = []
        for num_people in people:
            print('\tsize: {num_people}'.format(num_people=num_people))
            data = read_messages('./logs/minutes_{minutes}_numDevices_{num_devices}_bitListInterval_{bitlist_interval}_move_{move}_uniform_{uniform}_uniformSpacing_{uniform_spacing}_sendRate_{send_rate}.csv'.format(
                minutes=MINUTES,
                num_devices=num_people,
                bitlist_interval=BITLIST_INTERVAL,
                move=MOVE,
                uniform=UNIFORM,
                uniform_spacing=space,
                send_rate=SEND_RATE))
            data = get_incoming_bandwidth(data)
            results[space] += [data['MB'].quantile(quantile)]

        ax.plot(people, results[space], color=color,
                label='{space} ft apart'.format(space=space))

    # for space, color in zip(spacing, colors):

    #     dfs = [read_messages('./logs/minutes_{minutes}_numDevices_{num_devices}_bitListInterval_{bitlist_interval}_move_{move}_uniform_{uniform}_uniformSpacing_{uniform_spacing}_sendRate_{send_rate}.csv'.format(
    #         minutes=MINUTES,
    #         num_devices=num_people,
    #         bitlist_interval=BITLIST_INTERVAL,
    #         move=MOVE,
    #         uniform=UNIFORM,
    #         uniform_spacing=space,
    #         send_rate=SEND_RATE)) for num_people in people]

    #     dfs = [get_incoming_bandwidth(data) for data in dfs]
    #     incoming_highs = [data['MB'].quantile(quantile) for data in dfs]

    #     ax.plot(people, incoming_highs, color=color,
    #             label='{space} spacing'.format(space=space))
    ax.legend()
    plt.savefig('./Figures/scaling_{quantile}.png'.format(quantile=quantile))

def find_capacities(space, num_devices):
    # TODO does it really make sense to be looking at the 95th percentile of all seconds for all devices?
    # TODO all this would mean is 1 device was borderline failing
    
    file_path = './logs/minutes_{minutes}_numDevices_{num_devices}_bitListInterval_{bitlist_interval}_move_{move}_uniform_{uniform}_uniformSpacing_{uniform_spacing}_sendRate_{send_rate}.csv'.format(
        minutes=MINUTES,
        num_devices=num_devices,
        bitlist_interval=BITLIST_INTERVAL,
        move=MOVE,
        uniform=UNIFORM,
        uniform_spacing=space,
        send_rate=SEND_RATE)

    data = read_incoming_bandwidth_chunked(file_path)

    print(data.memory_usage(index=True).sum())

    bandwidth = [data['MB'].quantile(0.95)]
    print(bandwidth)
    return

def graph_capacities():
    values = {}
    # spacing, num devices
    values[(2, 250)] = 0.241893
    values[(2, 300)] = 0.26735050000000016
    values[(2, 400)] = 0.404169
    values[(2, 800)] = 0.74761925
    values[(2, 1200)] = 1.02782435
    values[(2, 2000)] = 1.4674180999999997
    values[(2, 3000)] = 1.81204005
    values[(3, 250)] = 0.215656
    values[(3, 300)] = 0.2689146
    values[(3, 350)] = 0.283193
    values[(3, 400)] = 0.310822
    values[(3, 2000)] = 0.7000921499999998
    values[(5, 1000)] = 0.23671209999999998
    values[(5, 1500)] = 0.30088105
    values[(5, 2000)] = 0.338343
    values[(5, 2500)] = 0.379041
    values[(5, 6000)] = 0.6399040499999998
    values[(7, 1500)] = 0.24440050000000002
    values[(10, 1800)] = 0.25090379999999984
    values[(10, 2000)] = 0.29268180000000005
    values[(15, 2000)] = 0.27997949999999977
    values[(15, 2500)] = 0.3130936000000001
    values[(15, 3000)] = 0.364441
    values[(15, 5000)] = 0.5216594499999997
    # x axis -> different spacings
    # y axis -> number of devices that can handle < 2 Mb/s (0.25 MB/s) at 95th percentile
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('ft apart')
    ax.set_ylabel('# of devices')
    ax.set_title('Max Capacities')

    xs = [2, 3, 5, 7, 10, 15]
    ys = [250, 300, 1000, 1500, 1800, 2000] # TODO some above 0.25 and none include outgoing

    plt.plot(xs, ys)
    plt.savefig('./Figures/' + 'max_capacities.png')

def create_delivery_log(df):
    sender_message_pairs = df.groupby('msg_id').first().reset_index()[['sender', 'msg_id']].values
    return



def main():
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--Total", help="Read in log and write out in + out bandwidth", action="store_true")
    parser.add_argument("-l", "--Log", help="Path to log file")
    parser.add_argument("-s", "--Spacing", help="Spacing of devices")
    parser.add_argument("-d", "--Devices", help="Number of devices")
    parser.add_argument("-m", "--Minutes", help="Minutes that the simulation ran for")
    parser.add_argument("-b", "--BitListInterval", help="BitList Interval (ms")
    parser.add_argument("-v", "--Move", help="If people were moving (boolean)")
    parser.add_argument("-u", "--Uniform", help="If uniform (boolean)")
    parser.add_argument("-r", "--Rate", help="Send rate of new messages (ms)")
    parser.add_argument("-c", "--BroadcastType", type=str, help="simple or smart")
    args = parser.parse_args()

    # make folder for figures if it doesn't exist
    if not os.path.exists(FIGURES_PATH):
        os.makedirs(FIGURES_PATH)

    if args.Total:
        file_name = 'minutes_{minutes}_numDevices_{num_devices}_bitListInterval_{bitlist}_move_{move}_uniform_{uniform}_broadcastType_{broadcastType}_uniformSpacing_{space}_sendRate_{rate}.csv'.format(
            space=args.Spacing, 
            num_devices=args.Devices, 
            minutes=args.Minutes, 
            bitlist=args.BitListInterval, 
            move=args.Move, 
            uniform=args.Uniform, 
            broadcastType=args.BroadcastType,
            rate=args.Rate)

        log_path = './logs/' + file_name
        incoming = read_incoming_bandwidth_chunked(log_path)
        outgoing = read_outgoing_bandwidth_chunked(log_path)
        combined = combine_in_out(incoming, outgoing)

        combined.to_csv('./summaries/' + file_name, index=False)
        exit(0)


    # read and clean data
    # df = read_messages(FILE_PATH)
    # outgoing = get_outgoing_bandwidth(df)
    # incoming = get_incoming_bandwidth(df)

    # # incoming
    # print_statistics(incoming)
    # plot_bandwidth_pdf(incoming, 'MB', 30, 'Incoming')
    # plot_bandwidth_cdf(incoming, 'MB', 'Incoming')

    # # outgoing
    # print_statistics(outgoing)
    # plot_bandwidth_pdf(outgoing, 'MB', 30, 'Outgoing')
    # plot_bandwidth_cdf(outgoing, 'MB', 'Outgoing')

    # # message delivery
    # # message_delivery_percentage(df)
    # sender_message_pairs = df.groupby('msg_id').first().reset_index()[
    #     ['sender', 'msg_id']].values
    # plot_group_received_points(df, sender_message_pairs, 100, 150)

    # # scaling
    # spacing_scaling_percentile(0.95)

    # find_capacities(sys.argv[1], sys.argv[2])
    # graph_capacities()

    return


if __name__ == "__main__":
    main()
