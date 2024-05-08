import matplotlib.pyplot as plt
import numpy as np

plot_path = "analysis/plots/"

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
                if len(parts) > 1:
                    time_str = parts[0].strip().split(':')[1].strip()
                    event_type = parts[1].strip()
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



def get_cumulative_time(data, event):
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
        cumulative_time = np.sum(values['times'])

        config_data[config]['rounds_clients'] = rounds_clients
        config_data[config]['cumulative_time'] = cumulative_time

    labels = ['({}, {})'.format(*values['rounds_clients']) for values in config_data.values()]
    cumulative = [values['cumulative_time'] for values in config_data.values()]

    return labels, cumulative


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


def plot_stacked_bar(data, title, channel=False):

    labels, aggr_time = get_cumulative_time(data, "Aggregating")
    labels, round_time = get_cumulative_time(data, "Round")

    training_time = np.subtract(round_time, aggr_time).tolist()

    if channel:
        labels, opening_times = get_mean_time(data, "opening channels")
        labels, settling_times = get_mean_time(data, "settling channels")


    plt.figure(figsize=(16, 8))
    # create a stacked bar plot to show the time spent on training and aggregation and settling channels
    if channel:
        opening_and_training = np.add(opening_times, training_time).tolist()
        total_times = np.add(opening_and_training, aggr_time).tolist()

        plt.bar(labels, opening_times, tick_label=labels, color='green', label='Opening Channel')
        plt.bar(labels, training_time, tick_label=labels, color='blue', label='Training', bottom=opening_times)
        plt.bar(labels, aggr_time, tick_label=labels, color='orange', label='Aggregating', bottom=opening_and_training)
        plt.bar(labels, settling_times, tick_label=labels, color='red', label='Settling Channel', bottom=total_times)

    else:
        plt.bar(labels, training_time, tick_label=labels, color='blue', label='Training')
        plt.bar(labels, aggr_time, tick_label=labels, color='orange', label='Aggregating', bottom=training_time)


    plt.title(title)
    plt.xlabel('(ROUNDS, NUM_CLIENTS)')
    plt.ylabel('Time (seconds)')
    # plt.xticks(x, labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.legend()
    plt.savefig(plot_path + title + '.png')
    # plt.show()



def plot_mean_time_diff(data_FL, data_BCFL, data_StateFL, event, title):

    if event == 'Experiment':
        labels, mean_times_FL = get_mean_time(data_FL, "FL")
        labels, mean_times_StateFL_fl_time = get_mean_time(data_StateFL, "FL")
        labels, opening_times = get_mean_time(data_StateFL, "opening channels")
        labels, settling_times = get_mean_time(data_StateFL, "settling channels")
        channel_times = np.add(opening_times, settling_times).tolist()
        mean_times_StateFL = np.add(mean_times_StateFL_fl_time, channel_times).tolist()

        labels, mean_times_BCFL = get_mean_time(data_BCFL, 'FL')

    else:

        labels, mean_times_FL = get_mean_time(data_FL, event)
        labels, mean_times_StateFL = get_mean_time(data_StateFL, event)
        labels, mean_times_BCFL = get_mean_time(data_BCFL, event)

    min_len = min(len(mean_times_FL), len(mean_times_StateFL), len(mean_times_BCFL))
    mean_times_FL = mean_times_FL[:min_len]
    mean_times_StateFL = mean_times_StateFL[:min_len]
    mean_times_BCFL = mean_times_BCFL[:min_len]
    labels = labels[:min_len]

    plt.figure(figsize=(16, 8))
    width = 0.25
    x = np.arange(len(labels))

    plt.bar(x - width, mean_times_BCFL, width, label='Mean Times BCFL', color='orange')
    plt.bar(x, mean_times_StateFL, width, label='Mean Times StateFL', color='blue')
    plt.bar(x + width, mean_times_FL, width, label='Mean Times FL', color='gray')

    plt.title(title)
    plt.xlabel('Configuration (NUM_CLIENTS, ROUNDS)')
    plt.ylabel('Mean Time (seconds)')
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.legend()
    plt.savefig(plot_path + title + '.png')
    # plt.show()


def plot_cumulative_time_diff(data_FL, data_BCFL, data_StateFL, event, title):


    labels, times_FL = get_cumulative_time(data_FL, event)
    labels, times_StateFL = get_cumulative_time(data_StateFL, event)
    labels, times_BCFL = get_cumulative_time(data_BCFL, event)

    min_len = min(len(times_FL), len(times_StateFL), len(times_BCFL))
    times_FL = times_FL[:min_len]
    times_StateFL = times_StateFL[:min_len]
    times_BCFL = times_BCFL[:min_len]
    labels = labels[:min_len]

    plt.figure(figsize=(16, 8))
    width = 0.25
    x = np.arange(len(labels))

    plt.bar(x - width, times_BCFL, width, label='Cumulative Times BCFL', color='orange')
    plt.bar(x, times_StateFL, width, label='Cumulative Times StateFL', color='blue')
    plt.bar(x + width, times_FL, width, label='Cumulative Times FL', color='gray')

    plt.title(title)
    plt.xlabel('Configuration (NUM_CLIENTS, ROUNDS)')
    plt.ylabel('Cumulative Time (seconds)')
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


log_data_FL = parse_log("analysis/results/results_FL.txt")
log_data_StateFL = parse_log("analysis/results/results_StateFL.txt")
log_data_BCFL = parse_log("analysis/results/results_BCFL.txt")

plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Training", 'Mean Client Training Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Aggregating", 'Mean Aggregation Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Round", 'Mean Round Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "FL", 'Federated Learning Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Experiment", 'E2E Time: FL vs BCFL vs StateFL')

plot_cumulative_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Round", 'Cumulative Round Time: FL vs BCFL vs StateFL')
plot_cumulative_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Aggregating", 'Cumulative Aggregation Time: FL vs BCFL vs StateFL')
plot_cumulative_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Training", 'Cumulative training Time: FL vs BCFL vs StateFL')


plot_number_of_requests(log_data_StateFL, "ipfs", 'IPFS Requests')
plot_number_of_requests(log_data_StateFL, "perun", 'Perun Requests')



plot_channel_time(log_data_StateFL, 'Time to Handle Channel Opening and Closing')


plot_stacked_bar(log_data_StateFL, 'StateFL Events', channel=True)
plot_stacked_bar(log_data_FL, 'FL Events', channel=False)
plot_stacked_bar(log_data_BCFL, 'BCFL Events', channel=False)
