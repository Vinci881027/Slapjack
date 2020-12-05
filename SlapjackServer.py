from socket import *
import threading
import sys
import random
import time


class MultithreadingTCPServer:
    def __init__(self, name, port):
        self.serverName = name
        self.serverPort = port
        self.deck = StardardDeck()
        self.num = 0
        self.socketList = []

    def start(self):
        try:
            self.deck.shuffule()  # 洗牌
            with socket(AF_INET, SOCK_STREAM) as serverSocket:
                print('Bind server socket to',
                      self.serverName, ':', self.serverPort)
                serverSocket.bind((self.serverName, self.serverPort))
                serverSocket.listen(7)
                print('Multithreading server binding success')
                while True:
                    clientSocket, address = serverSocket.accept()
                    self.socketList.append(clientSocket)  # 把socket加入list
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
                # message = clientSocket.recv(1024)
                # if len(message) == 0:
                #     break
                # sentence = message.decode()
                # if sentence == 'start':
                while self.deck.length() > 0:
                    self.num = self.num % 13 + 1
                    card = self.deck.draw()
                    for i in self.socketList:  # loop all clients
                        i.send((str(card)+' '+str(self.num)).encode())
                    time.sleep(0.5)
                # elif sentence == 'again':
                #     self.deck.__init__()
                #     self.deck.shuffule()
        except:
            clientSocket.close()
        finally:
            print('Disconnecting to', clientName, ':', clientPort)


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
