#!/usr/bin/python

import socket
import time
from collections import deque
from _thread import *

MOTD = '''Message of the Day: Welcome to our IRC Server!'''

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
        # Aqui você deve implementar o processamento dos comandos
        pass

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


def main():
    s = Servidor(host='', port=6667, debug=True)
    s.start()

if __name__ == '__main__':         
    main()
