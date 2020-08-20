import sys,os
import socket
import threading
import tincanchat
import copy
from getpass import getpass

def prRed(skk): print("\033[91m{}\033[00m" .format(skk),end='') 
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk),end='') 
def prYellow(skk): print("\033[93m{}\033[00m" .format(skk),end='') 
def prLightPurple(skk): print("\033[94m{}\033[00m" .format(skk),end='') 
def prPurple(skk): print("\033[95m{}\033[00m" .format(skk),end='') 
def prCyan(skk): print("\033[96m{}\033[00m" .format(skk),end='') 
def prLightGray(skk): print("\033[97m{}\033[00m" .format(skk),end='') 
def prBlack(skk): print("\033[98m{}\033[00m" .format(skk),end='')

HOST = sys.argv[-1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = tincanchat.PORT

homeDir = ''
curDir = ''
DownloadFile = None     #File object in case of download from the server

def handle_response(msg):
    global curDir
    global DownloadFile
    data = msg.split('$$')
    if data[0] == 'Error':
        prRed(data[1])
        print('')
        return
    
    if data[0] == 'Success':
        prGreen(data[1])
        print('')
        return
    
    if data[0] == 'Dir':
        prCyan(data[1])
        print('  ',end='',flush=True)
        return

    if data[0] == 'File':
        print(data[1] + '  ',end='',flush=True)
        return

    if data[0] == 'Cd':
        curDir = os.path.join(curDir,data[1])
        return
    

    if data[0] == 'CreateFile':
        path = os.path.split(data[1])
        filename = path[1]
        DownloadFile = open(filename,"w")
        return
    
    if data[0] == 'Line':
        line = data[1]
        DownloadFile.write(line)
        return
    
    if data[0] == 'CloseFile':
        DownloadFile.close()
        prGreen('File downloaded')
        print('')
        return

def handle_request(msg,sock):
    global curDir
    data = msg.split(' ')
    request = data[0]
    if data[0] == 'mkdir':
        if len(data) < 2:
            prRed('Wrong usage')
            print('')
            return
        msg = 'mkdir$${}$$./{}'.format(data[1],curDir)
        try:
            tincanchat.send_msg(sock,msg)
        except (BrokenPipeError,ConnectionError):
            prRed('Something went wrong')
            print('')
            return
    

    if data[0] == 'ls':
        if len(data) == 1:  #List current directory
            msg = 'ls$$./{}'.format(curDir)
            try:
                tincanchat.send_msg(sock,msg)
                return
            except (BrokenPipeError,ConnectionError):
                prRed('Something went wrong')
                print('')
                return
        else:
            msg = 'ls$$./{}'.format(data[1])
            try:
                tincanchat.send_msg(sock,msg)
                return
            except (BrokenPipeError,ConnectionError):
                prRed('Something went wrong')
                print('')
                return
    

    if data[0] == 'cd':
        if len(data) == 1:  #Change current directory to home directory
            curDir = copy.deepcopy(homeDir)
            return
        else:
            if data[1] == '..':
                head_tail = os.path.split(curDir)
                requestedDir = head_tail[0]
                if len(requestedDir) < len(homeDir):
                    prRed('Permission Denied')
                    print('')
                    return
                else:
                    curDir = requestedDir
                    return
            else:
                path = os.path.join(curDir,data[1])
                msg = 'cd$$./{}'.format(path)
                tincanchat.send_msg(sock,msg)

    
    if data[0] == 'upload':
        if len(data) == 1:  #File name not given
            prRed('File name not given')
            print('')
            return
        else:
            path = os.path.split(data[1])
            filename = path[1]
            try:
                f = open(data[1],"r")
                msg = 'CreateFile$${}'.format(os.path.join(curDir,filename))
                tincanchat.send_msg(sock,msg)
                for line in f:
                    msg = 'Line$${}$${}'.format(line,os.path.join(curDir,filename))
                    tincanchat.send_msg(sock,msg)
                msg = 'CloseFile$${}'.format(os.path.join(curDir,filename))
                tincanchat.send_msg(sock,msg)
                f.close()
            except:
                prRed("File does not exist")
                print('')
                return


    if data[0] == 'download':
        if len(data) == 1:  #File name not given
            prRed('File name not given')
            print('')
            return
        else:
            filename = data[1]
            path = os.path.join(curDir,filename)
            msg = 'Download$${}'.format(path)
            tincanchat.send_msg(sock,msg)


def handle_input(sock):
    #Prompt user for message and it to server    
    while True:
        prGreen(curDir + '$')
        msg = input()   #Blocks
        if msg == 'q':
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            break
        handle_request(msg,sock)


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((HOST,PORT))
    print('Connected to {}:{}'.format(HOST,PORT))

    rest = bytes()
    #User authentication
    verified = 0
    while verified==0:
        username = input('Username:')
        password = getpass()
        login_data = '/Login$${}$${}'.format(username,password)
        tincanchat.send_msg(sock,login_data)
        try:
            #blocks
            (msgs,rest) = tincanchat.recv_msgs(sock,rest)
            for msg in msgs:
                #print(msg)
                if msg == '1':
                    prGreen('Login successfull')
                    print('')
                    prYellow('Enter your request and press Enter.To input another request press Enter.')
                    print('')
                    homeDir = os.path.join('Users',username)
                    curDir = os.path.join('Users',username)
                    verified=1
                else:
                    prRed('Wrong username or password')
                    print('')
        except ConnectionError:
            print('\nConnection to server closed')
            sock.close()
            break
    
    #prGreen(curDir + '$')
    #Create thread for handling user input and message sending
    thread = threading.Thread(target=handle_input,args=[sock],daemon=True)
    thread.start()
    addr = sock.getsockname()
    #Loop indefinitely to receive messages from server
    while True:
        try:
            #blocks
            (msgs,rest) = tincanchat.recv_msgs(sock,rest)
            for msg in msgs:
                handle_response(msg)
        except ConnectionError:
            print('Connection to server closed')
            sock.close()
            break