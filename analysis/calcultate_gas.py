import os
import re
import numpy as np
import pandas as pd
from natsort import index_natsorted
import matplotlib.pyplot as plt

def calculate_cumulative_gas_usage(directory):
    data = []

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        total_gas_usage = 0
        transaction_count = 0

        # Open each file
        with open(os.path.join(directory, filename), 'r') as file:
            # Read the file content
            content = file.read()

            # Find all gas usage values using regex
            gas_usages = re.findall(r'Gas usage: (\d+)', content)

            # Convert the gas usage values to integers and add them to the total
            total_gas_usage += sum(int(gas_usage) for gas_usage in gas_usages)

            # Count the number of transactions
            transaction_count = len(re.findall(r'Transaction:', content))

        # Remove the file extension from the filename
        filename_without_extension = os.path.splitext(filename)[0]

        # Append the filename without extension, total gas usage, and transaction count to the data list
        data.append([filename_without_extension, total_gas_usage, transaction_count])


    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=['#R', 'Total Gas Usage', 'TX Count'])
    # Sort the DataFrame by the 'Transaction Count' column
    df = df.sort_values(by='#R', key=lambda x: np.argsort(index_natsorted(df['Total Gas Usage'])))

    # Convert the 'Total Gas Usage' column from WEI to GWEI
    df['Total Gas Usage'] = df['Total Gas Usage'].div(1000000000)

    return df

directory = 'analysis/ganache_logs'
df = calculate_cumulative_gas_usage(directory)

# Save the DataFrame to a LaTeX table
with open('analysis/stats_table/gas_usage_table.tex', 'w') as f:
    f.write(df.to_latex(index=False))

    df = df.loc[df['#R'] != "no disputes"]

    # Plot the total gas usage
    plt.figure(figsize=(10, 6))
    plt.plot(df['#R'], df['Total Gas Usage'], marker='o')
    plt.title('Total Gas Usage with Disputes')
    plt.xlabel('Number of Rounds')
    plt.ylabel('Gas Usage (Gwei)')
    # plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('analysis/plots/gas_usage_plot.png')


