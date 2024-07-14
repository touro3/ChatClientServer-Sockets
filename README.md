# IRC Instant Messaging System

## System Overview
This instant messaging system is based on the IRC (Internet Relay Chat) protocol and consists of two main components:

- **Server (server.py)**: Manages communication between clients, distributing messages, and maintaining information about users and channels.
- **Client (client.py)**: User interface that allows interaction with the server, sending, and receiving messages.

---

## Client (client.py)
The client allows the user to connect to the IRC server, send commands, and receive messages.

### User Commands
- **/connect <host>**: Connects to the IRC server.
- **/nick <username>**: Sets the user's nickname.
- **/disconnect <reason>**: Disconnects from the IRC server.
- **/quit <reason>**: Exits the IRC client.
- **/join <channel>**: Joins a channel. **If the channel does not exist, it is created**
- **/leave <channel> <reason>**: Leaves a channel.
- **/channel <channel>**: Sets the current channel or lists the channels the user is participating in.
- **/list**: Lists available channels.
- **/names <channel>**: Lists users in a channel.
- **/msg <channel> <message>**: Sends a message to a channel. If the channel is not specified, sends to the default channel if it exists.
- **/help**: Shows the list of available commands.
- **ping <message>**: Sends a ping to the server.

### Features
- **Start Client**
  - **Method**: `main()`
  - **Description**: Initializes the client and starts processing user commands.
  - **Usage**: Running the `cliente.py` script starts the client.

- **Run Client**
  - **Method**: `executar()`
  - **Description**: Main loop that waits for and processes user commands.
  - **Usage**: Called by the `main()` method.

- **Connect to Server**
  - **Method**: `conectar(host, port=6667)`
  - **Description**: Establishes a TCP connection with the server and sends the NICK and USER commands.
  - **Usage**: User command `/connect <host>`.

- **Send Data**
  - **Method**: `enviar_dados(msg)`
  - **Description**: Sends encoded data to the server.
  - **Usage**: Internally called when processing commands.

- **Receive Data**
  - **Method**: `receber_dados()`
  - **Description**: Receives data from the server and processes received commands.
  - **Usage**: Internally called in a separate thread.

- **Process Server Commands**
  - **Method**: `processar_comando(linha)`
  - **Description**: Processes commands received from the server.
  - **Usage**: Internally called upon receiving data.

---

## Server (server.py)
The server is responsible for accepting client connections, processing commands, and managing communication between different users.

### Features

- **Start Server**
  - **Method**: `start()`
  - **Description**: Initializes the server and starts accepting client connections in a separate thread.

- **Accept Connections**
  - **Method**: `accept_connections()`
  - **Description**: Listens to the specified port for new client connections and creates a thread for each connected client using the Cliente class and run() method.

- **Process Commands**
  - **Methods**: `receive_data(), process_commands(), handle_command(command)`
  - **Description**: Within the run function that runs in a loop, it waits to receive data with receive_data(), processes the data, and then handles the commands with handle_command. Depending on the command, other methods are used.

### Implemented IRC Commands
- **NICK**: Sets the user's nickname.
- **USER**: Sets the user's real name.
- **PING**: Checks if the host is still connected.
- **JOIN**: Allows a user to join a channel.
- **PART**: Allows a user to leave a channel.
- **QUIT**: Disconnects the user from the server.
- **PRIVMSG**: Sends private messages to a channel.
- **NAMES**: Lists users in a channel.
- **LIST**: Lists available channels.

---

## How to Run

### Server
To start the server, run the following command in the terminal:
python3 server.py

### Client
To start the client, run the following command in the terminal:
python3 client.py

