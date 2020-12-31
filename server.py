import socket
import struct
import time
import threading
# from scapy.arch import get_if_addr

class Server:
    def __init__(self):
        # Server Authorization Parameters
        self.magic_cookie = 0xfeedbeef # 3000
        self.offer_message_type = 0x2

        # Server Global Parameters
        self.network_ip = "192.168.0.183" #get_if_addr('eth1')
        self.local_ip = "localhost"
        self.tcp_port = 2032
        self.udp_dest_port = 13117

        self.threads = []
        self.master_tcp_socket = None
        self.udp_socket = None

        self.timing = 10
        self.game_mode = False
        self.connections = {}  # {key: conn, value: (group_name, groupNumber)}
        self.groups = {1: {}, 2: {}}  # {key: groupNumber, value: {key: groupName, value: [connection, groupScore]}
        self.groups_scores = {1: 0, 2: 0}
        self.num_of_participants = 0

        # Initiate Threads for server: TCP and UDP Protocols
        self.tcp_thread = threading.Thread(target=self.server_tcp_binding)
        self.udp_thread = threading.Thread(target=self.server_udp_binding)

    def start_server(self):
        # Activate Ports
        try:
            self.tcp_thread.start()
            self.udp_thread.start()
            time.sleep(1.5)
        except OSError:
            return
        finally:
            self.server_state_tcp_listening()

    def server_state_udp(self):
        # starting socket as UDPSocket and bind it to our port ()
        # Enable broadcasting mode
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message_to_send = struct.pack('Ibh', self.magic_cookie, self.offer_message_type, self.tcp_port)

        # sending offers to port 13117 every second for 10 seconds
        counter = 0
        start = time.time()
        while counter < self.timing and time.time()-start < self.timing:
            self.udp_socket.sendto(message_to_send, ("<broadcast>", self.udp_dest_port))
            print("offer sent")
            time.sleep(1)
            counter += 1

    def server_tcp_binding(self):
        # starting socket as TCPSocket and bind it to our port (2032)
        self.master_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master_tcp_socket.bind((self.network_ip, self.tcp_port))

    def server_udp_binding(self):
        # starting socket as UDPSocket and bind it to our port ()
        # Enable broadcasting mode
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet # UDP
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def server_state_tcp_listening(self):
        # starting to listening the tcp port
        self.master_tcp_socket.listen(1)
        print("Server started, listening on IP address {}".format(self.network_ip))

        # starting udp connection thread
        udp_starter = threading.Thread(target=self.server_state_udp)
        udp_starter.start()

        # starting start game thread
        thread_start_game = threading.Timer(self.timing, self.start_game)
        thread_start_game.start()

        # listening to the port for 10 sec
        while not self.game_mode:
            conn, addr = self.master_tcp_socket.accept()
            if conn:
                team_name = conn.recv(20)
                team_name = str(team_name.decode("utf-8").rstrip())
                if not team_name:
                    conn.close()
                    break
                client_group_num = (self.num_of_participants % 2) + 1
                self.num_of_participants += 1
                print("------------------------- " + team_name + " try to connect ! --------------------------")
                self.connections[conn] = (team_name, client_group_num)
                self.groups[client_group_num][team_name] = conn

    def get_welcome_message(self):
        # creating the welcome message
        welcome = "Welcome to Keyboard Spamming Battle Royale."
        for group in self.groups.keys():
            welcome += "\nGroup {}:\n==\n".format(group)
            for team in self.groups[group].keys():
                welcome += "{}\n".format(team)
        welcome += "\nStart pressing keys on your keyboard as fast as you can!!\n"
        print(welcome)
        return welcome

    def start_game(self):
        # starting the game, activated slaves only if there is connections
        self.set_game_mode(True)
        if self.num_of_participants > 0:
            welcome_message = self.get_welcome_message()
            self.slaves_threads_manage()
            self.send_message_to_clients(welcome_message)

        thread_finish_game = threading.Timer(self.timing, self.finish_game)
        thread_finish_game.start()

    def kill_slaves_threads(self):
        self.threads.clear()

    def check_winning_group(self):
        # calculate the winning group and return a game over message
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

        for team in self.groups[curr_winning_team].keys():
            message += "{}\n".format(team)
        print(message)
        return message

    def finish_game(self):
        # finish the game, send summary message to clients if there is connection
        self.set_game_mode(False)
        if self.num_of_participants > 0:
            summary_message = self.check_winning_group()
            self.send_message_to_clients(summary_message)
            self.kill_slaves_threads()
        self.clean_last_game()

    def thread_slave_activate(self, connection):
        # each slave handle different client's msg
        group_num = self.connections[connection]
        while True:
            try:
                msg = connection.recv(2)
                print(msg.decode())
                if len(str(msg.decode())) == 1:
                    self.groups_scores[group_num] += 1
            except:
                return

    def slaves_threads_manage(self):
        # create slave thread for each connection
        for conn in self.connections.keys():
            x = threading.Thread(target=self.thread_slave_activate, args=(conn,))
            self.threads.append(x)
            x.start()

    def send_message_to_clients(self, message):
        # sends all the connection a given message
        for conn in self.connections.keys():
            try:
                conn.send(bytes(message, 'utf-8'))
            except:
                continue

    def set_game_mode(self, status):
        # set the game mode to a given boolean value
        self.game_mode = status

    def get_group_num(self):
        # get a group num (by modulo 2)
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
            except:
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
    while True:
        try:
            server.start_server()
        except:
            time.sleep(1)