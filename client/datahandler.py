def sendMessage(sock, data):
    sock.sendall(data.encode())