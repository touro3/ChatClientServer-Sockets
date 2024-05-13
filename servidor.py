#!/usr/bin/python

import socket
import queue
import time
from collections import deque
from _thread import *

MOTD = ''' servidor '''

class Cliente:
    def __init__(self, conn):
        self.conn = conn

    def receber_dados(self):
        pass

    def enviar_dados(self, msg):
        pass

class Servidor:
    def __init__(self, port=6667):
        self.conns = deque()
        self.port = port

    def run(self, conn):
        Cliente(conn)
        pass

    def listen(self):
        '''
        (não alterar)
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
        '''
        (não alterar)
        Inicia o servidor no método listen e fica em loop infinito.
        '''
        start_new_thread(self.listen, ())

        while True:
            time.sleep(60)
            print('Servidor funcionando...')


def main():
    s = Servidor(host='', port=6667, debug=True)
    s.start()

if __name__ == '__main__':         
    main()
