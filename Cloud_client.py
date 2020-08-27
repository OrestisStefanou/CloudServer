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
downloadDir = '/home/orestis/Downloads'
DownloadFile = None     #File object in case of download from the server


def printHelp():
    prYellow("mkdir <DirName> ->creates a new directory")
    print('')
    prYellow("ls->Shows the files and subdirs of remote current working directory")
    print('')
    prYellow("ls-s->Shows the size of the files and subdirs of remote current working directory")
    print('')
    prYellow("cd <DirName> ->Changes current working directory to DirName")
    print('')
    prYellow("upload <File Path> ->Uploads the file at File Path to the remote current working directory")
    print('')
    prYellow("uploadDir <Dir Path> ->Uploads the directory(not the subdirs) at Dir Path to the remote current working directory")
    print('')
    prYellow("download <Filename> ->Downloads the file at local current working directory ")
    print('')
    prYellow("rm <Filename> ->Removes the file from remote current working directory ")
    print('')
    prYellow("rm * ->Removes all the files from remote current working directory(Not the directories)")
    print('')
    prYellow("rmdir <Directory Name> ->Removes the directory from remote current working directory")
    print('')
    prYellow("clouspace ->Shows the available space in the cloud")
    print('')

def upload_file(filename,path,sock):
    try:
        f = open(path,"r")
        file_size = os.path.getsize(path)
        msg = 'CreateFile$${}$${}$${}'.format(os.path.join(curDir,filename),homeDir,file_size)
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



def handle_response(msg):
    global curDir
    global downloadDir
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
        try:
            path = os.path.split(data[1])
            filename = os.path.join(downloadDir,path[1])
            DownloadFile = open(filename,"w")
            return
        except:
            return
    
    if data[0] == 'Line':
        try:
            line = data[1]
            DownloadFile.write(line)
            return
        except:
            return
    
    if data[0] == 'CloseFile':
        try:
            DownloadFile.close()
            prGreen('File downloaded')
            print('')
            return
        except:
            return
    
    if data[0] == 'Mkdir':
        dirName = data[1]
        if not os.path.exists(os.path.join(downloadDir,dirName)):
            downloadDir = os.path.join(downloadDir,dirName)
            os.mkdir(downloadDir)
            curDir = os.path.join(curDir,dirName)
            return
        else:
            prRed('Directory already exists')
            return
    
    if data[0] == 'DownloadDirComplete':
        downloadDir = os.path.split(downloadDir)[0]
        return

def handle_request(msg,sock):
    global curDir
    data = msg.split(' ')
    request = data[0]

    if data[0] == 'help':
        printHelp()
        return

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
            msg = 'ls$$./{}'.format(os.path.join(curDir,data[1]))
            try:
                tincanchat.send_msg(sock,msg)
                return
            except (BrokenPipeError,ConnectionError):
                prRed('Something went wrong')
                print('')
                return
    

    if data[0] == 'ls-s':
        if len(data) == 1:  #List current directory
            msg = 'ls -s$$./{}'.format(curDir)
            try:
                tincanchat.send_msg(sock,msg)
                return
            except (BrokenPipeError,ConnectionError):
                prRed('Something went wrong')
                print('')
                return
        else:
            msg = 'ls -s$$./{}'.format(os.path.join(curDir,data[1]))
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
            """try:
                f = open(data[1],"r")
                file_size = os.path.getsize(data[1])
                msg = 'CreateFile$${}$${}$${}'.format(os.path.join(curDir,filename),homeDir,file_size)
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
                return"""
            upload_file(filename,data[1],sock)


    if data[0] == 'uploadDir':
        if len(data) == 1:
            prRed('Directory path not given')
            print('')
            return
        else:
            dirPath = data[1]
            try:
                files = os.listdir(dirPath)
                dirName = os.path.split(dirPath)[1]
                msg = 'mkdir$${}$$./{}'.format(dirName,curDir)
                tincanchat.send_msg(sock,msg)
                curDir = os.path.join(curDir,dirName)
                for file in files:
                    path = os.path.join(dirPath,file)
                    if os.path.isdir(path):
                        continue
                    else:
                        upload_file(file,path,sock)
            except:
                prRed('Directory does not exist')
                print('')

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


    if data[0] == 'downloadDir':
        if len(data) == 1:  
            prRed('Directory name not given')
            print('')
            return
        else:
            dirName = data[1]
            path = os.path.join(curDir,dirName)
            msg = 'DownloadDir$${}'.format(path)
            tincanchat.send_msg(sock,msg)


    if data[0] == 'rm':
        if len(data) == 1:  #File name not given
            prRed('File name not given')
            print('')
            return
        else:
            filename = data[1]
            path = os.path.join(curDir,filename)
            msg = 'rm$${}'.format(path)
            tincanchat.send_msg(sock,msg)


    if data[0] == 'rmdir':
        if len(data) == 1:  #Dir name not given
            prRed('Directory name not given')
            print('')
            return
        else:
            dirname = data[1]
            path = os.path.join(curDir,dirname)
            msg = 'rmdir$${}'.format(path)
            tincanchat.send_msg(sock,msg)
    

    if data[0] == 'cloudspace':
        #Get username from the homeDir
        split_path = os.path.split(homeDir)
        username = split_path[1]
        msg = 'cloudspace$${}$$./{}'.format(username,homeDir)
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
    #print('Connected to {}:{}'.format(HOST,PORT))

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
                msg = tincanchat.decrypt(msg)
                #print(msg)
                if msg == '1':
                    prGreen('Login successfull')
                    print('')
                    prYellow('Enter your request and press Enter.\nTo input another request press Enter again.\nTo quit press q.\nFor help type help\n')
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
                msg = tincanchat.decrypt(msg)
                handle_response(msg)
        except ConnectionError:
            print('Connection to server closed')
            sock.close()
            break