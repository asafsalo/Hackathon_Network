import socket
import numpy
#from scapy import get_if_addr

IP_NETWORK = socket.gethostbyname(socket.gethostname())

IP_LOCAL = "“localhost”"
UDP_PORT = 13117
BUFFER_SIZE = 1024
TEAM_NAME = "Yael and Asar\n"

sock_udp = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
sock_udp.bind((IP_NETWORK, UDP_PORT))

print(IP_NETWORK)  #need to be deleted
print("​Client started, listening for offer requests...")

while True:
    MESSAGE, SERVER_ADD = sock_udp.recvfrom(7) # buffer size is 7 bytes
    print("Received offer from %s, attempting to connect...​" % IP_NETWORK)
    print(MESSAGE[:-2])
 
    # sock_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock_TCP.connect((TCP_IP_SERVER, TCP_PORT))
    # sock_TCP.send(MESSAGE)
    # data = sock_TCP.recv(BUFFER_SIZE)
    # sock_TCP.close()