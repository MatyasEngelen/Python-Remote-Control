from asyncio.windows_events import NULL
import socket
from threading import Thread
from zlib import compress
from mss import mss
from datahandler import messageSort

WIDTH = 1900
HEIGHT = 1000

def retreive_screenshot(conn,sock):
    #The screen record part of this code is not mine
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while 'recording':
            try:
                print('open')
                # Capture the screen
                img = sct.grab(rect)
                # Tweak the compression level here (0-9)
                pixels = compress(img.rgb, 6)

                # Send the size of the pixels length
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                conn.send(bytes([size_len]))

                # Send the actual pixels length
                size_bytes = size.to_bytes(size_len, 'big')
                conn.send(size_bytes)

                # Send pixels
                conn.sendall(pixels)
            except:
                print("record err")
                sock.close()
                break

def main(host="0.0.0.0", port=65432):
    
    print(host)
    while True:
        print('loop')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(5)
        try:
            print('Server started.')
            threadStart = False
            conn = NULL
            addr = NULL
            recvErr = 0

            #start sock for video stream
            while threadStart == False and 'connected':
                conn, addr = sock.accept()
                print('Client connected IP:', addr)
                thread = Thread(target=retreive_screenshot, args=(conn,sock,))
                thread.start()
                threadStart = True
            while threadStart and 'connected':
                try:
                    print ("test")
                    data = conn.recv(1024)
                    if not data:
                        print("no data")
                    print(data.decode())
                    messageSort(data.decode())

                except:
                    print("recv err")
                    recvErr += 1
                    if recvErr >= 20:
                        break
        except:
            sock.close()
        finally:
            sock.close()
        sock.close()

if __name__ == '__main__':
    main()