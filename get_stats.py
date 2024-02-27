from datetime import datetime
import os

def parse_log_file(log_file_path):
    logs = []
    print_config = False
    with open(log_file_path, 'r') as file:
        for line in file:
            # print(line)
            tokenized_line = line.split(' | ')

            if not print_config:
                print(tokenized_line[3].replace("\n", ""))
                print_config = True

            timestamp = tokenized_line[1].split(" ")[2] + " " + tokenized_line[1].split(" ")[3]
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
            log_text = tokenized_line[3]
            if log_text.startswith("Start") or log_text.startswith("Done"):
                logs.append((timestamp, log_text))

    return logs

def calculate_elapsed_time(start_time, end_time):
    if start_time and end_time:
        elapsed_time = end_time - start_time
        return elapsed_time.total_seconds()
    else:
        return None


# loop through the logs and find the start and done logs with the same parameters
# then calculate the time between the start and done logs
# and print the time and the parameters
for file in os.listdir():
    if file.endswith(".log"):
        log_file_path = file
        timestamps = parse_log_file(log_file_path)

        for i, (timestamp, log_text) in enumerate(timestamps):
            if log_text.startswith("Start"):
                match_str = log_text.split(" ")
                for timestamp_second, log_text_second in timestamps[i+1:]:  # timestamps[i+1:] is the list of logs after the current log
                    if log_text_second.startswith("Done") and log_text_second.split(" ")[1:] == match_str[1:]:
                        elapsed_time = calculate_elapsed_time(timestamp, timestamp_second)
                        print(f"{timestamp} | time: {elapsed_time} seconds | {log_text.replace('Start ', '')}".replace("\n", ""))
                        break
        print("\n")
