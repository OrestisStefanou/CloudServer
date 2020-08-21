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

def add_user(username,password,email):

    mycol = mydb["users"]

    mydict = { "Username": username, "Password": password, "Email":email }

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