import threading
import socket
import time

class ClienteIRC:
    def __init__(self):
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nick = None
        self.canal_atual = None
        self.host = None
        self.porta = None
        self.ativo = False

    def conectar(self, endereco, porta):
        self.host = endereco
        self.porta = porta
        try:
            self.socket_cliente.connect((endereco, porta))
            self.ativo = True
            threading.Thread(target=self._receber_mensagens).start()
            print(f"Conectado ao servidor IRC em {endereco}:{porta}")
        except Exception as e:
            print(f"Erro ao conectar: {str(e)}")

    def _receber_mensagens(self):
        while self.ativo:
            try:
                mensagem = self.socket_cliente.recv(1024).decode().strip()
                if mensagem:
                    print(mensagem)
                    if mensagem.startswith("PING"):
                        self.enviar_comando("PONG" + mensagem[4:])
            except Exception as e:
                print(f"Erro ao receber mensagem: {str(e)}")
                self.desconectar()

    def enviar_comando(self, comando):
        if self.ativo:
            try:
                self.socket_cliente.sendall(comando.encode())
            except Exception as e:
                print(f"Erro ao enviar comando: {str(e)}")

    def enviar_mensagem(self, mensagem):
        if self.ativo and self.canal_atual:
            comando = f"PRIVMSG {self.canal_atual} :{mensagem}\r\n"
            self.enviar_comando(comando)

    def processar_comando(self, comando):
        if not comando:
            print("Comando vazio. Digite /help para ver os comandos disponíveis.")
            return

        partes = comando.split()
        if partes[0] == "/nick":
            if len(partes) == 2:
                self.nick = partes[1]
                self.enviar_comando(f"NICK {self.nick}\r\n")
                self.enviar_comando(f"USER {self.nick} 0 = :{self.nick}\r\n")
            else:
                print("Uso incorreto do comando. Uso correto: /nick <username>")
        elif partes[0] == "/connect":
            if len(partes) == 2:
                endereco = partes[1]
                self.conectar(endereco, 6667)
            else:
                print("Uso incorreto do comando. Uso correto: /connect <IP>")
        elif partes[0] == "/disconnect":
            motivo = " ".join(partes[1:])
            self.desconectar(motivo)
        elif partes[0] == "/quit":
            motivo = " ".join(partes[1:])
            self.desconectar(motivo)
            exit()
        elif partes[0] == "/join":
            if len(partes) == 2:
                canal = partes[1]
                self.enviar_comando(f"JOIN {canal}\r\n")
                self.canal_atual = canal
            else:
                print("Uso incorreto do comando. Uso correto: /join #<canal>")
        elif partes[0] == "/leave" or partes[0] == "/part":
            if len(partes) >= 2:
                canal = partes[1]
                motivo = " ".join(partes[2:])
                self.enviar_comando(f"PART {canal} :{motivo}\r\n")
                self.canal_atual = None
            else:
                print("Uso incorreto do comando. Uso correto: /leave #<canal> <motivo>")
        elif partes[0] == "/channel":
            if len(partes) == 1:
                print(f"Canal atual: {self.canal_atual}")
            else:
                canal = partes[1]
                self.canal_atual = canal
        elif partes[0] == "/list":
            if len(partes) == 1:
                self.enviar_comando("NAMES\r\n")
            else:
                canal = partes[1]
                self.enviar_comando(f"NAMES {canal}\r\n")
        elif partes[0] == "/msg":
            if len(partes) >= 3:
                canal = partes[1]
                mensagem = " ".join(partes[2:])
                self.enviar_mensagem(mensagem)
            else:
                print("Uso incorreto do comando. Uso correto: /msg #<canal> <mensagem>")
        elif partes[0] == "/help":
            print("Lista de comandos disponíveis:\n")
            print("/nick <username>: Altera o nome de usuário.")
            print("/connect <IP>: Conecta ao servidor IRC.")
            print("/disconnect :<motivo>: Desconecta do servidor IRC.")
            print("/quit :<motivo>: Sai do cliente IRC.")
            print("/join #<canal>: Entra em um canal.")
            print("/leave #<canal> <motivo>: Sai de um canal.")
            print("/channel #<canal>: Seleciona um canal padrão.")
            print("/list #<canal>: Lista os usuários de um canal.")
            print("/msg #<canal> <mensagem>: Envia uma mensagem para um canal.")
            print("/help: Exibe esta mensagem de ajuda.")
        else:
            print("Comando desconhecido. Digite /help para ver os comandos disponíveis.")

    def desconectar(self, motivo="Saindo"):
        if self.ativo:
            self.enviar_comando(f"QUIT :{motivo}\r\n")
            self.socket_cliente.close()

cliente = ClienteIRC()

while True:
    comando = input("Cliente IRC iniciado. Use /help para listar os comandos disponíveis.\n")
    cliente.processar_comando(comando)
