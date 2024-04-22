"""Communicate with the perun node using websockets."""
import ipfshttpclient
import socket
import time
import numpy as np
from config import IPFS_ON, NUM_CLIENTS

# Load network latencies from planet lab dataset https://github.com/uofa-rzhu3/NetLatency-Data
NETWORK_LATENCIES_DATASET = np.loadtxt('planet_lab_latencies_dataset.csv')
# Sample random latencies from the dateset to simulate network latencies
fl_conn = NUM_CLIENTS
perun_conn = NUM_CLIENTS + 1
ipfs_conn = NUM_CLIENTS + 1

total_num_connections = fl_conn + ipfs_conn + perun_conn
LINK_LATENCIES = np.random.choice(NETWORK_LATENCIES_DATASET, size=total_num_connections, replace=False)


FL_LINK_LATENCIES = LINK_LATENCIES[:fl_conn]
PERUN_LINK_LATENCIES = LINK_LATENCIES[len(FL_LINK_LATENCIES)+1:len(FL_LINK_LATENCIES)+1+perun_conn]
IPFS_LINK_LATENCIES = LINK_LATENCIES[len(PERUN_LINK_LATENCIES)+1:len(PERUN_LINK_LATENCIES)+1+ipfs_conn]


ipfs_client = None
if IPFS_ON:
    ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')


def post_to_ipfs(file_name: str, cid) -> str:
    if not IPFS_ON:
        return "IPFS is off"

    res = ipfs_client.add(file_name)
    # Simulate network latency
    time.sleep(IPFS_LINK_LATENCIES[cid] / 1000)
    return res

def send_command(host: str, port: int, request: bytes, caller: str="", cid: int=0) -> str:
    """Sent a command to the perun node using websockets and return the response."""
    # Connect to the server

    # print host, port and request
    # print("host: ", host)
    # print("port: ", port)
    # print("request: ", request)
    # print("caller: ", caller)
    try:
        conn = socket.create_connection((host, port))
    except socket.error as e:
        err_message = "Error connecting to the server:" + str(e)
        print("Error connecting to the server:", e)
        return err_message

    # Send a message to the server
    conn.send(request)

    # Read the server's response
    try:
        message = conn.recv(1024).decode('utf-8')
    except socket.error as e:
        err_message = "Error reading from the server: " + str(e)
        print(err_message)
        return err_message

    print("Server's response:", message)

    # Close the connection
    conn.close()


    # Simulate network latency
    time.sleep(PERUN_LINK_LATENCIES[cid] / 1000)
    return message


def open_channel(host: str, port: int, peer: str, deposit: int) -> str:
    """Open a channel with the perun node."""
    command = f"open,{peer},{deposit},{deposit}".encode()
    return send_command(host, port, command)


def test():
    """Test the communication with the perun node."""
    print("Opening channel...")
    command = b"open,peer_1,50,50"
    send_command("0.0.0.0", 8081, command)

    # time.sleep(0.01)

    print("Init FL...")
    command = b"set,peer_1,1,1,0,0,0"
    send_command("0.0.0.0", 8081, command)

    # time.sleep(1)


    print("Set weights...")
    command = b"set,peer_0,1,1,10,0,0"
    send_command("0.0.0.0", 8082, command)

    # time.sleep(1)


    print("Aggregate...")
    command = b"set,peer_1,1,1,10,66,34"
    send_command("0.0.0.0", 8081, command)

    print("Settle channel...")

    # time.sleep(1)

    # command = b"settle,peer_1"
    # send_command("0.0.0.0", 8081, command)

    command = b"settle,peer_0"
    send_command("0.0.0.0", 8082, command)


def testRounds():
    """Test the communication with the perun node."""
    print("Opening channel...")
    command = b"open,peer_1,50,50"
    send_command("0.0.0.0", 8081, command)

    print("Init FL...")
    command = b"set,peer_1,1,3,0,0,0"
    send_command("0.0.0.0", 8081, command)

    print("Set weights...")
    command = b"set,peer_0,1,3,10,0,0"
    send_command("0.0.0.0", 8082, command)

    print("Aggregate...")
    command = b"set,peer_1,1,3,10,66,34"
    send_command("0.0.0.0", 8081, command)

    print("Set weights...")
    command = b"set,peer_0,1,3,10,0,0"
    send_command("0.0.0.0", 8082, command)

    print("Aggregate...")
    command = b"set,peer_1,1,3,10,66,34"
    send_command("0.0.0.0", 8081, command)

    print("Set weights...")
    command = b"set,peer_0,1,3,10,0,0"
    send_command("0.0.0.0", 8082, command)

    print("Aggregate...")
    command = b"set,peer_1,1,3,10,66,34"
    send_command("0.0.0.0", 8081, command)

    time.sleep(0.1)

    print("Settle channel...")

    command = b"settle,peer_0"
    send_command("0.0.0.0", 8082, command)


def testTwoRounds():
    """Test the communication with the perun node."""
    print("Opening channel...")
    command = b"open,peer_1,50,50"
    send_command("0.0.0.0", 8081, command)

    print("Init FL...")
    command = b"set,peer_1,1,2,0,0,0"
    send_command("0.0.0.0", 8081, command)

    print("Set weights...")
    command = b"set,peer_0,1,2,10,0,0"
    send_command("0.0.0.0", 8082, command)

    print("Aggregate...")
    command = b"set,peer_1,1,2,0,0,99"
    send_command("0.0.0.0", 8081, command)

    print("Set weights...")
    command = b"set,peer_0,1,2,10,0,0"
    send_command("0.0.0.0", 8082, command)

    print("Aggregate...")
    command = b"set,peer_1,1,2,0,0,99"
    send_command("0.0.0.0", 8081, command)

    time.sleep(0.1)

    print("Settle channel...")

    command = b"settle,peer_0"
    send_command("0.0.0.0", 8082, command)


def testDisputes():
    """Test the communication with the perun node."""
    print("Opening channel...")
    command = b"open,peer_1,50,50"
    send_command("0.0.0.0", 8081, command)

    print("Init FL...")
    command = b"forceset,peer_1,1,1,0,0,0"
    send_command("0.0.0.0", 8081, command)

    print("Set weights...")
    command = b"forceset,peer_0,1,1,10,0,0"
    send_command("0.0.0.0", 8082, command)


    print("Aggregate...")
    command = b"forceset,peer_1,1,1,10,66,34"
    send_command("0.0.0.0", 8081, command)

    print("Settle channel...")
    time.sleep(0.1)

    # command = b"settle,peer_1"
    # send_command("0.0.0.0", 8081, command)

    command = b"settle,peer_0"
    send_command("0.0.0.0", 8082, command)


# test()
# testDisputes()
# testRounds()
# testTwoRounds()