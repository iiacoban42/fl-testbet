from flwr.common import Metrics
from model import Net, NUM_CLIENTS, NUM_ROUNDS, IPFS_ON, INCENTIVES_ON
from con import send_command
from typing import List, Tuple
from logging import INFO, DEBUG
from flwr.common.logger import log

import flwr as fl
import pickle
import uuid
import ipfshttpclient

fl.common.logger.configure(identifier="FL-experiment", filename="fllog.log")


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
        log(INFO, "Start Round=1")

        self.ipfs_hash = ipfs_model_hash
        self.perun_node_host = perun_node_host
        self.perun_node_port = perun_node_port

        if INCENTIVES_ON:
            log(INFO, "Start sharing model with perun nodes")
            for i in range(NUM_CLIENTS):
                request = f"set,peer_{i},1,{NUM_ROUNDS},0,0,0"
                log(INFO, "PERUN REQUEST: Sharing model with peer_%s, REQ=%s", i, request)
                # send_command(self.perun_node_host, self.perun_node_port, f"open,peer_{i},10,10".encode(), "server")
                send_command(self.perun_node_host, self.perun_node_port, request.encode(), "server")
            log(INFO, "Done sharing model with perun nodes")


    def aggregate_fit(self, rnd, results, failures):
        log(INFO, "Start Aggregating round=%s", rnd)
        aggregated_params = super().aggregate_fit(rnd, results, failures)

        # aggregated_loss, aggregated_accuracy = super().aggregate_evaluate(rnd, results, failures)
        # Save the aggregated parameters to a file
        if IPFS_ON:
            log(INFO, "Start saving aggregated model to storage (round=%s)", rnd)
        file_path = f'storage/aggregated_model_{uuid.uuid4()}.pkl'
        with open(file_path, 'wb') as f:
            pickle.dump(aggregated_params, f)

        self.ipfs_hash = file_path

        if IPFS_ON:
            res = ipfs_client.add(file_path)
            log(DEBUG, "File: %s IPFS file hash: %s", file_path, res['Hash'])

            self.ipfs_hash = res['Hash']
            log(INFO, "Done saving aggregated model to storage (round=%s)", rnd)

        # print(f"Round: {rnd}, Aggregated accuracy: {aggregated_accuracy}, Aggregated loss: {aggregated_loss}")

        return aggregated_params

    def aggregate_evaluate(self, rnd, results, failures):
        log(INFO, "Start evaluating fit round=%s", rnd)
        aggregated_loss, aggregated_accuracy = super().aggregate_evaluate(rnd, results, failures)
        log(INFO, "Done Evaluating fit round=%s", rnd)
        log(DEBUG, "Round: %s, Aggregated accuracy: %s, Aggregated loss: %s, IPFS hash: %s", rnd, aggregated_accuracy, aggregated_loss, self.ipfs_hash)

        if INCENTIVES_ON:
            log(INFO, "Start sending aggregated model to perun nodes round=%s", rnd)
            for i in range(NUM_CLIENTS):
                request = f"set,peer_{i},1,{NUM_ROUNDS},0,{int(aggregated_accuracy['accuracy'])},{int((100 - aggregated_accuracy['accuracy']))}"
                log(INFO, "PERUN REQUEST: Setting model with peer_%s, REQ=%s", i, request)

                send_command(self.perun_node_host,
                            self.perun_node_port,
                            request.encode(),
                            "server")

            log(INFO, "Done sending aggregated model to perun nodes round=%s", rnd)

        log(INFO, "Done Aggregating round=%s", rnd)
        log(INFO, "Done Round=%s", rnd)
        if rnd < NUM_ROUNDS:
            log(INFO, "Start Round=%s", rnd+1)
        return aggregated_loss, aggregated_accuracy


# Get the model
model = Net()
file_name = f'storage/init_model_{uuid.uuid4()}.pkl'
with open(file_name, 'wb') as f:
    pickle.dump(model.state_dict(), f)

init_model_hash = ""
if IPFS_ON:
    init_model_hash = ipfs_client.add(file_name)['Hash']
    log(DEBUG, "File: %s IPFS file hash: %s", file_name, init_model_hash)


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
    config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
    strategy=strategy,
)
