from typing import List, Tuple

import flwr as fl
from flwr.common import Metrics
import pickle
import numpy as np
import uuid
import ipfshttpclient
from model import Net, NUM_CLIENTS

# ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

# Define metric aggregation function
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


class CustomFedAvg(fl.server.strategy.FedAvg):
    def aggregate_fit(self, rnd, results, failures):
        aggregated_params = super().aggregate_fit(rnd, results, failures)

        # Save the aggregated parameters to a file
        with open(f'storage/aggregated_model_{uuid.uuid4()}.pkl', 'wb') as f:
            pickle.dump(aggregated_params, f)

        return aggregated_params

    def aggregate_evaluate(self, rnd, results, failures):
        aggregated_loss, aggregated_accuracy = super().aggregate_evaluate(rnd, results, failures)
        print(f"Round: {rnd}, Aggregated accuracy: {aggregated_accuracy}, Aggregated loss: {aggregated_loss}")
        return aggregated_loss, aggregated_accuracy



# Define strategy
strategy = CustomFedAvg(evaluate_metrics_aggregation_fn=weighted_average, min_available_clients=NUM_CLIENTS, min_fit_clients=NUM_CLIENTS)


# initial_model_params = model.get_weights()

# # Save the initial model parameters
# with open('initial_model.npy', 'wb') as f:
#     np.save(f, strategy.get_model_params())


# Get the model
model = Net()
# # Get the initial model parameters
# initial_model_params = model.get_weights()
file_name = f'storage/init_model_{uuid.uuid4()}.pkl'
with open(file_name, 'wb') as f:
    pickle.dump(model.state_dict(), f)

# res = ipfs_client.add(file_name)
# print('IPFS file hash:', res['Hash'])

# Start Flower server
fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=1),
    strategy=strategy,
)
