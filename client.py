import socket
import struct
from getch import _Getch
import time
from scapy.all import*


class Client:
    """
        This Client class.
        use as the player in the game.
        get UDP packets from the server and connect to TCP server
    """

    def __init__(self):
        """
        Initiation to the client class: initiate all the IP's ports and authorization parameter
        """

        # Server Authorization Parameters
        self.magic_cookie = 0xfeedbeef # 0xfeedbeef
        self.offer_message_type = 0x2

        # Client Global Parameters
        self.ip_network = get_if_addr('eth1')
        self.udp_listen_port = 13117
        self.buffer_size = 1024
        self.team_name = "The Secrets\n"
        self.sending_message_time = 8
        self.tcp_socket = None

    def listen_state(self):
        """
            This function means the client is in the listen (to udp) state:
                Client get udp from server, check the TCPs port to connect for starting the game
        """
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.bind(('', self.udp_listen_port))

        print("Client started, listening for offer requests...")

        # Client Listen to the udp port - 13117, until catch a message
        while True:
            try:
                message, addr = sock_udp.recvfrom(buffer_size)  # buffer size is 7 bytes
                print("Received offer from {}, attempting to connect...".format(addr[0]))

                # Handle properly message and extract the server's port number
                unpack_message = struct.unpack('Ibh', message)
                if len(unpack_message) == 3 and \
                        unpack_message[0] == self.magic_cookie and \
                        unpack_message[1] == self.offer_message_type:
                    self.connect_server_state(addr[0], unpack_message[2])
                    break
            except socket.error as e:
                time.sleep(1)


    def connect_server_state(self, server_address, server_port):
        """
        This function Try to connect the server and return a socket if succeed
        :param server_address: the server ip to connect to
        :param server_port: the server port to connect to
        """

        # print("trying to connect ip:{}, port:{}".format(server_address, server_port))
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((server_address, server_port))

    def send_details_to_server(self):
        """
        This function send the Team-Name to the server
        """

        self.sock_tcp.sendto(bytes(self.team_name, 'utf-8'))
        welcome_message, addr = self.sock_tcp.recv(self.buffer_size)
        if welcome_message:
            print(welcome_message)
        self.game_state()

    def game_state(self):
        """
        This function means the client is in the game state:
            meaning: the client sends messages to the server (chars)
                     the client listen to the server respond - "game is over"
        """
        start = time.time()
        while time.time()-start < self.sending_messgae_time:
            try:
                char = _Getch()
                sock_tcp.send(char)
            except:
                # probably server disconnected
                self.listen_state()

        message, addr = self.sock_tcp.recv(self.buffer_size)
        if not len(message) == 0:
            message_to_print = message.decode("utf-8")
            print(message_to_print)
        self.listen_state()

    def run_game(self):
        """
        This function initiate the game
        """

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