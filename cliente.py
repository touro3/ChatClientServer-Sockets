class Cliente:
    def __init__(self, conn):
        self.conn = conn
        self.username = None
        self.realname = None
        self.channel = None
        self.buffer = ""

    def receber_dados(self):
        try:
            data = self.conn.recv(512).decode()
            if data:
                self.buffer += data
                while "\r\n" in self.buffer:
                    message, self.buffer = self.buffer.split("\r\n", 1)
                    self.processar_comando(message)
        except:
            pass

    def enviar_dados(self, msg):
        try:
            self.conn.sendall(msg.encode() + b'\r\n')
        except:
            pass

    def processar_comando(self, message):
        if message.startswith("NICK"):
            self.processar_nick(message)
        elif message.startswith("USER"):
            self.processar_user(message)
        elif message.startswith("PING"):
            self.processar_ping(message)
        elif message.startswith("JOIN"):
            self.processar_join(message)
        # Adicionar outros comandos conforme necessário

    def processar_nick(self, message):
        _, username = message.split()
        if not username[0].isalpha() or len(username) > 9 or not all(c.isalnum() or c == '_' for c in username):
            self.enviar_dados(f"432 * {username} :Erroneous Nickname")
        elif username in servidor.clients:
            self.enviar_dados(f"433 * {username} :Nickname is already in use")
        else:
            old_username = self.username
            self.username = username.lower()
            servidor.clients[self.username] = self
            if old_username:
                del servidor.clients[old_username]
                servidor.broadcast(f":{old_username} NICK {self.username}")
            else:
                self.enviar_dados(f"001 {self.username} :Welcome to the Internet Relay Network {self.username}")
                self.enviar_dados(f":server 375 {self.username} :- {servidor.host} Message of the Day -")
                self.enviar_dados(f":server 372 {self.username} :- {MOTD}")
                self.enviar_dados(f":server 376 {self.username} :End of /MOTD command.")

    def processar_user(self, message):
        parts = message.split()
        self.realname = parts[4][1:]

    def processar_ping(self, message):
        payload = message.split(":", 1)[1]
        self.enviar_dados(f"PONG :{payload}")

    def processar_join(self, message):
        _, channel = message.split()
        if not channel.startswith("#"):
            self.enviar_dados(f":{servidor.host} 403 {self.username} {channel} :No such channel")
        else:
            self.channel = channel
            self.enviar_dados(f":{self.username} JOIN {channel}")
            servidor.broadcast(f":{self.username} JOIN {channel}", channel)
            users = " ".join([user.username for user in servidor.clients.values() if user.channel == channel])
            self.enviar_dados(f":{servidor.host} 353 {self.username} = {channel} :{users}")
            self.enviar_dados(f":{servidor.host} 366 {self.username} {channel} :End of /NAMES list")

class Servidor:
    def __init__(self, host='', port=6667, debug=False):
        self.conns = deque()
        self.host = host
        self.port = port
        self.debug = debug
        self.clients = {}

    def run(self, conn):
        cliente = Cliente(conn)
        self.conns.append(cliente)
        while True:
            cliente.receber_dados()

    def listen(self):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _socket.bind((self.host, self.port))
        _socket.listen(4096)
        while True:
            if self.debug:
                print(f'Servidor aceitando conexões na porta {self.port}...')
            client_conn, addr = _socket.accept()
            start_new_thread(self.run, (client_conn, ))

    def start(self):
        start_new_thread(self.listen, ())
        while True:
            time.sleep(60)
            if self.debug:
                print('Servidor funcionando...')

    def broadcast(self, message, channel=None):
        for client in self.clients.values():
            if not channel or client.channel == channel:
                client.enviar_dados(message)

def main():
    global servidor
    servidor = Servidor(host='', port=6667, debug=True)
    servidor.start()

if __name__ == '__main__':         
    main()
