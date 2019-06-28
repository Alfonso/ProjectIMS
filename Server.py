#                   IMPORTS
import threading
import sys
import socket
import signal

#                   GLOBALS
clientList = []
shutDown = False

#                   CLASS
class clientInfo:
    def __init__(self,name,ip,sock,chatRoom):
        self.name = name
        self.ip = ip
        self.sock = sock
        self.chatRoom = chatRoom

#                   FUNCTIONS
# Send message to all users
def sendAll(sender,message):
    for client in clientList:
        if client != sender:
            client.sock.send("{}: {}".format(sender.name,message).encode())

# Check if a name already exists
def checkName(name):
    for client in clientList:
        if client.name == name:
            return -1
    return 0

# Function that listens for what the client says to the server / handles recieving and sending messages
def client(sock, ip,info):
    global shutDown
    sock.send("WELCOME TO THE CHATROOM!".encode())

    # Loop through constantly waiting for something from the client
    while True:
        message = sock.recv(4096).decode()

        if shutDown == True:
            break

        if message == '!QUIT':
            sock.send('QUIT'.encode())
            clientList.remove(info)
            print('{} has disconnected'.format(ip))
            break
        elif message == '!SHUTDOWN':
            sock.send('QUIT'.encode())
            print('SHUTTING DOWN')
            shutDown = True
            # Create a local conncetion to break out of the socket.accept()
            localSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            localSock.connect((str(sys.argv[1]),int(sys.argv[2])))
            localSock.close()
            break
        else:
            # Do something with this message
            #print('Message from {}: {}'.format(ip,message))
            # Send message to everyone rn (change to chatroom after)
            sendAll(info,message)

# Signal Handler to handle Ctr-C
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

def terminateAll():
    for client in clientList:
        client.sock.send('SHUTDOWN'.encode())

#                   MAIN
if __name__ == '__main__':

    # Handle ctr-C
    signal.signal(signal.SIGINT, signal_handler)

    # Check arguments are correct
    if len(sys.argv) != 3:
        print('Please input the correct number of arguments')
        exit()

    ip = str(sys.argv[1])
    port = int(sys.argv[2])

    # Setup server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    server.bind((ip,port))

    # Listens for 10 active connections
    server.listen(10)

    # Listens for any attempted connections
    while True:
        # Accept any connection to server
        uSock, uIP = server.accept()
        if shutDown == True:
            # Call Functon to close all connections and threads
            terminateAll()
            break
        print('New Connection: {}'.format(uIP))

        tempName = uSock.recv(4096).decode()

        if checkName(tempName) == -1:
            uSock.send('Please pick another name'.encode())
            print('{} disconnected since Name was not valid'.format(uIP))
        else:
            uSock.send('Valid name'.encode())
            tempInfo = clientInfo(tempName,uIP,uSock,'test')
            clientList.append(tempInfo)
            thread = threading.Thread(target=client,args=(uSock,uIP,tempInfo))
            thread.start()
            print('Connection: {} established as {}'.format(uIP,tempName))

            # Have to add chatroom functionality here

    server.close()
    exit()
