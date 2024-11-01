# Necessary libraries
import threading
import socket
import os

def receive_from_server(sock):
    message = ""
    while True:
        data = sock.recv(4096).decode("utf-8")
        if not data:
            break
        message += data
        while "\n" in message:
            index = message.index("\n")
            line = message[:index+1]
            message = message[index+1:]
            try:
                if line == "SEND-OK\n":
                    print("Message sent successfully.")
                elif line == "BAD-DEST-USER\n":
                    print("User is not currently logged in.")
                elif line == "BUSY\n":
                    print("Server is full.")
                    sock.close()
                    os._exit(0)
                elif line == "BAD-RQST-HDR\n":
                    print("Please rewrite the message header.")
                    sock.close()
                    os._exit(0)
                elif line == "BAD-RQST-BODY\n":
                    print("Please rewrite the message body.")
                    sock.close()
                    os._exit(0)
                elif line == "IN-USE\n":
                    print("The name is already in use. Please choose another name:")
                    communicate_to_server(sock)
                elif line.startswith("DELIVERY "):
                    parts = line.split(" ")
                    if len(parts) > 2:
                        sender = parts[1]
                        msg = " ".join(parts[2:])
                        print(f"Message from {sender}: {msg}")
                else:
                    print(line)
            except:
                print("(FATAL ERROR) Cannot read message incoming from server.")

def send_message_to_server(sock):
    while True:                                                         # Sending messages function. Will be open continously for user.
        command = input()
        if command == "!quit":                                          # !quit implementation
            print("Chat closed.")                                       # P.S. dacă nu ne lasă cu librăria asta setăm librăriile daemon în true.
            sock.close()
            os._exit(0)
        elif command == "!who":                                         # !who implementation | elif = elseif
            try:
                sock.send("LIST\n".encode("utf-8"))                     # Send "LIST" command to server
            except OSError as msg:
                print(msg)
        elif command.startswith("@"):                                   # @user <msg> implementation
            split_command = command.split(" ", 1)                       # split takes 2 arguments. first is a space, second is the number of splits
            if len(split_command) == 2:                                 # split_command now is a list with 2 elements containing user and message
                user = split_command[0][1:]                             # define user + message from the split_command list
                message = split_command[1]
                try:
                    string_bytes = f"SEND {user} {message}\n".encode("utf-8")
                    bytes_len = len(string_bytes)
                    num_bytes_to_send = bytes_len                       # Sendall replaced. For more information on this part read the lab manual.
                    while num_bytes_to_send > 0:
                        num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])
                except OSError as msg:
                    print(msg)
            else:
                print("Invalid command format. Usage: @<user> <message>")
        else:
            print("Invalid command. Please try again.")


def communicate_to_server(sock):
    user_name = input("Please enter your name: ")                       # Get user username
    if user_name != '':
        sock.send(f"HELLO-FROM {user_name}\n".encode("utf-8"))          # First handshake
    else:
        print("Username cannot be empty!")
        exit(0)
    
    threading.Thread(target=receive_from_server, args=(sock, )).start() # Keep receiving messages even if not sending messages
    send_message_to_server(sock)                                        # Prompt user to send a message. If user doesn't send a message
                                                                        # messages incoming will still appear.

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            # Define the sock connection
    try:
        host_port = ("127.0.0.1", 1234)                                 # our server
        sock.connect(host_port)
        print(f"Succesfully connected to server.\n")
    except:
        print(f"Unable to connect to server.")

    print("Hello! This a simple chat room where you can chat with your friends!\n")
    print("To see the avalabile users, use the '!who' command.\n")
    print("To send a message to a user, type '@username message'\n")
    print("To quit, type '!quit'\n")


    communicate_to_server(sock)                                         # Call the function to start communication with the server
if __name__ == '__main__':
    main()