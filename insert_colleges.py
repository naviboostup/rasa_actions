
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    client = MongoClient("mongodb+srv://Admin:admin123@rasadynamic.5iza5.mongodb.net/test")
    client.server_info()
    print("Connected successfully!!!")
    mydb = client["dynamic_buttons"]
except ConnectionFailure:
   print("Connection failure")


def dbinsert(collection,data:dict):
    try:
        mycol = mydb[collection]
        mycol.insert_one(data)
        print("Data inserted successfully")
    except Exception as e:
        print(e)
    return None

if __name__ == "__main__":
    data = {
        "category" : "",
        "type" : "sub menu",
        "college_name" : "",
        "college_type":"public",
        "program_type":"public",
        "utterance":"",
        "country": "الامارات العربية المتحدة",
        "streams_available" : [
            {
                "stream_name": "المجتمع والثقافة",
                "program_list": [
                    {
                        "program_code": "SE903",
                        "details": """'رمز البرنامج SE903 :اسم البرنامج: القانون :المجال المعرفي: '
                            'المجتمع والثقافة :نوع البرنامج: منحة خارجية جزئية :اسم المؤسسة '
                            'التعليمية : دائرة البعثات الخارجية :بلد الدراسة : الامارات '
                            'العربية المتحدة :فئة الطلبة : غير اعاقة'"""
                    }
                ]
            },
            {
                "stream_name": "الهندسة والتقنيات ذات الصلة",
                "program_list": [
                    {
                        "program_code": "SE904",
                        "details": """رمز البرنامج SE904 :اسم البرنامج: الهندسة :المجال المعرفي: '
                            'الهندسة والتقنيات ذات الصلة :نوع البرنامج: منحة خارجية جزئية '
                            ':اسم المؤسسة التعليمية : دائرة البعثات الخارجية :بلد الدراسة : '
                            'الامارات العربية المتحدة :فئة الطلبة : غير اعاقة' """
                    }
                ]
            }
        ]
    }
        # "data": [
        #     {
        #     "title": "VC003",
        #     "payload": "/choose{\"option\":\"VC003\"}"
        #     },
        #     {
        #     "title": "VC004",
        #     "payload": "/choose{\"option\":\"VC004\"}"
        #     }]


    try:
        dbinsert(collection="college_details",data=data)
        print("Success!")
    except Exception as e:
        print(e)
