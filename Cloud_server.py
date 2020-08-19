import threading
import queue
import tincanchat
import database
import os

HOST = tincanchat.HOST
PORT = tincanchat.PORT

send_queues = {}
openfiles = {}
lock = threading.Lock()

def handle_request(data,q):
    global openfiles
    request = data[0]
    #print('Request is ' + request)
    if request == '/Login':
        username = data[1]
        password = data[2]
        verified = database.verify_user(username,password)
        q.put(verified)
        return
    
    if request == 'mkdir':
        dirName = data[1]
        dirLocation = data[2]
        path = os.path.join(dirLocation,dirName)
        if not os.path.exists(path):
            os.mkdir(path)
            return
        else:
            q.put('Error$$Directory already exists')
            return

    if request == 'ls':
        dirName = data[1]
        try:
            files = os.listdir(dirName)
            for file in files:
                path = os.path.join(dirName,file)
                if os.path.isdir(path):
                   q.put('Dir$$'+file)
                else:
                    q.put('File$$'+file)
        except:
            q.put('Error$$Directory does not exist')
    
    if request == 'cd':
        path = data[1]
        try:
            if os.path.isdir(path):
                new_dir = os.path.split(path)
                response = 'Cd$${}'.format(new_dir[1])
                q.put(response)
            else:
                q.put('Error$$Requested path is not a directory')
        except:
            q.put('Error$$Requested directory does not exists')


    if request == 'CreateFile':
        path = data[1]
        f = open(path,"w")
        openfiles[path] = f

    if request == 'Line':
        line = data[1]
        filename = data[2]
        openfiles[filename].write(line)
    
    if request == 'CloseFile':
        filename = data[1]
        openfiles[filename].close()
        del openfiles[filename]
        q.put("Success$$File uploaded")

def handle_client_recv(sock,addr):
    #Receive messages from client and broadcast them to
    #other clients until client disconnects
    rest = bytes()
    while True:
        try:
            (msgs,rest) = tincanchat.recv_msgs(sock,rest)
        except (EOFError,ConnectionError):
            handle_disconnect(sock,addr)
            break
        for msg in msgs:
            #msg = '{}: {}'.format(addr,msg)
            print(msg)
            #Split the message
            msg_data = msg.split('$$')
            handle_request(msg_data,send_queues[sock.fileno()])
            #broadcast_msg(msg)

def handle_client_send(sock,q,addr):
    #Monitor queue for new messages,send them to client as they arrive
    while True:
        msg = q.get()
        if msg == None:
            break
        try:
            tincanchat.send_msg(sock,msg)
        except (ConnectionError,BrokenPipeError):
            handle_disconnect(sock,addr)
            break

def broadcast_msg(msg):
    #Add message to each connected client's send queue
    with lock:
        for q in send_queues.values():
            q.put(msg)

def handle_disconnect(sock,addr):
    #Make sure queue is cleaned up and socket closed 
    #when a client disconnects
    fd = sock.fileno()
    with lock:
        #Get send queue for this client
        q = send_queues.get(fd,None)
    #If we find a queue then this disconnect has not yet been handled
    if q:
        q.put(None)
        del send_queues[fd]
        addr = sock.getpeername()
        print('Client {} disconnected'.format(addr))
        sock.close()


if __name__ == "__main__":
    listen_sock = tincanchat.create_listen_socket(HOST,PORT)
    addr = listen_sock.getsockname()
    print('Listening on {}'.format(addr))
    while True:
        client_sock,addr = listen_sock.accept()
        q = queue.Queue()
        with lock:
            send_queues[client_sock.fileno()] = q
        recv_thread = threading.Thread(target=handle_client_recv,args=[client_sock,addr],daemon=True)
        send_thread = threading.Thread(target=handle_client_send,args=[client_sock,q,addr],daemon=True)
        recv_thread.start()
        send_thread.start()
        print('Connection from {}'.format(addr))