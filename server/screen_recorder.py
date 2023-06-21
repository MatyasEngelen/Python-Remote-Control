from asyncio.windows_events import NULL
import socket
from threading import Thread
#from zlib import compress
from mss import mss
from blosc import compress
from PIL import Image

def retreive_screenshot(conn,sock, WIDTH, HEIGHT):
    #A part of the screenshare code was forked of https://stackoverflow.com/questions/48950962/screen-sharing-in-python. I would feel bad for not mentioning
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while 'recording':
            try:
                print('open')
                # Capture the screen
                img = sct.grab(rect)
        
                image = Image.frombytes('RGB', (WIDTH, HEIGHT), img.rgb)
        
                # Resize the image to half its original size
                #This is vital for speed, we cannot afford sending a 1 on 1 image.
                new_size = (1280, 720)
                resized_image = image.resize(new_size)
        
                # Get the pixel data of the resized image as a byte string
                resized_pixel_data = resized_image.tobytes()
        
                #compression
                compressed_data = compress(resized_pixel_data)
        
                # Send the size of the compressed data
                size = len(compressed_data)
                size_len = (size.bit_length() + 7) // 8
                conn.send(bytes([size_len]))
        
                # Send the actual compressed data length
                size_bytes = size.to_bytes(size_len, 'big')
                conn.send(size_bytes)
        
                # Send compressed data
                conn.sendall(compressed_data)
            except:
                print("record err")
                sock.close()
                break