"""Communicate with the perun node using websockets."""
import socket
import time

def send_command(host: str, port: int, request: bytes, caller: str="") -> str:
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