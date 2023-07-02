import keyboard

while True:
    if keyboard.read_key() != "":
        print(keyboard.read_key())
        print(ord(keyboard.read_key())