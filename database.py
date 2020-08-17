import pymongo
import os 

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CloudServer"]

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