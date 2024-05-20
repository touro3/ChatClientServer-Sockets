import socket
import threading
from queue import Queue

class Cliente:
    def __init__(self, conexao, endereco):
        self.conexao = conexao
        self.endereco = endereco
        self.buffer = b''
        self.nick = None
        self.canal = None
        self.ativo = True

    def enviar(self, mensagem):
        self.conexao.sendall(mensagem.encode())

    def receber(self):
        dados = self.conexao.recv(1024)
        if not dados:
            self.desconectar()
        else:
            self.buffer += dados
            linhas = self.buffer.split(b'\r\n')
            self.buffer = linhas.pop() if linhas[-1] != b'' else b''
            return [linha.decode() for linha in linhas]

    def desconectar(self):
        self.ativo = False
        self.conexao.close()

class Servidor:
    def __init__(self, host, porta):
        self.host = host
        self.porta = porta
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientes = []
        self.fila_mensagens = Queue()
        self.canais = {}
        self._iniciar()

    def _iniciar(self):
        self.socket_servidor.bind((self.host, self.porta))
        self.socket_servidor.listen()
        print(f"Servidor IRC iniciado em {self.host}:{self.porta}")
        threading.Thread(target=self._escutar).start()

    def _escutar(self):
        while True:
            conexao, endereco = self.socket_servidor.accept()
            cliente = Cliente(conexao, endereco)
            self.clientes.append(cliente)
            threading.Thread(target=self._atender_cliente, args=(cliente,)).start()

    def _atender_cliente(self, cliente):
        cliente.enviar("Conectado ao servidor IRC. Digite /help para ver os comandos disponíveis.\r\n")
        while cliente.ativo:
            mensagens = cliente.receber()
            if mensagens:
                for mensagem in mensagens:
                    self._processar_comando(cliente, mensagem)
        self.clientes.remove(cliente)

    def _processar_comando(self, cliente, mensagem):
        partes = mensagem.split()
        if not partes:  # Verifica se 'partes' está vazio
            cliente.enviar("Comando vazio. Digite /help para ver os comandos disponíveis.\r\n")
            return

        comando = partes[0]
        if comando == "NICK":
            self._comando_nick(cliente, partes)
        elif comando == "USER":
            self._comando_user(cliente, partes)
        elif comando == "JOIN":
            self._comando_join(cliente, partes)
        elif comando == "PART":
            self._comando_part(cliente, partes)
        elif comando == "QUIT":
            self._comando_quit(cliente, partes)
        elif comando == "PRIVMSG":
            self._comando_privmsg(cliente, partes)
        elif comando == "NAMES":
            self._comando_names(cliente, partes)
        elif comando == "PING":
            self._comando_ping(cliente, partes)
        elif comando == "/help":
            self._comando_help(cliente)
        else:
            cliente.enviar("Comando desconhecido. Digite /help para ver os comandos disponíveis.\r\n")

    def _comando_nick(self, cliente, partes):
        if len(partes) != 2:
            cliente.enviar("Uso incorreto do comando. Uso correto: NICK <username>\r\n")
            return
        nick = partes[1]
        if not self._validar_nick(nick):
            cliente.enviar("Nome de usuário inválido.\r\n")
            return
        if self._nick_em_uso(nick):
            cliente.enviar(f"O nickname {nick} já está em uso.\r\n")
            return
        cliente.nick = nick
        cliente.enviar(f"Seu nickname foi definido como {nick}.\r\n")

    def _validar_nick(self, nick):
        return nick.isalnum() and len(nick) <= 9

    def _nick_em_uso(self, nick):
        for c in self.clientes:
            if c.nick == nick:
                return True
        return False

    def _comando_user(self, cliente, partes):
        if len(partes) != 2:
            cliente.enviar("Uso incorreto do comando. Uso correto: USER <username>\r\n")
            return

        username = partes[1]
        cliente.username = username
        cliente.enviar(f"Seu nome de usuário foi definido como {username}.\r\n")


    def _comando_join(self, cliente, partes):
        if len(partes) != 2 or not partes[1].startswith("#"):
            cliente.enviar("Uso incorreto do comando. Uso correto: JOIN #<canal>\r\n")
            return
        canal = partes[1]
        cliente.canal = canal
        if canal not in self.canais:
            self.canais[canal] = []
        self.canais[canal].append(cliente)
        cliente.enviar(f"Entrou no canal {canal}.\r\n")
        self._enviar_mensagem_para_canal(cliente, f"{cliente.nick} entrou no canal.")

    def _enviar_mensagem_para_canal(self, cliente_origem, mensagem):
        canal = cliente_origem.canal
        if canal in self.canais:
            for cliente in self.canais[canal]:
                if cliente != cliente_origem:
                    cliente.enviar(f"{cliente_origem.nick}: {mensagem}\r\n")

    def _comando_part(self, cliente, partes):
        if len(partes) != 2 or not partes[1].startswith("#"):
            cliente.enviar("Uso incorreto do comando. Uso correto: PART #<canal>\r\n")
            return
        canal = partes[1]
        if canal in self.canais:
            self.canais[canal].remove(cliente)
            cliente.enviar(f"Saiu do canal {canal}.\r\n")
            self._enviar_mensagem_para_canal(cliente, f"{cliente.nick} saiu do canal.")
            cliente.canal = None
        else:
            cliente.enviar(f"Você não está no canal {canal}.\r\n")

    def _comando_quit(self, cliente, partes):
        motivo = " ".join(partes[1:]) if len(partes) > 1 else "Saindo"
        mensagem_quit = f"{cliente.nick} saiu ({motivo})."
        self._enviar_mensagem_para_canal(cliente, mensagem_quit)
        cliente.desconectar()

    def _comando_privmsg(self, cliente, partes):
        if len(partes) < 3 or not partes[1].startswith("#"):
            cliente.enviar("Uso incorreto do comando. Uso correto: PRIVMSG #<canal> <mensagem>\r\n")
            return
        canal = partes[1]
        mensagem = " ".join(partes[2:])
        self._enviar_mensagem_para_canal(cliente, f"{cliente.nick}: {mensagem}")

    def _comando_names(self, cliente, partes):
        if len(partes) != 2 or not partes[1].startswith("#"):
            cliente.enviar("Uso incorreto do comando. Uso correto: NAMES #<canal>\r\n")
            return
        canal = partes[1]
        if canal in self.canais:
            usuarios = " ".join([c.nick for c in self.canais[canal]])
            cliente.enviar(f"Usuários no canal {canal}: {usuarios}\r\n")
        else:
            cliente.enviar(f"Você não está no canal {canal}.\r\n")

    def _comando_ping(self, cliente, partes):
        payload = partes[1]
        cliente.enviar(f"PONG :{payload}\r\n")

    def _comando_help(self, cliente):
        cliente.enviar("""
            Lista de comandos disponíveis:
            /NICK <username>: Altera o nome de usuário.
            /JOIN #<canal>: Entra em um canal.
            /PART #<canal>: Sai de um canal.
            /QUIT :<motivo>: Sai do servidor IRC.
            /PRIVMSG #<canal> <mensagem>: Envia uma mensagem para um canal.
            /NAMES #<canal>: Lista os usuários de um canal.
            /PING :<payload>: Verifica a conexão com o servidor.
            /HELP: Exibe esta mensagem de ajuda.
            """)

    def iniciar(self):
        while True:
            conexao, endereco = self.socket_servidor.accept()
            cliente = Cliente(conexao, endereco)
            threading.Thread(target=self._atender_cliente, args=(cliente,)).start()

if __name__ == "__main__":
    servidor = Servidor('localhost', 6667)
    servidor.iniciar()
