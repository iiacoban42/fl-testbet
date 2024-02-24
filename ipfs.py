import io
from typing import List

import torch
import torch.nn as nn
import flwr as fl
import ipfshttpclient
# from ipfshttpclient import add_pybytes
import ipfshttpclient

import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    """Model (simple CNN adapted from 'PyTorch: A 60 Minute Blitz')"""

    def __init__(self) -> None:
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


# def share_model_on_ipfs(model: nn.Module) -> str:
#     # Use IPFS to share the model
#     # Example: Use py-ipfs-http-client to add the model to IPFS
#     # Consult IPFS documentation for details: https://github.com/ipfs/py-ipfs-http-client
#     ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
#     result = add_pybytes(ipfs_client, torch.save(model.state_dict(), io.BytesIO()))
#     model_cid = result['Hash']
#     return model_cid

# def post_weights_on_ipfs(weights: torch.Tensor) -> str:
#     # Use IPFS to post the weights
#     # Example: Use py-ipfs-http-client to add the weights to IPFS
#     # Consult IPFS documentation for details
#     ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
#     result = ipfs_client.add(torch.save(weights, io.BytesIO()))
#     weights_cid = result['Hash']
#     return weights_cid

# def update_model_on_ipfs(final_model: nn.Module) -> str:
#     # Use IPFS to update the final model
#     # Example: Use py-ipfs-http-client to add the final model to IPFS
#     # Consult IPFS documentation for details
#     ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
#     result = ipfs_client.add(torch.save(final_model.state_dict(), io.BytesIO()))
#     final_model_cid = result['Hash']
#     return final_model_cid

# def aggregate_final_model(clients: List[fl.client.Client]) -> Net:
#     # Your logic to aggregate the final model from client models
#     # Example: Simple average aggregation
#     final_model = Net()
#     for client in clients:
#         client_weights = client.get_weights()
#         final_model.load_state_dict({k: sum(t) / len(t) for k, t in zip(final_model.state_dict(), zip(*client_weights))})
#     return final_model

# # Example federated learning loop
# num_epochs = 10
# clients = [...]  # Your list of Flower clients

# model = Net()

# for epoch in range(num_epochs):
#     # Federated learning logic here
#     # ...

#     # Share the model on IPFS
#     model_cid = share_model_on_ipfs(model)

#     # Clients post weights on IPFS
#     for client in clients:
#         if hasattr(client, 'get_weights'):
#             weights_cid = post_weights_on_ipfs(client.get_weights())

#     # Aggregate the final model in the server
#     final_model = aggregate_final_model(clients)

#     # Update the final model on IPFS
#     final_model_cid = update_model_on_ipfs(final_model)
# files = [
# 'QmZbiYaLfH7CHkENeRrLJQmQYJHHSyjpV1cMrd9YfSFBmY',
# 'QmbZZrby6zTb1UUJqbMQSxCKwcsgr988aoV5wMhNe2VYt2',
# 'QmYEpTrbxU5KN8JbqH6s88Set33ngeVGfUEtnVgL5DPMd4',
# 'QmdmYx2wGxv28rLJtbVVCpWtyvyxGLi2k2JNHRfbDoeJEQ',
# 'QmXfnu1LzxaJ2YP2nPAvpKjKtw8jkbRY2CecSCuqPBJaoq',
# 'QmSnk3qKBmepPsVjEMnqdqXoRo5ievsBHhkHoarmZUxP2W',
# 'QmVsggqqRWMHTULEApmESVAunaDPWJgSHFfncAZRv3K2dP',
# 'QmVCvNn3ztupQWpEXBUCqjN8qqnQeDiGXydofN3BCm1GRh',
# 'QmWZWhJUmesdsedKQg9xZsNJfXjGT1AiJK4MrV8y88RaeZ',
# 'QmW6r8Uku5qtUvvxsB7F3Cnpcz4umAdoTAWPkchS17ftPa',
# 'Qma7sThFpRTtsdY5xzuRdg6UrXTaksJUvsRhAEdNu2RkWU',
# ]

# # Connect to the local IPFS node
# client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')


# for file_hash in files:

#     # Get the file from IPFS
#     res = client.cat(file_hash)

#     # The file content is returned as bytes, so you might want to decode it
#     # file_content = res.decode('utf-8')
#     print(file_hash)
#     print(res)
#     print('-----------------------')