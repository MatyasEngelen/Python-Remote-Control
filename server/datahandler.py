import mouse

def messageSort(message):
    message = message.split(':')
    location = message[1][1:][:-1].split(', ')
    match message[0]:
        case "click":
            print("click")
            mouseClick(location)
        case "hold":
            print("hold")
        case _:
            print("l")
    print(message)

def mouseClick(location):
    print(location)
    mouse.move(location[0],location[1])
    mouse.click()