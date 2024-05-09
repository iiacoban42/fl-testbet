
from fl_contract import GANACHE_URL, deploy_contract, set_aggregated_model, set_weight

from web3 import Web3
import time

import json


def run_bc_experiments():
    web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    server = "0x56FD289cEe714a5E471c418436EFA63E780D7a87"
    sk = "0x1af2e950272dd403de7a5760d41c6e44d92b6d02797e51810795ff03cc2cda4f"
    client = "0x6536425BE95A6661F6C6f68D709B6BE152785Df6"

    runs = {}

    for rep in range(7, 11):
        runs[rep] = []
        for i in range(1, 11):
            start = time.time()

            number_of_rounds = i
            model = "IDLNPosDxDgYnwguqIXcqYtaQeJrjySTTFjvzoLddFMrWM"

            server = web3.to_checksum_address(server)
            client = web3.to_checksum_address(client)
            contract, contract_address = deploy_contract(web3, model, number_of_rounds, server, sk)

            for r in range(number_of_rounds):
                set_weight(web3, contract, server, sk, client, "w"+str(r))
                set_aggregated_model(web3, contract, server, sk, client, "w"+str(r), 90, 10)

            done = time.time()
            runs[rep].append(done-start)

        print(f"Done rep {rep}")

        # dump to json
        with open(f"bc_latency_{rep}.json", "w") as f:
            json.dump(runs, f)

        print(runs)
