import socket
import struct
import pickle
import threading
from datetime import datetime
import hashlib

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 5000))
server_socket.listen(4)

clients_connected = {}
clients_data = {}
clients_port = {}
count = 1

listOfUser = {
    "admin": "e10adc3949ba59abbe56e057f20f883e",
    "hoang": "e10adc3949ba59abbe56e057f20f883e"
}

open("chatbox.txt",'w').close()

def connection_requests():
    global count
    while True:
        print("Waiting for connection...")
        client_socket, address = server_socket.accept()

        print(f"Connections from {address} has been established")
        print(len(clients_connected))
        if len(clients_connected) == 4:
            client_socket.send('not_allowed'.encode())

            client_socket.close()
            continue
        else:
            client_socket.send('allowed'.encode())
            #i = 0
            #Port = 0
            #for port in address:
            #    if (i == 1):
            #        Port = port
            #    else: i = 1
            #client_socket.send(str(Port).encode('utf-8'))
            

        try:
            client_name = client_socket.recv(1024).decode('utf-8')
            client_pass = client_socket.recv(1024).decode('utf-8')
        except:
            print(f"{address} disconnected")
            client_socket.close()
            continue
        
        ###
        if (listOfUser.get(client_name) == None):
            client_socket.send('wrong_name'.encode())

            if client_socket.recv(1024).decode() == 'loginStep':
                client_socket.close()
                continue
            else:
                listOfUser[client_name] = hashlib.md5(client_pass.encode()).hexdigest()

        elif (listOfUser.get(client_name) != hashlib.md5(client_pass.encode()).hexdigest()):
            client_socket.send('wrong_pass'.encode())

            if client_socket.recv(1024).decode() == 'loginStep' or client_socket.recv(1024).decode() == 'signupStep':
                client_socket.close()
                continue 
        else:
            client_socket.send('true_pass'.encode())
            
            if client_socket.recv(1024).decode() == 'signupStep':
                client_socket.close()
                continue 
        ###

        print(f"{address} identified itself as {client_name}")

        clients_connected[client_socket] = (client_name, count)
        clients_port[client_socket] = address

        image_size_bytes = client_socket.recv(1024)
        image_size_int = struct.unpack('i', image_size_bytes)[0]

        client_socket.send('received'.encode())
        image_extension = client_socket.recv(1024).decode()

        b = b''
        while True:
            image_bytes = client_socket.recv(1024)
            b += image_bytes
            if len(b) == image_size_int:
                break

        clients_data[count] = (client_name, b, image_extension)

        clients_data_bytes = pickle.dumps(clients_data)
        clients_data_length = struct.pack('i', len(clients_data_bytes))

        client_socket.send(clients_data_length)
        client_socket.send(clients_data_bytes)

        if client_socket.recv(1024).decode() == 'image_received':
            client_socket.send(struct.pack('i', count))

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode())
                    data = pickle.dumps(
                        {'message': f"{clients_connected[client_socket][0]} joined the chat", 'extension': image_extension,
                         'image_bytes': b, 'name': clients_connected[client_socket][0], 'n_type': 'joined', 'id': count})
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)

                    client.send(data)
        count += 1
        t = threading.Thread(target=receive_data, args=(client_socket,))
        t.start()


def receive_data(client_socket):
    while True:
        try:
            data_bytes = client_socket.recv(1024)

        except ConnectionResetError:
            print(f"{clients_connected[client_socket][0]} disconnected")

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode())

                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} left the chat",
                                         'id': clients_connected[client_socket][1], 'n_type': 'left'})

                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)

                    client.send(data)

            del clients_data[clients_connected[client_socket][1]]
            del clients_connected[client_socket]
            client_socket.close()
            break
        except ConnectionAbortedError:
            print(
                f"{clients_connected[client_socket][0]} disconnected unexpectedly.")

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode())
                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} left the chat",
                                         'id': clients_connected[client_socket][1], 'n_type': 'left'})
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)
                    client.send(data)

            del clients_data[clients_connected[client_socket][1]]
            del clients_connected[client_socket]
            client_socket.close()
            break

        data = pickle.loads(data_bytes)

        if data.get('to') == None:
            db = open("chatbox.txt", "a")
            db.write(str(data['from']) + ' ' + clients_connected[client_socket][0] + ' ' + datetime.now().strftime('%H:%M'))
            if data.get('message') != None:
                db.write(' message ' + data['message'] + '\n')
            elif data.get('image') != None:
                db.write(' image ' + data['image'] + '\n')
            elif data.get('file') != None:
                db.write(' file ' + data['file'] + '\n')
            db.close()

        for client in clients_connected:
            if client != client_socket:
                if data.get('message') != None:
                    client.send('message'.encode())
                    
                elif data.get('image') != None:
                    client.send('image'.encode())
                    
                elif data.get('file') != None:
                    client.send('file'.encode())
                    
                elif clients_connected[client][0] == data.get('toName'):
                    client.send('toClient'.encode())
                
                else: continue
                
                client.send(data_bytes)

connection_requests()
