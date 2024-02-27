"""Run payment channel fl experiments."""
import subprocess
import time
from con import send_command
from model import NUM_CLIENTS, INCENTIVES_ON, IPFS_ON, NUM_ROUNDS

import flwr as fl
from logging import INFO, DEBUG
from flwr.common.logger import log

def setup_channels():
    for i in range(NUM_CLIENTS):
        server_port = 8081 + NUM_CLIENTS
        send_command("127.0.0.1", server_port, f"open,peer_{i},10,10".encode())

def settle_channels():
    for i in range(NUM_CLIENTS):
        server_port = 8081 + NUM_CLIENTS
        send_command("127.0.0.1", server_port, f"settle,peer_{i},10,10".encode())
        time.sleep(1)


def main():
    fl.common.logger.configure(identifier="FL-experiment", filename="fllog.log")

    log(INFO, "Config: INCENTIVES_ON=%s, IPFS_ON=%s, NUM_CLIENTS=%s, NUM_ROUNDS=%s", INCENTIVES_ON, IPFS_ON, NUM_CLIENTS, NUM_ROUNDS)
    log(INFO, "Start Experiment")


    if not INCENTIVES_ON:
        subprocess.call("/Users/pi/Desktop/fl-testbet/run.sh", shell=True)
    else:
        log(INFO, "Start opening channels")
        setup_channels()
        log(INFO, "Done opening channels")

        subprocess.call("/Users/pi/Desktop/fl-testbet/run.sh", shell=True)

        log(INFO, "Start settling channels")
        settle_channels()
        log(INFO, "Done settling channels")

    log(INFO, "Done Experiment")


if __name__ == "__main__":
    main()
