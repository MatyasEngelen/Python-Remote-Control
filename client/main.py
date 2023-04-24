from socket import socket
#from zlib import decompress
from blosc import decompress
import pygame
from datahandler import sendMessage
from threading import Thread

sock = socket()
WIDTH = 1900
HEIGHT = 1000

def recvall(conn, length):
    """ Retreive all pixels. """
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def receiveVideo(screen,clock):
    while True:
        try:
            # Retreive the size of the pixels length, the pixels length and pixels
            size_len = int.from_bytes(sock.recv(1), byteorder='big')
            size = int.from_bytes(sock.recv(size_len), byteorder='big')
            pixels = decompress(recvall(sock, size))

            # Create the Surface from raw pixels
            img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

            # Display the picture
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(60)
        except:
            break

def main(port=65432):
    host = input('Enter host name: ')
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    watching = True    
    MouseLC = 0
    mouseOldPres = 0
    IsClick = False

    sock.connect((host, port))

    thread = Thread(target=receiveVideo, args=(screen,clock,))
    thread.start()
    try:
        #On the main thread the communication of commands will continue
        while watching:

            #check if the user is clicking or holding the mouse
            if pygame.mouse.get_pressed()[0]:
                mousePres = pygame.mouse.get_pos()
                if MouseLC == 0:
                    mouseOldPres = mousePres
                    MouseLC += 1
                else:
                    if mouseOldPres != mousePres:
                        print("hold")
                        mess = "hold:{}".format(str(pygame.mouse.get_pos()))
                        sendMessage(sock, str(mess))
                        mouseOldPres = mousePres
                    else:
                        IsClick = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break
                #register click, we need the mouse up event for this.
                if event.type == pygame.MOUSEBUTTONUP:
                    MouseLC = 0
                    if IsClick:
                        IsClick = False
                        print("click")
                        mess = "click:{}".format(str(pygame.mouse.get_pos()))
                        sendMessage(sock, str(mess))

                if event.type == pygame.KEYDOWN:

                    user_text = event.unicode
                    Bmess = "key:{}".format(user_text)
                    sendMessage(sock, str(Bmess))  
    finally:
        sock.close()

if __name__ == '__main__':
    main()