import socket
import struct
import time
import threading


def server_state_udp(ip, tcp_p, udp_p):
    udp_dest_port = udp_p
    tcp_port = tcp_p
    network_ip = ip

    magic_cookie = 0xfeedbeef
    offer_message_type = 0x2

    message_to_send = struct.pack('Ibh', magic_cookie, offer_message_type, tcp_port)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet # UDP

    counter = 0
    while counter < 10:
        udp_socket.sendto(message_to_send, (network_ip, udp_dest_port))
        print("offer announcement...")
        time.sleep(1)
        counter += 1
    udp_socket.close()


def server_state_tcp(ip, tcp_p):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, tcp_p))
    s.listen(1)
    time.sleep(2)
    print("Server started, listening on IP address {}".format(ip))
    conn, addr = s.accept()

    while 1:
        data = conn.recv(20)
        if not data:
            break
        conn.send(data)  # echo
        conn.close()


if __name__ == "__main__":
    IP_NETWORK = socket.gethostbyname(socket.gethostname())
    IP_LOCAL = "“localhost”"
    TCP_PORT = 2032
    UDP_DEST_PORT = 13117

    tcp_thread = threading.Thread(target=server_state_tcp, args=(IP_NETWORK, TCP_PORT))
    udp_thread = threading.Thread(target=server_state_udp, args=(IP_NETWORK, TCP_PORT, UDP_DEST_PORT))

    udp_thread.start()
    tcp_thread.start()
