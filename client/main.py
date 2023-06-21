from socket import socket
#from zlib import decompress

from datahandler import *
from threading import Thread
import globals
from video_handler import receiveVideo
import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import *
import pygame
from screeninfo import get_monitors


#Get window size
WIDTH = 1280
HEIGHT = 720

for m in get_monitors():
    if m.is_primary:
        WIDTH = m.width
        #-40 to solve pygame's wacky fullscreen
        HEIGHT = m.height - 40


sock = socket()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    
        self.setWindowTitle("MENG Remote")
        self.setFixedSize(QSize(300, 200))
        self.MainUI()

        self.Qlabel_log = "Log:"

        
    def start_connection(self):
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        clock = pygame.time.Clock()
        ip = self.InsertTxtName.text()
        try:
            sock.connect((ip, 65432))
            connection_message(sock)
        except:
            print("err")
            return "Error"
        globals.watching = True
        Thread(target=receiveVideo, args=(screen,clock,pygame,sock,WIDTH,HEIGHT,), daemon=True).start()
        Thread(target=Commands(sock).command_handler, args=(pygame,), daemon=True).start() 
            

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