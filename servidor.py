import socket
import queue
import time
from collections import deque
from _thread import start_new_thread
from _thread import *
# Mensagem do Dia
MOTD = 'Bem-vindo ao servidor IRC!'

class Cliente:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.username = None
        self.realname = None
        self.channels = set()
        self.connected = True

    def receber_dados(self):
        try:
            data = self.conn.recv(1024).decode('utf-8')
            return data
        except socket.error:
            return None

    def enviar_dados(self, msg):
        try:
            self.conn.sendall(msg.encode('utf-8'))
        except socket.error:
            self.connected = False

    def close(self):
        self.conn.close()


class Servidor:
    def __init__(self, host='', port=6667):
        self.conns = deque()
        self.clients = {}
        self.channels = {}
        self.port = port

    def run(self, client):
        self.conns.append(client)
        while client.connected:
            data = client.receber_dados()
            if data:
                self.handle_command(client, data.strip())
            else:
                client.connected = False

        self.conns.remove(client)
        for channel in client.channels:
            self.handle_leave(client, channel, "Disconnected")
        client.close()

    def handle_command(self, client, data):
        print(f"Received data from {client.addr}: {data}")
        if data.startswith("NICK"):
            self.handle_nick(client, data)
        elif data.startswith("USER"):
            self.handle_user(client, data)
        elif data.startswith("PING"):
            self.handle_ping(client, data)
        elif data.startswith("QUIT"):
            self.handle_quit(client, data)
        elif data.startswith("JOIN"):
            self.handle_join(client, data)
        elif data.startswith("PART"):
            self.handle_part(client, data)
        elif data.startswith("PRIVMSG"):
            self.handle_privmsg(client, data)
        else:
            client.enviar_dados(f"ERROR :Unknown command: {data}\r\n")

    def handle_nick(self, client, data):
        _, username = data.split(":", 1)
        client.username = username.strip()
        self.clients[client.username] = client
        client.enviar_dados(f":{client.username} NICK {client.username}\r\n")

    def handle_user(self, client, data):
        parts = data.split()
        if len(parts) > 1:
            client.realname = parts[1]
            client.enviar_dados(f":{client.username} USER {client.username} 0 * :{client.realname}\r\n")
            client.enviar_dados(f":{self.port} 001 {client.username} :Welcome to the IRC server\r\n")
            client.enviar_dados(f":{self.port} 376 {client.username} :End of /MOTD command.\r\n")

    def handle_ping(self, client, data):
        payload = data.split(":", 1)[1]
        client.enviar_dados(f"PONG :{payload}\r\n")

    def handle_quit(self, client, data):
        _, reason = data.split(":", 1)
        client.enviar_dados(f"ERROR :Closing Link: {client.username} ({reason.strip()})\r\n")
        client.connected = False

    def handle_join(self, client, data):
        _, channel = data.split()
        channel = channel.strip()
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(client)
        client.channels.add(channel)
        client.enviar_dados(f":{client.username} JOIN {channel}\r\n")

    def handle_part(self, client, data):
        parts = data.split()
        if len(parts) > 1:
            channel = parts[1]
            if channel in client.channels:
                reason = " ".join(parts[2:]).strip(":") if len(parts) > 2 else "Leaving"
                self.channels[channel].remove(client)
                client.channels.remove(channel)
                client.enviar_dados(f":{client.username} PART {channel} :{reason}\r\n")

    def handle_privmsg(self, client, data):
        parts = data.split(":", 2)
        if len(parts) > 2:
            channel = parts[1].split()[1]
            message = parts[2]
            if channel in self.channels and client in self.channels[channel]:
                for member in self.channels[channel]:
                    if member != client:
                        member.enviar_dados(f":{client.username} PRIVMSG {channel} :{message}\r\n")

    def listen(self):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _socket.bind((self.port, self.port))
        _socket.listen(4096)
        print(f"Servidor aceitando conexões na porta {self.port}...")

        while True:
            client_conn, client_addr = _socket.accept()
            client = Cliente(client_conn, client_addr)
            start_new_thread(self.run, (client,))

    def start(self):
        start_new_thread(self.listen, ())

        while True:
            time.sleep(10)
            print("Servidor funcionando...")


def main():
    server = Servidor()
    server.start()

if __name__ == "__main__":
    main()
