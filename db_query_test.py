from pymongo import MongoClient, response
from pymongo.collation import CollationAlternate
from pymongo.errors import ConnectionFailure
import functools

from global_variables import *

try:
    client = MongoClient(MONGO_URL)
    client.server_info()
    print("Connected successfully!!!")
    mydb = client["dynamic_buttons"]
except ConnectionFailure:
   print("Connection failure")
   
## ------------------------Search by program code----------------------------------------------

def fetch_details_from_program_code(program_code:str):
    try:
        mycol = mydb["college_details"]
        # x= mycol.find({"streams_available.0.programs.program_code":program_code})
        x= mycol.find({"streams_available.program_list.program_code":program_code},{"_id":0,"streams_available.program_list":1})
        data = list(x)[0]["streams_available"]
        # print(data)
        for i in data:
            for j in i["program_list"]:
                if j["program_code"] == program_code:
                    print(j['details'])
                    return j['details']
        # return response[0]
    except Exception as e:
        print(e)
        return None

#----------------------direct universities under Registrations------------------------------------
def fetch_direct_univ(program_type:str):
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"program_type":program_type},{"_id": 0,"college_name":1})
        data = list(x)
        x = list(i['college_name'] for i in data)
        # print(data)
        return x
    except Exception as e:
        print(e)
        return None

## ------------------------Outside Sultante----------------------------------------------
@functools.lru_cache(maxsize=None)
def outside_sul_disability(program_type:str,region:str,country:str):
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"program_type":program_type,"unique_title":region,"country":country},{"_id": 0,"streams_available":1})
        data = list(x)
        streams_available = data[0]["streams_available"]
        x = list(i['program_list'] for i in streams_available)[0]
        return x[0]['details']
    except Exception as e:
        print(e)
        return None

@functools.lru_cache(maxsize=None)
def fetch_streams_by_country(country:str,region:str): #* for outside sultanate
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"unique_title":region,"country":country},{"_id":0,"streams_available":1})
        data = list(x)[0]
        st_data = data["streams_available"]
        stream_names= list(i["stream_name"] for i in st_data)
        return stream_names
    except Exception as e:
        print(e)
        return None

@functools.lru_cache(maxsize=None)
def fetch_country_by_program_type_region(program_type:str,region:str): #* for outside sultanate 

    """[summary]

    Returns:
        variable [list]: Country list
    """
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"program_type":program_type,"unique_title":region},{"_id":0})
        data = list(x)
        # print(data)
        country_names= list(i["country"] for i in data)
        return country_names
    except Exception as e:
        print(e)
        return None 

# @functools.lru_cache(maxsize=None)
def fetch_program_codes_streams_outside_sul(region:str,country:str,program_type:str,stream:str):
    """Fetch program codes from stream name in outside sultanate flow in public prohrams and programs with disability """
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"unique_title":region,"country":country,"program_type":program_type},{"_id":0,"streams_available":1})
        data = list(x)
        streams_available = data[0]["streams_available"]
        print("Streams Available---",streams_available)
        x = list(i['program_list'] for i in streams_available if i['stream_name']== stream)[0]
        program_codes = list(i['program_code'] for i in x)
        #TODO: return program details by matching stream name
        return program_codes
    except Exception as e:
        print(e)
        return None

def outside_sul_direct_uni(program_type:str,country:str,region:str):
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"unique_title":region,"country":country,"program_type":program_type},{"_id":0,"college_name":1})
        data = list(x)
        # print(data)
        return data[0]["college_name"]
    except Exception as e:
        print(e)
        return None


##-------------------------Inside Sultante---------------------------------------------
def fetch_college_names_inside_sul(college_type:str,region:str,program_type:str):
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"college_type":college_type,"unique_title":region,"program_type":program_type},{"_id":0,"college_name":1})
        # print(list(x)) #* test with a list of names
        data = list(x)
        college_names = list(x['college_name'] for x in data)
        return college_names
    except Exception as e:
        print(e)
        return None


@functools.lru_cache(maxsize=None)
def fetch_streams_by_college(college_name:str,program_type:str):
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"college_name":college_name,"program_type":program_type},{"_id":0,"streams_available":1})
        data = list(x)[0]
        st_data = data["streams_available"]
        stream_names= list(i["stream_name"] for i in st_data)
        return stream_names
    except Exception as e:
        print(e)
        return None

@functools.lru_cache(maxsize=None)
def fetch_program_codes(college_name:str,stream_name:str,program_type:str): # inside sultanate
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"college_name":college_name,"program_type":program_type},{"_id":0,"streams_available":1})
        data = list(x)[0]
        st_data = data["streams_available"]
        data = list(i["program_list"] for i in st_data if i["stream_name"] == stream_name)
        program_names = list(i["program_code"] for i in data[0])
        return program_names,data
    except Exception as e:
        print(e)
        return None

def fetch_program_details(program_code:str,program_list:list):
    try:
        response= list(i["details"] for i in program_list if i["program_code"] == program_code)
        return response[0]
    except Exception as e:
        print(e)
        return None

def inside_sul_college_type(program_type:str,region:str):
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"program_type":program_type,"unique_title":region},{"_id":0,"college_type":1})
        data = list(x)
        college_type = list(i["college_type"] for i in data)
        return college_type
    except Exception as e:
        print(e)
        return None

@functools.lru_cache(maxsize=None)
def inside_sul_disability(program_type:str,region:str,college_name:str):
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"program_type":program_type,"unique_title":region,"college_name":college_name},{"_id": 0,"streams_available":1})
        data = list(x)
        streams_available = data[0]["streams_available"]
        x = list(i['program_list'] for i in streams_available)[0]
        return x[0]['details']
    except Exception as e:
        print(e)
        return None

#------------------------franchsise schools-----------------------------------------------
def fetch_school_prefecture(area:str):
    try:
        mycol = mydb["school_details"]

        x= mycol.find({"area":area})
        data = list(x)
        return data
    except Exception as e:
        print(e)
        return None

@functools.lru_cache(maxsize=None)
def fetch_state(prefecture:str):
    try:
        mycol = mydb["school_details"]
        x= mycol.find({"prefecture":prefecture})
        data = list(x)[0]
        st_data = data["states_list"]
        state_names= list(i["state"] for i in st_data)
        return state_names
    except Exception as e:
        print(e)
        return None

def fetch_school_details(area:str,prefecture:str,state:str):
    try:
        mycol = mydb["school_details"]
        x= mycol.find({"area":area,"prefecture":prefecture})
        data = list(x)[0]
        # print(data)
        states = data["states_list"]
        print("states",states)
        response= list(i["schools"] for i in states if i["state"] == state)
        print("response",response)
        return response[0]
    except Exception as e:
        print(e)
        return None

#------Direct University----------------

def fetch_country_by_program_type(program_type:str): #* for outside sultanate 

    """[summary]

    Returns:
        variable [list]: Country list
    """
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"program_type":program_type},{"_id":0})
        data = list(x)
        # print(data)
        country_names= list(i["country"] for i in data)
        return country_names
    except Exception as e:
        print(e)
        return None 

def college_direct_univ(program_type:str,country:str):
    try:
        mycol = mydb["college_details"]
        x= mycol.find({"country":country,"program_type":program_type},{"_id":0,"college_name":1})
        data = list(x)
        # print(data)
        return data[0]["college_name"]
    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    
    x= "Unit Testing"
    print(x.upper())
    code = "E001"
    # print(fetch_details_from_program_code(program_code= code.upper()))
    # print(x.upper())
    # print(fetch_streams(college_name="Saham Vocational College"))
    # sample_dict = {'streams_available': [
                        # {'stream_name': 'Engineering and related technologies', 
                        # 'program_list': [
                        #         {'program_code': 'VC003', 
                        #         "details": "Program code: VC003 Program name: Engineering: Knowledge area: Engineering and related technologies: Program"
                        #         },
                        #         {'program_code': 'VC004', 
                        #         "details": "Program code: VC004 Program name: Engineering: Knowledge area: Engineering and related technologies: Program"
                        #         }
                        #     ]
                        # },
                        # {'stream_name': 'Social Scieince'}
                        # ]}
    # st_data = sample_dict["streams_available"]
    # # print(st_data)
    # stream_names= []
    # for i in st_data:
    #     # print(i["stream_name"])
    #     stream_names.append(i["stream_name"])
    # print(stream_names)
        # for j in i["program_list"]:
        #     print(j["program_code"])
        #     print(j["details"])
    # print(fetch_streams(college_name="Saham Vocational College"))
    # plist= sample_dict["streams_available"][0]["program_list"]
    # print(type(plist),plist)

    # print(fetch_program_details(program_code="VC004",program_list=plist))

    # print(fetch_country_by_program_type_region(program_type="Direct Admission Universities",region="Outside Sultanate"))
    # print(fetch_streams_by_country(region="Outside Sultanate",country="Germany"))

    # print(fetch_school_prefecture(area="Franchise areas"))

    # print(fetch_college_names_inside_sul(college_type="Government",region="Inside Sultanate",program_type="Public Programs"))

    # print(fetch_program_codes(college_name="Saham Vocational College",stream_name="Engineering and related technologies"))
    
    # print(fetch_direct_univ(program_type="Direct Admission Universities"))
    # print(outside_sul_disability(program_type="Disability",region="Outside Sultanate",country="Jordan"))
    # print(inside_sul_disability(program_type="Disability",region="Inside Sultanate",college_name="University of Technology and Applied Sciences"))
    print(inside_sul_college_type(program_type="Public Programs",region="Inside Sultanate"))

# Indicators and statistics

@functools.lru_cache(maxsize=None)
def fetch_session_by_student_type(student_type:str): 
    try:
        mycol = mydb["statistic"]
        x= mycol.find({"student_type":student_type},{"_id":0,"session_list":1})
        print(x)
        data = list(x)[0]
        print(data)
        st_data = data["session_list"]
        print(st_data)
        session_names= list(i["session"] for i in st_data)
        return session_names
    except Exception as e:
        print(e)
        return None

def fetch_statistic_category(student_type:str,session:str):
    try:
        mycol = mydb["statistic"]
        x= mycol.find({"student_type":student_type},{"_id":0,"session_list":1})
        data = list(x)
        session_list = data[0]["session_list"]
        print("Streams session_list---",session_list)
        x = list(i['statistic_list'] for i in session_list if i['session']== session)[0]
        statistic_category = list(i['statistic_category'] for i in x)
        return statistic_category
    except Exception as e:
        print(e)
        return None

def fetch_details_from_statistic_category(statistic_category:str):
    try:
        mycol = mydb["statistic"]
    
        x= mycol.find({"session_list.statistic_list.statistic_category":statistic_category},{"_id":0,"session_list.statistic_list":1})
        data = list(x)[0]["session_list"]
        # print(data)
        for i in data:
            for j in i["statistic_list"]:
                if j["statistic_category"] == statistic_category:
                    print(j['statistic'])
                    return j['statistic']
        # return response[0]
    except Exception as e:
        print(e)
        return None

#----------------------------Qualification Majors--------------------------------------------------
def fetch_compatible(options:str):
    try:
        mycol = mydb["qualification_major"]

        x= mycol.find({"unique_title":options})
        data = list(x)
        return data
    except Exception as e:
        print(e)
        return None

def fetch_university_location(compatible_type:str):
    try:
        mycol = mydb["qualification_major"]

        x= mycol.find({"compatible_type":compatible_type})
        data = list(x)
        return data
    except Exception as e:
        print(e)
        return None

@functools.lru_cache(maxsize=None)
def fetch_majors(major_type:str,compatible_type:str):
    try:
        mycol = mydb["qualification_major"]
        x= mycol.find({"major_type":major_type,"compatible_type":compatible_type})
        data = list(x)[0]
        mj_data = data["major_list"]
        major_name= list(i["major_name"] for i in mj_data)
        return major_name
    except Exception as e:
        print(e)
        return None


def fetch_university(major_type:str,compatible_type:str,major_name:str):
    try:
        mycol = mydb["qualification_major"]
        x= mycol.find({"major_type":major_type,"compatible_type":compatible_type},{"_id":0,"major_list":1})
        data = list(x)  
        # print("data",data)
        major_list = data[0]["major_list"]
        print("major_list---",major_list)
        x = list(i['university_available'] for i in major_list if i['major_name']== major_name)[0]
        university_name = list(i['university_name'] for i in x)
        print("university_name",university_name)
        #TODO: return program details by matching stream name
        return university_name
    except Exception as e:
        print(e)
        return None

def fetch_subspeciality(major_type:str,compatible_type:str,major_name:str,university_name:str):
    try:
        mycol = mydb["qualification_major"]
        # x= mycol.find({"streams_available.0.programs.program_code":program_code})
        x= mycol.find({"major_type":major_type,"compatible_type":compatible_type,"major_list.major_name":major_name,"major_list.university_available.university_name":university_name},{"_id":0,"major_list.major_name":1,"major_list.university_available":1})
        print("major_type",major_type,"major_name",major_name,"-------  ",x[0])
        data = list(x)[0]["major_list"]
        for i in data:
            for j in i["university_available"]:
                if j["university_name"] == university_name and i["major_name"] == major_name:
                    # print(j["university_name"],j['subspeciality'])
                    return j['subspeciality']
        # return response[0]
    except Exception as e:
        print(e)
        return None

#---------------------Test Code------------------------------------------------------------

def fetch_testcode(testcode:str,detailsbycode:str):
    try:
        mycol = mydb["test_code"]

        x= mycol.find({"code":testcode,"unique_title":detailsbycode})
        data = list(x)
        return data
    except Exception as e:
        print(e)
        return None
