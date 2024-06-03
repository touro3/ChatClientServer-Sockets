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
import socket
import threading
import signal
import sys

class ClienteIRC:
    def __init__(self, host='localhost', porta=6667):
        self.host = host
        self.porta = porta
        self.sock = None
        self.apelido = None
        self.nome_real = None
        self.conectado = False
        self.canal_padrao = None

    def conectar(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.porta))
        self.conectado = True
        print(f"Conectado a {self.host}:{self.porta}")

        # Iniciar uma thread para escutar mensagens recebidas
        threading.Thread(target=self.receber_mensagens, daemon=True).start()

    def desconectar(self):
        if self.conectado:
            self.enviar_comando(f"QUIT :{self.apelido} saiu")
            self.sock.close()
            self.conectado = False
            print("Desconectado do servidor")

    def enviar_comando(self, comando):
        if self.conectado:
            self.sock.sendall(f"{comando}\r\n".encode('utf-8'))

    def receber_mensagens(self):
        while self.conectado:
            try:
                resposta = self.sock.recv(512).decode('utf-8').strip()
                if resposta:
                    print(f"Servidor: {resposta}")
                    self.lidar_com_mensagem_do_servidor(resposta)
                else:
                    break
            except:
                break
        self.desconectar()

    def lidar_com_mensagem_do_servidor(self, mensagem):
        if mensagem.startswith("PING"):
            payload = mensagem.split(":")[1]
            self.enviar_comando(f"PONG :{payload}")

    def executar(self):
        while True:
            try:
                comando = input("> ").strip()
                if comando.startswith("/connect"):
                    self.lidar_com_conexao(comando)
                elif comando.startswith("/disconnect"):
                    self.lidar_com_desconexao(comando)
                elif comando.startswith("/nick"):
                    self.lidar_com_apelido(comando)
                elif comando.startswith("/user"):
                    self.lidar_com_nome_real(comando)
                elif comando.startswith("/join"):
                    self.lidar_com_entrada_em_canal(comando)
                elif comando.startswith("/leave"):
                    self.lidar_com_saida_de_canal(comando)
                elif comando.startswith("/msg"):
                    self.lidar_com_mensagem_para_canal(comando)
                elif comando.startswith("/quit"):
                    self.lidar_com_saida(comando)
                elif comando.startswith("/channel"):
                    self.lidar_com_canal(comando)
                elif comando.startswith("/list"):
                    self.lidar_com_lista(comando)
                elif comando.startswith("/help"):
                    self.lidar_com_ajuda()
                else:
                    print("Comando desconhecido. Digite /help para ver a lista de comandos.")
            except KeyboardInterrupt:
                self.lidar_com_saida("/quit")
                break

    def lidar_com_conexao(self, comando):
        partes = comando.split(' ')
        if len(partes) == 2:
            self.host = partes[1]
        self.conectar()

    def lidar_com_desconexao(self, comando):
        self.desconectar()

    def lidar_com_apelido(self, comando):
        partes = comando.split(' ')
        if len(partes) == 2:
            self.apelido = partes[1]
            self.enviar_comando(f"NICK {self.apelido}")

    def lidar_com_nome_real(self, comando):
        partes = comando.split(' ', 1)
        if len(partes) == 2:
            self.nome_real = partes[1]
            self.enviar_comando(f"USER {self.apelido} 0 * :{self.nome_real}")

    def lidar_com_entrada_em_canal(self, comando):
        partes = comando.split(' ')
        if len(partes) == 2:
            canal = partes[1]
            self.enviar_comando(f"JOIN {canal}")
            self.canal_padrao = canal
            print(f"Entrou no canal {canal}")

    def lidar_com_saida_de_canal(self, comando):
        partes = comando.split(' ', 2)
        if len(partes) >= 2:
            canal = partes[1]
            motivo = partes[2] if len(partes) == 3 else ""
            self.enviar_comando(f"PART {canal} :{motivo}")
            if self.canal_padrao == canal:
                self.canal_padrao = None
                print(f"Saiu do canal {canal}")

    def lidar_com_mensagem_para_canal(self, comando):
        partes = comando.split(' ', 2)
        if len(partes) == 3:
            canal = partes[1]
            mensagem = partes[2]
            self.enviar_comando(f"PRIVMSG {canal} :{mensagem}")
        elif len(partes) == 2 and self.canal_padrao:
            mensagem = partes[1]
            self.enviar_comando(f"PRIVMSG {self.canal_padrao} :{mensagem}")

    def lidar_com_saida(self, comando):
        partes = comando.split(' ', 1)
        if len(partes) == 2:
            motivo = partes[1]
        else:
            motivo = "Cliente desconectado"
        self.enviar_comando(f"QUIT :{motivo}")
        self.desconectar()
        sys.exit()

    def lidar_com_canal(self, comando):
        partes = comando.split(' ')
        if len(partes) == 2:
            canal = partes[1]
            self.canal_padrao = canal
            print(f"Canal padrão definido para {canal}")
        else:
            print(f"Canal padrão: {self.canal_padrao}")

    def lidar_com_lista(self, comando):
        partes = comando.split(' ')
        if len(partes) == 2:
            canal = partes[1]
            self.enviar_comando(f"NAMES {canal}")
        elif self.canal_padrao:
            self.enviar_comando(f"NAMES {self.canal_padrao}")

    def lidar_com_ajuda(self):
        texto_ajuda = """
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
/help - Moostrar esta mensagem de ajuda
"""
        print(texto_ajuda)

if __name__ == "__main__":
    print("Digite /help para ver os comandos disponíveis.")
    cliente = ClienteIRC()
    cliente.executar()
