"""Run payment channel fl experiments."""
import subprocess
import time
import numpy as np
import uuid

from con import send_command

import flwr as fl
from logging import INFO
from flwr.common.logger import log

from config import INCENTIVES_ON, SOLO_BLOCKCHAIN_ON, NUM_CLIENTS, NUM_ROUNDS, IPFS_ON


LOG_FILE = ""

if INCENTIVES_ON:
    LOG_FILE = f"logs/logs_flchan/exp{NUM_CLIENTS}{NUM_ROUNDS}.log"
elif SOLO_BLOCKCHAIN_ON:
    LOG_FILE = f"logs/logs_bcfl/exp{NUM_CLIENTS}{NUM_ROUNDS}.log"
else:
    LOG_FILE = f"logs/logs_fl/exp{NUM_CLIENTS}{NUM_ROUNDS}.log"


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
    fl.common.logger.configure(identifier="FL-experiment", filename=LOG_FILE)

    log(INFO, "Config: INCENTIVES_ON=%s, BCFL=%s, IPFS_ON=%s, NUM_CLIENTS=%s, NUM_ROUNDS=%s,", INCENTIVES_ON, SOLO_BLOCKCHAIN_ON, IPFS_ON, NUM_CLIENTS, NUM_ROUNDS)
    log(INFO, "Start Experiment")

    server_sleep_time = 3

    if SOLO_BLOCKCHAIN_ON:
        server_sleep_time = 5 * NUM_CLIENTS

    if not INCENTIVES_ON:
        subprocess.call(f"/Users/pi/Desktop/fl-testbet/run.sh {NUM_CLIENTS-1} {server_sleep_time}", shell=True)
    else:
        log(INFO, "Start opening channels")
        setup_channels()
        log(INFO, "Done opening channels")

        subprocess.call(f"/Users/pi/Desktop/fl-testbet/run.sh {NUM_CLIENTS-1} {server_sleep_time}", shell=True)

        log(INFO, "Start settling channels")
        settle_channels()
        log(INFO, "Done settling channels")

    log(INFO, "Done Experiment")


if __name__ == "__main__":
    main()
