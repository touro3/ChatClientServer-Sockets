
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
