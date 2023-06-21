from asyncio.windows_events import NULL
import socket
from threading import Thread
#from zlib import compress
from datahandler import command_handler, connection_message
from screen_recorder import retreive_screenshot
from screeninfo import get_monitors

WIDTH = 1280
HEIGHT = 720

for m in get_monitors():
    if m.is_primary:
        WIDTH = m.width
        HEIGHT = m.height

def main(host="0.0.0.0", port=65432):
    
    print(host)
    while True:
        print('loop')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(1)
      #  try:
        print('Server started.')
        threadStart = False
        conn = NULL
        addr = NULL
        recvErr = 0

        #Conn message
        conn, addr = sock.accept()
        connection_message(conn)

        #start sock for video stream
        while threadStart == False and 'connected':
            print('Client connected IP:', addr)
            thread = Thread(target=retreive_screenshot, args=(conn,sock,WIDTH,HEIGHT,))
            thread.start()
            threadStart = True

        #Start input commands on main thread
        while threadStart and 'connected':
            try:
                data = conn.recv(1024)
                if not data:
                    print("no data")
                command_handler(data)
            except:
                print("recv err")
                recvErr += 1
                if recvErr >= 20:
                    break
            finally:
                sock.close()
        sock.close()

if __name__ == '__main__':
    main()