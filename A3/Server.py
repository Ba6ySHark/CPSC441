import socket
import threading
import random
import logging

logging.basicConfig(
    filename='server_log.txt',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

class Server:
    PANDA_EMOJIS = ["🐼", "🎋", "🐾", "🌿"]
    PANDA_FACTS = [
        "Pandas spend around 14 hours a day eating bamboo!",
        "Baby pandas are born pink and weigh only about 100 grams!",
        "A group of pandas is called an embarrassment!",
        "Pandas can swim and are excellent tree climbers!",
        "There are only about 1,800 giant pandas left in the wild!",
    ]
    clients = {}
    clients_lock = threading.Lock()

    def broadcast_message(self, message, sender_socket=None):
        decorated = f"{random.choice(self.PANDA_EMOJIS)} {message} {random.choice(self.PANDA_EMOJIS)}"
        logging.info(f"Broadcasting message: {message}")
        with self.clients_lock:
            for client_sock, _ in self.clients.items():
                if client_sock != sender_socket:
                    try:
                        client_sock.sendall(decorated.encode('utf-8'))
                    except Exception as e:
                        logging.error(f"Could not send message to a client: {e}")

    def handle_client(self, client_socket):
        try:
            panda_name = client_socket.recv(1024).decode('utf-8')
            if not panda_name:
                panda_name = "AnonymousPanda"
            with self.clients_lock:
                self.clients[client_socket] = panda_name
            welcome_msg = f"👋 Ahoy! Welcome abamboo, {panda_name}! Type @bamboo, @grove, or @leaves."
            client_socket.sendall(welcome_msg.encode('utf-8'))
            logging.info(f"{panda_name} connected.")
            self.broadcast_message(f"{panda_name} has joined the Panda Chat!\n", sender_socket=client_socket)
            while True:
                msg = client_socket.recv(1024).decode('utf-8')
                if not msg:
                    break
                command = msg.strip()
                if command == "@bamboo":
                    fact = random.choice(self.PANDA_FACTS)
                    try:
                        client_socket.sendall(f"🌱 Panda Fact: {fact}\n".encode('utf-8'))
                    except Exception as e:
                        logging.error(f"Failed to send fact to {panda_name}: {e}")
                elif command == "@grove":
                    with self.clients_lock:
                        user_list = ", ".join(self.clients.values())
                    try:
                        client_socket.sendall(f"Current Pandas in the grove: {user_list}\n".encode('utf-8'))
                    except Exception as e:
                        logging.error(f"Failed to send user list to {panda_name}: {e}")
                elif command == "@leaves":
                    farewell = f"{panda_name} has left the Panda Chat."
                    self.broadcast_message(farewell, sender_socket=client_socket)
                    logging.info(f"{panda_name} disconnected (via @leaves).")
                    break
                else:
                    self.broadcast_message(f"{panda_name}: {msg}")
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            with self.clients_lock:
                if client_socket in self.clients:
                    disconnected_name = self.clients[client_socket]
                    del self.clients[client_socket]
                    logging.info(f"{disconnected_name} removed from client list.")
            client_socket.close()

    def start_server(self, host='0.0.0.0', port=12345):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)
        logging.info(f"🐼 Panda Chat Server running on {host}:{port} 🐼")
        print(f"🐼 Panda Chat Server running on {host}:{port} 🐼")
        try:
            while True:
                client_sock, addr = server_socket.accept()
                logging.info(f"New connection from {addr}")
                print(f"New connection from {addr}")
                threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()
        except KeyboardInterrupt:
            logging.info("Server shutting down via KeyboardInterrupt.")
            print("\nServer shutting down.")
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            server_socket.close()
            logging.info("Server socket closed.")

if __name__ == "__main__":
    server = Server()
    server.start_server(host='127.0.0.1', port=12345)