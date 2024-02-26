import argparse
import warnings
import pickle
import uuid
from collections import OrderedDict

import flwr as fl
from flwr_datasets import FederatedDataset
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision.transforms import Compose, Normalize, ToTensor
from tqdm import tqdm
import numpy as np
from logging import INFO, DEBUG
from flwr.common.logger import log

from model import Net, NUM_CLIENTS, NUM_ROUNDS, IPFS_ON, INCENTIVES_ON
from con import send_command

import ipfshttpclient

ipfs_client = None
if IPFS_ON:
    ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')


# #############################################################################
# 1. Regular PyTorch pipeline: nn.Module, train, test, and DataLoader
# #############################################################################

warnings.filterwarnings("ignore", category=UserWarning)
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def train(net, trainloader, epochs):
    """Train the model on the training set."""
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    for _ in range(epochs):
        for batch in tqdm(trainloader, "Training"):
            images = batch["img"]
            labels = batch["label"]
            optimizer.zero_grad()
            criterion(net(images.to(DEVICE)), labels.to(DEVICE)).backward()
            optimizer.step()


def test(net, testloader):
    """Validate the model on the test set."""
    criterion = torch.nn.CrossEntropyLoss()
    correct, loss = 0, 0.0
    with torch.no_grad():
        for batch in tqdm(testloader, "Testing"):
            images = batch["img"].to(DEVICE)
            labels = batch["label"].to(DEVICE)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
    accuracy = correct / len(testloader.dataset)
    return loss, accuracy


def load_data(node_id):
    """Load partition CIFAR10 data."""
    fds = FederatedDataset(dataset="cifar10", partitioners={"train": NUM_CLIENTS})
    partition = fds.load_partition(node_id)
    # Divide data on each node: 80% train, 20% test
    partition_train_test = partition.train_test_split(test_size=0.2)
    pytorch_transforms = Compose(
        [ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )

    def apply_transforms(batch):
        """Apply transforms to the partition from FederatedDataset."""
        batch["img"] = [pytorch_transforms(img) for img in batch["img"]]
        return batch

    partition_train_test = partition_train_test.with_transform(apply_transforms)
    trainloader = DataLoader(partition_train_test["train"], batch_size=32, shuffle=True)
    testloader = DataLoader(partition_train_test["test"], batch_size=32)
    return trainloader, testloader


# #############################################################################
# 2. Federation of the pipeline with Flower
# #############################################################################

# Get node id
parser = argparse.ArgumentParser(description="Flower")
parser.add_argument(
    "--node-id",
    choices=np.arange(NUM_CLIENTS),
    required=True,
    type=int,
    help="Partition of the dataset divided into 3 iid partitions created artificially.",
)
node_id = parser.parse_args().node_id

# Load model and data (simple CNN, CIFAR-10)
net = Net().to(DEVICE)
trainloader, testloader = load_data(node_id=node_id)


# create an array containing all integers between 0 and 99

# Define Flower client
class FlowerClient(fl.client.NumPyClient):

    def __init__(self, cid):
        self.cid = cid
        self.perun_node_host = "127.0.0.1"
        self.perun_node_port = str(8081 + cid)

    def get_parameters(self, config):
        params = [val.cpu().numpy() for _, val in net.state_dict().items()]
        return params


    def set_parameters(self, parameters):
        params_dict = zip(net.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        net.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        log(INFO, "Start Training client=%s", self.cid)
        self.set_parameters(parameters)
        train(net, trainloader, epochs=1)
        params = self.get_parameters(config={})
        # Save the updated parameters to a file
        file_name = f'storage/updated_weights_{self.cid}_{uuid.uuid4()}.pkl'
        with open(file_name, 'wb') as f:
            pickle.dump(params, f)

        if IPFS_ON:
            res = ipfs_client.add(file_name)
            log(DEBUG, "File: %s IPFS file hash: %s", file_name, res['Hash'])

        log(INFO, "Start sending updated weights to the perun node (client=%s)", self.cid)
        if INCENTIVES_ON:
            log(INFO, "PERUN REQUEST: Setting weight client=%s", self.cid)
            send_command(self.perun_node_host, self.perun_node_port, f"set,peer_{NUM_CLIENTS},1,{NUM_ROUNDS},10,0,0".encode(), "client")
            log(INFO, "Done sending updated weights to the perun node (client=%s)", self.cid)


        log(INFO, "Done Training client=%s", self.cid)
        return params, len(trainloader.dataset), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        loss, accuracy = test(net, testloader)
        return loss, len(testloader.dataset), {"accuracy": accuracy}


fl.common.logger.configure(identifier="FL-experiment", filename="fllog.log")

# Start Flower client
fl.client.start_client(
    server_address="127.0.0.1:8000",
    client=FlowerClient(node_id).to_client(),
)
