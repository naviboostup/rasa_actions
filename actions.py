# This files contains your custom actions which can be used to run
# custom Python code.
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import json
from typing import Any, Dict, List, Optional, Text
import requests
# from sympy import comp
from rasa_sdk import Action, Tracker
from rasa_sdk.events import FollowupAction, SessionStarted, SlotSet,AllSlotsReset,Restarted,EventType,ActionExecuted,UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from requests.models import Response
from otp_push_pull import push_otp, pull_otp
import numpy as np

from db_query_test import (
    fetch_college_names_inside_sul,
    fetch_streams_by_college,
    fetch_program_codes,
    fetch_details_from_program_code,
    fetch_program_details,
    fetch_direct_univ,
    outside_sul_direct_uni,
    outside_sul_disability,
    inside_sul_college_type,
    inside_sul_disability,
    fetch_country_by_program_type_region,
    fetch_streams_by_country,
    fetch_school_prefecture,
    fetch_state,
    fetch_school_details,
    fetch_program_codes_streams_outside_sul,
    fetch_session_by_student_type,
    fetch_statistic_category,
    fetch_details_from_statistic_category,
    fetch_country_by_program_type,
    college_direct_univ,
    fetch_compatible,
    fetch_university_location,
    fetch_majors,
    fetch_university,
    fetch_subspeciality,
    fetch_testcode
)


import os
from dotenv import load_dotenv
load_dotenv()

MAIN_MENU_URL = os.getenv('MAIN_MENU_URL')
SUBMENU_URL = os.getenv('SUBMENU_URL')
MONGO_URL = os.getenv('MONGO_URL')
MOHE_URL = os.getenv('MOHE_URL')

senders_maintain = {}

#* Not needed for the time being
# class Action_Exit(Action):
#     def name(self) -> Text:
#         return "action_exit"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message(template="utter_exit")
#         return [AllSlotsReset(),Restarted()]

#----------------------------------Forms for Schools-------------------------------

class ValidateSchoolsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_schools_form"

    async def required_slots(self, 
        slots_mapped_in_domain: List[Text], 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: DomainDict) -> List[Text]:
        # print("Slots mapped in domain---",slots_mapped_in_domain,type(slots_mapped_in_domain))
        # area = tracker.get_slot("area")
        # print("School area---",area,)
        # print("slots_mapped_in_domain",slots_mapped_in_domain)
        # if area == "Franchise area":
            # additional_slots = ["state","schools_details"]
            # return slots_mapped_in_domain + additional_slots
        return ["prefecture","state","schools_details"]
        # return ["prefecture"]

    async def validate_prefecture(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        return {"prefecture":slot_value}
    async def validate_state(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "back":
            return {"state":None,"prefecture":None}
        return {"state":slot_value}
    async def validate_schools_details(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "back":
            return {"schools_details":None,"state":None}
        return {"schools_details":slot_value}

class Action_SchoolPrefecture(Action):
    def name(self) -> Text:
        return "action_ask_prefecture"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # get data from  db
        prefecture = tracker.get_slot("area")
        print("Selected Option", prefecture)
        response = fetch_school_prefecture(area=prefecture)
        buttons = []
        for items in response:
            item = items.get("prefecture")
            print("prefecture",item)
            payload = '/choose_option{"prefecture":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        utterance = "اختر المنطقة من القائمة"
        dispatcher.utter_message(text=utterance, buttons=buttons)

        # utterance = "سوف يتم تحديث القائمة للعام الأكاديمي 2023/2022 في وقت لاحق"
        # dispatcher.utter_message(text=utterance)
        return []

class Action_State(Action):
    def name(self) -> Text:
        return "action_ask_state" # shows streams by college name

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # get data from  db
        prefecture = tracker.get_slot("prefecture")
        print(prefecture)
        response = fetch_state(prefecture=prefecture)
        
        buttons = []
        utterance = "اختر الولاية من القائمة"
        for item in response:
            payload = '/choose_option{"state":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        pmenu_payload = '/choose_option{"state":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload})
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class Action_schools_detail(Action):
    def name(self) -> Text:
        return "action_ask_schools_details"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        option = tracker.get_slot("area")
        prefecture = tracker.get_slot("prefecture")
        state = tracker.get_slot("state")
        # states_list = tracker.get_slot("states_list")
        # print("Selected Option", state)
        # print("Program_list-------", states_list)
        response = fetch_school_details(
            state=state, area=option, prefecture=prefecture
        )
        print("response",response)
        buttons = []
        pmenu_payload = '/choose_option{"schools_details":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload})
        dispatcher.utter_message(text=response)
        return []


#----------------------------------Forms for Outside Sultanate-------------------------------

class ValidateOutSulForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_outside_inside_sul_form"

    async def required_slots(self, 
        slots_mapped_in_domain: List[Text], 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: DomainDict) -> List[Text]:
        # print("Slots mapped in domain---",slots_mapped_in_domain,type(slots_mapped_in_domain))
        program_type = tracker.get_slot("program_type")
        region = tracker.get_slot("region")
        # print("region--- inside form",region)
        additional_slots= []
        if region == "Outside Sultanate":
            if program_type!= None:
                # if program_type.lower() in ["برنامج القبول المباشر","برامج لذوي الإعاقة"]:
                #     additional_slots = ["country"]
                # elif program_type.lower() == "البرامج العامة":
                #     additional_slots = ["country","stream","program_code"]
                additional_slots = ["country","stream","program_code"]
            print("additional_slots---------",additional_slots)
            return slots_mapped_in_domain + additional_slots

        elif region == "Inside Sultanate":
            if program_type!= None:
                # if program_type in ["برامج لذوي الإعاقة"]:
                #     additional_slots = ["college_type","college"]
                # else:
                additional_slots = ["college_type","college","stream","program_code"]
        # print("additional_slots---------------",additional_slots)
            return slots_mapped_in_domain + additional_slots

#------------------------------------------------------------------------------------------
    async def validate_program_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "برنامج القبول المباشر":
            slot_value = "برنامج القبول المباشر"
        elif slot_value in ["برامج لذوي الإعاقة"]:
            slot_value = "برامج لذوي الإعاقة"
        print("Slot value in validate program type ", slot_value)
        return {"program_type":slot_value}

    async def validate_country(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "back":
            return {"program_type":None,"country":None}
        else:
            return {"country":slot_value}

    async def validate_stream(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        print("Stream inside form---",slot_value)
        print("Intent----",tracker.get_intent_of_latest_message())
        region = tracker.get_slot("region")
        # slots = self.fetch_slots(tracker)
        # slots = additional_slots
        # print("Slots inside form---",slots)
        # current_index = slots.index("stream")
        # print("Current index---",current_index)
        # pslot_index = current_index-1
        # print("Previous index---",slots[pslot_index])
        if slot_value == "back":
            if region.lower() == "Outside Sultanate":
                pslot = "country"
            elif region== "Inside Sultanate":
                pslot = "college"
            print("Previous slot---",pslot)
            return {"stream":None,pslot:None} # make dynamic
        else:
            return {"stream":slot_value}
    
    async def validate_program_code(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        print("Program code inside validate program code--",slot_value)
        print("Intent----",tracker.get_intent_of_latest_message())
        if slot_value == "back":
            return {"stream":None,"program_code":None} 
        else:
            return {"program_code":slot_value}

    async def validate_college_type(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, 
        domain: DomainDict) -> Dict[Text,Any]:
        print("College type inside form---",slot_value)
        if slot_value == "back":
            return{"college_type": None,"program_type":None}
        # elif slot_value in ["مؤسسات التعليم العالي الحكومية"]:
        #     # print("Inside loop-----")
        #     slot_value = "مؤسسات التعليم العالي الحكومية"
        #     return {"college_type": slot_value}
        # elif slot_value in ["مؤسسات التعليم العالي الخاصة"]:
        #     slot_value = "مؤسسات التعليم العالي الخاصة"
        #     return {"college_type": slot_value}
        else:
            return {"college_type":slot_value}

    async def validate_college(self,
        slot_value: Any, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker, 
        domain: DomainDict) -> Dict[Text,Any]:
        if slot_value == "back":
            return{"college": None,"college_type":None}
        else:
            return {"college":slot_value}

class AskforSlotAction1(Action):
    def name(self) -> Text:
        return "action_ask_program_type"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        region = tracker.get_slot("region")
        URL = SUBMENU_URL + region
        data = requests.get(url=URL)
        print(data,"inside action ask program_type")
        data = json.loads(data.text)
        buttons = data["data"]
        utterance = data.get("utterance")
        if utterance == None:
            utterance = "الرجاء تحديد خيار من أدناه"
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class AskForSlotAction2(Action):
    def name(self) -> Text:
        return "action_ask_country"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        region = tracker.get_slot("region")
        program_type = tracker.get_slot("program_type")
        response = fetch_country_by_program_type_region(program_type=program_type, region=region)
        print("Countries-----",response)
        buttons = []
        for item in response:
            payload = '/choose_country{"country":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        pmenu_payload = '/choose_country{"country":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload}) #* for القائمة السابقة option
        dispatcher.utter_message(text="Please select a country",buttons=buttons)
        return []

class AskForSlotAction3(Action):
    def name(self) -> Text:
        return "action_ask_stream"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        region= tracker.get_slot("region")
        country = tracker.get_slot("country")
        college  = tracker.get_slot("college")
        program_type = tracker.get_slot("program_type")
        if country:
            response = fetch_streams_by_country(region=region, country=country)
        elif college:
            response = fetch_streams_by_college(college_name=college,program_type=program_type)
        buttons = []
        utterance = "يرجى الاختيار من بين التدفقات المتاحة أدناه:"
        for item in response:
            payload = '/choose_stream{"stream":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        pmenu_payload = '/choose_stream{"stream":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload}) #* for القائمة السابقة option
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return [] 

class AskForSlotAction4(Action):
    def name(self) -> Text:
        return "action_ask_program_code"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        region= tracker.get_slot("region")
        country = tracker.get_slot("country")
        stream = tracker.get_slot("stream")
        program_type = tracker.get_slot("program_type")
        college  = tracker.get_slot("college")
        if region == "Outside Sultanate":
            program_code_list = fetch_program_codes_streams_outside_sul(region=region, country=country, program_type=program_type,stream=stream)
        elif region == "Inside Sultanate":
            program_code_list,details = fetch_program_codes(college_name=college,stream_name=stream,program_type=program_type)
            # print(response,"inside program code",type(response))
        buttons = []
        utterance = "لرجاء الاختيار من أدناه رمز البرنامج:"
        for item in program_code_list:
            payload = '/get_program_code{"program_code":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        pmenu_payload = '/get_program_code{"program_code":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload}) #* for القائمة السابقة option
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return [] 

#----------------------------Form Submit action----------------------------------
class ActionSubmit_Outside_sul_form(Action):
    def name(self) -> Text:
        return "action_submit_outside_inside_sul_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        program_type = tracker.get_slot("program_type")
        region = tracker.get_slot("region")
        country = tracker.get_slot("country")
        program_code = tracker.get_slot("program_code")
        if region == "Outside Sultanate":
            # if program_type == "البرامج العامة":
            #     response = fetch_details_from_program_code(program_code=program_code)
            # elif program_type  == "برنامج القبول المباشر":
            #     region = tracker.get_slot("region")
            #     response = outside_sul_direct_uni(country=country, region=region, program_type=program_type)
            # elif program_type == "برامج لذوي الإعاقة":
            #     response = outside_sul_disability(program_type=program_type,region=region,country=country)
            response = fetch_details_from_program_code(program_code=program_code)
        elif region == "Inside Sultanate":
            if program_type == "برامج لذوي الإعاقة":
                college= tracker.get_slot("college")
                response = inside_sul_disability(program_type=program_type,region=region,college_name=college)
            else:
                response = fetch_details_from_program_code(program_code=program_code)
        buttons = []
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=response,buttons=buttons)
        return []

#----------------------------------Forms for Inside Sultanate-------------------------------

class AskForSlotAction5(Action):
    def name(self) -> Text:
        return "action_ask_college_type"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        program_type = tracker.get_slot("program_type")
        region = tracker.get_slot("region")
        buttons = []
        utterance = "اختبار نوع المؤسسة التعليمية"
        if program_type:
            if program_type == "برامج لذوي الإعاقة":
                response = inside_sul_college_type(region=region,program_type=program_type)
                for r in response:
                    payload = '/choose_option{"college_type":"' + r + '"}'
                    buttons.append({"title": r, "payload": payload})
            #     # dispatcher.utter_message(text=utterance, buttons=buttons)
            else:
                try:
                    URL = SUBMENU_URL + program_type
                    data = requests.get(url=URL)
                    data = json.loads(data.text)
                    buttons = data["data"]
                except Exception as e:
                    print(e)
        
        print("Buttons value inside ask college type",buttons)
        buttons.append({"title": "القائمة السابقة", "payload": '/choose_option{"college_type":"back"}'})
        buttons.append({"title": "خروج", "payload": '/restart'})  
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []


class AskForSlotAction6(Action):
    def name(self) -> Text:
        return "action_ask_college"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        #get data from  db
        college_type = tracker.get_slot("college_type")
        region = tracker.get_slot("region")
        program_type = tracker.get_slot("program_type")
        print("Program type, region, college_type ---- ",program_type,region,college_type)
        response = fetch_college_names_inside_sul(
            college_type=college_type,
            region=region,
            program_type=program_type
            )
        print("College names--------------",response)
        buttons = []
        utterance = "الرجاء الاختيار من الكليات أدناه:"
        for r in response:
            payload = '/choose_option{"college":"' + r + '"}'
            buttons.append({"title": r, "payload": payload})
        buttons.append({"title": "القائمة السابقة", "payload": '/choose_option{"college":"back"}'})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

#-----------------------------------------------------------------------------------
class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_goto_main_menu"

    async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # the session should begin with a `session_started` event
        events = [AllSlotsReset()]
        events.append(FollowupAction("action_mainmenu"))
        return events

class Action_MainMenu(Action):
    """
    Action used for showing main menu
    """
    def name(self) -> Text:
        return "action_mainmenu"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # get data from  db
        data = requests.get(url=MAIN_MENU_URL)
        print(data)
        data = json.loads(data.text)
        buttons = data["data"]
        utterance = data.get("utterance")
        if utterance == None:
            utterance = "الرجاء تحديد خيار من أدناه"
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class Action_SubMenu(Action):
    """
    Action used for showing sub menu
    """
    def name(self) -> Text:
        return "action_submenu"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        option = tracker.get_slot("option")
        # program_type = tracker.get_slot("program_type")
        # region = tracker.get_slot("region")
        URL = SUBMENU_URL + option  
        data = requests.get(url=URL)
        print(data)
        data = json.loads(data.text)
        buttons = data["data"]
        utterance = data.get("utterance")
        if utterance == None:
            utterance = "الرجاء تحديد خيار من أدناه"
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class Action_ProgramDetails(Action):
    def name(self) -> Text:
        return "action_search_program_code"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # get data from  db
        program_code = tracker.latest_message.get("text")
        print("Program Code-----", program_code)
        program_code = program_code.upper()
        response = fetch_details_from_program_code(program_code=program_code)
        if response:
            utterance = response
        else:
            utterance = "رمز البرنامج غير موجود"
        dispatcher.utter_message(text=utterance)
        return []
# Indicators and statistics

class ValidatestatisticForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_statistic_form"

    async def required_slots(self, 
        slots_mapped_in_domain: List[Text], 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: DomainDict) -> List[Text]:

        return ["session","statistic_category","statistic"]


    async def validate_session(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        return {"session":slot_value}

    async def validate_statistic_category(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "back":
            return {"statistic_category":None,"session":None}
        return {"statistic_category":slot_value}

    async def validate_statistic(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        return {"statistic":slot_value}


class AskForSession(Action):
    def name(self) -> Text:
        return "action_ask_session"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        #get data from  db
        student_type = tracker.get_slot("student_type")
        print("student_type",student_type)
        response = fetch_session_by_student_type(
            student_type=student_type
            )
        print(response)
        buttons = []
        utterance = "الرجاء تحديد خيار من أدناه"
        for r in response:
            payload = '/choose_option{"session":"' + r + '"}'
            buttons.append({"title": r, "payload": payload})
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class AskForStatisticCategory(Action):
    def name(self) -> Text:
        return "action_ask_statistic_category"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        student_type= tracker.get_slot("student_type")
        session = tracker.get_slot("session")

        statistic_category_list = fetch_statistic_category(student_type=student_type, session=session)
        print('statistic_category_list',statistic_category_list)
        buttons = []
        utterance = "الرجاء تحديد خيار من أدناه"
        for item in statistic_category_list:
            payload = '/choose_option{"statistic_category":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        pmenu_payload = '/choose_option{"statistic_category":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload}) #* for القائمة السابقة option
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return [] 

class ActionStatistic(Action):
    def name(self) -> Text:
        return "action_ask_statistic"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        statistic_category = tracker.get_slot("statistic_category")
        
        response = fetch_details_from_statistic_category(statistic_category=statistic_category)
            
        buttons = []
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=response,buttons=buttons)
        return []
# class Action_specialization(Action):

#     def name(self) -> Text:
#         return "action_by_region"
#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         slot_value = tracker.get_slot("region")
#         if slot_value:
#             URL = SUBMENU_URL + slot_value
#             data = requests.get(url=URL)
#             print(data)
#             data = json.loads(data.text)
#             buttons = data["data"]
#             utterance = data.get("utterance")
#             if utterance == None:
#                 utterance = "Please select an option from below"
#             dispatcher.utter_message(text=utterance, buttons=buttons)
#             return []

# class Action_direct_universities(Action):
#     def name(self) -> Text:
#         return "action_show_collegelist"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         option = tracker.get_slot("option")
#         if option.lower() == "direct admission program": ## to be removed later
#             option = "Direct Admission Universities"
#         country = tracker.get_slot("country")
#         print(option,country)
#         response = fetch_direct_univ(option)
#         print("Response----",response)
#         for item in response:
#             if item.get("country")==country:
#                 colleges = item.get("college_name")
#                 dispatcher.utter_message(text=colleges)
#         return []


# class Action_programtype(Action):

#     def name(self) -> Text:
#         return "action_by_program_type"
#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         slot_value = tracker.get_slot("program_type")
#         if slot_value:
#             URL = SUBMENU_URL + slot_value
#             data = requests.get(url=URL)
#             print(data)
#             data = json.loads(data.text)
#             buttons = data["data"]
#             utterance = data.get("utterance")
#             if utterance == None:
#                 utterance = "Please select an option from below"
#             dispatcher.utter_message(text=utterance, buttons=buttons)
#             return []

# class Action_CollegeNames(Action):
#     """for inside sultanate flow to show the list of college names   
#     """
#     def name(self) -> Text:
#         return "action_show_college_names" 

    # def run(
    #     self,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> List[Dict[Text, Any]]:
    #     # get data from  db
    #     college_type = tracker.get_slot("college_type")
    #     region = tracker.get_slot("region")
    #     programtype = tracker.get_slot("program_type")

    #     print("College type", college_type)
    #     print("Region", region)
    #     print("Program Type", programtype)

    #     #TODO: Not required if db values are set as per frontend

    #     if programtype.lower() == "public programs":
    #         programtype = "public"
    #     elif programtype.lower() == "programs with people for disabilities":
    #         programtype = "disability"

    #     if college_type.lower() == "private higer education institutions":
    #         college_type = "private"
    #         response = fetch_college_names_inside_sul(college_type=college_type,region=region,program_type=programtype)
    #         print("--------------",response)
    #     elif college_type.lower() == "government higer education institutions":
    #         college_type = "government"
    #         response = fetch_college_names_inside_sul(college_type=college_type,region=region,program_type=programtype)
    #         print("--------------",response)
    #     response = response.get("college_name")
    #     # print(response)
    #     buttons = []
    #     utterance = "Please select a college"
    #     payload = '/choose_option{"college":"' + response + '"}'
    #     buttons.append({"title": response, "payload": payload})
    #     dispatcher.utter_message(text=utterance, buttons=buttons)
    #     return []


# class Action_Streams(Action):
#     def name(self) -> Text:
#         return "action_show_streams" # shows streams by college name

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         # get data from  db
#         region= tracker.get_slot("region")
#         country = tracker.get_slot("country")
#         college = tracker.get_slot("college")
#         if college:
#             response = fetch_streams(college_name=college)
#         elif all([region, country]):
#             response = fetch_streams_by_country(region=region, country=country)
#         buttons = []
#         utterance = "Please select a stream"
#         for item in response:
#             payload = '/choose_stream{"stream":"' + item + '"}'
#             buttons.append({"title": item, "payload": payload})
#         pmenu_payload = '/previous_menu{"previous_menu_slot":"' + "country"  + '"}'
#         buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload}) #* for القائمة السابقة option
#         dispatcher.utter_message(text=utterance, buttons=buttons)
#         return [] 

# class Inside_sul_program_codes(Action):
#     def name(self) -> Text:
#         return "action_inside_sul_show_program_codes"  #* inside sultanate flow to show the list of program codes

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         # get data from  db
#         college = tracker.get_slot("college")
#         stream = tracker.get_slot("stream")
#         print("Selected Option", stream)
#         response, program_list = fetch_program_codes(
#             college_name=college, stream_name=stream
#         )
#         print("program codes",response)
#         print("Program_list-------", program_list)
#         # utterance = data["utterance"]
#         buttons = []
#         utterance = "Please select a program code"
#         for item in response:
#             payload = '/choose_option{"program_code":"' + item + '"}'
#             buttons.append({"title": item, "payload": payload})
#         dispatcher.utter_message(text=utterance, buttons=buttons)
#         set_slot("program_list", program_list)
#         return []

# class Outside_sul_program_codes(Action):
#     def name(self) -> Text:
#         return "action_outside_sul_show_program_codes"  #* inside sultanate flow to show the list of program codes

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         # get data from  db

#         stream = tracker.get_slot("stream")
#         country =  tracker.get_slot("country")
#         program_type= tracker.get_slot("program_type")
#         region = tracker.get_slot("region")
#         print("region-",region,"program_type-",program_type)
#         response = fetch_program_codes_streams_outside_sul(country=country,region=region,program_type=program_type,stream=stream)
#         buttons = []
#         utterance = "Please select a program code"
#         for item in response:
#             payload = '/choose_option{"program_code":"' + item + '"}'
#             buttons.append({"title": item, "payload": payload})
#         dispatcher.utter_message(text=utterance, buttons=buttons)
#         return []

# class Action_ProgramList(Action):
#     def name(self) -> Text:
#         return "action_show_program_details"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         program_code = tracker.get_slot("program_code")
#         program_list = tracker.get_slot("program_list")
#         print("Selected Option", program_code)
#         print("Program_list-------", program_list)
#         response = fetch_program_details(
#             program_code=program_code, program_list=program_list[0]
#         )
#         dispatcher.utter_message(text=response)
#         return []

class ActionShowCountries(Action):
    def name(self) -> Text:
        return "action_show_country" #* for direct admission universities and direct outside sultanate options

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        option = tracker.get_slot("option")

        buttons = []
        response = None
        if option in ["برنامج القبول المباشر","Direct Admission Programs"]:
            option = "برنامج القبول المباشر"
            response = fetch_country_by_program_type(program_type= option)  
            print("Response----",response)
            # dispatcher.utter_message(text=response)
            # return []

        for item in response:
            payload = '/choose_country{"country":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        
        utterance = "الرجاء الاختيار من بين الدول التالية:"
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class ActionShowColleges(Action):
    def name(self) -> Text:
        return "action_show_direct_colleges"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        program_type = tracker.get_slot("option")
        country = tracker.get_slot("country")
        program_code = tracker.get_slot("program_code")
        if program_type in ["برنامج القبول المباشر","Direct Admission Programs"]:
            program_type = "برنامج القبول المباشر"
        region = tracker.get_slot("region")
        response = college_direct_univ(country=country, program_type=program_type)
        buttons = []
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=response,buttons=buttons)
        return []


# class Action_Previousmenu(Action):
#     def name(self) -> Text:
#         return "action_previous_menu"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         previous_menu = tracker.get_slot("previous_menu_slot")
#         if previous_menu == "country":
#             return [FollowupAction("action_show_country")]
#         elif previous_menu:
#             URL = SUBMENU_URL + previous_menu
#             data = requests.get(url=URL)
#             print(data)
#             data = json.loads(data.text)
#             buttons = data["data"]
#             utterance = data.get("utterance")
#             if utterance == None:
#                 utterance = "Please select an option from below"
#             dispatcher.utter_message(text=utterance, buttons=buttons)
#             return []
    
class OfferForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_offer_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
       
        return ["civil_number", "phone_number", "otp", "offer"]

    async def validate_civil_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {
            "civil_number": slot_value
        }

    async def validate_phone_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {
            "phone_number": slot_value
        }

    async def validate_otp(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        return {
            "otp": slot_value
        }
    async def validate_offer(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
      
        return {
                "offer": slot_value
            }
class AskForOtp(Action):
    def name(self) -> Text:
        return "action_ask_otp"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        civil_number = tracker.get_slot("civil_number")
        # print(tracker.events[3]['input_channel'])
        # if tracker.events[3]['input_channel'] == "web":
        phone_number = tracker.get_slot("phone_number")
        option = tracker.get_slot("option")
        # else:
        #     phone_number = tracker.sender_id[3:]
        if option == "thirdsort":
            url = MOHE_URL+"/api/student/checkAvailability2"
        else:
            url = MOHE_URL+"/api/student/checkAvailability"

        # if tracker.get_latest_input_channel().lower() == "web":
        querystring = {"civil": civil_number, "mobileNumber": phone_number, "web": "1"}
        # else:
            # querystring = {"civil": civil_number, "mobileNumber": phone_number}

        payload = ""
        response = requests.request("GET", url, data=payload, params=querystring)
        if response.json()["success"]:
            # otp_validate[phone_number] = response.json()["otp"]
            push_otp(phone_number, response.json()["otp"])
            print(20*"==")
            print("OTP: ", response.json()["otp"])
            print("phone_number: ", phone_number)
            print(20 * "==")
            dispatcher.utter_message(
                response="utter_otp_notify"
            )
            return []
        else:
            dispatcher.utter_message(
                text=response.json()[
                         'message'] + "\n" + """اكتب ""خروج"" لل"خروج" من المحادثة ، أو اكتب "1" للعودة إلى القائمة الرئيسية"""
            )
            # return [AllSlotsReset(), FollowupAction('humanhandoff_yesno_form')]

            return []



class ActionOfferYesno(Action):
    def name(self) -> Text:
        return "action_ask_offer"

    def run(
         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        civil_number = tracker.get_slot("civil_number")
        # if tracker.get_latest_input_channel().lower() == "web":
        phone_number = tracker.get_slot("phone_number")
        try:
            otp = pull_otp(phone_number)
        except:
            otp = "0000"
        # if tracker.get_slot("otp") == otp_validate[phone_number]:
        if tracker.get_slot("otp") == otp:
            pass
        else:
            dispatcher.utter_message(
                response="utter_otp_verification_failed"
            )
            return [AllSlotsReset(), Restarted()]
        # else:
        #     phone_number = tracker.sender_id[3:]
        # main_menu_option = tracker.get_slot("main_menu")
        option = tracker.get_slot("option")

        if option == "thirdsort":
            url = MOHE_URL+"/api/student/checkAvailability/duplicate2"
        else:
            url = MOHE_URL+"/api/student/checkAvailability/duplicate"
        # if tracker.get_latest_input_channel().lower() == "web":
        querystring = {"civil": civil_number, "mobileNumber": phone_number, "web": "1"}
        # else:
        #     querystring = {"civil": civil_number, "mobileNumber": phone_number}

        payload = ""
        response = requests.request("GET", url, data=payload, params=querystring)
        if not response.json()['success']:
            dispatcher.utter_message(
                text= response.json()['message'] + "\n" + """اكتب ""خروج"" لل"خروج" من المحادثة ، أو اكتب "1" للعودة إلى القائمة الرئيسية"""
            )
            return [ SlotSet(key="civil_number", value=None),
                    SlotSet(key="phone_number", value=None),
                    SlotSet(key="otp", value=None),
                FollowupAction('offer_form')]
        else:
            # print("else----", response.json()['ArabicName'])
            buttons = []
            utterance = "هل ترغب في الحصول على عرض؟"
            
            buttons.append({"title": "نعم", "payload": '/choose_option{"offer":"yes"}'})
            buttons.append({"title": "ليس", "payload": '/choose_option{"offer":"no"}'})
            buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
            buttons.append({"title": "خروج", "payload": '/restart'})
            dispatcher.utter_message(text=utterance,buttons=buttons)
            return []

class ActionSubmitOfferYesNoForm(Action):
    def name(self) -> Text:
        return "action_submit_offer_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        civil_number = tracker.get_slot("civil_number")
        # phone_number = tracker.sender_id[2:]

        option = tracker.get_slot("option")
        print("option..............",option)
        if option == "firstsort":
            option_type= 1
        elif option == "secondsort":
            option_type = 2
        elif option == "thirdsort":
            option_type = 3
        if tracker.get_slot('offer') == 'yes':
            url = MOHE_URL+"/api/student/getOffer"
            querystring = {"civil": civil_number, "type": option_type}
            payload = ""
            response = requests.request("GET", url, data=payload, params=querystring)
            if not response.json()['success']:
                new_response=response.json()['message'] + "\n" + """اكتب ""خروج"" لل"خروج" من المحادثة ، أو اكتب "1" للعودة إلى القائمة الرئيسية"""
                # [AllSlotsReset(), FollowupAction('humanhandoff_yesno_form')]
                # return [AllSlotsReset(), Restarted()]
            else:
                new_response='هذه الكلية متاحة في عرضك:\n' + response.json()['message'] + "\n" + """اكتب ""خروج"" لل"خروج" من المحادثة ، أو اكتب "1" للعودة إلى القائمة الرئيسية"""
                
                # return [
                #     AllSlotsReset(), Restarted()
                # ]

        else:
                new_response="utter_empty_record"
            
            # return [AllSlotsReset(), Restarted(), FollowupAction('action_exit')]
        buttons = []
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=new_response,buttons=buttons)
        return []

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # tell the user they are being passed to a customer service agent
        sender = tracker.sender_id

        try:
            number_of_fallback = senders_maintain["sender"]
            senders_maintain["sender"] = senders_maintain["sender"] + 1
        except:
            senders_maintain["sender"] = 0
            number_of_fallback = 0

        if number_of_fallback == 1:
            senders_maintain["sender"] = 0
            dispatcher.utter_message(
                text="""  لمزيد من المعلومات يمكنك التواصل بإحدى وسائل التواصل التالية

        هاتف رقم        

        24340900

        البريد الالكتروني

        public.services@mohe.gov.om

        تويتر

        @HEAC_INFO"""
            )

            return [UserUtteranceReverted()]
            # return [AllSlotsReset(), FollowupAction('humanhandoff_yesno_form')]
        else:
            dispatcher.utter_message(
                text="أنا آسف ، لم أفهم ذلك تمامًا. هل يمكنك إعادة الصياغة؟"
            )

            return [UserUtteranceReverted()]



class HumanhandoffYesNoForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_humanhandoff_yesno_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        return ["humanhandoff_yesno"]

    async def validate_humanhandoff_yesno(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {
                "humanhandoff_yesno": slot_value
            }
        
class ActionHemanHandsOff(Action):
    def name(self) -> Text:
        return "action_ask_humanhandoff_yesno"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

       
        buttons = []
        utterance = "Would you like to talk agent"
        
        buttons.append({"title": "yes", "payload": '/choose_option{"humanhandoff_yesno":"yes"}'})
        buttons.append({"title": "no", "payload": '/choose_option{"humanhandoff_yesno":"no"}'})
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'})
        dispatcher.utter_message(text=utterance,buttons=buttons)
        return []


class ActionSubmitHumanhandoffYesNoForm(Action):
    def name(self) -> Text:
        return "action_submit_humanhandoff_yesno_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("tracker.get_slot humanhandoff_yesno",tracker.get_slot("humanhandoff_yesno"))
        if tracker.get_slot("humanhandoff_yesno") == "yes":
            print("tracker.get_slot humanhandoff_yesno",tracker.get_slot("humanhandoff_yesno"))
            dispatcher.utter_message(
                response="utter_chat_transfer_message",
                json_message={
                    "handover": True
                }
            )


        else:
            dispatcher.utter_message(
                response="utter_handover_failed_message"
            )

        return [AllSlotsReset(), Restarted()]
    

class ValidateQualficationsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_qualifiation_form"

    async def required_slots(self, 
        slots_mapped_in_domain: List[Text], 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: DomainDict) -> List[Text]:
        # print("Slots mapped in domain---",slots_mapped_in_domain,type(slots_mapped_in_domain))
        # area = tracker.get_slot("area")
        # print("School area---",area,)
        # print("slots_mapped_in_domain",slots_mapped_in_domain)
        # if area == "Franchise area":
            # additional_slots = ["state","schools_details"]
            # return slots_mapped_in_domain + additional_slots
        return ["compatible","university_location","majors","university","subspeciality"]

    async def validate_compatible(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        # if slot_value == "back":
        #     return {"university_location":None,"compatible_graduates":None}
        return {"compatible":slot_value}

    async def validate_university_location(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "back":
            return {"university_location":None,"compatible":None}
        return {"university_location":slot_value}
    async def validate_majors(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "back":
            return {"majors":None,"university_location":None}
        return {"majors":slot_value}
    async def validate_university(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "back":
            return {"university":None,"majors":None}
        return {"university":slot_value}
    async def validate_subspeciality(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, Any]:
        if slot_value == "back":
            return {"subspeciality":None,"university":None}
        return {"subspeciality":slot_value}

class Action_CompatibleGraduates(Action):
    def name(self) -> Text:
        return "action_ask_compatible"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # get data from  db
        options = tracker.get_slot("option")
        print("Selected Option", options)
        response = fetch_compatible(options=options)
        buttons = []
        compatible_list = []
        for items in response:
            item = items.get("compatible_type")
            print("compatible_type",item)
            compatible_list.append(item)
            x = np.array(compatible_list)
            uniq_com = np.unique(x)
        for i in uniq_com: 
            utterance = "الرجاء تحديد مرحلة من القائمة أدناه:"
            payload = '/choose_option{"compatible":"' + i + '"}'
            buttons.append({"title": i, "payload": payload})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class Action_UniversityLocation(Action):
    def name(self) -> Text:
        return "action_ask_university_location"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # get data from  db
        compatible = tracker.get_slot("compatible")
        print("Selected Option", compatible)
        response = fetch_university_location(compatible_type=compatible)
        buttons = []
        for items in response:
            item = items.get("major_type")
            print("major_type",item)
            if compatible == "تخصصات الخرجين الغير متوافقة مع التخصص المطلوب للتأهيل التربوي":
                utterance = "للتعرف على تخصصات الخريجين من حملة مؤهل البكالوريوس غير المتوافقة مع التخصصات المطروحة لدبلوم التأهيل التربوي لعدم إستيفائهم لعدد الساعات المطلوبة المعتمدة لشغل الوظفية.  إختر الجهة المتخرج منهل لمؤهل البكالوريوس:"
            elif compatible == "تخصصات الخرجين المتوافقة مع التخصص المطلوب للتأهيل التربوي":
                utterance = "للتعرف على تخصصات الخريجين من حملة مؤهل البكالوريوس المتوافقة مع التخصصات المطروحة لدبلوم التأهيل التربوي . الرجاء تحديد مرحلة من القائمة أدناه:"
            payload = '/choose_option{"university_location":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        pmenu_payload = '/choose_option{"university_location":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class Action_Mojors(Action):
    def name(self) -> Text:
        return "action_ask_majors" # shows streams by college name

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # get data from  db
        university_location = tracker.get_slot("university_location")
        compatible = tracker.get_slot("compatible")
        print(university_location)
        response = fetch_majors(major_type=university_location,compatible_type=compatible)
        
        buttons = []
        utterance = "التخصصات التالية درست من قبل اللجنة المختصة بوزارة التربيةوالتعليم وأقرت بأنها  تخصصات متوافقة مع تخصصات دبلوم التأهيل التربوي.  للتعرف على تخصصات الخريجين من حملة مؤهل البكالوريوس المتوافقة مع التخصصات المطروحة لدبلوم التأهيل التربوي.  إختر تخصص التأهيل التربوي المطلوب:"
        for item in response:
            payload = '/choose_option{"majors":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        pmenu_payload = '/choose_option{"majors":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class Action_University(Action):
    def name(self) -> Text:
        return "action_ask_university"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        compatible = tracker.get_slot("compatible")
        university_location = tracker.get_slot("university_location")
        majors = tracker.get_slot("majors")
        # states_list = tracker.get_slot("states_list")
        # print("Selected Option", state)
        # print("Program_list-------", states_list)
        print(compatible,"    ",university_location,"    ", majors)
        response = fetch_university(
            compatible_type=compatible, major_type=university_location, major_name=majors
        )
        buttons = []
        utterance = "في حالة أن الجامعة المتخرج منها لم تذكر، يمكنك التقدم لبرنامج التأهيل التربوي وسوف يدرس الطلب ويتم الرد عليكم عن طريق الرسائل النصية والبريد الإلكتروني.  إختر المؤسسة التعليمية المتخرج منها لمؤهل البكالوريوس:"
        for item in response:
            payload = '/choose_option{"university":"' + item + '"}'
            buttons.append({"title": item, "payload": payload})
        pmenu_payload = '/choose_option{"university":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload})
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'})
        dispatcher.utter_message(text=utterance, buttons=buttons)
        return []

class Action_Subspeciality(Action):
    def name(self) -> Text:
        return "action_ask_subspeciality"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        compatible = tracker.get_slot("compatible")
        university_location = tracker.get_slot("university_location")
        majors = tracker.get_slot("majors")
        university= tracker.get_slot("university")
        # states_list = tracker.get_slot("states_list")
        # print("Selected Option", state)
        # print("Program_list-------", states_list)
        response = fetch_subspeciality(
            compatible_type=compatible, major_type=university_location, major_name=majors, university_name=university
        )
        print("response",response)
        buttons = []
        pmenu_payload = '/choose_option{"subspeciality":"back"}'
        buttons.append({"title": "القائمة السابقة", "payload": pmenu_payload})
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'})
        dispatcher.utter_message(text=response)
        return []

class TestCodeForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_testcode_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
       
        return ["testcode"]

    async def validate_testcode(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {
            "testcode": slot_value
        }

class Action_AskTestCode(Action):
    def name(self) -> Text:
        return "action_submit_testcode_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # get data from  db
        testcode = tracker.get_slot("testcode")
        detailsbycode = tracker.get_slot("detailsbycode")
        print("Selected Option", testcode)
        response = fetch_testcode(testcode=testcode.upper(),detailsbycode=detailsbycode)
        print(response)
        buttons = []
        if response == []:
            print("Program Code do not match")
            utterance= "Program Code do not match"
            dispatcher.utter_message(text=utterance)
            # return [AllSlotsReset(), Restarted(), FollowupAction('testcode_form')]
            return [
                SlotSet(key="testcode", value=None),
                FollowupAction('testcode_form')
             
            ]
        else:
            print("Program Code match")
            for items in response:
                item = items.get("details")
                utterance = item
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=utterance,buttons=buttons)
        return [AllSlotsReset(), Restarted()]

class CompRatesForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_competativerates_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
       
        return ["comp_code"]

    async def validate_comp_code(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {
            "comp_code": slot_value
        }


class ActionSubmitProgramCutoff(Action):
    def name(self) -> Text:
        return "action_submit_competativerates_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        code_from_user = tracker.get_slot('comp_code').lower()
#        a = """ويمكن الاطلاع على وصف البرنامج من خلال الرابط التالي مع مراعاة الترتيب عن اختيار المجال المعرفي واسم 
#        المؤسسة ورمز البرنامج لعرض الوصف 
#        https://apps.heac.gov.om:888/SearchEngine/faces/programsearchengine.jsf """
#        b = """اكتب 1 للعودة إلى القائمة الرئيسية ، أو اكتب ""خروج"" لل"خروج" من المحادثة"""
#        for program in school_codes:
#            if program["code"].lower() == code_from_user:
#                dispatcher.utter_message(
#                    text=program["details"] + "\n \n " + a + " \n \n" + b
#                )
#                return [AllSlotsReset(), Restarted()]
#        dispatcher.utter_message(
#            response="utter_invalid_code"
#        )

        url = MOHE_URL+"/api/student/getCutOff"
        querystring = {"programCode": code_from_user}
        payload = ""
        response = requests.request("GET", url, data=payload, params=querystring)
        if not response.json()['success']:
           
            new_response="""
              لقد قمت بكتابة رمز غير صحيح للتحقق من صحة الرمز
      يمكنك أيضًا التعرف على البرامج التي تقدمها المؤسسات من خلال العودة إلى قائمة التسجيل والبحث حسب المؤسسة أو التخصص"""

            # return [AllSlotsReset(), Restarted(), FollowupAction('competativerates_form')]
            # return [AllSlotsReset(), Restarted()]
            return [
                SlotSet(key="comp_code", value=None),
                FollowupAction('competativerates_form')
            ]
     
        else:
            new_response= response.json()['link']
        buttons = []
        buttons.append({"title": "القائمة الرئيسية", "payload": '/main_menu'})
        buttons.append({"title": "خروج", "payload": '/restart'}) 
        dispatcher.utter_message(text=new_response,buttons=buttons)
        return []
