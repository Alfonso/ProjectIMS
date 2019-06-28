#                   IMPORTS
import threading
import sys
import socket
import signal
import select
import time

#                   GLOBALS
shutDown = False
name = ''

#                   FUNCTIONS
def receive(sock,ip):
    while True:
        #sock.recv(1024)
        message  = sock.recv(4096).decode()
        if message == 'QUIT':
            break
        elif message == 'SHUTDOWN':
            print('')
            break
        else: print(message)

def send(sock,ip):
    time.sleep(1)
    while True:
        message = input('')
        if message == '!QUIT' or message == '!SHUTDOWN':
            sock.send(message.encode())
            break
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
    if len(sys.argv) != 3:
        print('Please input the correct number of arguments')
        exit()

    # Check IP
    ip = str(sys.argv[1])

    # Check Port
    port = int(sys.argv[2])

    # Create socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip,port))

    # Ask for username and see if valid
    name = input('Please input a username: ')
    client.send(name.encode())
    if client.recv(4096).decode() == 'Please pick another name':
        print('Please pick another name')
        exit()
    else: print('Valid name!')

    # Do chatroom stuff here

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
