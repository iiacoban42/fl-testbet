import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
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

    return np.array(sampled_data)


with_channel_setup = True

channel_opening_data = read_json('analysis/channel_latency/channel_opening.json')
channel_closure_data = read_json('analysis/channel_latency/channel_closure.json')
mean_channel_opening = np.array(get_mean_latency(channel_opening_data))
mean_channel_closure = np.array(get_mean_latency(channel_closure_data))

bc_data = read_json('analysis/channel_latency/bc.json')

no_disputes_data = read_json('analysis/channel_latency/disputes_0.json')
no_disputes_data = convert_to_seconds(no_disputes_data)

disputes_data = read_json('analysis/channel_latency/disputes_100.json')
disputes_data = convert_to_seconds(disputes_data)

bc_data = np.array(get_mean_latency(bc_data))
mean_no_disputes = np.array(get_mean_latency(no_disputes_data))
mean_disputes = np.array(get_mean_latency(disputes_data))

disputes_sample_25 = sample_data(disputes_data, no_disputes_data, 4, 6)
disputes_sample_50 = sample_data(disputes_data, no_disputes_data, 5, 5)
disputes_sample_75 = sample_data(disputes_data, no_disputes_data, 6, 4)

number_of_rounds = np.arange(1, 11).reshape((-1, 1))


model_bc = LinearRegression().fit(number_of_rounds, bc_data)
model_disputes = LinearRegression().fit(number_of_rounds, mean_disputes)
model_no_disputes = LinearRegression().fit(number_of_rounds, mean_no_disputes)

model_25_disputes = LinearRegression().fit(number_of_rounds, disputes_sample_25)
model_50_disputes = LinearRegression().fit(number_of_rounds, disputes_sample_50)
model_75_disputes = LinearRegression().fit(number_of_rounds, disputes_sample_75)

# Predict using the models
predicted_bc = model_bc.predict(number_of_rounds)
predicted_no_disputes = model_no_disputes.predict(number_of_rounds)
predicted_disputes = model_disputes.predict(number_of_rounds)
predicted_disputes_25 = model_25_disputes.predict(number_of_rounds)
predicted_disputes_50 = model_50_disputes.predict(number_of_rounds)
predicted_disputes_75 = model_75_disputes.predict(number_of_rounds)

plt.figure(figsize=(12, 6))

plt.plot(number_of_rounds[:10], predicted_bc[:10], label='Blockchain', color='black')
plt.plot(number_of_rounds[:10], predicted_no_disputes[:10], label='No disputes', color='blue')
plt.plot(number_of_rounds[:10], predicted_disputes_25[:10], label='State channels with 25% disputes', color='green')
plt.plot(number_of_rounds[:10], predicted_disputes_50[:10], label='State channels with 50% disputes', color='red')
plt.plot(number_of_rounds[:10], predicted_disputes_75[:10], label='State channels with 75% disputes', color='purple')
plt.plot(number_of_rounds[:10], predicted_disputes[:10], label='State channels with 100% disputes', color='orange')
plt.legend()

plt.xlabel('Number of Rounds')
plt.ylabel('Run Time (s)')

plt.title("Incentive Method Interaction Time")
plt.savefig(plot_path + "Channel Interaction Time" + '.png', bbox_inches='tight')


# create figure and axis objects with subplots()
fig, axs = plt.subplots(2, 1, figsize=(12, 16))


# Plot the predicted values until x=10
axs[0].plot(number_of_rounds[:10], predicted_bc[:10], label='Blockchain', color='black')
axs[0].plot(number_of_rounds[:10], predicted_no_disputes[:10], label='No disputes', color='blue')
axs[0].plot(number_of_rounds[:10], predicted_disputes_25[:10], label='State channels with 25% disputes', color='green')
axs[0].plot(number_of_rounds[:10], predicted_disputes_50[:10], label='State channels with 50% disputes', color='red')
axs[0].plot(number_of_rounds[:10], predicted_disputes_75[:10], label='State channels with 75% disputes', color='purple')
axs[0].plot(number_of_rounds[:10], predicted_disputes[:10], label='State channels with 100% disputes', color='orange')
axs[0].legend()

axs[0].set_xlabel('Number of Rounds')
axs[0].set_ylabel('Run Time (s)')

axs[0].set_title("Incentive Method Interaction Time")



mean_no_disputes = np.add(mean_no_disputes, mean_channel_opening)
mean_no_disputes = np.add(mean_no_disputes, mean_channel_closure)

mean_disputes = np.add(mean_disputes, mean_channel_opening)
mean_disputes = np.add(mean_disputes, mean_channel_closure)

disputes_sample_25 = np.add(disputes_sample_25, mean_channel_opening)
disputes_sample_25 = np.add(disputes_sample_25, mean_channel_closure)

disputes_sample_50 = np.add(disputes_sample_50, mean_channel_opening)
disputes_sample_50 = np.add(disputes_sample_50, mean_channel_closure)

disputes_sample_75 = np.add(disputes_sample_75, mean_channel_opening)
disputes_sample_75 = np.add(disputes_sample_75, mean_channel_closure)


model_bc = LinearRegression().fit(number_of_rounds, bc_data)
model_disputes = LinearRegression().fit(number_of_rounds, mean_disputes)
model_no_disputes = LinearRegression().fit(number_of_rounds, mean_no_disputes)

model_25_disputes = LinearRegression().fit(number_of_rounds, disputes_sample_25)
model_50_disputes = LinearRegression().fit(number_of_rounds, disputes_sample_50)
model_75_disputes = LinearRegression().fit(number_of_rounds, disputes_sample_75)

# Predict using the models
predicted_bc = model_bc.predict(number_of_rounds)
predicted_no_disputes = model_no_disputes.predict(number_of_rounds)
predicted_disputes = model_disputes.predict(number_of_rounds)
predicted_disputes_25 = model_25_disputes.predict(number_of_rounds)
predicted_disputes_50 = model_50_disputes.predict(number_of_rounds)
predicted_disputes_75 = model_75_disputes.predict(number_of_rounds)


# Plot the predicted values until x=10
axs[1].plot(number_of_rounds[:10], predicted_bc[:10], label='Blockchain', color='black')
axs[1].plot(number_of_rounds[:10], predicted_no_disputes[:10], label='No disputes', color='blue')
axs[1].plot(number_of_rounds[:10], predicted_disputes_25[:10], label='State channels with 25% disputes', color='green')
axs[1].plot(number_of_rounds[:10], predicted_disputes_50[:10], label='State channels with 50% disputes', color='red')
axs[1].plot(number_of_rounds[:10], predicted_disputes_75[:10], label='State channels with 75% disputes', color='purple')
axs[1].plot(number_of_rounds[:10], predicted_disputes[:10], label='State channels with 100% disputes', color='orange')
axs[1].legend()

axs[1].set_xlabel('Number of Rounds')
axs[1].set_ylabel('Run Time (s)')


axs[1].set_title("Incentive Method Interaction Time with Channel Setup")


plt.savefig(plot_path + "Channel Interaction Time joint plot" + '.png', bbox_inches='tight')


plt.figure(figsize=(12, 6))

plt.plot(number_of_rounds[:10], predicted_bc[:10], label='Blockchain', color='black')
plt.plot(number_of_rounds[:10], predicted_no_disputes[:10], label='No disputes', color='blue')
plt.plot(number_of_rounds[:10], predicted_disputes_25[:10], label='State channels with 25% disputes', color='green')
plt.plot(number_of_rounds[:10], predicted_disputes_50[:10], label='State channels with 50% disputes', color='red')
plt.plot(number_of_rounds[:10], predicted_disputes_75[:10], label='State channels with 75% disputes', color='purple')
plt.plot(number_of_rounds[:10], predicted_disputes[:10], label='State channels with 100% disputes', color='orange')
plt.legend()

plt.xlabel('Number of Rounds')
plt.ylabel('Run Time (s)')

plt.title("Incentive Method Interaction Time")
plt.savefig(plot_path + "Channel Interaction Time with Channel Opening and Closing" + '.png', bbox_inches='tight')
