from socket import *
import threading
import sys
import random
import tkinter as tk
import math


class MultithreadingTCPClient:
    def __init__(self, name, port, username):
        self.serverName = name
        self.serverPort = port
        self.username = username

    def start(self):
        try:
            with socket(AF_INET, SOCK_STREAM) as clientSocket:
                print('Connect to server', self.serverName, ':', self.serverPort)
                clientSocket.connect((self.serverName, self.serverPort))
                clientAddress, clientPort = clientSocket.getsockname()
                print('Client', clientAddress, ':', clientPort)
                print('Connecting to server',
                      self.serverName, ':', self.serverPort)
                thread = threading.Thread(
                    target=self.receive, args=(clientSocket,))
                thread.start()
                # while True:
                #     # sentence = input()
                #     # clientSocket.send(sentence.encode())
                #     pass
        except:
            pass
        finally:
            print('Connection shutdown')

    def receive(self, clientSocket):
        try:
            while True:
                message = clientSocket.recv(1024)
                if len(message) == 0:
                    break
                sentence = message.decode()
                card = sentence.split()[0]
                num = sentence.split()[1]
                print(card, num)
        except:
            pass


class LoginPage:
    def __init__(self, window):
        self.login_frame = tk.Frame(window)
        self.login_frame.pack()
        self.username_label = tk.Label(self.login_frame, text='請輸入暱稱：')
        self.username_label.pack(side=tk.LEFT)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack(side=tk.LEFT)
        self.login_button = tk.Button(
            self.login_frame, text='connect', command=submitUsername)
        self.login_button.pack(side=tk.LEFT)


class GamePage:
    def __init__(self, window, username):
        self.username = username
        self.game_frame = tk.Frame(window)
        self.game_frame.pack()
        self.username_label = tk.Label(self.game_frame, text=username)
        self.username_label.pack()
        self.start_button = tk.Button(
            self.game_frame, text='開始遊戲', command=self.start)
        self.start_button.pack()

    def start(self):
        # socket
        server = MultithreadingTCPClient(serverName, serverPort, self.username)
        server.start()


def enterKeyEvent(event):
    submitUsername()


def submitUsername():
    username = login.username_entry.get()
    login.username_entry.delete(0, tk.END)
    if len(username) != 0:
        # create new page
        login.login_frame.destroy()
        game = GamePage(window, username)


# socket
if len(sys.argv) < 3:
    serverName = '127.0.0.1'
    serverPort = 12000
else:
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])


# GUI
window = tk.Tk()
window.title('SlapJack')
window.geometry('800x600')
window.bind('<Return>', enterKeyEvent)
login = LoginPage(window)
window.mainloop()
