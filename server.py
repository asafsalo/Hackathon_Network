import socket
import struct
import time
from scapy.all import*
import threading


class Server:
    def __init__(self):
        # Server Authorization Parameters
        self.magic_cookie = 1000 #0xfeedbeef
        self.offer_message_type = 0x2

        # Server Global Parameters
        self.network_ip = get_if_addr('eth1')
        self.local_ip = "“localhost”"
        self.tcp_port = 2032
        self.udp_dest_port = 13117

        self.threads = []
        self.master_tcp_socket = None
        self.udp_socket = None

        self.timing = 10
        self.game_mode = False
        self.connections = {}  # {key: conn, value: (group_name, groupNumber)}
        self.groups = {1: [], 2: []}  # {key: groupNumber, value: {key: groupName, value: [connection, groupScore]}
        self.groups_scores = {1: 0, 2: 0}
        self.num_of_participants = 0

        # Initiate Threads for server: TCP and UDP Protocols
        self.tcp_thread = threading.Thread(target=self.server_tcp_binding)
        self.udp_thread = threading.Thread(target=self.server_udp_binding)

    def start_server(self):
        # Activate Ports
        self.tcp_thread.start()
        self.udp_thread.start()
        time.sleep(1)
        self.server_state_tcp_listening()

    def server_state_udp(self):
        # starting socket as UDPSocket and bind it to our port ()
        # self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet # UDP
        # Enable broadcasting mode
    
        message_to_send = struct.pack('Ibh', self.magic_cookie, self.offer_message_type, self.tcp_port)

        # sending offers to port 13117 every second for 10 seconds
        counter = 0
        while counter < self.timing:
            self.udp_socket.sendto(message_to_send, ("255.255.255.255", self.udp_dest_port))
            # TODO: remove this print:
            print("offer announcement...")
            time.sleep(1)
            counter += 1
        # udp_socket.close()

    def server_tcp_binding(self):
        # starting socket as TCPSocket and bind it to our port (2032)
        self.master_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master_tcp_socket.bind((self.network_ip, self.tcp_port))

    def server_udp_binding(self):
        # starting socket as UDPSocket and bind it to our port ()
        #self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet # UDP

        # Enable broadcasting mode
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def server_state_tcp_listening(self):
        self.master_tcp_socket.listen(1)
        print("Server started, listening on IP address {}".format(self.network_ip))
        self.server_state_udp()
        t = threading.Timer(self.timing, self.start_game)
        t.start()
        # listening to the port for 10 sec
        while not self.game_mode:
            conn, addr = self.master_tcp_socket.accept()
            while 1:
                team_name = conn.recv(1024)
                if not team_name:
                    conn.close()
                    break
                client_group_num = self.get_group_num()
                self.connections[conn] = (team_name, self.get_group_num())
                self.groups[client_group_num].append((team_name, conn))

    def get_welcome_message(self):
        welcome = "Welcome to Keyboard Spamming Battle Royale."
        for group in self.groups.keys():
            welcome += "\nGroup {}:\n==\n".format(group)
            for team in self.groups[group]:
                welcome += "{}\n".format(team[0])
        welcome += "\nStart pressing keys on your keyboard as fast as you can!!\n"
        return welcome

    def start_game(self):
        """ TODO: check number of participants """
        self.set_game_mode(True)
        if self.num_of_participants > 1:
            welcome_message = self.get_welcome_message()
            self.slaves_threads_manage()
            self.send_message_to_clients(welcome_message)

            # TODO: remove this print:
            print(welcome_message)
        t = threading.Timer(self.timing, self.finish_game)
        t.start()

    def kill_slaves_threads(self):
        for index, thread in enumerate(self.threads):
            thread.kill()

    def check_winning_group(self):
        group_score, max_score, curr_winning_team = 0, 0, 1
        message = "Game over!\n"

        # check who is the winning team (by score)
        for group in self.groups_scores.keys():
            if self.groups_scores[group] > max_score:
                max_score = group_score
                curr_winning_team = group
            message += "Group {0} types in {1} characters. ".format(group, group_score)
            group_score = 0
        message += "\nGroup {} wins!\n".format(curr_winning_team)
        message += "\nCongratulations to the winners:\n==\n"

        for team in self.groups[curr_winning_team]:
            message += "{}\n".format(team[0])

        return message

    def finish_game(self):
        self.set_game_mode(False)
        self.kill_slaves_threads()
        summary_message = self.check_winning_group()

        # TODO: remove this print:
        print(summary_message)
        self.send_message_to_clients(summary_message)
        self.clean_last_game()

    def thread_slave_tcp(self, connection):
        group_num = self.connections[connection]
        while True:
            try:
                msg = connection.recv(1024)
                if len(msg) == 1:
                    self.groups_scores[group_num] += 1
            except err:
                return

    def slaves_threads_manage(self):
        for conn in self.connections.keys():
            x = threading.Thread(target=thread_slave_tcp, args=(conn,))
            self.threads.append(x)
            x.start()

    def send_message_to_clients(self, message):
        for conn in self.connections:
            try:
                conn.send(bytes(message, 'utf-8'))
            except err:
                continue

    def set_game_mode(self, status):
        self.game_mode = status

    def get_group_num(self):
        threading.Lock()
        group = (self.num_of_participants % 2) + 1
        self.num_of_participants += 1
        threading.RLock()
        return group

    def clean_last_game(self):
        # closing the tcp connections with clients
        for conn in self.connections.keys():
            try:
                conn.close()
            except err:
                continue
            finally:
                del conn

        # cleaning the game properties
        self.num_of_participants = 0
        for group in self.groups.keys():
            self.groups[group] = {}

        print("Game over, sending out offer requests...")
        self.server_state_tcp_listening()


if __name__ == "__main__":
    server = Server()
    server.start_server()