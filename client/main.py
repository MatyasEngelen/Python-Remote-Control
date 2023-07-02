import socket
from datahandler import *
from threading import Thread
import globals
from video_handler import receiveVideo
import sys
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import *
import pygame
from screeninfo import get_monitors
import secrets

#Get window size
WIDTH = 1280
HEIGHT = 720

for m in get_monitors():
    if m.is_primary:
        WIDTH = m.width
        #-40 to solve pygame's wacky fullscreen
        HEIGHT = m.height - 40

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    
        self.setWindowTitle("MENG Remote")
        self.setFixedSize(QSize(300, 200))
        self.MainUI()

        self.Qlabel_log = "Log:"

        
    def start_connection(self):
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ip = self.InsertTxtName.text()
        error = False

        #try:
        sock.connect((ip, 65432))
        connection_message(sock)
        #except:
        #print("err")
        error = False
        if error == False:
            print("thread start")
            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            clock = pygame.time.Clock()

            thread_hash = str(secrets.token_urlsafe(16))
            globals.active_threads.append(thread_hash)
            Thread(target=receiveVideo, args=(screen,clock,pygame,sock,WIDTH,HEIGHT,thread_hash,), daemon=True).start()
            Thread(target=Commands(sock,WIDTH,HEIGHT).command_handler, args=(pygame,thread_hash,), daemon=True).start()
            

    def MainUI(self):
        self.InsertLabelName = QLabel("Device / IP:", self)
        self.InsertLabelName.setGeometry(5, 5, 500, 60)
        self.InsertTxtName = QLineEdit(self)
        self.InsertTxtName.move(75, 25)
        self.InsertTxtName.resize(150,20)

        self.MainBtn = QPushButton('CONNECT', self)
        self.MainBtn.setGeometry(75, 50, 150, 35)
        self.MainBtn.clicked.connect(lambda: self.start_connection())

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()