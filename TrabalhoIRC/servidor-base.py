import socket
import threading
import re
import random
import time
from _thread import start_new_thread

class IRCServer:
    def __init__(self, host='0.0.0.0', port=6667, version='1.0', created='2024-05-27'):
        self.host = host
        self.port = port
        self.version = version
        self.created = created
        self.nicknames = {}  
        self.channels = {}  

    def listen(self):
        '''(não alterar)
        Escuta múltiplas conexões na porta definida, chamando o método run para
        cada uma. Propriedades da classe Servidor são vistas e podem 
        ser alteradas por todas as conexões.
        '''
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _socket.bind(('', self.port))
        _socket.listen(4096)
        while True:
            print(f'Servidor aceitando conexões na porta {self.port}...')
            client, addr = _socket.accept()
            start_new_thread(self.run, (client, ))

    def start(self):
        '''(não alterar)
        Inicia o servidor no método listen e fica em loop infinito.
        '''
        start_new_thread(self.listen, ())

        while True:
            time.sleep(60)
            print('Servidor funcionando...')

    def broadcast(self, channel, message, exclude_self=False):
        for client in self.channels.get(channel, []):
            if not exclude_self or client.nickname != message.split(' ')[0][1:]:
                client.conn.send(message.encode('utf-8'))

    def run(self, conn):
        client_handler = ClientHandler(conn, conn.getpeername(), self)
        client_handler.start()

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, server):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.server = server
        self.nickname = None
        self.realname = None
        self.channels = []

    def run(self):
        while True:
            try:
                message = self.conn.recv(512)
                if not message:
                    break
                message = message.strip()
                if not message:
                    continue
                try:
                    message = message.decode('utf-8')
                except UnicodeDecodeError:
                    print(f"Erro ao decodificar mensagem de {self.addr}: {message}")
                    continue
                print(f"Mensagem recebida de {self.addr}: {message}")
                self.handle_message(message)
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"Erro ao lidar com mensagem de {self.addr}: {e}")
                break
        self.disconnect()

    def handle_message(self, message):
        if len(message) > 512:
            self.conn.send(b':server 500 :Mensagem muito longa\r\n')
            return

        if message.startswith('NICK'):
            self.handle_nick(message)
        elif message.startswith('USER'):
            self.handle_user(message)
        elif message.startswith('JOIN'):
            self.handle_join(message)
        elif message.startswith('PART'):
            self.handle_part(message)
        elif message.startswith('QUIT'):
            self.handle_quit(message)
        elif message.startswith('PRIVMSG'):
            self.handle_privmsg(message)
        elif message.startswith('NAMES'):
            self.handle_names(message)
        elif message.startswith('LIST'):
            self.handle_list(message)
        elif message.startswith('PING'):
            self.handle_ping(message)
        else:
            self.conn.send(b':server 421 :Comando desconhecido\r\n')

    def handle_nick(self, message):
        nickname = message.split(' ')[1]
        if re.match(r'^[a-zA-Z][a-zA-Z0-9_]{0,8}$', nickname):
            if nickname not in self.server.nicknames:
                if self.nickname:
                    del self.server.nicknames[self.nickname]
                self.nickname = nickname
                self.server.nicknames[nickname] = self
                self.conn.send(f':server 001 {nickname} :Bem-vindo ao servidor IRC de Crias {nickname}!\r\n'.encode('utf-8'))
                motd = [
                    "Bem-vindo ao nosso servidor IRC!",
                    "Esperamos que você tenha uma ótima experiência aqui.",
                    "Obrigado por se juntar à nossa comunidade!",
                    "Aproveite o tempo e faça novos amigos!",
                    "Lembre-se sempre de ser gentil e respeitoso com os outros usuários.",
                    "Sinta-se à vontade para participar das conversas nos canais disponíveis.",
                    "Se precisar de ajuda, não hesite em pedir a um dos nossos moderadores."
                ]
                selected_motd = random.choice(motd)
                self.conn.send(f':server 372 {nickname} :Mensagem do Dia:{selected_motd}\r\n'.encode('utf-8'))
                print(f"Usuário {nickname} criado com sucesso.")
            else:
                self.conn.send(f':server 433 * {nickname} :Apelido já está em uso\r\n'.encode('utf-8'))
        else:
            self.conn.send(f':server 432 * {nickname} :Apelido inválido\r\n'.encode('utf-8'))

    def handle_user(self, message):
        parts = message.split(' ', 4)
        if len(parts) == 5:
            self.realname = parts[4][1:]
            print(f"Usuário {self.nickname} definiu o nome real para {self.realname}")

    def handle_join(self, message):
        parts = message.split(' ')
        if len(parts) < 2:
            self.conn.send(f':server 461 {self.nickname} JOIN :Parâmetros insuficientes\r\n'.encode('utf-8'))
            return
        channel = parts[1]
        if re.match(r'^#[a-zA-Z0-9_]{1,63}$', channel):
            if channel not in self.server.channels:
                self.server.channels[channel] = []
                print(f"Canal {channel} criado com sucesso.")
            self.server.channels[channel].append(self)
            self.channels.append(channel)
            self.conn.send(f':{self.nickname} JOIN {channel}\r\n'.encode('utf-8'))
            self.server.broadcast(channel, f':{self.nickname} JOIN {channel}\r\n')
            self.conn.send(f':server 353 {self.nickname} = {channel} :{" ".join([client.nickname for client in self.server.channels[channel]])}\r\n'.encode('utf-8'))
            self.conn.send(f':server 366 {self.nickname} {channel} :Fim da lista de /NAMES.\r\n'.encode('utf-8'))
            self.server.broadcast(channel, f':server NOTICE {channel} :{self.nickname} agora está online\r\n')
            print(f"Usuário {self.nickname} entrou no canal {channel}.")
        else:
            self.conn.send(f':server 403 {self.nickname} {channel} :Canal inexistente\r\n'.encode('utf-8'))

    def handle_part(self, message):
        parts = message.split(' ')
        if len(parts) < 2:
            self.conn.send(f':server 461 {self.nickname} PART :Parâmetros insuficientes\r\n'.encode('utf-8'))
            return
        channel = parts[1]
        if channel in self.server.channels and self in self.server.channels[channel]:
            self.server.channels[channel].remove(self)
            self.channels.remove(channel)
            self.server.broadcast(channel, f':{self.nickname} PART {channel}\r\n')
            self.server.broadcast(channel, f':server NOTICE {channel} :{self.nickname} agora está offline\r\n')
            print(f"Usuário {self.nickname} saiu do canal {channel}.")
        else:
            self.conn.send(f':server 442 {self.nickname} {channel} :Você não está neste canal\r\n'.encode('utf-8'))

    def handle_quit(self, message):
        self.disconnect()

    def handle_privmsg(self, message):
        parts = message.split(' ', 2)
        if len(parts) == 3:
            target = parts[1]
            msg = parts[2][1:]
            if target.startswith("#"):
                if target in self.server.channels and self in self.server.channels[target]:
                    self.server.broadcast(target, f':{self.nickname} PRIVMSG {target} :{msg}\r\n', exclude_self=True)
            else:
                if target in self.server.nicknames:
                    self.server.nicknames[target].conn.send(f':{self.nickname} PRIVMSG {target} :{msg}\r\n'.encode('utf-8'))
                    print(f"Mensagem privada de {self.nickname} para {target}: {msg}")
                else:
                    self.conn.send(f':server 401 {self.nickname} {target} :Nick/canal inexistente\r\n'.encode('utf-8'))
        else:
            self.conn.send(f':server 461 {self.nickname} PRIVMSG :Parâmetros insuficientes\r\n'.encode('utf-8'))

    def handle_names(self, message):
        parts = message.split(' ')
        if len(parts) < 2:
            for channel, users in self.server.channels.items():
                self.conn.send(f':server 353 {self.nickname} = {channel} :{" ".join([client.nickname for client in users])}\r\n'.encode('utf-8'))
                self.conn.send(f':server 366 {self.nickname} {channel} :Fim da lista de /NAMES.\r\n'.encode('utf-8'))
            return
        channel = parts[1]
        if channel in self.server.channels:
            users = ' '.join([client.nickname for client in self.server.channels[channel]])
            self.conn.send(f':server 353 {self.nickname} = {channel} :{users}\r\n'.encode('utf-8'))
            self.conn.send(f':server 366 {self.nickname} {channel} :Fim da lista de /NAMES.\r\n'.encode('utf-8'))
        else:
            self.conn.send(f':server 403 {self.nickname} {channel} :Canal inexistente\r\n'.encode('utf-8'))

    def handle_list(self, message):
        if len(self.server.channels) == 0:
            self.conn.send(f':server 321 {self.nickname} :Canal :Usuários  Nome\r\n'.encode('utf-8'))
            self.conn.send(f':server 323 {self.nickname} :Fim de /LIST\r\n'.encode('utf-8'))
        else:
            for channel, users in self.server.channels.items():
                self.conn.send(f':server 322 {self.nickname} {channel} {len(users)} :{" ".join([client.nickname for client in users])}\r\n'.encode('utf-8'))
            self.conn.send(f':server 323 {self.nickname} :Fim de /LIST\r\n'.encode('utf-8'))

    def handle_ping(self, message):
        payload = message.split(' ', 1)[1]
        self.conn.send(f'PONG :{payload}\r\n'.encode('utf-8'))

    def disconnect(self):
        if self.nickname:
            del self.server.nicknames[self.nickname]
        for channel in self.channels:
            if self in self.server.channels.get(channel, []):
                self.server.channels[channel].remove(self)
                self.server.broadcast(channel, f':{self.nickname} PART {channel}\r\n')
                self.server.broadcast(channel, f':server NOTICE {channel} :{self.nickname} agora está offline\r\n')
        self.conn.close()
        print(f"Usuário {self.nickname} desconectado.")

if __name__ == '__main__':
    server = IRCServer()
    server.start()
