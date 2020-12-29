import socket
import struct


def listen_state(ip, udp_port):

    """ Bind the udp port - 13117 """
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Socket
    sock_udp.bind((ip, udp_port))
    print("Client started, listening for offer requests...")

    """ Client Listen to the udp port - 13117, until catch a message """
    while True:
        message, server_address = sock_udp.recvfrom(7)  # buffer size is 7 bytes
        print("Received offer from {}, attempting to connect...".format(server_address[0]))

        """ Handle properly message and extract the server's port number """
        unpack_message = struct.unpack('Ibh', message)
        if len(unpack_message) == 3 and unpack_message[0] == magic_cookie and unpack_message[1] == offer_message_type:
            return unpack_message[2]


def connect_server_state(ip, server_port_connect):
    """ Try to connect the server and return a socket if succeed """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((ip, server_port_connect))
    return tcp_socket


def send_details_to_server(sock_tcp, buffer_s, team):
    """ Send Team-Name """
    sock_tcp.send(team)
    sock_tcp.recv(buffer_s)
    game_state(sock_tcp)


def game_state(sock_tcp):
    pass


if __name__ == "__main__":

    # Server Authorization Parameters
    magic_cookie = 0xfeedbeef
    offer_message_type = 0x2

    # Client Global Parameters
    ip_network = socket.gethostbyname(socket.gethostname())
    udp_listen_port = 13117
    buffer_size = 1024
    team_name = "Yael and Asar\n"

    while True:
        server_port = listen_state(ip_network, udp_listen_port)
        connection = connect_server_state(ip_network, server_port)
        if connection:
            send_details_to_server(connection, buffer_size, team_name)