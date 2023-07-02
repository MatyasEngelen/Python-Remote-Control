import struct
import win32api, win32con
import keyboard
from screeninfo import get_monitors
import globals

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
    
    def read_str_rest(self) -> str:
        return self.__read_bytes('s', 49)

  
    def __read_bytes(self, type_str: str, length: int) -> any:
        # read exactly `length` bytes from `data`, starting at `cursor`
        payload = self.data[self.cursor:self.cursor + length]
        assert len(payload) == length

        # interpret the bytes into the requested type using network endian (big endian)
        value = struct.unpack(f'!{type_str}', payload)[0]

        # advance the cursor by `length` bytes now that we have read it
        self.cursor += length
        return value

def mouse_click(decode):
    if globals.mouse_holding == False:
        location_x: int = decode.read_i32()
        location_y: int = decode.read_i32()
        print("Location: " + str(location_x) + " | " + str(location_y))
        #pyautogui.mouseUp()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,location_x,location_y,0,0)
        win32api.SetCursorPos((location_x,location_y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,location_x,location_y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,location_x,location_y,0,0)
    else:
        print("click out of sync")

def mouse_rclick(decode):
    location_x: int = decode.read_i32()
    location_y: int = decode.read_i32()
    print("Location: " + str(location_x) + " | " + str(location_y))
    #pyautogui.mouseUp()
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,location_x,location_y,0,0)
    win32api.SetCursorPos((location_x,location_y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,location_x,location_y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,location_x,location_y,0,0)

def mouse_move(decode):
    location_x: int = decode.read_i32()
    location_y: int = decode.read_i32()
    #print("Location: " + str(location_x) + " | " + str(location_y))
    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,location_x,location_y,0,0)
    if globals.mouse_holding != True:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,location_x,location_y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,location_x,location_y,0,0)
    win32api.SetCursorPos((location_x,location_y))
    globals.mouse_holding = True

def mouse_end_hold(decode):
    location_x: int = decode.read_i32()
    location_y: int = decode.read_i32()
    win32api.SetCursorPos((location_x,location_y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,location_x,location_y,0,0)
    globals.mouse_holding = False

def keyboard_press(decode):
    key = decode.read_u8()
    keyboard.press_and_release(key)


def command_handler(data):
        decode = ByteBuffer(data)
        command = decode.read_u8()
        match command:
            case 1:
                print("mouse click")
                mouse_click(decode)
            case 2:
                print("mouse hold")
                mouse_move(decode)
            case 3:
                print("left click")
                mouse_rclick(decode)
            case 4:
                keyboard_press(decode)
            case 5:
                print("stop hold")
                mouse_end_hold(decode)

#Outgoing
def connection_message(conn):
    monitors = []
    for m in get_monitors():
        monitors.append(m.is_primary)
        monitors.append(m.width)
        monitors.append(m.height)


    message = struct.pack("!i",len(monitors))
    for x in monitors:
        print(x)
        message += struct.pack("!i", int(x))

    conn.sendall(message)