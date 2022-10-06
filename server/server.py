import socket
import random
import string
from threading import Thread
import os
import time
import shutil
from pathlib import Path


def get_working_directory_info(working_directory):
    """
    Creates a string representation of a working directory and its contents.
    :param working_directory: path to the directory
    :return: string of the directory and its contents.
    """
    dirs = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_dir()])
    files = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_file()])
    dir_info = f'Current Directory: {working_directory}:\n|{dirs}{files}'
    return dir_info


def generate_random_eof_token():
    """Helper method to generates a random token that starts with '<' and ends with '>'.
     The total length of the token (including '<' and '>') should be 10.
     Examples: '<1f56xc5d>', '<KfOVnVMV>'
     return: the generated token.
     """
    return '<'+''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=8))+'>'


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in client.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """
    print("Receiving message from client.....")
    res_content = b''
    while True:
        _encodedData = active_socket.recv(buffer_size)
        # print("_encodedData",_encodedData)
        # res_content.extend(_encodedData)
        if _encodedData[-10:] == eof_token.encode():
            res_content += _encodedData[:-10]
            break
        else:
            res_content += _encodedData
    # print(res_content)
    return res_content
    # raise NotImplementedError('Your implementation here.')


def handle_cd(current_working_directory, new_working_directory):
    """
    Handles the client cd commands. Reads the client command and changes the current_working_directory variable 
    accordingly. Returns the absolute path of the new current working directory.
    :param current_working_directory: string of current working directory
    :param new_working_directory: name of the sub directory or '..' for parent
    :return: absolute path of new current working directory
    """
    # print(current_working_directory,new_working_directory)
    if new_working_directory == "..":
        os.chdir("..")
    elif " " not in new_working_directory:
        os.chdir(new_working_directory)
    return get_working_directory_info(os.getcwd())
    # raise NotImplementedError('Your implementation here.')


def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """
    if " " not in directory_name:
        os.mkdir(os.path.join(os.getcwd(),directory_name))
    return get_working_directory_info(os.getcwd())
    # raise NotImplementedError('Your implementation here.')


def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """
    if " " not in object_name:
        os.remove(os.path.join(os.getcwd(),object_name))
    return get_working_directory_info(os.getcwd())
    # raise NotImplementedError('Your implementation here.')


def handle_ul(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
    file in the current working directory.
    Use the helper method: receive_message_ending_with_token() to receive the message from the client.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be created.
    :param service_socket: active socket with the client to read the payload/contents from.
    :param eof_token: a token to indicate the end of the message.
    """
    fileContent = receive_message_ending_with_token(service_socket,1024,eof_token)
    with open(file_name, 'wb') as file:
        file.write(fileContent)
    file.close()
    return get_working_directory_info(os.getcwd())
    # raise NotImplementedError('Your implementation here.')


def handle_dl(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
    given socket.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be sent to client
    :param service_socket: active service socket with the client
    :param eof_token: a token to indicate the end of the message.
    """
    with open(file_name, 'rb') as file:
        fileContent = file.read()
    fileContentWithToken = fileContent + eof_token.encode()
    # print(f'[LOG]Uploding the file "{file_name}" to: server')
    # print("fileContentWithToken",fileContentWithToken)
    print(f'[LOG]Sending the file "{file_name}" to: client')
    service_socket.sendall(fileContentWithToken)
    print(f'[LOG]File "{file_name}" sent to: client')
    print('Sending cwd.')
    time.sleep(1)
    return get_working_directory_info(os.getcwd())
    # raise NotImplementedError('Your implementation here.')


class ClientThread(Thread):
    def __init__(self, service_socket : socket.socket, address : str):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address

    def run(self):
        print ("Incomming connection from : ", self.address)
        # raise NotImplementedError('Your implementation here.')
        # initialize the connection
        # send random eof token
        endOfFileToken = generate_random_eof_token()
        self.service_socket.send(endOfFileToken.encode())


        # establish working directory
        _cwd = os.getcwd()

        # send the current dir info
        self.service_socket.send((get_working_directory_info(_cwd)+endOfFileToken).encode())


        while True:
            responce = self.service_socket.recv(1024).decode()
            # print("responce",responce)
            try:
                command = responce.split()[0]
            except:
                command = ""
            try:
                arguments = responce.split()[1]
            except:
                arguments = ""
            # get the command and arguments and call the corresponding method
            if(command == "cd"):
                # print("Sending message from server.....")
                self.service_socket.send((handle_cd(get_working_directory_info(_cwd),arguments)+endOfFileToken).encode())
                # print("Message sent from server.....")
            elif(command == "mkdir"):
                self.service_socket.send((handle_mkdir(get_working_directory_info(_cwd),arguments)+endOfFileToken).encode())
            elif(command=="rm"):
                self.service_socket.send((handle_rm(get_working_directory_info(_cwd),arguments)+endOfFileToken).encode())
            elif(command == "ul"):
                self.service_socket.send((handle_ul(get_working_directory_info(_cwd),arguments,self.service_socket,endOfFileToken)+endOfFileToken).encode())
            elif(command == "dl"):
                self.service_socket.send((handle_dl(get_working_directory_info(_cwd),arguments,self.service_socket,endOfFileToken)+endOfFileToken).encode())
                print('Sent cwd.')
            elif(command=="exit"):
                self.service_socket.close()
                print('Connection closed from:', self.address)
                break

            # send current dir info


        

def main():
    HOST = "127.0.0.1"
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[SERVER-STARTED-LISTENING] Server is available on {HOST}:{PORT}.")
        while True:
            conn, addr = s.accept()
            clientThread = ClientThread(conn, addr)
            clientThread.start()
        # raise NotImplementedError('Your implementation here.')




if __name__ == '__main__':
    main()


