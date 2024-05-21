import socket
import threading
import signal
import sys

class IRCClient:
    def __init__(self, host='localhost', port=6667):
        self.host = host
        self.port = port
        self.sock = None
        self.nickname = None
        self.realname = None
        self.connected = False
        self.default_channel = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.connected = True
        print(f"Connected to {self.host}:{self.port}")

        # Start a thread to listen for incoming messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def disconnect(self):
        if self.connected:
            self.send_command(f"QUIT :{self.nickname} has quit")
            self.sock.close()
            self.connected = False
            print("Disconnected from server")

    def send_command(self, command):
        if self.connected:
            self.sock.sendall(f"{command}\r\n".encode('utf-8'))

    def receive_messages(self):
        while self.connected:
            try:
                response = self.sock.recv(512).decode('utf-8').strip()
                if response:
                    print(f"Server: {response}")
                    self.handle_server_message(response)
                else:
                    break
            except:
                break
        self.disconnect()

    def handle_server_message(self, message):
        if message.startswith("PING"):
            payload = message.split(":")[1]
            self.send_command(f"PONG :{payload}")

    def run(self):
        while True:
            try:
                command = input("> ").strip()
                if command.startswith("/nick"):
                    self.handle_nick(command)
                elif command.startswith("/user"):
                    self.handle_user(command)
                elif command.startswith("/join"):
                    self.handle_join(command)
                elif command.startswith("/leave"):
                    self.handle_leave(command)
                elif command.startswith("/msg"):
                    self.handle_msg(command)
                elif command.startswith("/quit"):
                    self.handle_quit(command)
                elif command.startswith("/connect"):
                    self.handle_connect(command)
                elif command.startswith("/disconnect"):
                    self.handle_disconnect(command)
                elif command.startswith("/channel"):
                    self.handle_channel(command)
                elif command.startswith("/list"):
                    self.handle_list(command)
                elif command.startswith("/help"):
                    self.handle_help()
                else:
                    print("Unknown command. Type /help for a list of commands.")
            except KeyboardInterrupt:
                self.handle_quit("/quit")
                break

    def handle_connect(self, command):
        parts = command.split(' ')
        if len(parts) == 2:
            self.host = parts[1]
        self.connect()

    def handle_disconnect(self, command):
        self.disconnect()

    def handle_nick(self, command):
        parts = command.split(' ')
        if len(parts) == 2:
            self.nickname = parts[1]
            self.send_command(f"NICK {self.nickname}")

    def handle_user(self, command):
        parts = command.split(' ', 1)
        if len(parts) == 2:
            self.realname = parts[1]
            self.send_command(f"USER {self.nickname} 0 * :{self.realname}")

    def handle_join(self, command):
        parts = command.split(' ')
        if len(parts) == 2:
            channel = parts[1]
            self.send_command(f"JOIN {channel}")
            self.default_channel = channel
            print(f"Joined channel {channel}")

    def handle_leave(self, command):
        parts = command.split(' ', 2)
        if len(parts) >= 2:
            channel = parts[1]
            reason = parts[2] if len(parts) == 3 else ""
            self.send_command(f"PART {channel} :{reason}")
            if self.default_channel == channel:
                self.default_channel = None
                print(f"Left channel {channel}")

    def handle_msg(self, command):
        parts = command.split(' ', 2)
        if len(parts) == 3:
            channel = parts[1]
            message = parts[2]
            self.send_command(f"PRIVMSG {channel} :{message}")
        elif len(parts) == 2 and self.default_channel:
            message = parts[1]
            self.send_command(f"PRIVMSG {self.default_channel} :{message}")

    def handle_quit(self, command):
        parts = command.split(' ', 1)
        if len(parts) == 2:
            reason = parts[1]
        else:
            reason = "Client Quit"
        self.send_command(f"QUIT :{reason}")
        self.disconnect()
        sys.exit()

    def handle_channel(self, command):
        parts = command.split(' ')
        if len(parts) == 2:
            channel = parts[1]
            self.default_channel = channel
            print(f"Switched to channel {channel}")
        else:
            print(f"Default channel: {self.default_channel}")

    def handle_list(self, command):
        parts = command.split(' ')
        if len(parts) == 2:
            channel = parts[1]
            self.send_command(f"NAMES {channel}")
        elif self.default_channel:
            self.send_command(f"NAMES {self.default_channel}")

    def handle_help(self):
        help_text = """
Comandos disponíveis:
/connect <IP> - Conectar ao servidor IRC no endereço IP especificado
/disconnect - Desconectar do servidor IRC
/nick <apelido> - Definir seu apelido
/user <nome real> - Definir seu nome real
/join <#canal> - Entrar no canal especificado
/leave <#canal> - Sair do canal especificado
/channel <#canal> - Definir ou mostrar o canal padrão
/list <#canal> - Listar usuários no canal especificado
/msg <#canal> <msg> - Enviar uma mensagem para o canal especificado
/quit <motivo> - Sair do cliente IRC com um motivo opcional
/help - Mostrar esta mensagem de ajuda
"""
        print(help_text)

if __name__ == "__main__":
    print("Digite /help para ver os comandos disponíveis.")
    client = IRCClient()
    client.run()
