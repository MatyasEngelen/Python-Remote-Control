import struct
import globals
import keyboard

def sendMessage(sock, data):
    sock.sendall(data)

class Commands:

    def __init__(self, sock,WIDTH,HEIGHT):
        self.sock = sock
        self.MouseLC = 0
        self.mouseOldPres = 0
        self.IsClick = False
        self.holding = False
        print(globals.monitor_in_use)
        self.scale_value_x = globals.monitor_in_use[0] / WIDTH
        self.scale_value_y = globals.monitor_in_use[1] / HEIGHT

    def command_handler(self, pygame, thread_hash):
            while thread_hash in globals.active_threads:
              #  try:
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
                                x = struct.pack("!i", (int(x * self.scale_value_x)))
                                y = struct.pack("!i", (int(y * self.scale_value_y)))
                                mess = command + x + y
                                sendMessage(self.sock, mess)
                                self.mouseOldPres = mousePres
                                self.holding = True
                            else:
                                self.IsClick = True

                    if pygame.mouse.get_pressed()[2]:
                        command = struct.pack("!B", 3)
                        x, y = pygame.mouse.get_pos()
                        x = struct.pack("!i", (int(x * self.scale_value_x)))
                        y = struct.pack("!i", (int(y * self.scale_value_y)))
                        mess = command + x + y
                        sendMessage(self.sock, mess)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            for i in [i for i,x in enumerate(globals.active_threads) if x == thread_hash]:
                                del globals.active_threads[i]
                            break
                        #register click, we need the mouse up event for this.
                        if event.type == pygame.MOUSEBUTTONUP:
                            self.MouseLC = 0

                            #send click
                            if self.IsClick and self.holding == False:
                                self.IsClick = False
                                print("click")
                                command = struct.pack("!B", 1)
                                x, y = pygame.mouse.get_pos()
                                x = struct.pack("!i", (int(x * self.scale_value_x)))
                                y = struct.pack("!i", (int(y * self.scale_value_y)))
                                mess = command + x + y
                                sendMessage(self.sock, mess)
                            
                            #send the end of the hold
                            if self.holding:
                                command = struct.pack("!B", 5)
                                x, y = pygame.mouse.get_pos()
                                x = struct.pack("!i", (int(x * self.scale_value_x)))
                                y = struct.pack("!i", (int(y * self.scale_value_y)))
                                mess = command + x + y
                                sendMessage(self.sock, mess)
                                self.holding = False

                        #send key strokes
                        if event.type == pygame.KEYDOWN:
                            if keyboard.read_key() != "":
                                command = struct.pack("!B", 4)
                                user_text = keyboard.read_key()
                                Bmess = command + user_text.encode('utf8')
                                print("ord teext= " + user_text)
                                print(str(Bmess))  
                                sendMessage(self.sock, Bmess)

                    ''' if event.type == pygame.KEYDOWN:
                            command = struct.pack("!B", 4)
                            user_text = event.unicode
                            print("user teext= " + user_text)
                            if user_text != "":
                                Bmess = command + struct.pack("!B",ord(user_text))
                                print("ord teext= " + str(ord(user_text)))
                                print(str(Bmess))  
                                sendMessage(self.sock, Bmess)'''
               #╔ except:
                 #   print("Datahandler error")
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

    Primary_found = False
    Primary_Count = 0
    decode_m = ByteBuffer(sock_mess)
    for x in range(sock_ilength):
        data = decode_m.read_i32()
        globals.monitors.append(data)

        if x == 1:
            Primary_found = True

        if Primary_found:
            globals.monitor_in_use.append(data)
            Primary_Count += 1
            if Primary_Count == 2:
                Primary_found = False
    
    print(globals.monitor_in_use)