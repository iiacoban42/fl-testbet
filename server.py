from flwr.common import Metrics
from model import Net, NUM_CLIENTS, NUM_ROUNDS, IPFS_ON, INCENTIVES_ON
from con import send_command
from typing import List, Tuple

import flwr as fl
import pickle
import uuid
import ipfshttpclient

ipfs_client = None
if IPFS_ON:
    ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

# Define metric aggregation function
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


class CustomFedAvg(fl.server.strategy.FedAvg):

    def __init__(self, evaluate_metrics_aggregation_fn, min_available_clients, min_fit_clients, ipfs_model_hash="", perun_node_host="", perun_node_port=""):
        super().__init__(evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn, min_available_clients=min_available_clients, min_fit_clients=min_fit_clients)
        self.ipfs_hash = ipfs_model_hash
        self.perun_node_host = perun_node_host
        self.perun_node_port = perun_node_port
        if INCENTIVES_ON:
            for i in range(NUM_CLIENTS):
                # send_command(self.perun_node_host, self.perun_node_port, f"open,peer_{i},10,10".encode(), "server")
                send_command(self.perun_node_host, self.perun_node_port, f"set,peer_{i},1,1,0,0,0".encode(), "server")


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
        if INCENTIVES_ON:
            for i in range(NUM_CLIENTS):
               send_command(self.perun_node_host,
                            self.perun_node_port,
                            f"set,peer_{i},1,{NUM_ROUNDS},0,{int(aggregated_accuracy['accuracy'])},{int((100 - aggregated_accuracy['accuracy']))}".encode(),
                            "server")
        return aggregated_loss, aggregated_accuracy


# Get the model
model = Net()
file_name = f'storage/init_model_{uuid.uuid4()}.pkl'
with open(file_name, 'wb') as f:
    pickle.dump(model.state_dict(), f)

init_model_hash = ""
if IPFS_ON:
    init_model_hash = ipfs_client.add(file_name)['Hash']
    print(f"File: {file_name} IPFS file hash: {init_model_hash}")


# Define strategy
strategy = CustomFedAvg(evaluate_metrics_aggregation_fn=weighted_average,
                        min_available_clients=NUM_CLIENTS,
                        min_fit_clients=NUM_CLIENTS,
                        ipfs_model_hash=init_model_hash,
                        perun_node_host="127.0.0.1",
                        perun_node_port=str(8080 + NUM_CLIENTS + 1),
                        )

# Start Flower server
fl.server.start_server(
    server_address="0.0.0.0:8000",
    config=fl.server.ServerConfig(num_rounds=1),
    strategy=strategy,
)
