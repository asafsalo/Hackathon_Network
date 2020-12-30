import socket
import struct
from getch import _Getch


class Client:

    def __init__(self):
        # Server Authorization Parameters
        self.magic_cookie = 0xfeedbeef
        self.offer_message_type = 0x2


        # Client Global Parameters
        self.ip_network = socket.gethostbyname(socket.gethostname())
        self.udp_listen_port = 13117
        self.buffer_size = 1024
        self.team_name = "Yael and Asar\n"


    def listen_state(self):
        """ Bind the udp port - 13117 """
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Socket
        sock_udp.bind((self.ip_network, self.udp_listen_port))
        print("Client started, listening for offer requests...")

        """ Client Listen to the udp port - 13117, until catch a message """
        while True:
            message, server_address = sock_udp.recvfrom(7)  # buffer size is 7 bytes
            print("Received offer from {}, attempting to connect...".format(server_address[0]))

            """ Handle properly message and extract the server's port number """
            unpack_message = struct.unpack('Ibh', message)
            if len(unpack_message) == 3 and unpack_message[0] == self.magic_cookie and unpack_message[1] == self.offer_message_type:
                return unpack_message[2]


    def connect_server_state(self, server_port):
        """ Try to connect the server and return a socket if succeed """
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((self.ip_network, server_port))
        return tcp_socket


    def send_details_to_server(self, sock_tcp):
        """ Send Team-Name """
        sock_tcp.send(self.team_name)  
        sock_tcp.recv(self.buffer_size)
        self.game_state(sock_tcp)


    def game_state(self, sock_tcp):
        while True:
            char = _Getch()
            sock_tcp.send(char)
            try:
                message = sock_tcp.recv(self.buffer_size)
                if(len(message) == 0):
                    break
                message_to_print = message.decode("utf-8")
                print(message_to_print)
                
            except: 
                self.listen_state()


if __name__ == "__main__":
    client = Client()

    while True:
        server_port = client.listen_state()
        connection = client.connect_server_state(server_port)
        if connection != None:
            client.send_details_to_server(connection)