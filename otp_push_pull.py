from pymongo import MongoClient, response

mongo_uri = "mongodb://admin:KnMjFHNSnrDsymrJ@10.8.46.185:27017,10.8.46.184:27017,10.8.46.183:27017/rasacentral?authSource=admin&replicaSet=happy"


def push_otp(phone_number, otp):
    myclient = MongoClient(mongo_uri)
    mydb = myclient["rasacentral"]
    mycol = mydb["otp"]
    # mydict = {"phone_number": phone_number, "otp": otp}
    myquery = {"phone_number": phone_number}
    newvalues = {"$set": {"otp": otp}}
    mycol.update_one(myquery, newvalues, upsert=True)


def pull_otp(phone_number):
    myclient = MongoClient(mongo_uri)
    mydb = myclient["rasacentral"]
    mycol = mydb["otp"]
    get = mycol.find({"phone_number": phone_number}, {"otp": 1})
    for x in get:
        return x["otp"]


if __name__ == '__main__':
    push_otp("9168810003", "123456")
    # print(pull_otp("9168810003"))
