from blosc import decompress
import globals
from PIL import Image

def recvall(conn, length):
    """ Retreive all pixels. """
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def receiveVideo(screen,clock,pygame,sock,WIDTH,HEIGHT):
    while globals.watching:
        try:
            # Retreive the size of the pixels length, the pixels length and pixels
            size_len = int.from_bytes(sock.recv(1), byteorder='big')
            size = int.from_bytes(sock.recv(size_len), byteorder='big')
            pixels = decompress(recvall(sock, size))

            # Create the Surface from raw pixels
            img = pygame.image.fromstring(pixels, (globals.video_parameter[0], globals.video_parameter[1]), 'RGB')

            # Create the Surface from raw pixels
            #img = Image.frombytes('RGB', (globals.video_parameter[0], globals.video_parameter[1]), pixels.rgb)

            #resize
            img = pygame.transform.scale(img, (WIDTH, HEIGHT))

            # Display the picture
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(60)
        except:
            print("hmmm")
            break
    pygame.display.quit()
    pygame.quit()
    sock.close()