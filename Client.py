#                   IMPORTS
import threading
import sys
import socket
import signal
import select
import time
from os import system, name

#                   GLOBALS
shutDown = False
username = ''
chatRoom = ''

#                   FUNCTIONS
# Clears screen
def clear():
    if name == 'nt':
        _ = system('cls')
    else: _ = system('clear')

def receive(sock,ip):
    global chatRoom
    while True:
        #sock.recv(1024)
        message  = sock.recv(4096).decode()
        if message == 'QUIT':
            break
        elif message == 'SHUTDOWN':
            print('')
            break
        elif message.startswith('SWITCH'):
            chatRoom = message[7:]
            clear()
            print('Switched chatrooms to: {}'.format(chatRoom))
        elif message == 'KICKED':
            sock.send('!KICKED'.encode())
            print('You have been kicked!')
            break
        else: print(message)

def send(sock,ip):
    time.sleep(1)
    while True:
        message = input('')
        if message == '!QUIT':
            sock.send(message.encode())
            break
        elif message == '!CLEAR':
            clear()
            print('You are currently in: {}'.format(chatRoom))
        elif message == '!HELP':
            # print out the different commands that can be used
            print('Help is on the way!')
        elif message == '!KICKED':
            print('This is not a command')
        else: sock.send(message.encode())

# Signal Handler to handle Ctr-C
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

#                   MAIN
if __name__ == '__main__':

    # Handle ctr-C
    signal.signal(signal.SIGINT, signal_handler)

    # Check arguments are correct
    #if len(sys.argv) != 3:
    #    print('Please input the correct number of arguments')
    #    exit()

    # Check IP
    #ip = str(sys.argv[1])
    ip = input('Please input the ip you wish to connect: ')
    # Check Port
    #port = int(sys.argv[2])
    port = int(input('Please input the port you wish to connect: '))

    # Create socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip,port))

    # Ask for username and see if valid
    while True:
        username = input('Please input a username: ')
        if username != '':
            break

    client.send(username .encode())
    if client.recv(4096).decode() == 'Please pick another name':
        print('Please pick another name')
        exit()

    clear()
    # Do chatroom stuff here
    print(client.recv(4096).decode())
    chatRoom = input('Please input a chat room you would like to join: ')
    client.send(chatRoom.encode())
    if client.recv(4096).decode() == 'Please pick a valid room':
        print('Please pick a valid room')
        exit()
    else: print('Connecting to room!')
    clear()
    print('Connected to {}!: '.format(chatRoom))

    receiveThread = threading.Thread(target=receive,args=(client,ip))
    sendingThread = threading.Thread(target=send,args=(client,ip))
    sendingThread.daemon = True
    receiveThread.start()
    sendingThread.start()

    receiveThread.join()
    #sendingThread.join()

    # Done
    client.close()
    print('Disconnected')
    exit()
