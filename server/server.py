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
    # message="[LOG] Somthing Went wrong...  :("
    if new_working_directory == "..":
        os.chdir("..")
        # message="[LOG] Command executed successfully.  :)"
    elif os.path.exists(os.path.join(current_working_directory,new_working_directory)) and os.path.isdir(os.path.join(current_working_directory,new_working_directory)):
        # print("\n\nbefore:\n",os.path.join(current_working_directory,new_working_directory))
        os.chdir(os.path.join(current_working_directory,new_working_directory))
        # print("\n\nafter:\n",os.path.join(current_working_directory,new_working_directory))
        # message="[LOG] Command executed successfully.  :)"
    else:
        print("[LOG] Somthing Went wrong...  :(")
    return os.path.abspath(os.getcwd())
    # raise NotImplementedError('Your implementation here.')


def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """
    # if " " not in directory_name:
    try:
        os.mkdir(os.path.join(current_working_directory,directory_name))
        # message="[LOG] Command executed successfully.  :)"
    except:
        print("[LOG] Somthing Went wrong...  :(")
    # raise NotImplementedError('Your implementation here.')


def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """
    # message="[LOG] Somthing Went wrong...  :("
    if os.path.exists(os.path.join(current_working_directory,object_name)):
        if os.path.isfile(os.path.join(current_working_directory,object_name)):
            os.remove(os.path.join(current_working_directory,object_name))
            # message="[LOG] Command executed successfully.  :)"
        else:
            shutil.rmtree(os.path.join(current_working_directory,object_name))
            # message="[LOG] Command executed successfully.  :)"
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
    try:
        fileContent = receive_message_ending_with_token(service_socket,1024,eof_token)
        with open(os.path.join(current_working_directory,file_name), 'wb') as file:
            file.write(fileContent)
        file.close()
        # message="[LOG] Command executed successfully.  :)"
    except:
        print("[LOG] Somthing Went wrong...  :(")
        # message="[LOG] Somthing Went wrong...  :("
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
    # message="[LOG] Somthing Went wrong...  :("
    try:
        if os.path.exists(os.path.join(current_working_directory,file_name)) and os.path.isfile(os.path.join(current_working_directory,file_name)):
            with open(os.path.join(current_working_directory,file_name), 'rb') as file:
                fileContent = file.read()
            fileContentWithToken = fileContent + eof_token.encode()
            # print(f'[LOG]Uploding the file "{file_name}" to: server')
            # print("fileContentWithToken",fileContentWithToken)
            print(f'[LOG]Sending the file "{file_name}" to: client')
            service_socket.sendall(fileContentWithToken)
            print(f'[LOG]File "{file_name}" sent to: client')
            # message="[LOG] Command executed successfully.  :)"
        else:
            service_socket.sendall(b"404"+eof_token.encode())
    except:
        print("[LOG] Somthing Went wrong...  :(")
        service_socket.sendall(b"[LOG] Somthing Went wrong...  :("+eof_token.encode())
        # message="[LOG] Somthing Went wrong...  :("
    time.sleep(1.5)
    # raise NotImplementedError('Your implementation here.')


class ClientThread(Thread):
    def __init__(self, service_socket : socket.socket, address : str):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address
    
    def setCWD(self,workingDirectory):
        self.workingDirectory = workingDirectory

    def run(self):
        print ("Incomming connection from : ", self.address)
        # raise NotImplementedError('Your implementation here.')
        # initialize the connection
        # send random eof token
        endOfFileToken = generate_random_eof_token()
        self.service_socket.send(endOfFileToken.encode())


        # establish working directory
        self.setCWD(initDirectory)
        # print("\n\nworkingDirectory\n",self.workingDirectory)

        # send the current dir info
        self.service_socket.send((get_working_directory_info(self.workingDirectory)+endOfFileToken).encode())


        while True:
            # responce = self.service_socket.recv(1024).decode()
            # print("responce",responce)
            responce = receive_message_ending_with_token(self.service_socket,1024,endOfFileToken).decode()
            try:
                command = responce.split(" ",1)[0].lower()
            except:
                command = ""
            try:
                arguments = responce.split(" ",1)[1]
            except:
                arguments = ""
            # get the command and arguments and call the corresponding method
            cwd=self.workingDirectory
            if(command == "cd"):
                # print("Sending message from server.....")
                cwd = handle_cd(self.workingDirectory,arguments)
                # print("\n\n\ncwd\n",cwd)
                # print("Message sent from server.....")
            elif(command == "mkdir"):
                handle_mkdir(self.workingDirectory,arguments)
            elif(command=="rm"):
                handle_rm(self.workingDirectory,arguments)
            elif(command == "ul"):
                handle_ul(self.workingDirectory,arguments,self.service_socket,endOfFileToken)
            elif(command == "dl"):
                handle_dl(self.workingDirectory,arguments,self.service_socket,endOfFileToken)
                # print('Sent cwd.')
            elif(command=="exit"):
                self.service_socket.close()
                print('Connection closed from:', self.address)
                break
            self.setCWD(cwd)
            self.service_socket.sendall((get_working_directory_info(self.workingDirectory)+endOfFileToken).encode())

            # send current dir info


        

def main():
    HOST = "127.0.0.1"
    PORT = 65432
    global initDirectory
    initDirectory = os.getcwd()

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


