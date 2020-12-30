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

        self.master_tcp_socket = None
        self.udp_socket = None

        self.timing = 2
        self.game_mode = False
        self.connections = {} # {key: conn, value: groupNumber}
        self.groups = {1: {"asaf": ["conn", 10], "maayan": ["conn", 3]}, 2: {"yael": ["conn", 14]}} # {key: groupNumber, value: {key: groupName, value: [connection, groupScore]}
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
        # starting socket as UDPSocket
        message_to_send = struct.pack('Ibh', self.magic_cookie, self.offer_message_type, self.tcp_port)

        # sending offers to port 13117 every second for 10 seconds
        counter = 0
        while counter < self.timing:
            self.udp_socket.sendto(message_to_send, (self.network_ip, self.udp_dest_port))
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
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet # UDP

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
                self.connections[conn] = (team_name, self.get_group_num())

        # for socket_client in
        # while self.game_mode:
        #     conn, addr = self.master_tcp_socket.accept()
        #     if conn in self.connections.keys():
        #


    def start_game(self):
        '''TODO: check number of participants'''

        self.set_game_mode(True)
        welcome = "Welcome to Keyboard Spamming Battle Royale."
        for group in self.groups.keys():
            welcome += "\nGroup {}:\n==\n".format(group)
            for team in self.groups[group].keys():
                welcome += "{}\n".format(team)
        welcome += "\nStart pressing keys on your keyboard as fast as you can!!\n"
        self.send_message_to_clients(welcome)
        print(welcome)
        t = threading.Timer(self.timing, self.finish_game)
        t.start()

    def finish_game(self):
        self.set_game_mode(False)

        group_score, max_score, curr_winning_team = 0, 0, 0
        message = "Game over!\n"

        # check who is the winning team (by score)
        for group in self.groups.keys():
            for team in self.groups[group].keys():
                group_score += self.groups[group][team][1]
                if group_score > max_score:
                    max_score = group_score
                    curr_winning_team = group
            message += "Group {0} types in {1}. ".format(group, group_score)
            group_score = 0
        message += "\nGroup {} wins!\n".format(curr_winning_team)
        message += "\nCongratulations to the winners:\n==\n"

        # add names of winning team to message
        for team in self.groups[curr_winning_team].keys():
            message += "{}".format(team)

        print(message)
        self.send_message_to_clients(message)
        self.clean_last_game()

    def send_message_to_clients(self, message):
        for conn in self.connections:
            conn.send(bytes(message, 'utf-8'))

    def set_game_mode(self, status):
        self.game_mode = status

    def get_group_num(self):
        threading.Lock()
        group = self.num_of_participants % 2
        self.num_of_participants += 1
        threading.RLock()
        return group

    def clean_last_game(self):

        # closing the tcp connections with clients
        for conn in self.connections.keys():
            conn.close()
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