import socket
import struct
from getch import _Getch
import time
# from scapy.all import*

class Client:

    def __init__(self):
        # Server Authorization Parameters
        self.magic_cookie = 0xfeedbeef # 0xfeedbeef
        self.offer_message_type = 0x2

        # Client Global Parameters
        self.ip_network = "192.168.14.16" # get_if_addr('eth1')
        self.udp_listen_port = 13117
        self.buffer_size = 1024
        self.team_name = "The Secrets\n"
        self.tcp_socket = None

    def listen_state(self):
        """ Bind the udp port - 13117 """
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.bind((self.ip_network, self.udp_listen_port))


        print("Client started, listening for offer requests...")

        """ Client Listen to the udp port - 13117, until catch a message """
        while True:
            try:
                message, addr = sock_udp.recvfrom(self.buffer_size)  # buffer size is 7 bytes
                print("Received offer from {}, attempting to connect...".format(addr[0]))
                """ Handle properly message and extract the server's port number """
                unpack_message = struct.unpack('Ibh', message)
                if len(unpack_message) == 3 and \
                        unpack_message[0] == self.magic_cookie and \
                        unpack_message[1] == self.offer_message_type:
                    self.connect_server_state(addr[0], unpack_message[2])
                    break
            except socket.error as e:
                print("problem")
        self.connect_server_state(addr[0], unpack_message[2])

    def connect_server_state(self, server_address, server_port):
        """ Try to connect the server and return a socket if succeed """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((server_address, server_port))

    def send_details_to_server(self):
        """ Send Team-Name """
        self.sock_tcp.send(bytes(self.team_name.encode('utf-8')))
        self.sock_tcp.recv(self.buffer_size)
        self.game_state()

    def game_state(self):
        while True:
            try:
                char = _Getch()
                sock_tcp.send(char)
                message = self.sock_tcp.recv(self.buffer_size)
                if len(message) == 0:
                    break
                message_to_print = message.decode("utf-8")
                print(message_to_print)
            except: 
                self.listen_state()

    def run_game(self):
        self.listen_state()
        if self.tcp_socket:
            self.send_details_to_server()


if __name__ == "__main__":
    client = Client()
    while True:
        try:
            client.run_game()
        except:
            time.sleep(1)