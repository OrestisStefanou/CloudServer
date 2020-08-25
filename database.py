import pymongo
import os
from datetime import datetime, date, time, timezone 

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CloudServer"]

#Add a log message to the database
def add_log(msg):
    dt = datetime.now()
    tt = dt.timetuple()

    mycol = mydb['logs']
    mydict = {"Message":msg,"Year":tt[0],"Month":tt[1],"Day":tt[2],"Hour":tt[3],"Minute":tt[4],"Second":tt[5]}

    x = mycol.insert_one(mydict)

#Create a new user.dir_size is the size that the user can use in bytes
def add_user(username,password,email,dir_size):

    mycol = mydb["users"]

    mydict = { "Username": username, "Password": password, "Email":email,"DirSize":dir_size *1024 }

    x = mycol.insert_one(mydict)

    #Create user's directory
    path = os.path.join('./Users',username)

    if not os.path.exists(path):
        os.mkdir(path)
        return 0
    else:
        print('Directory already exists')
        return 1

#If login info is correct return '1' else return '0'
def verify_user(username,password):
    mycol = mydb["users"]

    myquery = { "Username": username }

    mydoc = mycol.find(myquery)

    for x in mydoc:
        #print(x)
        if x['Password'] == password:
            return '1'
        else:
            return '0'
    return '0'


#Get the size of a directory in bytes
def get_directory_size(directory):
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total


#Get user's directory size
def get_users_dir_size(username):
    mycol = mydb["users"]

    myquery = { "Username": username }

    mydoc = mycol.find(myquery)

    for x in mydoc:
        #print(x)
        return x['DirSize']

#Update a user's directory size
def update_dir_size(username,size):
    mycol = mydb['users']

    myquery = { "Username":username }
    new_values = { "$set":{ "DirSize":size * 1024 } }

    mycol.update_one(myquery,new_values)