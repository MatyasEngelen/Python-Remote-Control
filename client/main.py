from socket import socket
from zlib import decompress
import pygame
from datahandler import sendMessage

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

def main(port=65432):
    host = input('Enter host name: ')
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    watching = True    
    MouseLC = 0

    sock.connect((host, port))
    try:
        while watching:

            if pygame.mouse.get_pressed()[0]:
                MouseLC += 1
                if MouseLC >= 3:
                    print("hold")
                    mess = "hold:{}".format(str(pygame.mouse.get_pos()))
                    sendMessage(sock, str(mess))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break
                #register click
                if event.type == pygame.MOUSEBUTTONUP:
                    if MouseLC > 3:
                        MouseLC = 0
                    else:
                        MouseLC = 0
                        print("click")
                        mess = "click:{}".format(str(pygame.mouse.get_pos()))
                        sendMessage(sock, str(mess))

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
    finally:
        sock.close()

if __name__ == '__main__':
    main()