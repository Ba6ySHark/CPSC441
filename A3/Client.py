import socket
import sys
import threading

def receive_messages(sock):
    """
    Continuously listens for messages from the server
    and prints them to the local console.
    """
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Disconnected from server.")
                break
            print(data.decode('utf-8'))
        except:
            print("Error receiving data. Connection closed.")
            break

def start_client(server_host='127.0.0.1', server_port=12345, panda_name="MyPanda"):
    """
    Connects to the chat server, sends the panda name,
    and starts threads to handle user input and server responses.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    # Send our chosen panda name first
    client_socket.sendall(panda_name.encode('utf-8'))

    # Start a thread to listen for incoming messages
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    print("Type your messages below. Use @bamboo, @grove, or @leaves for special commands.")

    # Main loop: read user input and send to server
    try:
        while True:
            user_input = sys.stdin.readline()
            if not user_input:
                break
            client_socket.sendall(user_input.strip().encode('utf-8'))

            # If user typed @leaves, break local loop as well
            if user_input.strip() == "@leaves":
                print("You have left the Panda Chat. Goodbye!")
                break

    except KeyboardInterrupt:
        print("Client shutting down.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    # If you want to allow users to specify host, port, or name, parse sys.argv here.
    # For example: python client.py 127.0.0.1 12345 "BambooWarrior"
    if len(sys.argv) >= 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
        name = sys.argv[3] if len(sys.argv) > 3 else "MysteryPanda"
        start_client(host, port, name)
    else:
        start_client()
