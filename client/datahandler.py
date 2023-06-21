import struct
import globals

def sendMessage(sock, data):
    sock.sendall(data)

class Commands:

    def __init__(self, sock):
        self.sock = sock
        self.MouseLC = 0
        self.mouseOldPres = 0
        self.IsClick = False

    def command_handler(self, pygame):
            while globals.watching:
                #check if the user is clicking or holding the mouse
                if pygame.mouse.get_pressed()[0]:
                    mousePres = pygame.mouse.get_pos()
                    if self.MouseLC == 0:
                        self.mouseOldPres = mousePres
                        self.MouseLC += 1
                    else:
                        if self.mouseOldPres != mousePres:
                            print("hold")
                            command = struct.pack("!B", 2)
                            x, y = pygame.mouse.get_pos()
                            x = struct.pack("!i", x)
                            y = struct.pack("!i", y)
                            mess = command + x + y
                            sendMessage(self.sock, mess)
                            self.mouseOldPres = mousePres
                        else:
                            self.IsClick = True

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        globals.watching = False
                        break
                    #register click, we need the mouse up event for this.
                    if event.type == pygame.MOUSEBUTTONUP:
                        self.MouseLC = 0
                        if self.IsClick:
                            self.IsClick = False
                            print("click")
                            command = struct.pack("!B", 1)
                            x, y = pygame.mouse.get_pos()
                            x = struct.pack("!i", x)
                            y = struct.pack("!i", y)
                            mess = command + x + y
                            sendMessage(self.sock, mess)

                    if event.type == pygame.KEYDOWN:

                        user_text = event.unicode
                        Bmess = "key:{}".format(user_text)
                        sendMessage(self.sock, str(Bmess))  
            self.sock.close()

#incomming
class ByteBuffer:
    data = b''
    cursor = 0

    #Thank you mari for helping me with this

    def __init__(self, data: bytes):
        self.data = data


    '''
    reads a unsigned char (1 bytes or 8 bits) from the underlying buffer
    '''
    def read_u8(self) -> int:
        return self.__read_bytes('B', 1)
    
    def read_i32(self) -> int:
        return self.__read_bytes('I', 4)

  
    def __read_bytes(self, type_str: str, length: int) -> any:
        # read exactly `length` bytes from `data`, starting at `cursor`
        payload = self.data[self.cursor:self.cursor + length]
        assert len(payload) == length

        # interpret the bytes into the requested type using network endian (big endian)
        value = struct.unpack(f'!{type_str}', payload)[0]

        # advance the cursor by `length` bytes now that we have read it
        self.cursor += length
        return value
    
def connection_message(sock):
    sock_length = sock.recv(4)
    decode_l = ByteBuffer(sock_length)
    sock_ilength = decode_l.read_i32()
    sock_mess = sock.recv((sock_ilength * 4))

    decode_m = ByteBuffer(sock_mess)
    for x in range(sock_ilength):
        globals.monitors.append(decode_m.read_i32())