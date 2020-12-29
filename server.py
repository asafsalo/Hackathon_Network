import socket
import struct
import time
import threading

class Server:
    def __init__(self):
        # Server Authorization Parameters
        self.magic_cookie = 0xfeedbeef
        self.offer_message_type = 0x2

        # Server Global Parameters
        self.network_ip = socket.gethostbyname(socket.gethostname())
        self.local_ip = "“localhost”"
        self.tcp_port = 2032
        self.udp_dest_port = 13117
        self.game_mode = False

        # Initiate Threads for server: TCP and UDP Protocols
        tcp_thread = threading.Thread(target=self.server_state_tcp)
        udp_thread = threading.Thread(target=self.server_state_udp)

        # Activate Ports
        tcp_thread.start()
        udp_thread.start()


    def server_state_udp(self):
        # starting socket as UDPSocket
        message_to_send = struct.pack('Ibh', self.magic_cookie, self.offer_message_type, self.tcp_port)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet # UDP

        # sending offers to port 13117 every second for 10 seconds
        counter = 0
        while counter < 10:
            udp_socket.sendto(message_to_send, (self.network_ip, self.udp_dest_port))
            print("offer announcement...")
            time.sleep(1)
            counter += 1
        udp_socket.close()


    def server_state_tcp(self):
        # starting socket as TCPSocket and bind it to our port (2032)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.network_ip, self.tcp_port))
        s.listen(1)
        print("Server started, listening on IP address {}".format(self.network_ip))
        threading.Timer(10.0, self.set_game_mode)

        # listening to the port for 10 sec
        conn, addr = s.accept()
        while 1:
            data = conn.recv(20)
            if not data:
                break
            conn.send(data)  # echo
            conn.close()

    def set_game_mode(self):
        self.game_mode = True


if __name__ == "__main__":