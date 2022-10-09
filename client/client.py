import socket
import os


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in server.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """
    print("Receiving message from server.....")
    res_content = b''
    while True:
        # print("IN")
        _encodedData = active_socket.recv(buffer_size)
        # res_content.extend(_encodedData)
        if _encodedData[-10:] == eof_token.encode():
            # print("IN-if")
            res_content += _encodedData[:-10]
            # print("IN-if-OUT")
            break
        else:
            # print("IN-eles")
            res_content += _encodedData
            # print("IN-else-OUT")
    # print("OUT")
    return res_content

    # raise NotImplementedError('Your implementation here.')


def initialize(host, port):
    """
    1) Creates a socket object and connects to the server.
    2) receives the random token (10 bytes) used to indicate end of messages.
    3) Displays the current working directory returned from the server (output of get_working_directory_info() at the server).
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param host: the ip address of the server
    :param port: the port number of the server
    :return: the created socket object
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    global eof_token
    eof_token = client.recv(1024).decode()
    # _ack,message = data.split('|')
    # if cmd == "DISCONNECTED":
    #     print(f"[CLIENT---SERVER]: {msg}")
    #     break
    # elif cmd == "200":
    #     print(f"{msg}")

    print('Connected to server at IP:', host, 'and Port:', port)

    print('Handshake Done. EOF is:', eof_token)
    cwd = f'{receive_message_ending_with_token(client,1024,eof_token).decode()}'
    print(cwd)
    return client

    # raise NotImplementedError('Your implementation here.')


def issue_cd(command_and_arg, client_socket, eof_token):
    """
    Sends the full cd command entered by the user to the server. The server changes its cwd accordingly and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_socket.sendall((command_and_arg+eof_token).encode())
    print(f'{receive_message_ending_with_token(client_socket,1024,eof_token).decode()}')
    # getUserInput(client_socket)
    # raise NotImplementedError('Your implementation here.')


def issue_mkdir(command_and_arg, client_socket, eof_token):
    """
    Sends the full mkdir command entered by the user to the server. The server creates the sub directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_socket.sendall((command_and_arg+eof_token).encode())
    print(f'{receive_message_ending_with_token(client_socket,1024,eof_token).decode()}')
    # getUserInput(client_socket)
    # raise NotImplementedError('Your implementation here.')


def issue_rm(command_and_arg, client_socket, eof_token):
    """
    Sends the full rm command entered by the user to the server. The server removes the file or directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_socket.sendall((command_and_arg+eof_token).encode())
    print(f'{receive_message_ending_with_token(client_socket,1024,eof_token).decode()}')
    # getUserInput(client_socket)
    # raise NotImplementedError('Your implementation here.')


def issue_ul(command_and_arg, client_socket, eof_token):
    """
    Sends the full ul command entered by the user to the server. Then, it reads the file to be uploaded as binary
    and sends it to the server. The server creates the file on its end and sends back the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    command, arguments = command_and_arg
    try:
        # print("\n\ncwd:\n",os.getcwd())
        with open(arguments, 'rb') as file:
            fileContent = file.read()
        fileContentWithToken = fileContent + eof_token.encode()
        client_socket.sendall((" ".join(command_and_arg)+eof_token).encode())
        print(f'[LOG]Uploding the file "{arguments}" to: server')
        # print("fileContentWithToken",fileContentWithToken)
        client_socket.sendall(fileContentWithToken)
        print(f'[LOG]File "{arguments}" uploaded to: server')
        print(f'{receive_message_ending_with_token(client_socket,1024,eof_token).decode()}')
    except:
        print("[LOG] Somthing Went wrong...  :(")
    # getUserInput(client_socket)
    # raise NotImplementedError('Your implementation here.')


def issue_dl(command_and_arg, client_socket, eof_token):
    """
    Sends the full dl command entered by the user to the server. Then, it receives the content of the file via the
    socket and re-creates the file in the local directory of the client. Finally, it receives the latest cwd info from
    the server.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    :return:
    """
    command, arguments = command_and_arg
    try:
        client_socket.sendall((" ".join(command_and_arg)+eof_token).encode())
        print(f'[LOG]Waiting for server responce for the file "{arguments}"')
        fileContent = receive_message_ending_with_token(
            client_socket, 1024, eof_token)
        print(f'[LOG]File "{arguments}" recived from server')
        print(f'[LOG]Saving file "{arguments}" to the root folder.')
        if fileContent != b'404':
            with open(arguments, 'wb') as file:
                file.write(fileContent)
            file.close()
            print(f'[LOG]File "{arguments}" saved to the root folder.')
            print(f'{receive_message_ending_with_token(client_socket,1024,eof_token).decode()}')
        else:
            print(str(fileContent))
    except:
        print("[LOG] Somthing Went wrong...  :(")
    # getUserInput(client_socket)
    # raise NotImplementedError('Your implementation here.')


# def getUserInput(connection):


def main():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    # raise NotImplementedError('Your implementation here.')

    # initialize
    connection = initialize(HOST, PORT)

    # get user input
    while True:
        userInput = input("> ")
        try:
            command = userInput.split(" ", 1)[0].lower()
        except:
            command = ""
        try:
            arguments = userInput.split(" ", 1)[1]
        except:
            arguments = ""
        if (command == "cd"):
            issue_cd(userInput, connection, eof_token)
        elif (command == "mkdir"):
            issue_mkdir(userInput, connection, eof_token)
        elif (command == "rm"):
            issue_rm(userInput, connection, eof_token)
        elif (command == "ul"):
            # issue_ul(userInput,connection,eof_token)
            issue_ul([command, arguments], connection, eof_token)
        elif (command == "dl"):
            issue_dl([command, arguments], connection, eof_token)
        elif (command == "exit"):
            print('Exiting the application.')
            connection.sendall(("exit"+eof_token).encode())
            break
        else:
            print("Please Enter valid command")
        # getUserInput(connection)

    # call the corresponding command function or exit

    # print('Exiting the application.')


if __name__ == '__main__':
    # global bufferSize = 1024
    main()
