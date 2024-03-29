from datetime import datetime
import os
from natsort import natsorted
import re

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

def get_stats(path, output_path=None):

    # open output file in append mode and write the results to it
    res = ""

    for file in natsorted(os.listdir(path)):
        if file.endswith(".log"):
            log_file_path = path + file
            timestamps, ipfs_rec, perun_reg = parse_log_file(log_file_path)

            for i, (timestamp, log_text) in enumerate(timestamps):
                if log_text.startswith("Config"):
                    res += log_text + "\n"
                    res += f"NET | IPFS Requests: {ipfs_rec} | PERUN Requests: {perun_reg}\n"

                    print(log_text)

                if log_text.startswith("FL finished"):
                    match = re.search(r'\d+\.\d+', log_text)
                    if match:
                        fl_time = float(match.group())
                        line = f"{timestamp} | time: {fl_time} seconds| {log_text}".replace("\n", "")
                        res += line + "\n"
                        print(line)

                if log_text.startswith("Start"):
                    match_str = log_text.split(" ")
                    for timestamp_second, log_text_second in timestamps[i+1:]:  # timestamps[i+1:] is the list of logs after the current log
                        if log_text_second.startswith("Done") and log_text_second.split(" ")[1:] == match_str[1:]:
                            elapsed_time = calculate_elapsed_time(timestamp, timestamp_second)
                            line = f"{timestamp} | time: {elapsed_time} seconds | {log_text.replace('Start ', '')}".replace("\n", "")
                            res += line + "\n"
                            print(line)
                            break
            res += "\n"
            print("\n")

    if output_path:
        with open(output_path, 'a') as file:
            file.write(res)

get_stats("logs/logs_fl/", "logs/results_FL.txt")
get_stats("logs/logs_flchan/", "logs/results_chanFL.txt")
get_stats("logs/logs_bcfl/", "logs/results_BCFL.txt")
