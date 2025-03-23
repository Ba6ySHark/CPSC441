import customtkinter as ctk
import coolname
import socket
import threading
import queue

# client side logic
class ChatClientLogic:
    def __init__(self):
        self.client_socket = None
        self.receive_thread = None
        self.messages_queue = queue.Queue()

    def connect(self, host, port, name):
        # connect to the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        self.client_socket.sendall(name.encode("utf-8"))

        # bg thread
        self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
        self.receive_thread.start()

        self.messages_queue.put(f"Connected as {name}!\n"
                                f"Type @bamboo, @grove, or @leaves for special commands.\n")

    def send_message(self, msg):
        # sends message to the server
        if self.client_socket is None:
            self.messages_queue.put("You are not connected to the server.\n")
            return

        try:
            self.client_socket.sendall(msg.encode("utf-8"))
        except Exception as e:
            self.messages_queue.put(f"Error sending message: {e}\n")

        # type @leaves to exit
        if msg.strip() == "@leaves":
            self.messages_queue.put("You left the Panda Chat. Closing connection...\n")
            self.close()

    def close(self):
        if self.client_socket is not None:
            try:
                self.client_socket.close()
            except Exception as e:
                self.messages_queue.put(f"Error closing socket: {e}\n")
            finally:
                self.client_socket = None
                self.messages_queue.put("You have been disconnected.\n")

    def _receive_messages(self):
        # receives messages from the server
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    self.messages_queue.put("Disconnected from server.\n")
                    break
                message = data.decode("utf-8")
                self.messages_queue.put(message)
            except OSError:
                break
            except Exception as e:
                self.messages_queue.put(f"Error receiving data: {e}\n")
                break

        # If we exit this loop, ensure the socket is closed
        self.close()

    def get_new_messages(self):
        msgs = []
        while not self.messages_queue.empty():
            msgs.append(self.messages_queue.get_nowait())
        return msgs

    def is_connected(self) -> bool:
        return self.client_socket is not None

    def generate_random_name(self):
        # generates random name
        return "-".join(coolname.generate())


# UI class implementation
class UI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # window config
        self.title("Panda Chat Client")
        self.geometry("600x500")

        self.logic = ChatClientLogic()

        self.connection_frame = ctk.CTkFrame(self, corner_radius=10)
        self.connection_frame.pack(pady=10, padx=10, fill="x")

        self.host_label = ctk.CTkLabel(self.connection_frame, text="Host:", text_color="black")
        self.host_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.host_entry = ctk.CTkEntry(self.connection_frame, text_color="black")
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)
        self.host_entry.insert(0, "127.0.0.1")

        self.port_label = ctk.CTkLabel(self.connection_frame, text="Port:", text_color="black")
        self.port_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        self.port_entry = ctk.CTkEntry(self.connection_frame, text_color="black")
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)
        self.port_entry.insert(0, "12345")

        self.name_label = ctk.CTkLabel(self.connection_frame, text="Panda Name:", text_color="black")
        self.name_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.name_entry = ctk.CTkEntry(self.connection_frame, placeholder_text="BambooWarrior", text_color="black")
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.name_entry.insert(0, self.logic.generate_random_name())

        self.connect_button = ctk.CTkButton(
            self.connection_frame,
            text="Connect",
            command=self.on_connect_clicked,
            fg_color="#90EE90",
            text_color="black"
        )
        self.connect_button.grid(row=1, column=2, padx=5, pady=5)

        self.chat_frame = ctk.CTkFrame(self, corner_radius=10)
        self.chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.chat_display = ctk.CTkTextbox(self.chat_frame, wrap="word", state="disabled", text_color="black")
        self.chat_display.pack(padx=10, pady=10, fill="both", expand=True)

        self.entry_frame = ctk.CTkFrame(self, corner_radius=10)
        self.entry_frame.pack(pady=5, padx=10, fill="x")

        self.message_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Type a message...", text_color="black")
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.send_button = ctk.CTkButton(
            self.entry_frame,
            text="Send",
            command=self.on_send_clicked,
            fg_color="#90EE90",
            text_color="black"
        )
        self.send_button.pack(side="left", padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.check_for_incoming_messages()

    def on_connect_clicked(self):
        host = self.host_entry.get().strip()
        port = int(self.port_entry.get().strip())

        # In case user deletes pre-made name and does not input anything, we'll set it to Anonymous
        name = self.name_entry.get().strip() or "AnonymousPanda"

        try:
            self.logic.connect(host, port, name)
            self.append_message_to_chat(f"Connecting to {host}:{port} as {name}...")
            self.connect_button.configure(state="disabled")
        except Exception as e:
            self.append_message_to_chat(f"Connection failed: {e}")

    def on_send_clicked(self):
        msg = self.message_entry.get().strip()
        self.message_entry.delete(0, "end")  # clear input

        if not msg:
            return

        self.logic.send_message(msg)

    def on_closing(self):
        # if the user closes UI, send @leaves so the server
        if self.logic.is_connected():
            self.logic.send_message("@leaves")  # This also calls logic.close() internally
        self.destroy()

    def append_message_to_chat(self, message: str):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message + "\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def check_for_incoming_messages(self):
        for msg in self.logic.get_new_messages():
            self.append_message_to_chat(msg.rstrip("\n"))

        # Re-schedule this method to be called again after 100ms
        self.after(100, self.check_for_incoming_messages)


if __name__ == "__main__":
    app = UI()
    app.mainloop()