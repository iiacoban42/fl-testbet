from typing import List, Tuple

import flwr as fl
from flwr.common import Metrics
import numpy as np

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
        with open('aggregated_model.npy', 'wb') as f:
            np.save(f, aggregated_params)

        return aggregated_params

# Define strategy
strategy = CustomFedAvg(evaluate_metrics_aggregation_fn=weighted_average, min_available_clients=2)


# initial_model_params = model.get_weights()

# # Save the initial model parameters
# with open('initial_model.npy', 'wb') as f:
#     np.save(f, strategy.get_model_params())


# Start Flower server
fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=3),
    strategy=strategy,
)
