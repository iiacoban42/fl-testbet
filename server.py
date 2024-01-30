from flwr.common import Metrics
from model import Net, NUM_CLIENTS, IPFS_ON
from typing import List, Tuple

import flwr as fl
import pickle
import uuid
import ipfshttpclient

ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

# Define metric aggregation function
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


class CustomFedAvg(fl.server.strategy.FedAvg):

    def __init__(self, evaluate_metrics_aggregation_fn, min_available_clients, min_fit_clients, ipfs_model_hash="" ):
        super().__init__(evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn, min_available_clients=min_available_clients, min_fit_clients=min_fit_clients)
        self.ipfs_hash = ipfs_model_hash

    def aggregate_fit(self, rnd, results, failures):
        aggregated_params = super().aggregate_fit(rnd, results, failures)
        # aggregated_loss, aggregated_accuracy = super().aggregate_evaluate(rnd, results, failures)
        # Save the aggregated parameters to a file
        file_path = f'storage/aggregated_model_{uuid.uuid4()}.pkl'
        with open(file_path, 'wb') as f:
            pickle.dump(aggregated_params, f)

        self.ipfs_hash = file_path

        if IPFS_ON:
            res = ipfs_client.add(file_path)
            print(f"File: {file_path} IPFS file hash: {res['Hash']}")

            self.ipfs_hash = res['Hash']

        # print(f"Round: {rnd}, Aggregated accuracy: {aggregated_accuracy}, Aggregated loss: {aggregated_loss}")

        return aggregated_params

    def aggregate_evaluate(self, rnd, results, failures):
        aggregated_loss, aggregated_accuracy = super().aggregate_evaluate(rnd, results, failures)
        print(f"Round: {rnd}, Aggregated accuracy: {aggregated_accuracy}, Aggregated loss: {aggregated_loss}, IPFS hash: {self.ipfs_hash}")
        return aggregated_loss, aggregated_accuracy


# Get the model
model = Net()
file_name = f'storage/init_model_{uuid.uuid4()}.pkl'
with open(file_name, 'wb') as f:
    pickle.dump(model.state_dict(), f)

if IPFS_ON:
    res = ipfs_client.add(file_name)
    print(f"File: {file_name} IPFS file hash: {res['Hash']}")


# Define strategy
strategy = CustomFedAvg(evaluate_metrics_aggregation_fn=weighted_average, min_available_clients=NUM_CLIENTS, min_fit_clients=NUM_CLIENTS)

# Start Flower server
fl.server.start_server(
    server_address="0.0.0.0:8000",
    config=fl.server.ServerConfig(num_rounds=1),
    strategy=strategy,
)
