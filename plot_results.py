import matplotlib.pyplot as plt
import numpy as np

plot_path = "plots/"

plt.rcParams.update({'font.size': 16})

def parse_log(file_path):
    data = []
    current_config = None

    with open(file_path, 'r') as file:
        ipfs_req = 0
        perun_req = 0

        for line in file:
            line = line.strip()

            if line.startswith('Config'):
                current_config = line
            if line.startswith('NET'):
                parts = line.split('|')
                ipfs_req = int(parts[1].strip().split(':')[1])
                perun_req = int(parts[2].strip().split(':')[1])
            elif line:
                parts = line.split('|')
                if len(parts) > 2:
                    timestamp_str = parts[0].strip()
                    time_str = parts[1].strip().split(':')[1].strip()
                    event_type = parts[2].strip()

                    time_seconds = float(time_str.split()[0])

                    data.append({
                        'config': current_config,
                        'time_seconds': time_seconds,
                        'event_type': event_type,
                        'ipfs_req': ipfs_req,
                        'perun_req': perun_req
                    })

    return data


def get_number_of_requests(data):
    config_data = {}

    for entry in data:
        config = entry['config']
        if config not in config_data:
            config_data[config] = {'ipfs_req': entry['ipfs_req'], "perun_req": entry['perun_req'], 'rounds_clients': ''}

    for config, values in config_data.items():
        rounds_clients = tuple(map(int, [s.split('=')[1] for s in config.split(',') if 'ROUNDS' in s or 'NUM_CLIENTS' in s]))

        config_data[config]['rounds_clients'] = rounds_clients
        config_data[config]['ipfs_req'] = values["ipfs_req"]
        config_data[config]['perun_req'] = values["perun_req"]

    labels = ['({}, {})'.format(*values['rounds_clients']) for values in config_data.values()]
    ipfs_req = [values['ipfs_req'] for values in config_data.values()]
    perun_req = [values['perun_req'] for values in config_data.values()]


    return labels, ipfs_req, perun_req



def get_mean_time(data, event):
    config_data = {}
    for entry in data:
        if event in entry['event_type']:
            config = entry['config']
            time_seconds = entry['time_seconds']

            if config not in config_data:
                config_data[config] = {'times': [], 'rounds_clients': ''}

            config_data[config]['times'].append(time_seconds)

    for config, values in config_data.items():
        rounds_clients = tuple(map(int, [s.split('=')[1] for s in config.split(',') if 'ROUNDS' in s or 'NUM_CLIENTS' in s]))
        mean_time = np.mean(values['times'])

        config_data[config]['rounds_clients'] = rounds_clients
        config_data[config]['mean_time'] = mean_time

    labels = ['({}, {})'.format(*values['rounds_clients']) for values in config_data.values()]
    mean_times = [values['mean_time'] for values in config_data.values()]


    return labels, mean_times

def plot_mean_time_diff(data_FL, data_BCFL, data_FLChan, event, title):

    labels, mean_times_FL = get_mean_time(data_FL, event)
    labels, mean_times_FLChan = get_mean_time(data_FLChan, event)
    labels, mean_times_BCFL = get_mean_time(data_BCFL, event)

    min_len = min(len(mean_times_FL), len(mean_times_FLChan), len(mean_times_BCFL))
    mean_times_FL = mean_times_FL[:min_len]
    mean_times_FLChan = mean_times_FLChan[:min_len]
    mean_times_BCFL = mean_times_BCFL[:min_len]
    labels = labels[:min_len]

    plt.figure(figsize=(12, 6))
    width = 0.25
    x = np.arange(len(labels))

    plt.bar(x - width, mean_times_BCFL, width, label='Mean Times BCFL', color='orange')
    plt.bar(x, mean_times_FLChan, width, label='Mean Times StateFL', color='blue')
    plt.bar(x + width, mean_times_FL, width, label='Mean Times FL', color='gray')

    plt.title(title)
    plt.xlabel('Configuration (NUM_CLIENTS, ROUNDS)')
    plt.ylabel('Mean Time (seconds)')
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.legend()
    plt.savefig(plot_path + title + '.png')
    # plt.show()


def plot_channel_time(data, title):

    labels, opening_times = get_mean_time(data, "opening channels")
    labels, settling_times = get_mean_time(data, "settling channels")

    plt.figure(figsize=(12, 6))
    width = 0.35
    x = np.arange(len(labels))
    plt.bar(x - width/2, opening_times, width, label='Open channel', color='orange')
    plt.bar(x + width/2, settling_times, width, label='Settle channel', color='blue')
    plt.title(title)
    plt.xlabel('(ROUNDS, NUM_CLIENTS)')
    plt.ylabel('Time (seconds)')
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.legend()
    plt.savefig(plot_path + title + '.png')
    # plt.show()

def plot_number_of_requests(data, event, title):

    requests = None
    labels, ipfs_req, perun_req = get_number_of_requests(data)
    if event == 'ipfs':
        requests = ipfs_req
    elif event == 'perun':
        requests = perun_req

    plt.figure(figsize=(12, 6))
    width = 0.35
    x = np.arange(len(labels))

    plt.figure(figsize=(12, 6))
    plt.bar(range(len(labels)), requests, tick_label=labels, color='blue')
    plt.title(title)
    plt.xlabel('(ROUNDS, NUM_CLIENTS)')
    plt.ylabel('# requests')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(plot_path + title + '.png')
    # plt.show()


log_data_FL = parse_log("logs/res_plot/results_FL.txt")
log_data_FLChan = parse_log("logs/res_plot/results_chanFL.txt")
log_data_BCFL = parse_log("logs/res_plot/results_BCFL.txt")

plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_FLChan, "Training", 'Mean Client Training Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_FLChan, "Aggregating", 'Mean Aggregation Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_FLChan, "Round", 'Mean Round Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_FLChan, "FL", 'Federated Learning Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_FLChan, "Experiment", 'E2E Time: FL vs BCFL vs StateFL')

plot_number_of_requests(log_data_FLChan, "ipfs", 'IPFS Requests')
plot_number_of_requests(log_data_FLChan, "perun", 'Perun Requests')



plot_channel_time(log_data_FLChan, 'Time to Handle Channel Opening and Closing')
