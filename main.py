"""Run payment channel fl experiments."""
import subprocess
import time
from con import send_command
from model import NUM_CLIENTS

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
    setup_channels()
    subprocess.call("/Users/pi/Desktop/fl-testbet/run.sh", shell=True)
    settle_channels()


if __name__ == "__main__":
    main()
