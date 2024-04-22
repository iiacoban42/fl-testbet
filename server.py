from flwr.common import Metrics
from model import Net
from config import NUM_CLIENTS, NUM_ROUNDS, IPFS_ON, INCENTIVES_ON, SOLO_BLOCKCHAIN_ON
from main import LOG_FILE
from con import send_command, post_to_ipfs
from typing import List, Tuple
from logging import INFO, DEBUG
from flwr.common.logger import log
from fl_contract import deploy_contract, set_weight, set_aggregated_model, GANACHE_URL

import flwr as fl
import pickle
import uuid
from web3 import Web3
import json


web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

fl.common.logger.configure(identifier="FL-experiment", filename=LOG_FILE)


# Define metric aggregation function
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


class CustomFedAvg(fl.server.strategy.FedAvg):

    def __init__(self, evaluate_metrics_aggregation_fn, min_available_clients, min_fit_clients,
                 ipfs_model_hash="", perun_node_host="", perun_node_port="", secret_key="", account="", client_addresses=None):
        super().__init__(evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn, min_available_clients=min_available_clients, min_fit_clients=min_fit_clients)
        log(INFO, "Start Round=1")

        self.ipfs_hash = ipfs_model_hash
        self.perun_node_host = perun_node_host
        self.perun_node_port = perun_node_port
        self.secret_key = secret_key
        self.address = account
        self.client_addresses = client_addresses
        self.contracts = []

        if INCENTIVES_ON:
            log(INFO, "Start sharing model with perun nodes")
            for i in range(NUM_CLIENTS):
                request = f"set,peer_{i},{self.ipfs_hash},{NUM_ROUNDS},0,0,0"
                log(INFO, "PERUN REQUEST: Sharing model with peer_%s, REQ=%s", i, request)
                send_command(self.perun_node_host, self.perun_node_port, request.encode(), "server", NUM_CLIENTS)
            log(INFO, "Done sharing model with perun nodes")

        elif SOLO_BLOCKCHAIN_ON:
            log(INFO, "Start deploying contract")
            for i in range(NUM_CLIENTS):
                contract = deploy_contract(web3, self.ipfs_hash, NUM_ROUNDS, self.address, self.secret_key)
                self.contracts.append(contract)
            log(INFO, "Done deploying contract")


    def aggregate_fit(self, rnd, results, failures):
        log(INFO, "Start Aggregating round=%s", rnd)

        if SOLO_BLOCKCHAIN_ON:
            log(INFO, "Start setting weights to the blockchain")
            for i, (_, fit_res) in enumerate(sorted(results, key=lambda x: x[0].cid)):

                file_path = f'storage/updated_weights_{i}_{uuid.uuid4()}.pkl'
                with open(file_path, 'wb') as file:
                    pickle.dump(fit_res, file)

                res = post_to_ipfs(file_path, NUM_CLIENTS)
                log(DEBUG, "File: %s IPFS file hash: %s", file_name, res['Hash'])

                set_weight(web3, self.contracts[i][0], self.address, self.secret_key, self.client_addresses[i], res['Hash'])
            log(INFO, "Done setting weights to the blockchain")

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
            res = post_to_ipfs(file_path, NUM_CLIENTS)
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
                request = f"set,peer_{i},{self.ipfs_hash},{NUM_ROUNDS},0,{int(aggregated_accuracy['accuracy'])},{int((100 - aggregated_accuracy['accuracy']))}"
                log(INFO, "PERUN REQUEST: Setting model with peer_%s, REQ=%s", i, request)

                send_command(self.perun_node_host,
                            self.perun_node_port,
                            request.encode(),
                            "server",
                            NUM_CLIENTS,
                            )

            log(INFO, "Done sending aggregated model to perun nodes round=%s", rnd)

        elif SOLO_BLOCKCHAIN_ON:
            log(INFO, "Start setting aggregated model to the blockchain round=%s", rnd)
            for i, (_, _) in enumerate(sorted(results, key=lambda x: x[0].cid)):
                set_weight(web3, self.contracts[i][0], self.address, self.secret_key, self.client_addresses[i], self.ipfs_hash)
            log(INFO, "Done setting aggregated model to the blockchain round=%s", rnd)

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
    init_model_hash = post_to_ipfs(file_name, NUM_CLIENTS)['Hash']
    log(DEBUG, "File: %s IPFS file hash: %s", file_name, init_model_hash)



if SOLO_BLOCKCHAIN_ON:
    #  Read the keys and the addresses from the keys.json file
    with open('keys.json', 'r') as f:
        keys_data = json.load(f)

    keys = keys_data['private_keys']
    addresses = []

    server_key = ""
    for address, key in keys.items():
        addresses.append(web3.to_checksum_address(address))
        server_key = key
    # Define strategy
    strategy = CustomFedAvg(evaluate_metrics_aggregation_fn=weighted_average,
                            min_available_clients=NUM_CLIENTS,
                            min_fit_clients=NUM_CLIENTS,
                            ipfs_model_hash=init_model_hash,
                            perun_node_host="127.0.0.1",
                            perun_node_port=str(8080 + NUM_CLIENTS + 1),
                            secret_key=server_key,
                            account=addresses[-1],
                            client_addresses=addresses[:-1],
                            )
else:

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
