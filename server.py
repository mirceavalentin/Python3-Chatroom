import select
import socket
import threading

# Store the connected clients and their respective sockets
clients = {} 


def broadcast_message(sender, message):
     # send a message to all connected clients except the sender
     for client_socket in clients.values():
         if client_socket != sender:
             client_socket.send(message.encode("utf-8"))


def remove_client(client_socket):
    # remove a client from the list of connected clients
    username = [key for key, value in clients.items() if value == client_socket]
    if username:
        username = username[0]
        del clients[username]
        print(f"User '{username}' disconnected.")


def recieve_complete_message(client_socket):
    message = ""
    while True:
        try:
            incoming_chunk =  client_socket.recv(4096).decode("utf-8")
            message += incoming_chunk 
            if not incoming_chunk or "\n" in incoming_chunk: 
                break
        except ConnectionResetError:
            remove_client(client_socket)
            print("BAD-RQST-BODY\n")
            break
    return message

# each connected client is handled in a separate thread
def handle_client(client_socket):
    user_list = {}
    while True:
        try:
            message = recieve_complete_message(client_socket).strip()
            print(message)
            if not message:
                # No data received, client has disconnected
                remove_client(client_socket)
                break
            header, body = None, None
            parts = message.split(" ", 1)
            if parts:
                header = parts[0]
                if len(parts) > 1:
                    body = parts[1]
            
            if not ("HELLO-FROM" in header or "LIST" in header or "SEND" in header):
                print("BAD-RQST-HDR\n")
                client_socket.send("BAD-RQST-HDR\n".encode("utf-8"))
                break
            
            if not body and not "LIST" in message:
                print("BAD-RQST-BODY\n")
                client_socket.send("BAD-RQST-BODY\n".encode("utf-8"))
                break

            # process the received message
            if message.startswith("HELLO-FROM"):
                incoming_username = body

                # check if the username contains whitespace
                if " " in incoming_username:
                    client_socket.send("BAD-RQST-BODY\n".encode("utf-8"))
                    remove_client(client_socket)
                    break           
                
                handshake_msg = f"IN-USE\n"
                incoming_username = body.split()[0].strip()
                
                if incoming_username not in clients:
                    handshake_msg = f"HELLO {incoming_username}\n"
                    clients[incoming_username] = client_socket

                client_socket.send(handshake_msg.encode("utf-8"))
            
                print(f"User '{incoming_username}' connected.")
                
                
            elif message.startswith("LIST"):
                user_list = ""
                user_list = ",".join(clients.keys())
                client_socket.send(f'LIST-OK {user_list}\n'.encode("utf-8"))
            
            elif message.startswith("SEND"):
                parts = message.split(" ", 2)
                recipient = parts[1]
                msg = parts[2].strip()
                
                # print(parts, recipient, msg)
                
                if recipient in clients:
                    incoming_username_socket = clients[incoming_username]
                    delivery_message = f"SEND-OK\n"
                    incoming_username_socket.sendall(delivery_message.encode("utf-8"))
                    
                    recipient_socket = clients[recipient]
                    delivery_message = f"DELIVERY {incoming_username} {msg}\n" 
                    recipient_socket.sendall(delivery_message.encode("utf-8"))
                else:
                    client_socket.send("BAD-DEST-USER\n".encode("utf-8"))
                    
            else:
                client_socket.send("Invalid command\n".encode("utf-8"))
                
        
        except ConnectionResetError:
            break

def start_server():
    max_nr_clients = 2   # set to 2 for testing purposes
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 1234))
    
    print("Chat server started.") 

    while True:
        server_socket.listen()
        
        client_socket, address = server_socket.accept()
        
        if len(clients) == max_nr_clients:
        # Send "BUSY\n" message to the new client
            client_socket.send("BUSY\n".encode("utf-8"))
            client_socket.close()
        else:    
            # New connection, accept it and start a new thread to handle it
            threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()