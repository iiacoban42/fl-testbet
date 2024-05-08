import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import math
from sklearn.linear_model import LinearRegression

plot_path = 'analysis/plots/'

plt.rcParams.update({'font.size': 16})

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.loads(file.read())

# Function to convert time string to seconds
def parse_time(time_str):

    match = re.compile(r'(?:(\d+)m)?(\d+\.\d+)s').match(time_str)
    if match:
        minutes = int(match.group(1) or 0)
        seconds = float(match.group(2))
        return minutes * 60 + seconds

    match = re.compile(r'(\d+\.\d+)(ms|s)').match(time_str)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        if unit == 's':
            return value
        elif unit == 'ms':
            return value / 1000  # Convert milliseconds to seconds
    return None


def convert_to_seconds(json_data):
    experiment_data = {}
    # Accessing the values
    for key, value in json_data.items():
        if key not in experiment_data:
            experiment_data[key] = []
        experiment_data[key] = [parse_time(num) for num in value]

    return experiment_data


def get_mean_latency(json_data):
    experiment_data = []
    # Accessing the values
    for _, value in json_data.items():
        experiment_data.append([float(num) for num in value])

    df = pd.DataFrame(experiment_data, columns=[str(i) for i in range(1, 11)])

    # calculate mean per column
    mean = df.mean().to_list()
    return mean


def sample_data(data_disputes, data_no_disputes, num_samples_disputes, num_samples_no_disputes):
    sampled_data = []

    for r in range(1, 11):
        # Sample indices for sampling
        sample_indices_disputes = np.random.choice(10, size=num_samples_disputes, replace=False)
        sample_indices_no_disputes = np.random.choice(10, size=num_samples_no_disputes, replace=False)

        # Create a new array to store sampled x and y values
        current_number_of_rounds = []
        for i in sample_indices_disputes:
            # Store sampled values from the first array
            current_number_of_rounds.append(data_disputes[str(i+1)][r-1])

        for i in sample_indices_no_disputes:
            # Store sampled values from the second array
            current_number_of_rounds.append(data_no_disputes[str(i+1)][r-1])


        sampled_data.append(np.mean(current_number_of_rounds))

    return sampled_data



no_disputes_data = read_json('analysis/channel_latency/disputes_0.json')
no_disputes_data = convert_to_seconds(no_disputes_data)


disputes_data = read_json('analysis/channel_latency/disputes_100.json')
disputes_data = convert_to_seconds(disputes_data)

mean_no_disputes = np.array(get_mean_latency(no_disputes_data))
mean_disputes = np.array(get_mean_latency(disputes_data))

number_of_rounds = np.arange(1, 11).reshape((-1, 1))

model_disputes = LinearRegression().fit(number_of_rounds, mean_disputes)
model_no_disputes = LinearRegression().fit(number_of_rounds, mean_no_disputes)

model_25_disputes = LinearRegression().fit(number_of_rounds, sample_data(disputes_data, no_disputes_data, 4, 6,))
model_50_disputes = LinearRegression().fit(number_of_rounds, sample_data(disputes_data, no_disputes_data, 5, 5))
model_75_disputes = LinearRegression().fit(number_of_rounds, sample_data(disputes_data, no_disputes_data, 6, 4))

# Predict using the models
predicted_no_disputes = model_no_disputes.predict(number_of_rounds)
predicted_disputes = model_disputes.predict(number_of_rounds)
predicted_disputes_25 = model_25_disputes.predict(number_of_rounds)
predicted_disputes_50 = model_50_disputes.predict(number_of_rounds)
predicted_disputes_75 = model_75_disputes.predict(number_of_rounds)

plt.figure(figsize=(12, 6))

# Plot the predicted values
plt.plot(predicted_no_disputes, label='No disputes', color='blue')
plt.plot(predicted_disputes, label='With 100% disputes', color='orange')
plt.plot(predicted_disputes_25, label='With 25% disputes', color='green')
plt.plot(predicted_disputes_50, label='With 50% disputes', color='red')
plt.plot(predicted_disputes_75, label='With 75% disputes', color='purple')

plt.xlabel('Number of Rounds')
plt.ylabel('Channel Latency (s)')
plt.tight_layout()

plt.title("Mean Channel Interaction Time")
plt.legend()
plt.savefig(plot_path + "Channel Interaction Time" + '.png')