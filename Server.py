#                   IMPORTS
import threading
import sys
import socket
import signal
from os import system, name as machineName

#                   GLOBALS
clientList = []
roomList = []
shutDown = False
ip = ''
port = 0

#                   CLASS
class clientInfo:
    def __init__(self,name,ip,sock,chatRoom,admin):
        self.name = name
        self.ip = ip
        self.sock = sock
        self.chatRoom = chatRoom
        self.admin = admin

#                   FUNCTIONS
# Clears screen
def clear():
    if machineName == 'nt':
        _ = system('cls')
    else: _ = system('clear')

# Breaks the accept() in the main while loop because windows
def breakAccept():
    localSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    localSock.connect((ip,port))
    localSock.close()

# Send message to all users
def sendAll(sender,message):
    for client in clientList:
        if sender != None and client != sender:
            client.sock.send("{}: {}".format(sender.name,message).encode())
        elif sender == None:
            client.sock.send('{}: {}'.format('SERVER',message).encode())

# Send message to users in chatRoom
def sendRoom(sender,message):
    for client in clientList:
        if client != sender and sender.chatRoom == client.chatRoom:
            client.sock.send("{}: {}".format(sender.name,message).encode())

# Check if a name already exists
def checkName(name):
    # We do not want users to have these names. Having SWITCH can cause issues while any form of server can be confusing
    # Since that is the tag that we have for the server talking to all users
    if name.lower() == 'server' or name == 'SWITCH':
        return -1
    for client in clientList:
        if client.name == name:
            return -1
    return 0

# Check if the room exists
def checkRoom(room):
    for item in roomList:
        if room == item:
            return 0
    return -1

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
            if info.admin == True:
                sock.send('QUIT'.encode())
                print('{} \'{}\' is initiating SHUTTING DOWN'.format(ip,info.name))
                shutDown = True
                # Create a local conncetion to break out of the socket.accept()
                breakAccept()
                break
            else: sock.send('You do not have appropriate permissions'.encode())
        elif message == '!ROOMS':
            sock.send('Current rooms are: {}'.format(roomList).encode())
        elif message.startswith('!SWITCH'):
            if checkRoom(message[8:]) == -1:
                sock.send('That room does not exist'.encode())
            else:
                info.chatRoom = message[8:]
                sock.send(message[1:].encode())
        elif message == '!KICKED':
            print('{} \'{}\' has been kicked'.format(ip,info.name))
            break
        else:
            # Do something with this message
            #print('Message from {}: {}'.format(ip,message))
            # Send message to everyone rn (change to chatroom after)
            sendRoom(info,message)

# Signal Handler to handle Ctr-C
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

# Turn off all clients
def terminateAll():
    for client in clientList:
        client.sock.send('SHUTDOWN'.encode())

# Server command line interface
def commandLine():
    global shutDown
    while True:
        command = input()
        if command == 'off':
            shutDown = True
            terminateAll()
            breakAccept()
            break
        elif command == 'help':
            print('this will say the commands and shit')
        elif command.startswith('say'):
            sendAll(None,command[4:])
        elif command.startswith('add'):
            roomList.append(command[4:])
        elif command.startswith('admin'):
            for client in clientList:
                if client.name == command[6:]:
                    client.admin = True
                    print('{} successfully given admin'.format(client.name))
                    break
        elif command == 'users':
            print('Current users are: ',end='')
            for client in clientList:
                print('{}({})'.format(client.name,client.chatRoom),end=', ')
            print('')
        elif command == 'clear':
            clear()
        elif command == 'rooms':
            print('Current rooms are: {}'.format(roomList))
        elif command.startswith('kick'):
            if checkName(command[5:]) == -1:
                for tempClient in clientList:
                    if tempClient.name == command[5:]:
                        clientList.remove(tempClient)
                        tempClient.sock.send('KICKED'.encode())
                        break
            else: print('\'{}\' User not found'.format(command[5:]))
        elif command == 'ip' or command == 'port':
            print('Your ip for clients to connect is: {} and the port is: {}'.format(ip,port))

# Thread that handles name and room
def acceptor(uSock,uIP):
    tempName = uSock.recv(4096).decode()

    if checkName(tempName) == -1:
        uSock.send('Please pick another name'.encode())
        print('{} disconnected since \'{}\' is already in use'.format(uIP,tempName))
    else:
        uSock.send('Valid name.\nAvailable rooms: '.encode())

        # handle chatroom joining?
        uSock.send('Current rooms: \n{}'.format(', '.join(roomList)).encode())
        tempRoom = uSock.recv(4096).decode()
        if checkRoom(tempRoom) == -1:
            uSock.send('Please pick a valid room'.encode())
            print('{} disconnected since \'{}\' is not a room'.format(uIP,tempRoom))
        else:
            tempInfo = clientInfo(tempName,uIP,uSock,tempRoom,False)
            clientList.append(tempInfo)
            thread = threading.Thread(target=client,args=(uSock,uIP,tempInfo))
            thread.start()
            print('Connection: {} established as {} in {}'.format(uIP,tempName,tempRoom))
            sendRoom(clientInfo('SERVER',None,None,tempRoom,False),'{} has joined the room'.format(tempName))

#                   MAIN
if __name__ == '__main__':

    # General is the starting chatRoom
    roomList.append('General')
    roomList.append('Erin')

    # Handle ctr-C
    signal.signal(signal.SIGINT, signal_handler)

    # Check arguments are correct
    #if len(sys.argv) != 2:
        #print('Please input the correct number of arguments')
        #exit()

    ip = str(socket.gethostbyname(socket.gethostname()))
    #port = int(sys.argv[1])
    port = int(input('Please input the port you would like to use: '))
    print('Your ip for clients to connect is: {}'.format(ip))
    # Setup server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    server.bind((ip,port))

    # Listens for 10 active connections
    server.listen(10)

    commandThread = threading.Thread(target=commandLine,)
    commandThread.daemon = True
    commandThread.start()

    # Listens for any attempted connections
    while True:
        # Accept any connection to server
        uSock, uIP = server.accept()
        if shutDown == True:
            # Call Functon to close all connections and threads
            terminateAll()
            break
        print('New Connection: {}'.format(uIP))

        # Spawn acceptor thread that handles name and room
        acceptorThread = threading.Thread(target=acceptor,args=(uSock,uIP))
        acceptorThread.daemon = True
        acceptorThread.start()

    server.close()
    exit()
