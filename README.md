# ProjectIMS
## What is this?
ProjectIMS stands for Project Intern Messaging System. It essentially is a chatroom that is hosted on one machine and allows others to connect to it. It incorporates usernames to distinguish users and contains some basic user commands (and a admin role). There also exists a server command line to run commands behind the scenes.

## What did I use?
Using multithreading and sockets inside of Python I was able to create both the client and server

## How does it work?
To run the server:
python server.py IP SOCKET
Where IP is the IP of the hosting machine and SOCKET is the socket you intend to use

To run the client:
python client.py IP SOCKET
Where IP is the IP of the machine the server is running on and SOCKET is the socket being used by the server

## Credit
Built by Alfonso Buono
