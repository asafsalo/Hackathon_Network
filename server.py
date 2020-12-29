import numpy
import scapy
import socket
import struct
import time
import threading

def server_state_udp(ip, tcp_p, udp_p):
    udp_dest_port = udp_p
    tcp_port = tcp_p
    network_ip = ip

    magic_cookie = "0xfeedbeef"
    message_type = "0x2"

    MESSAGE = bytes(magic_cookie + message_type + tcp_port, "utf-8")

    SOCK_UDP = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    counter = 0
    while counter < 2:
        SOCK_UDP.sendto(MESSAGE, (network_ip, udp_dest_port))
        print("lisining on....")
        time.sleep(1)
        counter += 1

    SOCK_UDP.close()


def server_state_tcp(ip ,tcp_p):
    tcp_port = tcp_p
    network_ip = ip

    print("Server started, listening on IP address {}".format(network_ip))
    print(tcp_port)


if __name__=="__main__":
    IP_NETWORK = socket.gethostbyname(socket.gethostname())
    IP_LOCAL = "“localhost”"
    TCP_PORT = "2032"
    UDP_DEST_PORT = 13117

    server_state_tcp(IP_NETWORK, TCP_PORT)
    server_state_udp(IP_NETWORK, TCP_PORT, UDP_DEST_PORT)