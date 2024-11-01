Small chatroom written in python3 using socks.
A convention is used between the client and server code and hidden from the user.
The server needs to be run on a host machine, then multiple clients can connect and use this to chat to other clients.
Functions like !who, to see the connected clients, !quit and @message are implemented.

The third client (unreliable_network_client.py) uses a checksum to check if the receiver received the message completely.
This is done by checking if the message sent is complete, if not, it communicates the bytes lost and completes the message.
