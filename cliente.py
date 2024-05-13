#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import socket

class Cliente(Exception):
    def __init__(self):
        self.conectado = False

        signal.signal(signal.SIGALRM, self.exception_handler)

    def exception_handler(self, signum, frame):
        raise 'EXCEÇÃO (timeout)'

    def receber_dados(self):
        pass

    def executar(self):
        cmd = ''
        print('Cliente!')

        while True:
            signal.alarm(20)
            try:
                cmd = input()
            except Exception as e:
                print()
                continue
            signal.alarm(0)

            # Um comando foi digitado. Tratar!
            # ...
            

def main():
    c = Cliente()
    c.executar()


if __name__ == '__main__':
    main()
