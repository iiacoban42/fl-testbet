"""Communicate with the perun node using websockets."""
import socket

def send_command(host: str, port: int, request: bytes) -> str:
    """Sent a command to the perun node using websockets and return the response."""
    # Connect to the server
    try:
        conn = socket.create_connection((host, port))
    except socket.error as e:
        err_message = "Error connecting to the server:" + str(e)
        print("Error connecting to the server:", e)
        return err_message

    # Send a message to the server
    conn.sendall(request)

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


def test():
    print("Opening channel...")
    command = b"open,peer_1,500,500"
    send_command("0.0.0.0", 8081, command)

    print("Init FL...")
    command = b"set,peer_1,1,1,0,0,0"
    send_command("0.0.0.0", 8081, command)

    print("Set weights...")
    command = b"set,peer_0,1,1,10,0,0"
    send_command("0.0.0.0", 8082, command)

    print("Aggregate...")
    command = b"set,peer_1,1,1,10,66,34"
    send_command("0.0.0.0", 8081, command)

    print("Settle channel...")
    command = b"settle,peer_1"
    send_command("0.0.0.0", 8081, command)

    # command = b"settle,peer_0"
    # send_command("0.0.0.0", 8082, command)


test()
