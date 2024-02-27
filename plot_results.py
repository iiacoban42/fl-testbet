import matplotlib.pyplot as plt
import numpy as np

def parse_log(file_path):
    data = []
    current_config = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            if line.startswith('Config'):
                current_config = line
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
                        'event_type': event_type
                    })

    return data


def get_mean_time(data, event):
    config_data = {}
    for entry in data:
        if event in entry['event_type'].lower():
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


def plot_mean_time_diff(data_FL, data_FLChan, event, title):

    labels, mean_times_FL = get_mean_time(data_FL, event)
    labels, mean_times_FLChan = get_mean_time(data_FLChan, event)

    plt.figure(figsize=(12, 6))
    width = 0.35
    x = np.arange(len(labels))

    plt.bar(x - width/2, mean_times_FL, width, label='Mean Times FL', color='blue')
    plt.bar(x + width/2, mean_times_FLChan, width, label='Mean Times FLChan', color='orange')

    plt.title(title)
    plt.xlabel('Configuration (NUM_CLIENTS, ROUNDS)')
    plt.ylabel('Mean Time (seconds)')
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.legend()
    plt.savefig(title + '.png')
    plt.show()


def plot_mean_time(data, event, title):

    labels, mean_times = get_mean_time(data, event)

    plt.figure(figsize=(12, 6))
    width = 0.35
    x = np.arange(len(labels))

    plt.figure(figsize=(12, 6))
    plt.bar(range(len(labels)), mean_times, tick_label=labels, color='blue')
    plt.title(title)
    plt.xlabel('(ROUNDS, NUM_CLIENTS)')
    plt.ylabel('Mean Time (seconds)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(title + '.png')
    plt.show()


log_data_FL = parse_log("results_FL.txt")
log_data_FLChan = parse_log("results_chanFL.txt")

plot_mean_time_diff(log_data_FL, log_data_FLChan, "training", 'Mean Training Time FL vs FLChan')
plot_mean_time_diff(log_data_FL, log_data_FLChan, "round", 'Mean Round Time FL vs FLChan')
plot_mean_time_diff(log_data_FL, log_data_FLChan, "experiment", 'Mean E2E Time FL vs FLChan')

plot_mean_time(log_data_FLChan, "opening channels", 'Mean Time to Open Channels')
plot_mean_time(log_data_FLChan, "settling channels", 'Mean Time to Settle Channels')
