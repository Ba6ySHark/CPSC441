import socket
import threading
import random

# Panda emojis and facts as specified:
PANDA_EMOJIS = ["🐼", "🎋", "🐾", "🌿", "🐾🐼"]  # Add more if you'd like
PANDA_FACTS = [
    "Pandas spend around 14 hours a day eating bamboo!",
    "Baby pandas are born pink and weigh only about 100 grams!",
    "A group of pandas is called an embarrassment!",
    "Pandas can swim and are excellent tree climbers!",
    "There are only about 1,800 giant pandas left in the wild!",
]

# Global data structures:
clients = {}  # Maps a client socket to the panda name
clients_lock = threading.Lock()

def broadcast_message(message, sender_socket=None):
    """
    Sends 'message' to all connected clients except (optionally) the sender.
    Also decorates messages with random panda emojis.
    """
    decorated = f"{random.choice(PANDA_EMOJIS)} {message} {random.choice(PANDA_EMOJIS)}"
    with clients_lock:
        for client_sock, _ in clients.items():
            if client_sock != sender_socket:  # avoid echoing back to sender
                try:
                    client_sock.sendall(decorated.encode('utf-8'))
                except:
                    print("Error: Could not send message to a client.")

def handle_client(client_socket):
    """
    Receives messages from a client, handles special commands,
    and broadcasts messages to other clients.
    """
    try:
        # The first message from the client is assumed to be its panda name
        panda_name = client_socket.recv(1024).decode('utf-8')
        if not panda_name:
            panda_name = "MysteryPanda"
        with clients_lock:
            clients[client_socket] = panda_name

        welcome_msg = f"👋 Welcome, {panda_name}! Type @bamboo, @grove, or @leaves."
        client_socket.sendall(welcome_msg.encode('utf-8'))

        # Announce new arrival to other users
        broadcast_message(f"{panda_name} has joined the Panda Chat!\n", sender_socket=client_socket)

        # Listen for further messages
        while True:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg:
                break  # socket closed
            
            # Check for special commands
            if msg.strip() == "@bamboo":
                fact = random.choice(PANDA_FACTS)
                client_socket.sendall(f"🌱 Panda Fact: {fact}\n".encode('utf-8'))
            elif msg.strip() == "@grove":
                with clients_lock:
                    user_list = ", ".join(clients.values())
                client_socket.sendall(f"Current Pandas in the grove: {user_list}\n".encode('utf-8'))
            elif msg.strip() == "@leaves":
                # Graceful disconnect
                farewell = f"{panda_name} has left the Panda Chat."
                broadcast_message(farewell, sender_socket=client_socket)
                break
            else:
                # Normal message broadcast
                broadcast_message(f"{panda_name}: {msg}")

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Cleanup: remove client from dictionary, close socket
        with clients_lock:
            if client_socket in clients:
                disconnected_name = clients[client_socket]
                del clients[client_socket]
        client_socket.close()


def start_server(host='0.0.0.0', port=12345):
    """
    Creates a socket, binds, listens, and spawns threads to handle new clients.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"🐼 Panda Chat Server running on {host}:{port} 🐼")

    try:
        while True:
            client_sock, addr = server_socket.accept()
            print(f"New connection from {addr}")
            threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    # You can change the host and port as needed or parse them from sys.argv
    start_server(host='127.0.0.1', port=12345)
