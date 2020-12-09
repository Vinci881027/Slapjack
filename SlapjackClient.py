from socket import *
import threading
import sys
import random
import tkinter as tk
import time
import json
import subprocess


class MultithreadingTCPClient:
    def __init__(self, name, port, username):
        self.serverName = name
        self.serverPort = port
        self.username = username
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.cardValue = 1
        self.numValue = 0

    def start(self, game):
        try:
            print('Connect to server', self.serverName, ':', self.serverPort)
            self.clientSocket.connect((self.serverName, self.serverPort))
            clientAddress, clientPort = self.clientSocket.getsockname()
            print('Client', clientAddress, ':', clientPort)
            print('Connecting to server',
                  self.serverName, ':', self.serverPort)
            # send username to server
            self.clientSocket.send(self.username.encode())
            self.receive(self.clientSocket, game)
        except:
            pass
        finally:
            print('Connection shutdown')

    def end(self):
        self.clientSocket.close()

    def receive(self, clientSocket, game):
        try:
            while True:
                message = clientSocket.recv(1024)
                if len(message) == 0:
                    break
                data = json.loads(message.decode())
                # start
                print(data['score'])
                if data['start'] == 'true':
                    game.card_label['text'] = data['card']
                    cardStr = data['card'][:-1]
                    if cardStr == 'A':
                        self.cardValue = 1
                    elif cardStr == 'J':
                        self.cardValue = 11
                    elif cardStr == 'Q':
                        self.cardValue = 12
                    elif cardStr == 'K':
                        self.cardValue = 13
                    else:
                        self.cardValue = int(cardStr)
                    self.numValue = data['num']
                    thread = threading.Thread(
                        target=self.mediaPlayer, args=(data,))
                    thread.start()
                else:
                    game.again_button['state'] = tk.NORMAL
                # again
                if data['again'] == 'true':
                    game.start_button['state'] = tk.NORMAL
                    game.again_button['state'] = tk.DISABLED
        except:
            pass

    def mediaPlayer(self, data):
        subprocess.call(['afplay', 'media/'+str(data['num'])+'.m4a'])


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
        self.server = MultithreadingTCPClient(
            serverName, serverPort, username)
        # GUI
        self.window = window
        self.window.bind('<space>', self.space)
        self.username = username
        self.user_frame = tk.Frame(self.window)
        self.user_frame.pack()
        self.username_label = tk.Label(self.user_frame, text=username)
        self.username_label.pack()
        self.start_button = tk.Button(
            self.user_frame, text='開始遊戲', command=self.gameStart)
        self.start_button.pack()
        self.again_button = tk.Button(
            self.user_frame, text='再來一局', command=self.gameAgain, state=tk.DISABLED)
        self.again_button.pack()
        self.game_frame = tk.Frame(self.window)
        self.game_frame.pack()
        self.card_label = tk.Label(self.game_frame, font=("Times", 80))
        self.card_label.pack()
        self.exit_button = tk.Button(
            self.user_frame, text='離開遊戲', command=self.exit)
        self.exit_button.pack(side=tk.BOTTOM)
        # create new thread
        thread = threading.Thread(target=self.clientThread)
        thread.start()

    def clientThread(self):
        # socket
        self.server.start(self)

    def exit(self):
        self.server.end()
        self.window.destroy()

    def gameStart(self):
        self.start_button['state'] = tk.DISABLED
        self.server.clientSocket.send('start'.encode())

    def gameAgain(self):
        self.again_button['state'] = tk.DISABLED
        self.server.clientSocket.send('again'.encode())

    def space(self, event):
        if self.server.cardValue == self.server.numValue:
            self.server.cardValue = 1
            self.server.numValue = 0
            self.server.clientSocket.send('match'.encode())
        else:
            self.server.clientSocket.send('not match'.encode())


def enter(event):
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
window.bind('<Return>', enter)
login = LoginPage(window)
window.mainloop()
