import matplotlib.pyplot as plt

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

def plot_data(data):
    for config in set(entry['config'] for entry in data):
        config_data = [entry for entry in data if entry['config'] == config]
        event_types = [entry['event_type'] for entry in config_data]
        time_seconds = [entry['time_seconds'] for entry in config_data]

        plt.figure(figsize=(10, 5))
        plt.bar(event_types, time_seconds, label='Time (seconds)')
        plt.title(f'Config: {config}')
        plt.xlabel('Event Type')
        plt.ylabel('Time (seconds)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


log_file_path = "results.txt"
log_data = parse_log(log_file_path)
plot_data(log_data)
