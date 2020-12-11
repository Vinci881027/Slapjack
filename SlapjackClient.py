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
                # update score board
                for i in range(len(data['user'])):
                    if i == 0:
                        game.user1_label['text'] = data['user'][i]
                        game.user1_label.pack()
                        game.score1_label['text'] = data['score'][i]
                        game.score1_label.pack()
                    elif i == 1:
                        game.user2_label['text'] = data['user'][i]
                        game.user2_label.pack()
                        game.score2_label['text'] = data['score'][i]
                        game.score2_label.pack()
                    elif i == 2:
                        game.user3_label['text'] = data['user'][i]
                        game.user3_label.pack()
                        game.score3_label['text'] = data['score'][i]
                        game.score3_label.pack()
                    elif i == 3:
                        game.user4_label['text'] = data['user'][i]
                        game.user4_label.pack()
                        game.score4_label['text'] = data['score'][i]
                        game.score4_label.pack()
                # start
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
                elif data['start'] == 'false':
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
        self.card_label = tk.Label(self.game_frame, font=("Times", 100))
        self.card_label.pack()
        self.board_frame = tk.Frame(self.window)
        self.board_frame.pack()
        self.exit_button = tk.Button(
            self.user_frame, text='離開遊戲', command=self.exit)
        self.exit_button.pack()
        # player 1
        self.player1_frame = tk.Frame(self.board_frame)
        self.player1_frame.pack(side=tk.LEFT)
        self.user1_label = tk.Label(self.player1_frame)
        self.score1_label = tk.Label(self.player1_frame)
        # player 2
        self.player2_frame = tk.Frame(self.board_frame)
        self.player2_frame.pack(side=tk.LEFT)
        self.user2_label = tk.Label(self.player2_frame)
        self.score2_label = tk.Label(self.player2_frame)
        # player 3
        self.player3_frame = tk.Frame(self.board_frame)
        self.player3_frame.pack(side=tk.LEFT)
        self.user3_label = tk.Label(self.player3_frame)
        self.score3_label = tk.Label(self.player3_frame)
        # player 4
        self.player4_frame = tk.Frame(self.board_frame)
        self.player4_frame.pack(side=tk.LEFT)
        self.user4_label = tk.Label(self.player4_frame)
        self.score4_label = tk.Label(self.player4_frame)
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
            thread = threading.Thread(
                target=self.yes)
            thread.start()
        else:
            self.server.clientSocket.send('not match'.encode())
            thread = threading.Thread(
                target=self.no)
            thread.start()

    def yes(self):
        subprocess.call(['afplay', 'media/yes.mp3'])

    def no(self):
        subprocess.call(['afplay', 'media/no.mp3'])


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
