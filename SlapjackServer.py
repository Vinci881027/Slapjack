from socket import *
import threading
import sys
import random
import time
import json


class MultithreadingTCPServer:
    def __init__(self, name, port):
        self.serverName = name
        self.serverPort = port
        self.deck = StardardDeck()
        self.num = 0
        self.socketList = []
        self.username = []
        self.startList = []
        self.againList = []
        self.matchList = []
        self.scoreList = []

    def start(self):
        try:
            self.deck.shuffule()  # 洗牌
            with socket(AF_INET, SOCK_STREAM) as serverSocket:
                print('Bind server socket to',
                      self.serverName, ':', self.serverPort)
                serverSocket.bind((self.serverName, self.serverPort))
                serverSocket.listen(4)
                print('Multithreading server binding success')
                while True:
                    clientSocket, address = serverSocket.accept()
                    # add socket to list
                    self.socketList.append(clientSocket)
                    # receive username from client
                    name = clientSocket.recv(1024)
                    self.username.append(name.decode())
                    self.startList.append(False)
                    self.againList.append(False)
                    self.matchList.append(False)
                    self.scoreList.append(0)
                    thread = threading.Thread(
                        target=self.__handleClient, args=(clientSocket,))
                    thread.start()
        except:
            pass
        finally:
            print('Server shutdown.')

    def __handleClient(self, clientSocket):
        clientName, clientPort = clientSocket.getpeername()
        print('Connecting to', clientName, clientPort)
        try:
            while True:
                message = clientSocket.recv(1024)
                if len(message) == 0:
                    break
                sentence = message.decode()
                for i in range(len(self.socketList)):
                    if self.socketList[i] == clientSocket:
                        if sentence == 'start':
                            self.startList[i] = True
                        elif sentence == 'again':
                            self.againList[i] = True
                        elif sentence == 'match':
                            self.scoreList[i] = self.scoreList[i]+1
                            data = {'start': 'none', 'again': 'none',
                                    'card': 'card', 'num': 0, 'score': self.scoreList, 'user': self.username}
                            for i in self.socketList:
                                i.send(json.dumps(data).encode())
                        elif sentence == 'not match':
                            self.scoreList[i] = self.scoreList[i]-1
                            data = {'start': 'none', 'again': 'none',
                                    'card': 'card', 'num': 0, 'score': self.scoreList, 'user': self.username}
                            for i in self.socketList:
                                i.send(json.dumps(data).encode())
                if all(self.startList) == True:
                    self.startList = [
                        False for i in range(len(self.startList))]
                    # thread to draw card
                    thread = threading.Thread(
                        target=self.drawCard, args=(clientSocket,))
                    thread.start()
                if all(self.againList) == True:
                    self.againList = [
                        False for i in range(len(self.againList))]
                    self.deck.__init__()
                    self.deck.shuffule()
                    data = {'start': 'false', 'again': 'true',
                            'card': 'card', 'num': 0, 'score': self.scoreList, 'user': self.username}
                    for i in self.socketList:
                        i.send(json.dumps(data).encode())
        except:
            clientSocket.close()
        finally:
            print('Disconnecting to', clientName, ':', clientPort)

    def drawCard(self, clientSocket):
        while self.deck.length() > 0:
            # send card to client
            self.num = self.num % 13 + 1
            card = self.deck.draw()
            data = {'start': 'true', 'again': 'false', 'card': str(
                card), 'num': self.num, 'score': self.scoreList, 'user': self.username}
            for i in self.socketList:
                i.send(json.dumps(data).encode())
            time.sleep(0.7)
        # all cards clear
        data = {'start': 'false', 'again': 'false',
                'card': 'card', 'num': 0, 'score': self.scoreList, 'user': self.username}
        for i in self.socketList:
            i.send(json.dumps(data).encode())


class Card():
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        suits = {"s": "♠", "h": "♡", "d": "♢", "c": "♣"}
        values = {**{i: str(i) for i in range(2, 11)},
                  **{11: 'J', 12: 'Q', 13: 'K', 14: 'A'}}
        return values[self.value] + suits[self.suit]


class StardardDeck():
    def __init__(self):
        self.cards = [Card(value, suit)
                      for value in range(2, 15) for suit in 'cdhs']

    def __repr__(self):
        return ' '.join([card.__repr__() for card in self.cards])

    def shuffule(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop(0)

    def length(self):
        return len(self.cards)


# socket
if len(sys.argv) < 3:
    serverName = '127.0.0.1'
    serverPort = 12000
else:
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])

server = MultithreadingTCPServer(serverName, serverPort)
server.start()
