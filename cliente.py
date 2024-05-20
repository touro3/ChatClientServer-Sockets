import signal
import socket
import threading

class Cliente:
    def __init__(self):
        self.conectado = False
        self.servidor = None
        self.nick = None
        self.canal_padrao = None
        self.servidor_socket = None
        self.lock = threading.Lock()

        # Exceção para alarme de tempo (não alterar esta linha)
        signal.signal(signal.SIGALRM, self.exception_handler)

    def exception_handler(self, signum, frame):
        raise Exception('EXCEÇÃO (timeout)')

    def conectar(self, ip):
        try:
            self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.servidor_socket.connect((ip, 6667))
            self.conectado = True
            print(f"Conectado ao servidor {ip} na porta 6667")
        except Exception as e:
            print(f"Erro ao conectar no servidor: {e}")

    def enviar_dados(self, mensagem):
        if self.conectado:
            try:
                self.servidor_socket.sendall((mensagem + "\r\n").encode())
            except Exception as e:
                print(f"Erro ao enviar dados: {e}")

    def receber_dados(self):
        while self.conectado:
            try:
                dados = self.servidor_socket.recv(4096).decode()
                if dados:
                    print(dados)
            except Exception as e:
                print(f"Erro ao receber dados: {e}")
                self.desconectar("Erro ao receber dados")
                break

    def executar(self):
        print("Cliente IRC iniciado. Use /help para listar os comandos disponíveis.")
        while True:
            signal.alarm(20)
            try:
                cmd = input()
                signal.alarm(0)
                self.processar_comando(cmd)
            except Exception as e:
                print(e)
                self.verificar_mensagens_servidor()
                continue

    def processar_comando(self, cmd):
        if cmd.startswith("/nick"):
            partes = cmd.split()
            if len(partes) == 2:
                self.nick = partes[1]
                if self.conectado:
                    self.enviar_dados(f"NICK :{self.nick}")
            else:
                print("Uso correto: /nick <username>")
        elif cmd.startswith("/connect"):
            partes = cmd.split()
            if len(partes) == 2:
                threading.Thread(target=self.conectar, args=(partes[1],)).start()
            else:
                print("Uso correto: /connect <IP>")
        elif cmd.startswith("/disconnect"):
            partes = cmd.split(":", 1)
            motivo = partes[1] if len(partes) > 1 else ""
            self.desconectar(motivo)
        elif cmd.startswith("/quit"):
            partes = cmd.split(":", 1)
            motivo = partes[1] if len(partes) > 1 else ""
            self.desconectar(motivo)
            print("Cliente encerrado.")
            exit(0)
        elif cmd.startswith("/join"):
            partes = cmd.split()
            if len(partes) == 2:
                self.enviar_dados(f"JOIN {partes[1]}")
            else:
                print("Uso correto: /join #<canal>")
        elif cmd.startswith("/leave") or cmd.startswith("/part"):
            partes = cmd.split(" ", 2)
            if len(partes) >= 2:
                motivo = partes[2] if len(partes) == 3 else ""
                self.enviar_dados(f"PART {partes[1]} :{motivo}")
            else:
                print("Uso correto: /leave #<canal> <motivo>")
        elif cmd.startswith("/channel"):
            partes = cmd.split()
            if len(partes) == 2:
                self.canal_padrao = partes[1]
                print(f"Canal padrão alterado para {self.canal_padrao}")
            elif len(partes) == 1:
                print(f"Canais: {self.canal_padrao}")
            else:
                print("Uso correto: /channel #<canal>")
        elif cmd.startswith("/list"):
            partes = cmd.split()
            if len(partes) == 2:
                self.enviar_dados(f"NAMES {partes[1]}")
            else:
                if self.canal_padrao:
                    self.enviar_dados(f"NAMES {self.canal_padrao}")
                else:
                    print("Uso correto: /list #<canal>")
        elif cmd.startswith("/msg"):
            partes = cmd.split(" ", 2)
            if len(partes) == 3:
                self.enviar_dados(f"PRIVMSG {partes[1]} :{partes[2]}")
            elif len(partes) == 2 and self.canal_padrao:
                self.enviar_dados(f"PRIVMSG {self.canal_padrao} :{partes[1]}")
            else:
                print("Uso correto: /msg #<canal> <mensagem>")
        elif cmd.startswith("/help"):
            self.exibir_ajuda()
        else:
            print("Comando não reconhecido. Use /help para listar os comandos disponíveis.")

    def desconectar(self, motivo):
        if self.conectado:
            self.enviar_dados(f"QUIT :{motivo}")
            self.servidor_socket.close()
            self.conectado = False
            print("Desconectado do servidor")

    def verificar_mensagens_servidor(self):
        if self.conectado:
            self.receber_dados()

    def exibir_ajuda(self):
        comandos = {
            "/nick": "Altera o nome de usuário. Uso: /nick <username>",
            "/connect": "Conecta ao servidor. Uso: /connect <IP>",
            "/disconnect": "Desconecta do servidor. Uso: /disconnect :<motivo>",
            "/quit": "Encerra o cliente. Uso: /quit :<motivo>",
            "/join": "Entra em um canal. Uso: /join #<canal>",
            "/leave": "Sai de um canal. Uso: /leave #<canal> <motivo>",
            "/channel": "Seleciona canal padrão. Uso: /channel #<canal>",
            "/list": "Lista usuários de um canal. Uso: /list #<canal>",
            "/msg": "Envia mensagem para um canal. Uso: /msg #<canal> <mensagem>",
            "/help": "Lista comandos disponíveis."
        }
        for cmd, desc in comandos.items():
            print(f"{cmd}: {desc}")

def main():
    cliente = Cliente()
    cliente.executar()

if __name__ == "__main__":
    main()
