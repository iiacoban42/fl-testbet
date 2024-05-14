from datetime import datetime
import os
import re
import numpy as np
from pathlib import Path

def parse_log_file(log_file_path):
    logs = []
    print_config = False

    ipfs_req = 0
    perun_req = 0

    with open(log_file_path, 'r') as file:
        for line in file:
            # print(line)
            tokenized_line = line.split(' | ')

            if not print_config:
                print(tokenized_line[3].replace("\n", ""))
                logs.append(("Config", tokenized_line[3].replace("\n", "")))
                print_config = True

            timestamp = tokenized_line[1].split(" ")[2] + " " + tokenized_line[1].split(" ")[3]
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
            log_text = tokenized_line[3]
            if log_text.startswith("Start") or log_text.startswith("Done") or log_text.startswith("FL finished"):
                logs.append((timestamp, log_text))

            if log_text.startswith("File"):
                ipfs_req += 1

            if log_text.startswith("PERUN REQUEST"):
                perun_req += 1

    return logs, ipfs_req, perun_req


def calculate_elapsed_time(start_time, end_time):
    if start_time and end_time:
        elapsed_time = end_time - start_time
        return elapsed_time.total_seconds()
    else:
        return None


# loop through the logs and find the start and done logs with the same parameters
# then calculate the time between the start and done logs
# and print the time and the parameters


def dump_mean_timing(logs_per_config, output_path):

    for config, events in logs_per_config.items():
        res = f"{config}\n"
        for event, timings in events.items():
            mean_time = np.mean(timings)
            res += f"time: {mean_time} seconds | {event}\n"
        res += "\n"
        with open(output_path, 'a') as file:
            file.write(res)


def get_event_timing(path, output_path=None):

    # open output file in append mode and write the results to it
    logs_per_config = {}

#     lst = os.listdir(whatever_directory)
# lst.sort()

    for file in sorted(Path(path).iterdir(), key=os.path.getmtime):
        if file.suffix == ".log":
            timestamps, ipfs_rec, perun_reg = parse_log_file(file)

            current_config = ""

            for i, (timestamp, log_text) in enumerate(timestamps):
                if log_text.startswith("Config"):
                    current_config = log_text.replace("\n", "")
                    if current_config not in logs_per_config:
                        logs_per_config[current_config] = {}

                    # res += log_text + "\n"
                    # res += f"NET | IPFS Requests: {ipfs_rec} | PERUN Requests: {perun_reg}\n"

                    # print(log_text)

                if log_text.startswith("FL finished"):
                    match = re.search(r'\d+\.\d+', log_text)
                    if match:
                        fl_time = float(match.group())
                        event = "FL"
                        line = f"time: {fl_time} seconds | FL"
                        if event not in logs_per_config[current_config]:
                            logs_per_config[current_config][event] = []
                        logs_per_config[current_config][event].append(fl_time)

                        # res += line + "\n"
                        # print(line)

                if log_text.startswith("Start"):
                    match_str = log_text.split(" ")
                    for timestamp_second, log_text_second in timestamps[i+1:]:  # timestamps[i+1:] is the list of logs after the current log
                        if log_text_second.startswith("Done") and log_text_second.split(" ")[1:] == match_str[1:]:
                            elapsed_time = calculate_elapsed_time(timestamp, timestamp_second)
                            line = f"time: {elapsed_time} seconds | {log_text.replace('Start ', '')}".replace("\n", "")

                            event = log_text.replace('Start ', '').replace("\n", "")

                            if event not in logs_per_config[current_config]:
                                logs_per_config[current_config][event] = []
                            logs_per_config[current_config][event].append(elapsed_time)
                            break

                            # res += line + "\n"
                            # print(line)

            # res += "\n"
            # print("\n")

    if output_path is not None:
        dump_mean_timing(logs_per_config, output_path)
        with open("logs.txt", 'a') as file:
            file.write(str(logs_per_config))

    return logs_per_config

