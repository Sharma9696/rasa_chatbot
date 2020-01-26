# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 15:49:49 2019
@author: kamalpreet.singh
"""
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk import Action
from rasa_sdk import ActionExecutionRejection
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.events import UserUttered, FollowupAction, BotUttered
from rasa_sdk.events import AllSlotsReset, Restarted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
import parsedatetime
import requests
import datetime
import base64
import collections
import json
import re
import csv
from word2number import w2n
import logging
import random
import string
from calendar import monthrange


logger = logging.getLogger(__name__)
# requests = requests.sessions.Session()
# # requests.verify = "Cyberoam_SSL_CA.pem"
NEWS_API_KEY = 'b3cf4fdc268945a990fd6dcb7878899f'


"""reset slots at the end of a conversation, so that bot can take fresh/new values for next action"""
class ResetSlot(Action):
    def name(self):
        return "reset_slot"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_attachment({"data_type": "faq_disable", "data": 'enable button'})
        return [SlotSet('FromDate', None), SlotSet('LeaveReason', None), SlotSet('LeaveType', None), SlotSet('noofDays', None),
                SlotSet('ToDate', None), SlotSet('Other_ar', None),SlotSet('od_reason_list', None),SlotSet('ar_reason_list', None),
                SlotSet('FromTime', None), SlotSet('ToTime', None), SlotSet('Reason_ar', None), SlotSet('Remark', None),
                SlotSet('requested_slot', None), SlotSet('cancel_leave_remark', None), SlotSet('cancel_leave_text', None),
                SlotSet('ODStart', None), SlotSet('ODEnd', None), SlotSet('cancel_leave_confirm', None),SlotSet('cancel_leave_data', None),
                SlotSet('ODNatureWork', None), SlotSet('Reason_od', None),SlotSet('view_leave_text', None),
                SlotSet('leave_transactions', None), SlotSet('view_ar_text', None),SlotSet('Past_transactions', None),
                SlotSet('view_od_text', None), SlotSet('OD_transactions', None),SlotSet('leave_type_list', None),
                SlotSet('cancel_ar_remark', None), SlotSet('cancel_ar_text', None), SlotSet('cancel_od_remark', None),
                SlotSet('cancel_od_text', None), SlotSet('cancel_ar_confirm', None),SlotSet('cancel_ar_data', None),
                SlotSet('cancel_od_confirm', None),SlotSet('cancel_od_data', None), SlotSet('team_detail_slot', None),
                SlotSet('view_team_text', None), SlotSet('FromYear', None), SlotSet('FromMonth',None),SlotSet('location', None),
                SlotSet('topic_news', None), SlotSet('headline_country', None), SlotSet('todo_data', None), SlotSet('detailed_todo_text', None),
                SlotSet('todo_list_text', None), SlotSet('todo_all_data', None), SlotSet('emp_todo_data', None), SlotSet('remark_todo', None),
                SlotSet('manager_decision', None), SlotSet('serial_no_todo', None), SlotSet('affirm_deny_todo', None),
                SlotSet('move_forward_todo', None), SlotSet('faq_subject', None), SlotSet('faq_body', None), SlotSet('holiday_type', None),
                SlotSet('attendance_status', None), SlotSet('AttendanceDate', None), SlotSet("HoursLeave", None)]


""" for generating random prefix and suffix """
class RandomDigits:
    def random_characters(self, stringlength = 3):
        random_char = string.ascii_letters + string.digits
        return ''.join(random.choice(random_char) for i in range(stringlength))


""" for getting apikey from company code"""
class DynamicApi(Tracker):
    def __init__(self,function):
        self.function = function
    
    def get_api(self,tracker):
        function = self.function
        _, comp_code = (tracker.current_state())['sender_id'].split('_')
        base_url = "https://"+comp_code+".honohr.com/sapi/Service/dynamicAPIKeys_v2?"
        api_url = base_url+'comp_code='+comp_code+'&api_key=b9317ab4b73bf5bf9a9ccf5a1344bb18'
        encryptedKey = base64.b64encode(api_url.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        api_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        api_trans_url = base_url + 'encryption_key=' + api_key + '&type=ios'
        r = requests.get(api_trans_url)
        data = r.json()['api_keys']
        api_key = data[function]
        return api_key

"""for getting number of applicable days and number of hours for short leave LeaveApplicableDays_v2"""
class LeaveApplicableDays_v2(Tracker):

    def __init__(self,leave_type_id,from_date,to_date,period1='2FD',period2='2FD'):
        self.leave_type_id = leave_type_id
        self.from_date = from_date
        self.to_date = to_date
        self.period1 = period1
        self.period2 = period2

    def get_data(self,tracker):
        leave_type_id = self.leave_type_id
        from_date = self.from_date
        to_date = self.to_date
        period1 = self.period1  
        period2 = self.period2
        comp_code = tracker.get_slot("comp_code")
        emp_code = tracker.get_slot("emp_code")
        apiKey = DynamicApi('LEAVE').get_api(tracker)
        access_token = tracker.get_slot("access_token")
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        bal_check_url = 'https://'+comp_code+'.honohr.com/sapi/LeaveMaster/LeaveApplicableDays_v2?'
        nURL = bal_check_url +'comp_code='+comp_code+'&emp_code='+emp_code+'&api_key='+apiKey+'&leave_type_id='+str(leave_type_id)+'&from_date='+from_date+'&to_date='+to_date+'&period1='+period1+'&period2='+period2+'&token='+access_token
        encryptedKey = base64.b64encode(nURL.encode('utf-8'))
        bal_val_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        bal_val_url = bal_check_url + 'encryption_key=' + bal_val_key + '&type=ios'
        req = requests.get(bal_val_url)
        data = req.json()
        return data, req

""" for gettin leave balance data getLeaveBalances_v2 """
class getLeaveBalances_v2(Tracker):

    def __init__(self,apiKey):
        self.apiKey = apiKey

    def get_data(self,tracker):
        apiKey = self.apiKey
        comp_code = tracker.get_slot("comp_code")
        emp_code = tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")
        get_url= 'https://'+comp_code+'.honohr.com/sapi/LeaveMaster/getLeaveBalances_v2?'
        bal_key = get_url + 'comp_code='+comp_code+'&emp_code='+emp_code+'&api_key='+apiKey+'&token='+access_token
        encryptedKey = base64.b64encode(bal_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        balance_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        balance_url= get_url +'encryption_key=' + balance_key + '&type=ios'
        req = requests.get(balance_url)
        data = req.json()
        return data, req

""" for getting leave rules accoring to leave type getLeaveRules_v2"""
class getLeaveRules_v2(Tracker):

    def __init__(self,apiKey,leave_type_id):
        self.apiKey = apiKey
        self.leave_type_id = leave_type_id
    
    def get_data(self,tracker):
        apiKey = self.apiKey
        leave_type_id = self.leave_type_id
        comp_code = tracker.get_slot("comp_code")
        access_token = tracker.get_slot("access_token")
        emp_code = tracker.get_slot("emp_code")
        base_url = "https://"+comp_code+".honohr.com/sapi/LeaveMaster/getLeaveRules_v2?"
        url_key = base_url+"comp_code="+comp_code+"&api_key="+apiKey+"&leave_type_id="+leave_type_id+"&emp_code="+emp_code+"&token="+access_token
        encryptedKey = base64.b64encode(url_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        rule_key = prefix + str(encryptedKey.decode('utf-8'))  + suffix
        rule_url = base_url + 'encryption_key=' + rule_key + '&type=ios'
        req = requests.get(rule_url)
        data = req.json()
        return data, req

""" for getting employee name, employee id, company code"""
class ActionGetUsersDetails(Action):

    def name(self):
        return "user_details"
    
    def run(self, dispatcher, tracker, domain):
        name = (tracker.current_state())['sender_id']
        # name = '4937acc63a69ae4ac976c9098bf819_mial'
        # name = '5c3372422896d2151bc79cc7e1db91_testproduction'
        # name = '42436e2f94e9e9fe4a4ea7d7f3a5bf_sequelone'
        access_token, comp_code = name.split('_')
        print(name)
        apiKey = DynamicApi('EMPLOYEE').get_api(tracker)
        get_url= 'https://'+comp_code+'.honohr.com/api/EmpInformation/showPersonalData?'
        cal_key = get_url + 'comp_code='+comp_code+'&api_key='+apiKey+'&auth_token='+access_token
        r = requests.get(cal_key)
        
        if r.status_code == 200:
            try:
                data = r.json()["personal_data"]
                emp_code = data["Emp_Code"]
                print(data["Emp_Name"])
                try:
                    emp_name = data["Emp_Name"].split(" ")[0]
                except:
                    emp_name = data["Emp_Name"]

                base_url = 'https://'+comp_code+'.honohr.com/sapi/OrganisationChart/OrgChart_v2?'
                chart_url = base_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&token='+access_token
                encryptedKey = base64.b64encode(chart_url.encode('utf-8'))
                prefix = RandomDigits.random_characters(3)
                suffix = RandomDigits.random_characters(3)
                chart_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                api_trans_url = base_url + 'encryption_key=' + chart_key + '&type=ios'
                r = requests.get(api_trans_url)
                if r.status_code == 200:
                    try:
                        data = r.json()['data']
                        profile_image = data['child']['EmpImage']
                    except:
                        profile_image = './static/img/userAvatar.png'
                    dispatcher.utter_attachment({"data_type": "profile_pic", "data": profile_image})
                else:
                    dispatcher.utter_message("Something went wrong, please try again after sometime.")
                return [SlotSet("access_token", access_token),
                        SlotSet("comp_code", comp_code),
                        SlotSet("emp_code", emp_code),
                        SlotSet("emp_name", emp_name),
                        SlotSet("user_data", data)]

            except:
                dispatcher.utter_message("Something went wrong, please try again after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try again after sometime.")

""" for restarting the server"""
class ActionRestarted(Action):

    def name(self):
        return "action_chat_restart"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_attachment({"data_type": "restarted_chatbot", "data": 'current stage of bot is restarted.'})
        return [Restarted()]


""" form to get details from user to apply for ar/attendance regularization"""
class ActionApplyAR(FormAction):
    def name(self):
        return 'ar_form'

    
    @staticmethod
    def required_slots(tracker: Tracker):

        comp_code = tracker.get_slot("comp_code")
        if comp_code in ["dbcorp","check"]:
            return []
        else:
            if tracker.get_slot('Reason_ar') in ['4','other','Other']:
                return ['FromDate','FromTime','ToTime','Reason_ar', 'Other_ar']
            else:
                return ['FromDate','FromTime','ToTime','Reason_ar']


    def slot_mappings(self):
        return {
            'FromDate':[
                self.from_entity(entity='FromDate'),
                self.from_text(not_intent=['deny', 'stop','reset_bot','reset_bot'])],

            'FromTime': [
                self.from_entity(entity='FromTime', intent=['apply_ar', 'inform']),
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            'ToTime': [
                self.from_entity(entity='ToTime', intent=['apply_ar','inform']),
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            'Reason_ar': [
                self.from_text(not_intent=['reset_bot'])],
            'Other_ar': [
                self.from_text()]}

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'Reason_ar':
                        logger.debug("Request next slot '{}'".format(slot))
                        if tracker.get_slot('ar_reason_list') != None:
                            ls= []
                            new_data = []
                            data=tracker.get_slot('ar_reason_list')
                            for i in data:
                                if i['reason_value'] not in ls:
                                    ls.append(i['reason_value'])
                                    new_data.append(i)
                            sorted_data = sorted(new_data, key = lambda i: i['reason_id'])
                            buttons = []
                            for t in sorted_data:
                                payload = "/ar_form{\"Reason_ar\": \"" + t['reason_value'] + "\"}"
                                buttons.append({"title": "{0}. {1}".format(sorted_data.index(t)+1,t['reason_value']), "payload": payload})
                            text = "Kindly select one of the following reasons for applying AR:"
                            dispatcher.utter_button_message(text, buttons)
                            return [SlotSet(REQUESTED_SLOT, slot)] 

                        else:
                            comp_code = tracker.get_slot("comp_code")
                            emp_code =  tracker.get_slot("emp_code")
                            access_token = tracker.get_slot("access_token")
                            apiKey = DynamicApi('ATTENDANCE').get_api(tracker)
                            show_base_url='https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/showAttendanceApprover_v2?'
                            aa_key=show_base_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&token='+access_token
                            encryptedKey = base64.b64encode(aa_key.encode('utf-8'))
                            prefix = RandomDigits.random_characters(3)
                            suffix = RandomDigits.random_characters(3)
                            trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                            aa_url = show_base_url + 'encryption_key=' + trans_key + '&type=ios'
                            req = requests.get(aa_url)
                            ls= []
                            new_data = []
                            data=req.json()['past_attendance_reason']
                            for i in data:
                                if i['reason_value'] not in ls:
                                    ls.append(i['reason_value'])
                                    new_data.append(i)
                            sorted_data = sorted(new_data, key = lambda i: i['reason_id'])
                            buttons = []
                            for t in sorted_data:
                                payload = "/ar_form{\"Reason_ar\": \"" + t['reason_value'] + "\"}"
                                buttons.append({"title": "{0}. {1}".format(sorted_data.index(t)+1,t['reason_value']), "payload": payload})
                            text = "Kindly select one of the following reasons for applying AR:"
                            dispatcher.utter_button_message(text, buttons)
                            return [SlotSet(REQUESTED_SLOT, slot),SlotSet("ar_reason_list", data)] 
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

            logger.debug("No slots left to request")
            return None

    def validate_FromDate(self,value, dispatcher, tracker, domain):

        pdt = parsedatetime.Calendar()
        from_dt, stamp = pdt.parseDT(value)
        current_date = datetime.date.today()
        frm_dt=from_dt.date()
        ls = [int(i) for i in re.findall(r'-?\d+', value)]
        if stamp == 0:
            dispatcher.utter_message("That's an invalid date, try using formats like 26 sep or sep 26 etc.")
        elif len(ls)>0 and (ls[0]>31 or ls[0]<=0):
            dispatcher.utter_message("Date out of range, kindly provide a valid date.")
        else:
            num_days = (frm_dt-current_date).days
            if num_days < 100 or 273 < num_days <= 365:
                if num_days < 100:
                    dispatcher.utter_message("AR can't be appplied for future dates.")
                elif 273 < num_days <= 365:
                    Fromdate = frm_dt-datetime.timedelta(days=366)
                    Fromdate = Fromdate.strftime("%d-%m-%Y")
                    return {"FromDate": Fromdate}
            else:
                dispatcher.utter_message("Sorry, you can't apply AR for this date.")
            

    def validate_FromTime(self, value, dispatcher, tracker, domain):
        now = datetime.datetime.now()
        pdt=parsedatetime.Calendar()
        frm_time,_=pdt.parseDT(value)
        frmtime=frm_time.time()
        if frmtime.strftime("%H:%M") == now.strftime("%H:%M"):
            dispatcher.utter_message("That's an invalid time value, try using formats like 10:30 am or 18:23 etc.")
        else:
            return {"FromTime":str(frmtime)}
    

    def validate_ToTime(self, value, dispatcher, tracker, domain):
        now = datetime.datetime.now()
        pdt=parsedatetime.Calendar()
        to_time,_=pdt.parseDT(value)
        totime=to_time.time()
        if totime.strftime("%H:%M") == now.strftime("%H:%M"):
            dispatcher.utter_message("That's an invalid time value, try using formats like 10:30 am or 18:23 etc.")
        else:
            return {"ToTime":str(totime)}

    def validate_Reason_ar(self, value, dispatcher, tracker, domain):
        ls= []
        new_data = []
        data=tracker.get_slot("ar_reason_list")
        for i in data:
            if i['reason_value'] not in ls:
                ls.append(i['reason_value'])
                new_data.append(i)
        sorted_data = sorted(new_data, key = lambda i: i['reason_id'])
        if value != "":
            wrong_value = False
            for t in sorted_data:
                if value.lower() in [t['reason_value'].lower(),str(sorted_data.index(t)+1),"{0}. {1}".format(sorted_data.index(t)+1,t['reason_value'].lower())]:
                    wrong_value = True
                    return {"Reason_ar":t['reason_value'].lower()}

            if wrong_value == False:
                dispatcher.utter_message("That's an invalid AR reason.")
        else:
            dispatcher.utter_message("AR reason can't be empty.")

    def submit(self, dispatcher, tracker, domain):
        return[]

class ActionUtterARDetails(Action):

    def name(self):
        return "apply_ar_values"

    def run(self, dispatcher, tracker, domain):
        comp_code = tracker.get_slot("comp_code")
        if comp_code in ["dbcorp","check"]:
            dispatcher.utter_message("Functionality coming soon.")
            intent = {
                "confidence":1,
                "name":"affirm",
                "entities":[]
            }
            return [UserUttered("yes", intent)]
        else:
            ls = []
            for_date = tracker.get_slot("FromDate")
            ls.append({'key': 'Starting Date', 'value': for_date})
            ar_reason = tracker.get_slot("Reason_ar")
            FromTime = tracker.get_slot("FromTime")
            ls.append({'key': 'From Time', 'value': FromTime})
            ToTime = tracker.get_slot("ToTime")
            ls.append({'key': 'To Time', 'value': ToTime})
            if tracker.get_slot('Other_ar'):
                remarks = tracker.get_slot('Other_ar')
            else:
                remarks = ar_reason
            ls.append({'key': 'Leave Reason', 'value': remarks})

            data_leave = {"data_type": "key_value", "data" : ls}
            dispatcher.utter_template('utter_check_details', tracker)
            dispatcher.utter_attachment(data_leave)
            dispatcher.utter_message("Do you want me to apply attendance regularization with above mentioned details? (Yes/No)")
            return []


"""function to apply ar after getting details from user"""
class ActionApplyARrequest(Action):

    def name(self):
        return 'apply_ar_request'

    def run(self, dispatcher, tracker, domain):
        comp_code = tracker.get_slot("comp_code")
        if comp_code in ["dbcorp","check"]:
            return []
        else:
            emp_code =  tracker.get_slot("emp_code")
            access_token = tracker.get_slot("access_token")
            apiKey = DynamicApi('ATTENDANCE').get_api(tracker)
            submit_base_url= 'https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/submitPastAttendance_v2?'
            for_date = tracker.get_slot("FromDate")
            in_date = tracker.get_slot("FromDate")
            out_date = tracker.get_slot("FromDate")
            ar_reason = tracker.get_slot("Reason_ar").lower()
            FromTime = tracker.get_slot("FromTime")
            ToTime = tracker.get_slot("ToTime")
            if tracker.get_slot('Other_ar'):
                remarks = tracker.get_slot('Other_ar')
            else:
                remarks = ar_reason
            inhour = FromTime[:2]
            inMinute = FromTime[3:5]
            outhour = ToTime[:2]
            outMinute = ToTime[3:5]
            inap = 'AM' if int(inhour) < 12 else 'PM'
            outap = 'PM' if inap == 'AM' else 'AM'
            IH = int(inhour)-12 if int(inhour) > 12 else inhour
            OH = int(outhour)-12 if int(outhour) > 12 else outhour
            inHour = str(IH) if len(str(IH)) == 2 else '0'+str(IH) 
            outHour = str(OH) if len(str(OH)) == 2 else '0'+str(OH)

            new_data = []
            ls = []

            dataget=tracker.get_slot("ar_reason_list")
            for i in dataget:
                if i['reason_value'] not in ls:
                    ls.append(i['reason_value'])
                    new_data.append(i)
            for i in new_data:
                if ar_reason in i['reason_value'].lower():
                    notMarkingReas = i['reason_id']
                else:
                    pass


            ar_key = submit_base_url + 'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&for_date='+for_date+'&in_date='+in_date+'&out_date='+out_date+'&inHour='+inHour+'&inMinute='+inMinute+'&inap='+inap+'&outHour='+outHour+'&outMinute='+outMinute+'&outap='+outap+'&notMarkingReas='+notMarkingReas+'&remarks='+remarks+'&token='+access_token
            encryptedKey = base64.b64encode(ar_key.encode('utf-8'))
            prefix = RandomDigits.random_characters(3)
            suffix = RandomDigits.random_characters(3)
            data = {'encryption_key': prefix + str(encryptedKey.decode('utf-8')) + suffix, 'type' : 'ios'}
            r = requests.post(url=submit_base_url, data=data)

            if r.status_code == 200:
                try:
                    response = r.json()
                    if response['result'] in ['true', True]:
                        dispatcher.utter_message(response['past_attendance_submit'])
                    elif response['result'] in ['false', False]:
                        dispatcher.utter_message(response['error'])
                        return []
                    else:
                        dispatcher.utter_message('Something went wrong, kindly check your AR status before applying again.')
                        return []
                except:
                    dispatcher.utter_message('Something went wrong, kindly check your AR status before applying again.')
            elif r.status_code == 400:
                dispatcher.utter_message('Something went wrong, please try again after sometime.')
            else:
                dispatcher.utter_message('Something went wrong, kindly check your AR status before applying again.')


"""form for getting details to apply leave"""
class leave_action(FormAction):

    def name(self):
    
        return "leave_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        comp_code = tracker.get_slot("comp_code")

        if comp_code in ["dbcorp","check"]:
            return []
        else:
            if tracker.get_slot("LeaveType"):
                if tracker.get_slot("LeaveType").strip().lower() == 'short leave':
                    return ['LeaveType','FromDate','LeaveReason']
                elif tracker.get_slot('noofDays'):
                    return ['LeaveType','FromDate','noofDays','LeaveReason']
                elif tracker.get_slot('ToDate'):
                    return ['LeaveType','FromDate','ToDate','LeaveReason']
                else:
                    return ['LeaveType','FromDate','ToDate','noofDays','LeaveReason']
            elif tracker.get_slot('noofDays'):
                return ['LeaveType','FromDate','noofDays','LeaveReason']
            elif tracker.get_slot('ToDate'):
                return ['LeaveType','FromDate','ToDate','LeaveReason']
            else:
                return ['LeaveType','FromDate','ToDate','noofDays','LeaveReason']
            # elif tracker.get_slot('noofDays'):
            #     return ['LeaveType','FromDate','noofDays','LeaveReason']
            # elif tracker.get_slot('ToDate'):
            #     return ['LeaveType','FromDate','ToDate','LeaveReason']
            # else:
            #     return ['LeaveType','FromDate','ToDate','noofDays','LeaveReason']


    def slot_mappings(self):
        
        return {
                'LeaveType': [
                    self.from_entity(entity='LeaveType', intent='apply_leave'),
                    self.from_text(not_intent=['deny', 'stop','reset_bot'])],

                'FromDate': [
                    self.from_entity(entity='FromDate', intent='apply_leave'),
                    self.from_text(not_intent=['deny','stop','reset_bot'])],

                'ToDate': [
                    self.from_entity(entity='ToDate', intent='apply_leave'),
                    self.from_text(not_intent=['deny', 'stop','reset_bot'])],

                'noofDays': [
                    self.from_entity(entity='noofDays', intent='apply_leave'),
                    self.from_text(not_intent=['deny', 'stop','reset_bot'])],

                'LeaveReason': [
                    self.from_text()
                    ]
                }


    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):                
                    if slot == 'LeaveType':
                        logger.debug("Request next slot '{}'".format(slot))
                        if tracker.get_slot('leave_type_list') != None:
                            ls =[]
                            new_data = []                       
                            data=tracker.get_slot('leave_type_list')
                            #working on dynamic leave type buttons
                            for i in data:
                                if i['lv_Type'] not in ls:
                                    ls.append(i['lv_Type'])
                                    new_data.append(i)
                            sorted_data = sorted(new_data, key = lambda i: i['lv_Type_id'])
                            buttons = []
                            for t in sorted_data:
                                payload = "/leave_form{\"LeaveType\": \"" + t['lv_Type'] + "\"}"
                                buttons.append({"title": "{0}. {1} ({2})".format(sorted_data.index(t)+1,t['lv_Type'],t['lv_Value']), "payload": payload})
                            text = "Kindly select the type of leave you want to apply:"
                            dispatcher.utter_button_message(text, buttons)
                            return [SlotSet(REQUESTED_SLOT, slot)]  

                        else:
                            apiKey = DynamicApi('LEAVE').get_api(tracker)
                            data, req = getLeaveBalances_v2(apiKey).get_data(tracker)
                            data = data['leave_balance']
                            ls =[]
                            new_data = []                       
                            #working on dynamic leave type buttons
                            for i in data:
                                if i['lv_Type'] not in ls:
                                    ls.append(i['lv_Type'])
                                    new_data.append(i)
                            sorted_data = sorted(new_data, key = lambda i: i['lv_Type_id'])
                            buttons = []
                            for t in sorted_data:
                                payload = "/leave_form{\"LeaveType\": \"" + t['lv_Type'] + "\"}"
                                buttons.append({"title": "{0}. {1} ({2})".format(sorted_data.index(t)+1,t['lv_Type'],t['lv_Value']), "payload": payload})
                            text = "Kindly select the type of leave you want to apply:"
                            dispatcher.utter_button_message(text, buttons)
                            return [SlotSet(REQUESTED_SLOT, slot),SlotSet('leave_type_list',data)]                        
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]
            return None

    def validate_LeaveType(self, value, dispatcher, tracker, domain):

        apiKey = DynamicApi('LEAVE').get_api(tracker)
        data, req = getLeaveBalances_v2(apiKey).get_data(tracker)
        data = data['leave_balance']
        ls =[]
        new_data = []                       

        for i in data:
            if i['lv_Type'] not in ls:
                ls.append(i['lv_Type'])
                new_data.append(i)
        sorted_data = sorted(new_data, key = lambda i: i['lv_Type_id'])
        if value != "":
            leave_count = value.split(' ')[-1][1:-1]
            if leave_count == '0':
                dispatcher.utter_message("Leave balance for selected leave type is zero.")
            else:
                wrong_value = False
                for t in sorted_data:
                    if value.lower() in [t['lv_Type'].strip().lower(),str(sorted_data.index(t)+1),"{0}. {1} ({2})".format(sorted_data.index(t)+1,t['lv_Type'].strip().lower(),t['lv_Value'])]:
                        wrong_value = True
                        if t['lv_Type'].strip().lower() == "short leave":
                            for LeaveValue in sorted_data:
                                if LeaveValue['lv_Type'].strip().lower() == "short leave":
                                    leave_master_key = LeaveValue['ms_id']
                            data, req = getLeaveRules_v2(apiKey,str(leave_master_key)).get_data(tracker)
                            leave_hours = data['data']['LeaveRules']['LeaveHours']
                            max_number_days = data['data']['LeaveRules']['MaxAllowed']
                            dispatcher.utter_message("<b>Note:</b> Short Leave can only be applied for maximum of {0} hours, {1} times in a month.".format(leave_hours,max_number_days))
                        else:
                            pass
                        return {"LeaveType":t['lv_Type'].strip().lower()}

                if wrong_value == False:
                    dispatcher.utter_message("That's an invalid leave type value.")
        else:
            dispatcher.utter_message("Leave reason can't be empty.")
    
    def validate_FromDate(self,value, dispatcher, tracker, domain):
        pdt = parsedatetime.Calendar()
        from_dt, stamp = pdt.parseDT(value)
        current_date = datetime.date.today()
        frm_dt=from_dt.date()
        ls = [int(i) for i in re.findall(r'-?\d+', value)]
        if stamp == 0:
            dispatcher.utter_message("That's an invalid date, try using formats like 26 sep or sep 26 etc.")
        elif len(ls)>0 and (ls[0]>31 or ls[0]<=0):
            dispatcher.utter_message("Date out of range, kindly provide a valid date.")
        else:
            num_days = int((frm_dt-current_date).days)
            if num_days < 100 or 273 < num_days <= 365:
                if num_days < 100:
                    frm_dt = frm_dt.strftime("%Y-%m-%d")
                    return {"FromDate": frm_dt}
                elif 273 < num_days <= 365:
                    Fromdate = frm_dt-datetime.timedelta(days=366)
                    frm_dt = Fromdate.strftime("%Y-%m-%d")
                    return {"FromDate": frm_dt}
            else:
                dispatcher.utter_message("Sorry, you can't apply leave for this date.")

            
    def validate_ToDate(self, value, dispatcher, tracker, domain):

        pdt=parsedatetime.Calendar()
        to_dt,stamp=pdt.parseDT(value)
        todt=to_dt.date()
        current_date = datetime.date.today()

        if tracker.get_slot("FromDate") == None:
            try:
                abc = tracker.latest_message['entities']
                for i in abc:
                    if i['entity'] == "FromDate":
                        from_dt =  i['value']
                frm_dt,_=pdt.parseDT(from_dt)
                frm_dt = frm_dt.date()
                frm_dt = frm_dt.replace(year = current_date.year)
            except:
                pass
        else:
            from_dt = tracker.get_slot("FromDate")
            frm_dt,_=pdt.parseDT(from_dt)
            frm_dt = frm_dt.date()

        # leave_type = tracker.get_slot("LeaveType")
        # print("####################################", leave_type)
        # if leave_type.strip().lower() == "short leave":
        #     ls = [int(i) for i in re.findall(r'-?\d+', value)]
        #     if stamp == 0:
        #         dispatcher.utter_message("That's an invalid date, try using formats like 26 sep or sep 26 etc.")
        #     elif len(ls)>0 and (ls[0]>31 or ls[0]<=0):
        #         dispatcher.utter_message("Date out of range, kindly provide a valid date.")
        #     else:
        #         num_days = int((todt-current_date).days)
        #         print("number of daysssssssssssssssssssssssss",num_days)
        #         if num_days < 100 or 273 < num_days <= 365:
        #             if num_days < 100:
        #                 if int((todt-frm_dt).days) >= 0:
        #                     from_date = frm_dt.strftime("%d-%m-%Y")
        #                     print("first from dateeeeeeeeee", from_date)
        #                     to_date = todt.strftime("%d-%m-%Y")
        #                     print("firrst to dateeeeeeeeeee", to_date)
        #                     leave_type = tracker.get_slot("LeaveType")
        #                     apiKey = DynamicApi('LEAVE').get_api(tracker)
        #                     data, req = getLeaveBalances_v2(apiKey).get_data(tracker)
        #                     data = data["leave_balance"]
        #                     for i in data:
        #                         if leave_type.strip().lower() == i['lv_Type'].strip().lower():
        #                             leave_type_id = i['ms_id']
        #                             print("first $$$$$$$$$$$$$$$$$$$$$$$$$$$$",leave_type_id)
        #                     data, req = getLeaveRules_v2(apiKey,str(leave_type_id)).get_data(tracker)
        #                     number_days = data['data']['LeaveRules']['MaxAllowed']
        #                     print("first leave rulesssssssssssssssssss", number_days)
        #                     data, req = LeaveApplicableDays_v2(leave_type_id,from_date,to_date).get_data(tracker)
        #                     org_days = data['data']['LvDays']
        #                     print("first applicable dayssssssssssssssssssss",org_days)
        #                     if int(org_days) <= int(number_days):
        #                         todt = todt.strftime("%Y-%m-%d")
        #                         return {"ToDate": todt}
        #                     else:
        #                         dispatcher.utter_message("Short leave can only be applied for max of {0} days.".format(number_days))
        #                 else:
        #                     dispatcher.utter_message('To Date cannot be prior From Date.')
        #             elif 273 < num_days <= 365:
        #                 Todt = todt-datetime.timedelta(days=366)
        #                 if int((Todt-frm_dt).days) >=0:
        #                     from_date = frm_dt.strftime("%d-%m-%Y")
        #                     print("second from dateeeeeeeeeee",from_date)
        #                     to_date = Todt.strftime("%d-%m-%Y")
        #                     print("second to dateeeeeeeeeeeee", to_date)
        #                     leave_type = tracker.get_slot("LeaveType")
        #                     apiKey = DynamicApi('LEAVE').get_api(tracker)
        #                     data, req = getLeaveBalances_v2(apiKey).get_data(tracker)
        #                     data = data["leave_balance"]
        #                     for i in data:
        #                         if leave_type.strip().lower() == i['lv_Type'].strip().lower():
        #                             leave_type_id = i['lv_Type_id']
        #                             leave_master_id = i['ms_id']
        #                             print("second $$$$$$$$$$$$$$$$$$$$$$$$$$$$",leave_type_id)
        #                     data, req = getLeaveRules_v2(apiKey,str(leave_master_id)).get_data(tracker)
        #                     number_days = data['data']['LeaveRules']['MaxAllowed']
        #                     print("second leave rulesssssssssssssssssss", number_days)
        #                     data, req = LeaveApplicableDays_v2(leave_type_id,from_date,to_date).get_data(tracker)
        #                     org_days = data['data']['LvDays']
        #                     print("second applicable dayssssssssssssssssssss",org_days)
        #                     if int(org_days) <= int(number_days):
        #                         todt = Todt.strftime("%Y-%m-%d")
        #                         return {"ToDate": todt}
        #                     else:
        #                         dispatcher.utter_message("Short leave can only be applied for max of {0} days.".format(number_days))
        #                 else:
        #                     dispatcher.utter_message('To Date cannot be prior From Date.')
        #             else:
        #                 pass
        #             # return {"ToDate": todt}
        #         else:
        #             dispatcher.utter_message("Sorry, you can't apply leave for this date.")
        

        ls = [int(i) for i in re.findall(r'-?\d+', value)]
        if stamp == 0:
            dispatcher.utter_message("That's an invalid date, try using formats like 26 sep or sep 26 etc.")
        elif len(ls)>0 and (ls[0]>31 or ls[0]<=0):
            dispatcher.utter_message("Date out of range, kindly provide a valid date.")
        else:
            num_days = int((todt-current_date).days)
            if num_days < 100 or 273 < num_days <= 365:
                if num_days < 100:
                    if int((todt-frm_dt).days) >= 0:
                        todt = todt.strftime("%Y-%m-%d")
                        # return {"ToDate": todt}
                    else:
                        dispatcher.utter_message('To Date cannot be prior From Date.')
                elif 273 < num_days <= 365:
                    Todt = todt-datetime.timedelta(days=366)
                    if int((Todt-frm_dt).days) >=0:
                        todt = Todt.strftime("%Y-%m-%d")
                        # return {"ToDate": todt}
                    else:
                        dispatcher.utter_message('To Date cannot be prior From Date.')
                else:
                    pass
                return {"ToDate": todt}
            else:
                dispatcher.utter_message("Sorry, you can't apply leave for this date.")

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:

        """Define what the form has to do
            after all required slots are filled"""
        # utter submit template
        # dispatcher.utter_template("utter_check_details", tracker)

        return []

"""function to get number of days/to date for apply leave"""
class ActionValidateDayNumber(Action):
    def name(self):
        return "day_date_parser"


    def run(self, dispatcher, tracker, domain):
        
        comp_code = tracker.get_slot("comp_code")
        leave_type = tracker.get_slot('LeaveType')
        if comp_code in ["dbcorp","check"]:
            dispatcher.utter_message("Functionality coming soon.")
        else:
            if leave_type.strip().lower() == 'short leave':
                from_date = tracker.get_slot('FromDate')
                to_date = from_date
                org_days = '1'
                apiKey = DynamicApi('LEAVE').get_api(tracker)
                data, req = getLeaveBalances_v2(apiKey).get_data(tracker)
                data = data['leave_balance']
                for i in data:
                    if i['lv_Type'].strip().lower() == 'short leave':
                        leave_master_key = i['ms_id']
                data, req = getLeaveRules_v2(apiKey,str(leave_master_key)).get_data(tracker)
                leave_hours = data['data']['LeaveRules']['LeaveHours']
                return [SlotSet("noofDays", org_days), SlotSet("ToDate", to_date), SlotSet("HoursLeave", leave_hours)]
            else:
                pdt = parsedatetime.Calendar()
                leave_type = tracker.get_slot('LeaveType') 
                apiKey = DynamicApi('LEAVE').get_api(tracker)
                data, req = getLeaveBalances_v2(apiKey).get_data(tracker)                  
                data = data['leave_balance']
                if tracker.get_slot('ToDate') != None:
                    
                    to_date=tracker.get_slot('ToDate')
                    to_dat,_ = pdt.parseDT(to_date)
                    to_dt=to_dat.date()

                    from_date=tracker.get_slot('FromDate')
                    frm_dt,_=pdt.parseDT(from_date)
                    frm_dt=frm_dt.date()

                    from_date=frm_dt.strftime("%Y-%m-%d")
                    to_date=to_dt.strftime("%Y-%m-%d")

                    for i in data:
                        if i['lv_Type'].strip().lower()==leave_type:
                            leave_type_id=i['lv_Type_id']

                    data, req = LeaveApplicableDays_v2(leave_type_id,from_date,to_date).get_data(tracker)
                    org_days = data['data']['LvDays']

                    return [SlotSet("noofDays", org_days), SlotSet("ToDate", to_date)]

                elif tracker.get_slot('noofDays') != None:
                    no_of_days=tracker.get_slot('noofDays')
                    from_date=tracker.get_slot('FromDate')
                    frm_dt,_=pdt.parseDT(from_date)
                    frm_dt = frm_dt.date()
                    to_dt=frm_dt+datetime.timedelta(days=(int(no_of_days)-1))
                    from_date=frm_dt.strftime("%Y-%m-%d")
                    to_date=to_dt.strftime("%Y-%m-%d")

                    for i in data:
                        if i['lv_Type'].strip().lower()==leave_type:
                            leave_type_id=i['lv_Type_id']
                    data, req = LeaveApplicableDays_v2(leave_type_id,from_date,to_date).get_data(tracker)
                    org_days = data['data']['LvDays']
                    no_day = int(no_of_days)

                    while org_days<int(no_of_days):
                        to_dt = frm_dt+datetime.timedelta(days=no_day)
                        to_date=to_dt.strftime("%Y-%m-%d")
                        
                        for i in data:
                            if i['lv_Type'].strip().lower()==leave_type:
                                leave_type_id=i['lv_Type_id']

                        data, req = LeaveApplicableDays_v2(leave_type_id,from_date,to_date).get_data(tracker)
                        org_days = data['data']['LvDays']
                        no_day += 1
                    else:
                        return [SlotSet('noofDays',org_days), SlotSet('ToDate',to_date)]

class ActionUtterLeaveDetails(Action):

    def name(self):
        return "apply_leave_values"

    def run(self, dispatcher, tracker, domain):

        comp_code = tracker.get_slot("comp_code")
        if comp_code in ["dbcorp","check"]:
            intent = {
                "confidence":1,
                "name":"affirm",
                "entities":[]
            }
            return [UserUttered("yes", intent)]
        else:
            ls = []
            leave_type = tracker.get_slot('LeaveType')
            ls.append({'key':'Leave Type', 'value':leave_type})
            date_from = tracker.get_slot('FromDate')
            ls.append({'key':'From Date', 'value':date_from})
            if leave
            date_to = tracker.get_slot('ToDate')
            ls.append({'key':'To Date', 'value':date_to})   
            no_of_day = tracker.get_slot('noofDays')
            ls.append({'key':'No of Days', 'value':no_of_day})
            applying_reason = tracker.get_slot('LeaveReason')
            ls.append({'key':'Leave Reason', 'value':applying_reason})

            # if leave_type == "short leave":
            #     date_to = date_from
            #     ls.append({'key':'To Date', 'key_value':date_to})
            data_leave = {"data_type": "key_value", "data" : ls}
            dispatcher.utter_attachment(data_leave)
            dispatcher.utter_message("Do you want me to apply leave with above mentioned details? (Yes/No)")
            return []

"""function to apply leave after gettting necessary details from user"""
class ActionApplyLeave(Action):

    def name(self):
        return "apply_leave_request"

    def run(self,dispatcher,tracker,domain):
        comp_code = tracker.get_slot("comp_code")
        if comp_code in ["dbcorp","check"]:
            return []
        else:
            leave_type = tracker.get_slot('LeaveType')
            from_date = tracker.get_slot('FromDate')
            leaveReason = tracker.get_slot('LeaveReason')
            if leave_type.strip().lower() == "short leave":
                to_date = from_date
            else:
                to_date = tracker.get_slot('ToDate')        
            emp_code =  tracker.get_slot("emp_code")
            access_token = tracker.get_slot("access_token")
            apiKey = DynamicApi('LEAVE').get_api(tracker)
            data=tracker.get_slot("leave_type_list")
            for i in data:
                if i['lv_Type'].strip().lower()==leave_type:
                    leave_type_id=i['lv_Type_id']

            apply_url= 'https://'+comp_code+'.honohr.com/sapi/' + 'LeaveMaster/leave_request_v2?'
            apply_key = apply_url + 'comp_code='+comp_code+'&emp_code='+emp_code+'&api_key='+apiKey+'&token='+access_token+'&declareText=&from_date='+from_date+'&from_type=2FD&lvType='+str(leave_type_id)+'&optionalleave=&plan_unplan=1&reason='+leaveReason+'&to_date='+to_date+'&to_type=2FD&type=create&unplan_type=0'
            encryptedKey = base64.b64encode(apply_key.encode('utf-8'))
            prefix = RandomDigits.random_characters(3)
            suffix = RandomDigits.random_characters(3)
            data = {'encryption_key': prefix + str(encryptedKey.decode('utf-8')) + suffix, 'type' : 'ios'}
            r = requests.post(url=apply_url, data=data)

            if r.status_code == 200:
                try:
                    response=r.json()
                    if response['result'] in ['true', True]:
                        dispatcher.utter_message(response['message'])
                    elif response['result'] in ['false', False]:
                        dispatcher.utter_message(response['error'])
                        return []
                    else:
                        dispatcher.utter_message('Something went wrong, kindly check your leave status before applying again.')
                        return []
                except:
                    dispatcher.utter_message('Something went wrong, kindly check your leave status before applying again.')
            elif r.status_code == 400:
                dispatcher.utter_message("Something went wrong, please try again after sometime.")
            else:
                dispatcher.utter_message("Something went wrong, kindly check your leave status before applying again.")

"""form for getting necessary details from user to apply for od/out on duty"""
class ActionODForm(FormAction):
    def name(self):
        return 'od_form'

    
    @staticmethod
    def required_slots(tracker: Tracker):
        comp_code = tracker.get_slot("comp_code")
        fromdate = tracker.get_slot("FromDate")
        todate = tracker.get_slot("ToDate")
        if comp_code in ["dbcorp","check"]:
            return []
        else:
            if fromdate == todate:
                return ['FromDate','ToDate','ODStart','ODNatureWork', 'Reason_od']
            else:
                return ['FromDate','ToDate','ODStart','ODEnd','ODNatureWork', 'Reason_od']


    def slot_mappings(self):
        return {
            'FromDate':[
                self.from_entity(entity='FromDate'),
                self.from_text(not_intent=['deny', 'stop','reset_bot','reset_bot'])],
            'ToDate':[
                self.from_entity(entity='ToDate'),
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            'ODStart': [
                self.from_entity(entity='ODStart', intent=['apply_od','inform']),
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            'ODEnd': [
                self.from_entity(entity='ODEnd', intent=['apply_od','inform']),
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            'ODNatureWork': [
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            'Reason_od': [
                self.from_text()]
                }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""
            fromdate = tracker.get_slot("FromDate")
            todate = tracker.get_slot("ToDate")
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'ODStart':
                        if fromdate != todate:
                            logger.debug("Request next slot '{}'".format(slot))
                            lst = ['1. Second Half', '2. Full Day']
                            buttons = []
                            for t in lst:
                                payload = "/od_form{\"ODStart\": \"" + t + "\"}"
                                buttons.append({"title": "{}".format(t), "payload": payload})
                            # text = "Kindly select Out on Duty start timings:"
                            dispatcher.utter_button_template('utter_ask_ODStart', buttons,tracker)
                            return [SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            logger.debug("Request next slot '{}'".format(slot))
                            lst = ['1. First Half', '2. Second Half', '3. Full Day']
                            buttons = []
                            for t in lst:
                                payload = "/od_form{\"ODStart\": \"" + t + "\"}"
                                buttons.append({"title": "{}".format(t), "payload": payload})
                            # text = "Kindly select Out on Duty start timings:"
                            dispatcher.utter_button_template('utter_ask_ODStart', buttons,tracker)
                            return [SlotSet(REQUESTED_SLOT, slot)]
                    elif slot == 'ODEnd':
                        logger.debug("Request next slot '{}'".format(slot))
                        lst = ['1. First Half', '2. Full Day']
                        buttons = []
                        for t in lst:
                            payload = "/od_form{\"ODEnd\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        # text = "Kindly select Out on Duty End timings:"
                        dispatcher.utter_button_template('utter_ask_ODEnd', buttons, tracker)
                        return [SlotSet(REQUESTED_SLOT, slot)]
                    elif slot == 'ODNatureWork':
                        logger.debug("Request next slot '{}'".format(slot))
                        if tracker.get_slot('od_reason_list') != None:
                            ls =[]
                            new_data = []
                            data=tracker.get_slot('od_reason_list')
                            for i in data:
                                if i['reason_value'] not in ls:
                                    ls.append(i['reason_value'])
                                    new_data.append(i)
                            sorted_data = sorted(new_data, key = lambda i: i['reason_id'])
                            buttons = []
                            for t in sorted_data:
                                payload = "/od_form{\"ODNatureWork\": \"" + t['reason_value'] + "\"}"
                                buttons.append({"title": "{0}. {1}".format(sorted_data.index(t)+1,t['reason_value']), "payload": payload})
                            # text = "Kindly select one of the following reasons for applying Out on Duty:"
                            dispatcher.utter_button_template('utter_ask_ODNatureWork', buttons, tracker)
                            return [SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            comp_code = tracker.get_slot("comp_code")
                            emp_code =  tracker.get_slot("emp_code")
                            access_token = tracker.get_slot("access_token")
                            apiKey = DynamicApi('ATTENDANCE').get_api(tracker)
                            show_base_url='https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/showAttendanceApprover_v2?'
                            aa_key=show_base_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&token='+access_token
                            encryptedKey = base64.b64encode(aa_key.encode('utf-8'))
                            prefix = RandomDigits.random_characters(3)
                            suffix = RandomDigits.random_characters(3)
                            trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                            aa_url = show_base_url + 'encryption_key=' + trans_key + '&type=ios'
                            req = requests.get(aa_url)

                            ls =[]
                            new_data = []
                            data=req.json()['out_on_duty_nature_work']
                            for i in data:
                                if i['reason_value'] not in ls:
                                    ls.append(i['reason_value'])
                                    new_data.append(i)
                            sorted_data = sorted(new_data, key = lambda i: i['reason_id'])
                            buttons = []
                            for t in sorted_data:
                                payload = "/od_form{\"ODNatureWork\": \"" + t['reason_value'] + "\"}"
                                buttons.append({"title": "{0}. {1}".format(sorted_data.index(t)+1,t['reason_value']), "payload": payload})
                            text = "Kindly select one of the following reasons for applying Out on Duty:"
                            dispatcher.utter_button_message(text, buttons)
                            return [SlotSet(REQUESTED_SLOT, slot),SlotSet('od_reason_list',data)]                        
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

            logger.debug("No slots left to request")
            return None

    def validate_FromDate(self,value, dispatcher, tracker, domain):

        pdt = parsedatetime.Calendar()
        from_dt, stamp = pdt.parseDT(value)
        current_date = datetime.date.today()
        frm_dt=from_dt.date()
        ls = [int(i) for i in re.findall(r'-?\d+', value)]
        if stamp == 0:
            dispatcher.utter_message("That's an invalid date, try using formats like 26 sep or sep 26 etc.")
        elif len(ls)>0 and (ls[0]>31 or ls[0]<=0):
            dispatcher.utter_message("Date out of range, kindly provide a valid date.")
        else:
            num_days = int((frm_dt-current_date).days)
            if num_days < 100 or 273 < num_days <= 365:
                if num_days < 100:
                    frm_dt = frm_dt.strftime("%Y-%m-%d")
                    return {"FromDate": frm_dt}
                elif 273 < num_days <= 365:
                    Fromdate = frm_dt-datetime.timedelta(days=366)
                    Fromdate = Fromdate.strftime("%Y-%m-%d")
                    return {"FromDate": Fromdate}
            else:
                dispatcher.utter_message("Sorry, you can't apply od for this date.")
            

    
    def validate_ToDate(self, value, dispatcher, tracker, domain):

        pdt=parsedatetime.Calendar()
        to_dt,stamp=pdt.parseDT(value)
        todt=to_dt.date()
        current_date = datetime.date.today()
        
        if tracker.get_slot("FromDate") == None:
            try:
                abc = tracker.latest_message['entities']
                for i in abc:
                    if i['entity'] == "FromDate":
                        from_dt =  i['value']
                frm_dt,_=pdt.parseDT(from_dt)
                frm_dt = frm_dt.date()
                frm_dt = frm_dt.replace(year = current_date.year)
            except:
                pass
        else:
            from_dt = tracker.get_slot("FromDate")
            frm_dt,_=pdt.parseDT(from_dt)
            frm_dt = frm_dt.date()

        ls = [int(i) for i in re.findall(r'-?\d+', value)]

        if stamp == 0:
            dispatcher.utter_message("That's an invalid date, try using formats like 26 sep or sep 26 etc.")
        elif len(ls)>0 and (ls[0]>31 or ls[0]<=0):
            dispatcher.utter_message("Date out of range, kindly provide a valid date.")
        else:
            num_days = int((todt-current_date).days)
            if num_days < 100 or 273 < num_days <= 365:
                if num_days < 100:
                    if int((todt-frm_dt).days) >= 0:
                        todt = todt.strftime("%Y-%m-%d")
                        return {"ToDate": todt}
                    else:
                        dispatcher.utter_message('To Date cannot be prior From Date.')
                elif 273 < num_days <= 365:
                    Todt = todt-datetime.timedelta(days=366)
                    if int((Todt-frm_dt).days) >=0:
                        todt = Todt.strftime("%Y-%m-%d")
                        return {"ToDate": todt}
                    else:
                        dispatcher.utter_message('To Date cannot be prior From Date.')                    
            else:
                dispatcher.utter_message("Sorry, you can't apply od for this date.")          

    def validate_ODStart(self, value, dispatcher, tracker, domain):
        fromdate = tracker.get_slot('FromDate')
        todate = tracker.get_slot('ToDate')
        if value != "":
            if fromdate == todate:
                if value.lower() in ["1","first half","first","1. first half","first_half"]:
                    return {"ODStart": "first_half"}
                elif value.lower() in ["2","second half","second","2. second half",'second_half']:
                    return {"ODStart": "second_half"}
                elif value.lower() in ["3","full day","full","3. full day","full_day"]:
                    return {"ODStart": "full_day"}
                else:
                    dispatcher.utter_message("That's an invalid time value.")
            else:
                if value.lower() in ["1","second half","second","1. second half","second_half"]:
                    return {"ODStart": "socond_half"}
                elif value.lower() in ["2","full day","full","2. full day","full_day"]:
                    return {"ODStart": "full_day"}
                else:
                    dispatcher.utter_message("That's an invalid time value.")
        else:
            dispatcher.utter_message("Start time value can't be empty.")

    def validate_ODEnd(self, value, dispatcher, tracker, domain):
        if value != "":
            if value.lower() in ["1","first half","first","1. first half", "first_half"]:
                return {"ODEnd": "first_half"}
            elif value.lower() in ["2","full day","full","2. full day","full_day"]:
                return {"ODEnd": "full_day"}
            else:
                dispatcher.utter_message("That's an invalid time value.")      
        else:
            dispatcher.utter_message("End time value can't be empty.")


    def validate_ODNatureWork(self, value, dispatcher, tracker, domain):
        ls =[]
        new_data = []
        data=tracker.get_slot("od_reason_list")
        for i in data:
            if i['reason_value'] not in ls:
                ls.append(i['reason_value'])
                new_data.append(i)
        sorted_data = sorted(new_data, key = lambda i: i['reason_id'])
        if value != "":
            wrong_value = False
            for t in sorted_data:
                if value.lower() in [t['reason_value'].lower(),str(sorted_data.index(t)+1),"{0}. {1}".format(sorted_data.index(t)+1,t['reason_value'].lower())]:
                    wrong_value = True
                    return {"ODNatureWork":t['reason_value'].lower()}

            if wrong_value == False:
                dispatcher.utter_message("That's an invalid Out on duty reason.")
        else:
            dispatcher.utter_message("Out on duty reason can't be empty.")

    def submit(self, dispatcher, tracker, domain):
        # dispatcher.utter_template('utter_check_details', tracker)
        return[]

class ActionUtterODDetails(Action):

    def name(self):
        return "apply_od_values"

    def run(self, dispatcher, tracker, domain):
        comp_code = tracker.get_slot("comp_code")
        if comp_code in ["dbcorp","check"]:
            dispatcher.utter_message("Functionality coming soon.")
            return []
        else:
            fromdate = tracker.get_slot("FromDate")
            todate = tracker.get_slot("ToDate")
            ls = []
            date_from = tracker.get_slot("FromDate")
            # date_from = date_from.strftime('%Y-%m-%d')
            ls.append({'key': 'From Date', 'value': date_from})
            date_to = tracker.get_slot("ToDate")
            # date_to = date_to.strftime('%Y-%m-%d')
            ls.append({'key': 'To Date', 'value': date_to})
            intime = tracker.get_slot("ODStart").replace("_"," ").title()
            ls.append({'key': 'OD Period Start', 'value': intime})
            if fromdate == todate:
                outtime = tracker.get_slot("ODStart").replace("_"," ").title()
                ls.append({'key': 'OD Period End', 'value': outtime})
            else:
                outtime = tracker.get_slot("ODEnd").replace("_"," ").title()
                ls.append({'key': 'OD Period End', 'value': outtime})
            NatureOfWorkCause = tracker.get_slot("ODNatureWork").replace("_"," ").title()
            ls.append({'key': 'Nature Of Work', 'value': NatureOfWorkCause})
            Reason = tracker.get_slot("Reason_od")
            ls.append({'key': 'OD Reason', 'value': Reason})

            data_leave = {"data_type": "key_value", "data" : ls}
            dispatcher.utter_message("Thank you, kindly check the below mentioned details:")
            dispatcher.utter_attachment(data_leave)
            dispatcher.utter_message("Do you want me to raise an Out on Duty with above mentioned details? (Yes/No)")
            return []

"""function to apply od/out on duty after getting necessary details from user"""
class ActionApplyOD(Action):
    
    def name(self):
        return "apply_od_request"

    def run(self, dispatcher, tracker, domain):
        comp_code = tracker.get_slot("comp_code")
        if comp_code in ["dbcorp","check"]:
            return []
        else:
            api_key = DynamicApi('ATTENDANCE').get_api(tracker)
            emp_code = tracker.get_slot("emp_code")
            date_from = tracker.get_slot("FromDate")
            date_to = tracker.get_slot("ToDate")
            intime = tracker.get_slot("ODStart")
            if date_from == date_to:
                outtime = tracker.get_slot("ODStart")
            else:
                outtime = tracker.get_slot("ODEnd")
            Reason = tracker.get_slot("Reason_od")
            NatureOfWorkCause = tracker.get_slot("ODNatureWork")
            considerWeekOffHoliday = '0'
            datetime_from_wh = 'null'
            datetime_to_wh = 'null'
            datetime_from = 'null'
            datetime_to = 'null'
            access_token = tracker.get_slot("access_token")
            od_base_url = 'https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/submitOutOnDuty_New_v3?'

            new_data = []
            ls = []

            dataget=tracker.get_slot("od_reason_list")
            for i in dataget:
                if i['reason_value'] not in ls:
                    ls.append(i['reason_value'])
                    new_data.append(i)
            for i in new_data:
                if NatureOfWorkCause in i['reason_value'].lower():
                    NatureOfWork = i['reason_id']
                else:
                    pass

            od_apply_url = od_base_url+"comp_code="+comp_code+"&api_key="+api_key+"&emp_code="+emp_code+"&date_from="+date_from+"&date_to="+date_to+"&intime="+intime+"&outtime="+outtime+"&Reason="+Reason+"&NatureOfWorkCause="+NatureOfWork+"&considerWeekOffHoliday="+considerWeekOffHoliday+"&datetime_from_wh="+datetime_from_wh+"&datetime_to_wh="+datetime_to_wh+"&datetime_from="+datetime_from+"&datetime_to="+datetime_to+"&token="+access_token
            encryptedKey = base64.b64encode(od_apply_url.encode('utf-8'))
            prefix = RandomDigits.random_characters(3)
            suffix = RandomDigits.random_characters(3)
            data = {'encryption_key': prefix + str(encryptedKey.decode('utf-8')) + suffix, 'type' : 'ios'}
            r = requests.post(url=od_base_url, data=data)

            if r.status_code == 200:
                try:
                    response = r.json()
                    if response['result'] in ['true', True]:
                        dispatcher.utter_message(response['OD_submit'])
                    elif response['result'] in ['false', False]:
                        dispatcher.utter_message(response['error'])
                    else:
                        dispatcher.utter_message('Something went wrong, kindly check your OD status before applying again.')
                except:
                    dispatcher.utter_message('Something went wrong, kindly check your OD status before applying again.')
            elif r.status_code == 400:
                dispatcher.utter_message('Something went wrong, please try again after sometime.')
            else:
                dispatcher.utter_message('Something went wrong, kindly check your OD status before applying again.')



"""form for getting remarks for cancel ar/attendance regualrization"""
class ActionShowPendingARRequest(Action):

    def name(self):
        return "show_pending_ar_request"

    def run(self, dispatcher, tracker, domain):

        comp_code = tracker.get_slot("comp_code")
        emp_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")
        apiKey = DynamicApi('ATTENDANCE').get_api(tracker)
        page = '1'
        get_trans_url='https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/pastAttendanceTransactions_New_v2?'
        get_trans_key= get_trans_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&page='+page+'&token='+access_token
        encryptedKey = base64.b64encode(get_trans_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        ar_trans_url = get_trans_url + 'encryption_key=' + trans_key + '&type=ios'
        r = requests.get(ar_trans_url)

        if r.status_code == 200:
            try:
                data = r.json()['Past_transactions']
                
                count = dict(collections.Counter(i['Status'] for i in data))
                ar_db = [i for i in count]
                if 'Pending for Approval' not in ar_db:
                    return [SlotSet('cancel_ar_confirm', 'no_record')]
                else:
                    dispatcher.utter_message('You have {} pending request.<br> Below are the details:'.format(count['Pending for Approval']))  
                    n=0
                    ks = []
                    for i in data:
                        if i['Status']=='Pending for Approval':
                            n+=1
                            ks.append({"SNo": "S No", "n": n,"applied_date": "Applied Date","Applied_Date_Time": i['Applied_Date_Time'], 
                                    "from_date": "From Date", "From_date": i['From_date'], "to_date": "To Date", "To_date": i['To_date'], 
                                    "in_time": "In Time", "In_time": i['In_time'], "out_time": "Out Time", "Out_time": i['Out_time'], 
                                    "reason": "Reason", "Not_marking_reason": i['Not_marking_reason']})
                    data_ar_detail = {"data_type": "pending_ar_details", "data": ks}
                    dispatcher.utter_attachment(data_ar_detail)
                    return [SlotSet('cancel_ar_data', data)]
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime.")

class ActionCancelARRemark(FormAction):
    def name(self):
        return "cancel_ar_remarks"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        if tracker.get_slot('cancel_ar_confirm') == 'no_record':
            return []
        else:
            return ["cancel_ar_text", "cancel_ar_remark","cancel_ar_confirm"]

    def slot_mappings(self):
        return {
            "cancel_ar_text":[
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            "cancel_ar_remark":[                    
                self.from_text()],
            "cancel_ar_confirm":[
                self.from_text(not_intent=['reset_bot'])]
            }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'cancel_ar_confirm':
                        logger.debug("Request next slot '{}'".format(slot))
                        status_buttons =  ['1. Yes','2. No']
                        buttons = []
                        for t in status_buttons:
                            payload = "/cancel_ar_remarks{\"cancel_ar_confirm\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        text = "Thanks for providing the remarks. Do you want to cancel the selected AR application?"
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)] 
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_cancel_ar_text(self,value, dispatcher, tracker, domain):
        if value != "":
            data = tracker.get_slot('cancel_ar_data')
            count = dict(collections.Counter([i['Status'] for i in data]))
            count_number = count['Pending for Approval']
            try:
                sn = w2n.word_to_num(value)
                if 0< sn <= count_number:
                    return {"cancel_ar_text":sn}
                else:
                    dispatcher.utter_message('No record found for this serial number.')

            except:
                dispatcher.utter_message('Kindly provide a valid pending serial number.')
        else:
            dispatcher.utter_message('Kindly provide a serial number.')

    def validate_cancel_ar_confirm(self,value, dispatcher, tracker, domain):
        if value != "":
            if value.lower() in ["1","yes","1. yes"]:
                return {"cancel_ar_confirm":"yes"}
            elif value.lower() in ["2","no","2. no"]:
                return {"cancel_ar_confirm":"no"}
            else:
                text = "That's an invalid input."
                dispatcher.utter_button_message(text)
        else:
            text = "Input cannot be blank."
            dispatcher.utter_button_message(text)

    def submit(self, dispatcher, tracker, domain):
        return []

class ActionCancelAR(Action):
    
    def name(self):
        return "cancel_pending_ar_request"

    def run(self, dispatcher, tracker, domain):
        confirm_ar = tracker.get_slot("cancel_ar_confirm")

        if confirm_ar == "no_record":
            dispatcher.utter_message('No Pending AR Request.')
            return []
        elif confirm_ar == "no":
            dispatcher.utter_template('utter_not_cancel_ar', tracker)
            return []
        else:
            comp_code = tracker.get_slot("comp_code")
            emp_code =  tracker.get_slot("emp_code")
            cancel_ar_url='https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/cancelMarkPast_v2?'
            access_token = tracker.get_slot("access_token")
            apiKey = DynamicApi('ATTENDANCE').get_api(tracker) 
            remark = tracker.get_slot('cancel_ar_remark')
            data=tracker.get_slot('cancel_ar_data')
            attn_key_ls=[]
            markPastId_ls=[]
            for i in data:
                if i['Status']=='Pending for Approval':
                    attn_key_ls.append(i['Attn_key'])
                    markPastId_ls.append(i['markPastId'])

            sn = tracker.get_slot('cancel_ar_text')
            Attn_key=attn_key_ls[sn-1]
            markPastId=markPastId_ls[sn-1]
            
            ar_post_key = cancel_ar_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&markPastId='+str(markPastId)+'&Attn_key='+str(Attn_key)+'&remark='+remark+'&token='+access_token
            encryptedKey = base64.b64encode(ar_post_key.encode('utf-8'))
            prefix = RandomDigits.random_characters(3)
            suffix = RandomDigits.random_characters(3)
            data = {'encryption_key': prefix + str(encryptedKey.decode('utf-8')) + suffix, 'type' : 'ios'}
            r = requests.post(url=cancel_ar_url, data=data)
            if r.status_code == 200:
                try:
                    response = r.json()
                    if response['result'] in ['true', True]:
                        dispatcher.utter_message(response['MarkPastcancelled'])
                    elif response['result'] in ['false', False]:
                        dispatcher.utter_message(response['error'])
                    else:
                        dispatcher.utter_message('Something went wrong, kindly check your AR status before cancelling again.')
                except:
                    dispatcher.utter_message('Something went wrong, kindly check your AR status before cancelling again.')
            elif r.status_code == 400:
                dispatcher.utter_message('Something went wrong, please try again after sometime.')
            else:
                dispatcher.utter_message('Something went wrong, kindly check your AR status before cancelling again.')
            return []


"""for getting cancel leave remarks"""

class ActionGetLeaveTransactions(Action):

    def name(self):
        return 'get_leave_transaction'

    def run(self, dispatcher, tracker, domain):

        comp_code = tracker.get_slot("comp_code")
        emp_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")
        apiKey = DynamicApi('LEAVE').get_api(tracker)
        page = 1
        get_trans_url = 'https://'+comp_code+'.honohr.com/sapi/LeaveMaster/getLeaveTransactionsNew_v2?'
        get_trans_key = get_trans_url+'comp_code='+comp_code+'&emp_code='+emp_code+'&api_key='+apiKey+'&token='+access_token+'&declareText=&page='+str(page)+'&type=ios'
        encryptedKey = base64.b64encode(get_trans_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        trans_url = get_trans_url + 'encryption_key=' + trans_key + '&type=ios'
        r = requests.get(trans_url)

        if r.status_code == 200:
            try:
                data = r.json()['leave_transactions']

                count = dict(collections.Counter([i['Status'] for i in data]))
                leave_db = [i for i in count]
                """   need to add function for approved and rejected ar """
                if 'Pending for Approval' not in leave_db:
                    return [SlotSet('cancel_leave_confirm', 'no_record')]
                else:
                    dispatcher.utter_message('You have {} pending request.<br> Below are the details:'.format(count['Pending for Approval']))
                    ks = []
                    n = 0
                    for i in data:
                        if i['Status']=='Pending for Approval':
                            n+=1
                            ks.append({"SNo": "S No", "n": n,"leave_type": "Leave Type", "Leave_type": i['Leave_type'],
                                    "applied_date": "Applied Date","Applied_Date_Time": i['Applied_Date_Time'], 
                                    "from_date": "From Date", "From_date": i['From_date'], 
                                    "to_date": "To Date", "To_date": i['To_date'], 
                                    "reason": "Reason", "Not_marking_reason": i['Reason']})
                    data_detail = {"data_type":"leave_transaction_detail", "data":ks}
                    dispatcher.utter_attachment(data_detail)        
                    return [SlotSet('cancel_leave_data', data)]
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime.")

class ActionCancelLeaveRemark(FormAction):
    def name(self):
        return "cancel_leave_remarks"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        if tracker.get_slot('cancel_leave_confirm') == 'no_record':
            return []
        else:
            return ["cancel_leave_text", "cancel_leave_remark","cancel_leave_confirm"]

    def slot_mappings(self):
        return {
            "cancel_leave_text":[
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            "cancel_leave_remark":[
                self.from_text()],
            "cancel_leave_confirm":[
                self.from_text(not_intent=['reset_bot'])]
            }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'cancel_leave_confirm':
                        logger.debug("Request next slot '{}'".format(slot))
                        status_buttons =  ['1. Yes','2. No']
                        buttons = []
                        for t in status_buttons:
                            payload = "/cancel_leave_remarks{\"cancel_leave_confirm\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        text = "Thanks for providing the remarks. Do you want to cancel the selected leave application?"
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)] 
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_cancel_leave_text(self,value, dispatcher, tracker, domain):
        if value != "":
            data = tracker.get_slot('cancel_leave_data')
            count = dict(collections.Counter([i['Status'] for i in data]))
            count_number = count['Pending for Approval']
            try:
                sn = w2n.word_to_num(value)
                if 0< sn <= count_number:
                    return {"cancel_leave_text":sn}
                else:
                    dispatcher.utter_message('No record found for this serial number.')

            except:
                dispatcher.utter_message('Kindly provide a valid pending serial number.')
        else:
            dispatcher.utter_message('Kindly provide a serial number.')

    def validate_cancel_leave_confirm(self,value, dispatcher, tracker, domain):
        if value != "":
            if value.lower() in ["1","yes","1. yes"]:
                return {"cancel_leave_confirm":"yes"}
            elif value.lower() in ["2","no","2. no"]:
                return {"cancel_leave_confirm":"no"}
            else:
                text = "That's an invalid input."
                dispatcher.utter_button_message(text)
        else:
            text = "Input cannot be blank."
            dispatcher.utter_button_message(text)

    def submit(self, dispatcher, tracker, domain):
        return []

"""function to cancel applied leave"""
class ActionCancelLeave(Action):
    def name(self):
        return 'cancel_leave_request'

    def run(self, dispatcher, tracker, domain):
        
        confirm_leave = tracker.get_slot("cancel_leave_confirm")

        if confirm_leave == "no_record":
            dispatcher.utter_message('No Pending Leave Request.')
            return []
        elif confirm_leave == "no":
            dispatcher.utter_template('utter_not_cancel_leave', tracker)
            return []
        else:
            comp_code = tracker.get_slot("comp_code")
            emp_code =  tracker.get_slot("emp_code")
            access_token = tracker.get_slot("access_token")
            apiKey = DynamicApi('LEAVE').get_api(tracker)
            data=tracker.get_slot('cancel_leave_data')
            ls = []
            for i in data:
                if i['Status']=='Pending for Approval':
                    ls.append(i['leave_key'])
            sn = tracker.get_slot("cancel_leave_text")
            leave_key=ls[sn-1]
                
            remark = tracker.get_slot("cancel_leave_remark")
            cancel_url = 'https://'+comp_code+'.honohr.com/sapi/LeaveMaster/cancelleaveRequest_v2?'
            cancel_key = cancel_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&lvkey='+leave_key+'&remark='+remark+'&token='+access_token
            encryptedKey = base64.b64encode(cancel_key.encode('utf-8'))
            prefix = RandomDigits.random_characters(3)
            suffix = RandomDigits.random_characters(3)        
            data = {'encryption_key': prefix + str(encryptedKey.decode('utf-8')) + suffix, 'type' : 'ios'}
            r = requests.post(url=cancel_url, data=data)

            if r.status_code == 200:
                try:
                    response=r.json()
                    if response['result'] in ['true', True]:
                        dispatcher.utter_message(response['leavecancelled'])
                    elif response['result'] in ['false', False]:
                        dispatcher.utter_message(response['error'])
                    else:
                        dispatcher.utter_message('Something went wrong, kindly check your leave status before cancelling again.')
                except:
                    dispatcher.utter_message('Something went wrong, kindly check your leave status before cancelling again.')
            elif r.status_code == 400:
                dispatcher.utter_message("Something went wrong, please try again later after sometime.")
            else:
                dispatcher.utter_message("Something went wrong, kindly check your leave status before cancelling again.")


"""form for getting remarks for cancel od/out on duty"""
class ActionODTransaction(Action):
    def name(self):
        return 'show_pending_od_request'

    def run(self, dispatcher, tracker, domain):

        comp_code = tracker.get_slot("comp_code")
        emp_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")
        apiKey = DynamicApi('ATTENDANCE').get_api(tracker)
        page='1'
        base_url='https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/ODTransactions_New_v3?'
        od_trans_key= base_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&page='+page+'&token='+access_token
        encryptedKey = base64.b64encode(od_trans_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        od_trans_url = base_url + 'encryption_key=' + trans_key + '&type=ios'
        r = requests.get(od_trans_url)

        if r.status_code == 200:
            try:
                data = r.json()['OD_transactions']

                count = dict(collections.Counter(i['Status'] for i in data))
                od_db = [i for i in count]
                if 'Pending for Approval' not in od_db:
                    return [SlotSet('cancel_od_confirm', 'no_record')]
                else:
                    dispatcher.utter_message('You have {} pending request.<br> Below are the details:'.format(count['Pending for Approval']))

                    ks = []
                    n=0
                    for i in data:
                        if i['Status']=='Pending for Approval':
                            n+=1
                            ks.append({"SNo": "S No", "n": n,"applied_date": "Applied Date","Applied_Date_Time": i['Applied_Date_Time'], 
                                    "from_date": "From Date", "From_date": i['From_date'], "to_date": "To Date", "To_date": i['To_date']})

                    data_od_detail = {"data_type": "pending_od_details", "data": ks}
                    dispatcher.utter_attachment(data_od_detail)
                    return [SlotSet('cancel_od_data', data)]
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message('You have {} pending request.<br> Below are the details:'.format(count['Pending for Approval']))

class ActionCancelODRemark(FormAction):
    def name(self):
        return "cancel_od_remarks"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        if tracker.get_slot('cancel_od_confirm') == 'no_record':
            return []
        else:
            return ["cancel_od_text", "cancel_od_remark","cancel_od_confirm"]

    def slot_mappings(self):
        return {
            "cancel_od_text":[
                self.from_text(not_intent=['deny', 'stop','reset_bot'])],
            "cancel_od_remark":[                    
                self.from_text()],
            "cancel_od_confirm":[
                self.from_text(not_intent=['reset_bot'])]
            }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'cancel_od_confirm':
                        logger.debug("Request next slot '{}'".format(slot))
                        status_buttons =  ['1. Yes','2. No']
                        buttons = []
                        for t in status_buttons:
                            payload = "/cancel_od_remarks{\"cancel_od_confirm\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        text = "Thanks for providing the remarks. Do you want to cancel the selected OD application?"
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)] 
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_cancel_od_text(self,value, dispatcher, tracker, domain):
        if value != "":
            data = tracker.get_slot('cancel_od_data')
            count = dict(collections.Counter([i['Status'] for i in data]))
            count_number = count['Pending for Approval']
            try:
                sn = w2n.word_to_num(value)
                if 0< sn <= count_number:
                    return {"cancel_od_text":sn}
                else:
                    dispatcher.utter_message('No record found for this serial number.')

            except:
                dispatcher.utter_message('Kindly provide a valid pending serial number.')
        else:
            dispatcher.utter_message('Kindly provide a serial number.')

    def validate_cancel_od_confirm(self,value, dispatcher, tracker, domain):
        if value != "":
            if value.lower() in ["1","yes","1. yes"]:
                return {"cancel_od_confirm":"yes"}
            elif value.lower() in ["2","no","2. no"]:
                return {"cancel_od_confirm":"no"}
            else:
                text = "That's an invalid input."
                dispatcher.utter_button_message(text)
        else:
            text = "Input cannot be blank."
            dispatcher.utter_button_message(text)

    def submit(self, dispatcher, tracker, domain):
        return []


"""cancel applied ar/attendance regularization application"""
class ActionCancelOD(Action):
    
    def name(self):
        return "cancel_pending_od_request"

    def run(self, dispatcher, tracker, domain):
        
        confirm_od = tracker.get_slot("cancel_od_confirm")

        if confirm_od == "no_record":
            dispatcher.utter_message('No Pending OD Request.')
            return []
        elif confirm_od == "no":
            dispatcher.utter_template('utter_not_cancel_od', tracker)
            return []
        else:        
            comp_code = tracker.get_slot("comp_code")
            emp_code =  tracker.get_slot("emp_code")
            access_token = tracker.get_slot("access_token")
            api_key = DynamicApi('ATTENDANCE').get_api(tracker)
            data=tracker.get_slot('cancel_od_data')

            """try to fill slot with list from 'show_pending_od_request', this will eliminate above block of code"""
            OdKey=[]
            OutWorkID=[]
            for i in data:
                if i['Status'] == 'Pending for Approval':
                    OdKey.append(i['OD_key'])
                    OutWorkID.append(i['outWorkId'])


            sn = tracker.get_slot('cancel_od_text')
            outWorkId=OutWorkID[sn-1]
            OD_key=OdKey[sn-1]
            
            remark = tracker.get_slot('cancel_od_remark')
            cancel_od_url =  'https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/cancelOD_v2?'
            od_post_key = cancel_od_url+'comp_code='+comp_code+'&api_key='+api_key+'&emp_code='+emp_code+'&outWorkId='+str(outWorkId)+'&OD_key='+str(OD_key)+'&token='+access_token+'&remark='+remark
            encryptedKey = base64.b64encode(od_post_key.encode('utf-8'))
            prefix = RandomDigits.random_characters(3)
            suffix = RandomDigits.random_characters(3)
            data = {'encryption_key': prefix + str(encryptedKey.decode('utf-8')) + suffix, 'type' : 'ios'}
            r = requests.post(url=cancel_od_url, data=data)
            if r.status_code == 200:
                try:
                    response = r.json()
                    if response['result'] in ['true', True]:
                        dispatcher.utter_message(response['ODcancelled'])
                    elif response['result'] in ['false', False]:
                        dispatcher.utter_message(response['error'])
                    else:
                        dispatcher.utter_message('Something went wrong, kindly check your OD status before cancelling again.')
                except:
                    dispatcher.utter_message('Something went wrong, kindly check your OD status before cancelling again.')
            elif r.status_code == 400:
                dispatcher.utter_message('Something went wrong, please try again after sometime.')
            else:
                dispatcher.utter_message('Something went wrong, kindly check your OD status before cancelling again.')

""" send faq to support team """
class GetFAQData(FormAction):
    def name(self):
        return "faq_form"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        return ["faq_subject", "faq_body"]

    def slot_mappings(self):
        return {
            "faq_subject":[
                self.from_text(not_intent=['stop','reset_bot'])],
            "faq_body":[                    
                self.from_text()]
            }

    def submit(self, dispatcher, tracker, domain):
        return []

class EmailFAQ(Action):

    def name(self):
        return "send_faq"

    def run(self, dispatcher, tracker, domain):

        subject = tracker.get_slot('faq_subject')
        comp_code = tracker.get_slot("comp_code")
        faq_body = tracker.get_slot('faq_body')
        user_data = tracker.get_slot('user_data')
        email = user_data['child']['OEMailID']
        emp_name = user_data['child']['EMP_NAME']
        subject_new = subject+" [{}]".format(comp_code)

        data = {'ticket': {'subject': subject_new, 'comment': {'body': faq_body},
                   'requester': {'name': emp_name,'email': email}}}

        payload = json.dumps(data)

        url = 'https://sequelhrohelpdesk.zendesk.com/api/v2/tickets.json'
        user = 'Varun.vats@honohr.com'
        pwd = 'Honohr@123'
        headers = {'content-type': 'application/json'}

        response = requests.post(url, data=payload, auth=(user, pwd), headers=headers)

        if response.status_code != 200:
            # print('Status:', response.status_code, 'Problem with the request. Exiting.')
            dispatcher.utter_message('Problem with the request. Kindly contact admin.')
            return []
        else:
            data = response.json()
            dispatcher.utter_message('Your request ({}) has been received and is being reviewed by our support staff.'.format(data['ticket']['id']))
            return []

class ActionWhatsPossible(Action):

    def name(self):
        return "action_ask_whatspossible"

    def run(self, dispatcher, tracker, domain):

        dispatcher.utter_message('Below is the list of tasks I can do for now:<br>\
                                1. Apply Leave/Attendance Regularization/Out on Duty<br>\
                                2. View Applied Leave/Attendance Regularization/Out on Duty<br>\
                                3. Cancel Applied Leave/Attendance Regularization/Out on Duty<br>\
                                <span id="dots"></span><span id="more"></span>\
                                <button class="see_more" style="display: "block";" id="myBtn">see more...</button>')
        return []


"""function to handle small chitchats in conversations"""
class ActionChitchat(Action):

    def name(self):
        return "action_chitchat"

    def run(self, dispatcher, tracker, domain):
        intent = tracker.latest_message["intent"].get("name")

        # retrieve the correct chitchat utterance dependent on the intent
        if intent in [
            "ask_builder",
            "ask_howdoing",
            "ask_whatspossible",
            "ask_isbot",
            "ask_howold",
            "ask_languagesbot",
            "ask_wherefrom",
            "ask_whoami",
            "slang",
            "telljoke",
            "ask_whatismyname",
            "ask_howbuilt",
            "ask_whoisit",
            "affirm",
            "out_of_scope"
        ]:
            dispatcher.utter_template("utter_" + intent, tracker)
        return []

"""view upcoming birthday, anniversary, events"""
class Actionanniversary(Action):
    def name(self):
        return 'get_anniversary_list'

    def run(self, dispatcher, tracker, domain):
        comp_code = tracker.get_slot("comp_code")
        token = tracker.get_slot("access_token")
        apiKey = DynamicApi('BIRTHDAY').get_api(tracker)
        base_url = 'https://'+comp_code+'.honohr.com/sapi/EventMaster/anniversary_New_v2?'
        ani_trans_key = base_url+'comp_code='+comp_code+'&api_key='+apiKey
        encryptedKey = base64.b64encode(ani_trans_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        ani_trans_url = base_url + 'encryption_key=' + trans_key + '&type=ios'
        r = requests.get(ani_trans_url)

        if r.status_code == 200:
            try:
                data = r.json()
                max_page_yesterday = data['maximum_pages_yesterday']
                max_page_today = data['maximum_pages_today']
                max_page_tomorrow = data['maximum_pages_tomorrow']

                ls_yesterday = []
                for i in range(max_page_yesterday):
                    page_yes = i+1
                    ani_trans_key = base_url+'comp_code='+comp_code+'&api_key='+apiKey+'&page='+str(page_yes)+'&token='+token
                    encryptedKey = base64.b64encode(ani_trans_key.encode('utf-8'))
                    trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                    ani_trans_url = base_url + 'encryption_key=' + trans_key + '&type=ios'
                    req = requests.get(ani_trans_url)
                    data_yes = req.json()['yesterday']
                    for i in data_yes:
                        ls_yesterday.append({"key": i["occassion"], "value": i["emp_name"]})
                if len(ls_yesterday) != 0:
                    dispatcher.utter_message("Below is the list of yesterday's events.")
                    data_anni_yes = {"data_type": "key_value", "data": ls_yesterday}
                    dispatcher.utter_attachment(data_anni_yes)
                else:
                    dispatcher.utter_message("No records found for yesterday events.")


                ls_today = []
                for i in range(max_page_today):
                    page_tod = i+1
                    ani_trans_key = base_url+'comp_code='+comp_code+'&api_key='+apiKey+'&page='+str(page_tod)+'&token='+token
                    encryptedKey = base64.b64encode(ani_trans_key.encode('utf-8'))
                    trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                    ani_trans_url = base_url + 'encryption_key=' + trans_key + '&type=ios'
                    req = requests.get(ani_trans_url)
                    data_today = req.json()['today']
                    for i in data_today:
                        ls_today.append({"key": i["occassion"], "value": i["emp_name"]})
                if len(ls_today) != 0:
                    dispatcher.utter_message("Below is the list of today's events.")
                    data_anni_today = {"data_type": "key_value", "data": ls_today}
                    dispatcher.utter_attachment(data_anni_today)
                else:
                    dispatcher.utter_message("No records found for today events.")


                ls_tomorrow = []
                for i in range(max_page_tomorrow):
                    page_tom = i+1
                    ani_trans_key = base_url+'comp_code='+comp_code+'&api_key='+apiKey+'&page='+str(page_tom)+'&token='+token
                    encryptedKey = base64.b64encode(ani_trans_key.encode('utf-8'))
                    trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                    ani_trans_url = base_url + 'encryption_key=' + trans_key + '&type=ios'
                    req = requests.get(ani_trans_url)
                    data_tomorrow = req.json()['tomorrow']
                    for i in data_tomorrow:
                        ls_tomorrow.append({"key": i["occassion"], "value": i["emp_name"]})
                if len(ls_tomorrow) != 0:
                    dispatcher.utter_message("Below is the list of tomorrow's events.")
                    data_anni_tomorrow = {"data_type": "key_value", "data": ls_tomorrow}
                    dispatcher.utter_attachment(data_anni_tomorrow)
                else:
                     dispatcher.utter_message("No records found for tomorrow events.")
                return[]
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime, except")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime, else.")



"""view applied ar/attendance regularization applications"""
class ActionGetARRequest(Action):

    def name(self):
        return "get_ar_request"

    def run(self, dispatcher, tracker, domain):
        comp_code = tracker.get_slot("comp_code")
        emp_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")
        apiKey = DynamicApi('ATTENDANCE').get_api(tracker)
        page = '1'
        get_trans_url='https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/pastAttendanceTransactions_New_v2?'
        get_trans_key= get_trans_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&page='+page+'&token='+access_token
        encryptedKey = base64.b64encode(get_trans_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        ar_trans_url = get_trans_url + 'encryption_key=' + trans_key + '&type=ios'
        r = requests.get(ar_trans_url)

        if r.status_code == 200:
            try:
                data = r.json()['Past_transactions']
                dispatcher.utter_message('Please find the summary of all applied attendance regularization requests:')
                
                count = dict(collections.Counter(i['Status'] for i in data))
                ar_db = [i for i in count]
                status_list =  ['Pending for Approval','Cancelled','Approved','Rejected']
                for i in status_list:
                    if i not in ar_db:
                        count.update({i:0})
                ls = [{"type":i,"number_of_days":count[i]} for i in status_list]
                data_ar_summary = {"data_type": "pending_ar_od_summary", "data": ls}

                dispatcher.utter_attachment(data_ar_summary)
                return [SlotSet("Past_transactions", data)]
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime.")


class ActionViewARStatus(FormAction):
    def name(self):
        return "view_ar_status"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        return ["view_ar_text"]

    def slot_mappings(self):
        return {
            "view_ar_text":[
                self.from_text(not_intent=['stop','reset_bot'])],
            }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'view_ar_text':
                        logger.debug("Request next slot '{}'".format(slot))
                        status_buttons =  ['1. Pending for Approval','2. Cancelled','3. Approved','4. Rejected']
                        buttons = []
                        for t in status_buttons:
                            payload = "/view_ar_status{\"view_ar_text\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        text = "Please Select One of the following AR Status."
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)] 
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_view_ar_text(self, value, dispatcher, tracker, domain):
        if value != "":
            if value.lower() in ["1","pending for approval","pending","1. pending for approval"]:
                return {"view_ar_text":"Pending for Approval"}
            elif value.lower() in ["2","cancelled","cancelled leaves","cancelled leave","2. cancelled"]:
                return {"view_ar_text":"Cancelled"}
            elif value.lower() in ["3","approved","approved leaves","approved leave","3. approved"]:
                return {"view_ar_text":"Approved"}
            elif value.lower() in ["4","rejected","rejected leaves","rejected leave","4. rejected"]:
                return {"view_ar_text":"Rejected"}
            else:
                dispatcher.utter_message("That's an invalid AR Status")
        else:
            dispatcher.utter_message('Ar Status cannot be blank.')


    def submit(self, dispatcher, tracker, domain):
        # dispatcher.utter_template('utter_check_details', tracker)

        return []

class ActionViewARRequest(Action):

    def name(self):
        return "view_ar_request"

    def run(self, dispatcher, tracker, domain):

        data = tracker.get_slot("Past_transactions")
        ar_status = tracker.get_slot("view_ar_text")
        count = dict(collections.Counter([i['Status'] for i in data]))
        ar_db = [i for i in count]
        if ar_status not in ar_db:
            status_text = "No Record found for this AR Status"
            dispatcher.utter_message(status_text)
        else:
            ar_text = 'Below are the details of all {} AR requests:'.format(ar_status)
            dispatcher.utter_message(ar_text)
            n=0
            ks = []
            for i in data:
                if i['Status']==ar_status:
                    n+=1
                    ks.append({"SNo": "S No", "n": n,"applied_date": "Applied Date","Applied_Date_Time": i['Applied_Date_Time'], 
                            "from_date": "From Date", "From_date": i['From_date'], "to_date": "To Date", "To_date": i['To_date'], 
                            "in_time": "In Time", "In_time": i['In_time'], "out_time": "Out Time", "Out_time": i['Out_time'], 
                            "reason": "Reason", "Not_marking_reason": i['Not_marking_reason']})
            data_ar_detail = {"data_type": "pending_ar_details", "data": ks}
            dispatcher.utter_attachment(data_ar_detail)
        return[]


class ActionCalendarDateForm(FormAction):
    def name(self):
        return "calendar_date_form"

    @staticmethod
    def required_slots(tracker: Tracker):
        try:
            entities = tracker.latest_message['entities']
        except:
            return []
        if len(entities) != 0:
            for i in entities:
                if i['entity'] == 'FromDate':
                    return ['FromDate']
                elif i['entity'] == 'ToDate':
                    return ['FromDate','ToDate']
                else:
                    return []
        else:
            return []

    def slot_mappings(self):
        return {
            "FromDate":[self.from_entity(entity='FromDate',intent='view_calendar'),
                        self.from_text(not_intent=['stop','deny','reset_bot'])],
            "ToDate":[self.from_entity(entity='ToDate',intent='view_calendar'),
                        self.from_text(not_intent=['stop','deny','reset_bot'])],
            }
    
    def validate_FromDate(self,value, dispatcher, tracker, domain):
        pdt = parsedatetime.Calendar()
        from_dt, stamp = pdt.parseDT(value)
        current_date = datetime.date.today()
        frm_dt=from_dt.date()
        # ls = [int(i) for i in re.findall(r'-?\d+', value)]
        if stamp == 0:
            dispatcher.utter_message("That's an invalid date, try using formats like 26 sep or sep 26 etc.")
        # elif len(ls)>0 and (ls[0]>31 or ls[0]<=0):
        #     dispatcher.utter_message("Date out of range, kindly provide a valid date.")
        else:
            if frm_dt>=current_date:
                frm_dt = frm_dt.replace(day=1)
                from_date = frm_dt.strftime("%d-%m-%Y")
                return {"FromDate": from_date}
            else:
                from_date = frm_dt.strftime("%d-%m-%Y")
                return {"FromDate": from_date}

    def validate_ToDate(self, value, dispatcher, tracker, domain):

        pdt=parsedatetime.Calendar()
        to_dt,stamp=pdt.parseDT(value)
        current_date = datetime.date.today()

        if tracker.get_slot("FromDate") == None:
            try:
                abc = tracker.latest_message['entities']
                for i in abc:
                    if i['entity'] == "FromDate":
                        from_dt =  i['value']
                frm_dt,_=pdt.parseDT(from_dt)
                frm_dt = frm_dt.date()
                frm_dt = frm_dt.replace(year = current_date.year)
            except:
                pass
        else:
            from_dt = tracker.get_slot("FromDate")
            frm_dt,_=pdt.parseDT(from_dt)
            frm_dt = frm_dt.date()


        # ls = [int(i) for i in re.findall(r'-?\d+', value)]

        if stamp == 0:
            dispatcher.utter_message("That's an invalid date, try using formats like 26 sep or sep 26 etc.")
        # elif len(ls)>0 and (ls[0]>31 or ls[0]<=0):
        #     dispatcher.utter_message("Date out of range, kindly provide a valid date.")
        elif to_dt.date() > current_date:
            to_date = current_date
            to_date = to_date.strftime("%d-%m-%Y")
            return {"ToDate": to_date}
        else:
            to_date = to_dt.strftime("%d-%m-%Y")
            return {"ToDate": to_date}


    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:

        """Define what the form has to do
            after all required slots are filled"""
        # utter submit template
        # dispatcher.utter_template("utter_check_details", tracker)

        return []


class ActionCalendarForm(FormAction):
    def name(self):
        return "calendar_form"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        return ['attendance_status']

    def slot_mappings(self):
        return {
             "attendance_status":[self.from_entity(entity='attendance_status',intent='view_calendar'),
                                self.from_entity(entity='view_team_text', intent='view_myteam'),
                                self.from_text(not_intent=['stop','deny','reset_bot'])],
            }

    def request_next_slot(self,
                        dispatcher,  # type: CollectingDispatcher
                        tracker,  # type: Tracker
                        domain  # type: Dict[Text, Any]
                        ):
        comp_code = tracker.get_slot('comp_code')
        emp_code = tracker.get_slot('emp_code')
        access_token = tracker.get_slot('access_token')
        apiKey = DynamicApi('CALENDAR').get_api(tracker)
        # data = tracker.get_slot('AttendanceDate')
        if tracker.get_slot('FromDate') == None:
            today = datetime.date.today()
            frm_dt = today.replace(day=1)
            frm_dt_view = frm_dt.strftime("%d-%b-%Y")
            to_dt_view = today.strftime("%d-%b-%Y")
            from_date = frm_dt.strftime("%d-%m-%Y")
            to_date = today.strftime("%d=%m-%Y")
        else:
            from_date = tracker.get_slot('FromDate')
            from_date = datetime.datetime.strptime(from_date, "%d-%m-%Y").date()
            frm_dt_view = from_date.strftime("%d-%b-%Y")
            from_date = tracker.get_slot('FromDate')
        if tracker.get_slot('ToDate') == None:
            from_date = datetime.datetime.strptime(from_date, "%d-%m-%Y").date()
            today = datetime.date.today()
            if from_date.month == today.month:
                to_dt = today
                frm_dt_view = from_date.strftime("%d-%b-%Y")
                from_date = from_date.strftime("%d-%m-%Y")
                to_dt_view = to_dt.strftime("%d-%b-%Y")
                to_date = to_dt.strftime("%d-%m-%Y")
            else:
                to_dt = from_date.replace(day=monthrange(from_date.year,from_date.month)[1])
                frm_dt_view = from_date.strftime("%d-%b-%Y")
                from_date = from_date.strftime("%d-%m-%Y")
                to_dt_view = to_dt.strftime("%d-%b-%Y")
                to_date = to_dt.strftime("%d-%m-%Y")
        else:
            to_date = tracker.get_slot("ToDate")
            to_date = datetime.datetime.strptime(to_date, "%d-%m-%Y").date()
            to_dt_view = to_date.strftime("%d-%b-%Y")
            to_date = tracker.get_slot("ToDate")
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                if slot == 'attendance_status':
                    logger.debug("Request next slot '{}'".format(slot))
                    get_url= 'https://'+comp_code+'.honohr.com/sapi/CalendarMaster/showCalendar_v2?'
                    cal_key = get_url + 'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&from_date='+from_date+'&to_date='+to_date+'&token='+access_token
                    encryptedKey = base64.b64encode(cal_key.encode('utf-8'))
                    prefix = RandomDigits.random_characters(3)
                    suffix = RandomDigits.random_characters(3)
                    cal_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                    cal_url= get_url +'encryption_key=' + cal_key + '&type=ios'
                    r = requests.get(cal_url)

                    data = r.json()['show_calendar']                    
                    count = dict(collections.Counter(i['status'] for i in data))
                    status_db = [i for i in count]
                    buttons = []
                    for t in status_db:
                        payload = "/calendar_form{\"attendance_status\": \"" + t + "\"}"
                        buttons.append({"title": "{0}. {1} ({2})".format(status_db.index(t)+1,t,count[t]), "payload": payload})
                    text = "Please find your attendance summary from {0} to {1}.<br>Kindly select one of the following to get details.".format(frm_dt_view,to_dt_view)
                    dispatcher.utter_button_message(text, buttons)
                    return [SlotSet(REQUESTED_SLOT, slot), SlotSet('AttendanceDate',data), SlotSet("FromDate",from_date), SlotSet("ToDate",to_date)]
                else:
                    logger.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template("utter_ask_{}".format(slot),
                                        tracker,
                                        silent_fail=False,
                                        **tracker.slots)
                    return [SlotSet(REQUESTED_SLOT, slot)]
    
    def validate_attendance_status(self, value, dispatcher, tracker, domain):
        attendance_status = 'abc'
        data = tracker.get_slot('AttendanceDate')
        count = dict(collections.Counter(i['status'] for i in data))
        status_db = [i for i in count]
        if value != '':
            wrong_value = False
            for i in status_db:
                if value.strip().lower() in [i.strip().lower(),str(status_db.index(i)+1),"{0}. {1} ({2})".format(status_db.index(i)+1,i.strip().lower(),count[i])]:
                    attendance_status = i.strip().lower()
                    wrong_value = True
                    return{'attendance_status':attendance_status}
            if wrong_value == False:
                dispatcher.utter_message("Invalid attendance status, kindly select again.")
        else:
            dispatcher.utter_message("Kindly select a valid value.")
        
    def submit(self, dispatcher, tracker, domain):
        return []

class GetAttendanceDetails(Action):
    def name(self):
        return 'get_attendance_details'
    
    def run(self,dispatcher,tracker,domain):
        data = tracker.get_slot('AttendanceDate')
        frm_dt = tracker.get_slot('FromDate')
        frmdt = datetime.datetime.strptime(frm_dt,"%d-%m-%Y")
        from_date = frmdt.strftime("%b-%d-%Y")
        to_dt = tracker.get_slot('ToDate')
        todt = datetime.datetime.strptime(to_dt,"%d-%m-%Y")
        to_date = todt.strftime("%b-%d-%Y")
        attendance_type = tracker.get_slot('attendance_status')
        ls = []
        for i in data:
            if i['title'].lower() == attendance_type.lower():
                ls.append({'key':i['status'], 'value':i['formattedDate']})
        data = {'data_type':'key_value','data':ls}
        dispatcher.utter_message("Please find your attendance report from {0} to {1}".format(from_date,to_date))
        dispatcher.utter_attachment(data)


class ActionViewHoliday(FormAction):
    def name(self):
        return "holiday_form"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        return ['holiday_type']

    def slot_mappings(self):
        return {
            "holiday_type":[self.from_entity(entity='holiday_type',intent='view_holiday'),
                self.from_text(not_intent=['stop','reset_bot'])],
            }   
    def request_next_slot(self,
                        dispatcher,  # type: CollectingDispatcher
                        tracker,  # type: Tracker
                        domain  # type: Dict[Text, Any]
                        ):
        # type: (...) -> Optional[List[Dict]]
        """Request the next slot and utter template if needed,
            else return None"""

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                if slot == 'holiday_type':
                    logger.debug("Request next slot '{}'".format(slot))
                    status_buttons =  ['1. Upcoming holidays','2. Past holidays']
                    buttons = []
                    for t in status_buttons:
                        payload = "/holiday_form{\"holiday_type\": \"" + t + "\"}"
                        buttons.append({"title": "{}".format(t), "payload": payload})
                    text = "Please Select One of the following."
                    dispatcher.utter_button_message(text, buttons)
                    return [SlotSet(REQUESTED_SLOT, slot)] 
                else:
                    logger.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template("utter_ask_{}".format(slot),
                                        tracker,
                                        silent_fail=False,
                                        **tracker.slots)
                    return [SlotSet(REQUESTED_SLOT, slot)]
    def validate_holiday_type(self, value, dispatcher, tracker, domain):
        if value != "":
            if value.strip().lower() in ["upcoming","coming",'1','1. Upcoming holidays','1. upcoming holidays']:
                return {"holiday_type":"upcomingholiday"}
            elif value.strip().lower() in ["past","previous", '2','2. Past holidays','2. past holidays']:
                return {"holiday_type":"pastholiday"}
            else:
                dispatcher.utter_message("That's an invalid value.")
        else:
            dispatcher.utter_message('value cannot be blank.')


    def submit(self, dispatcher, tracker, domain):
        # dispatcher.utter_template('utter_check_details', tracker)
        return []



"""view upcoming holidays"""
class view_holidays(Action):
    
    def name(self):
        
        return "get_holiday_list"  
    
    def run(self,dispatcher,tracker,domain):
        comp_code = tracker.get_slot("comp_code")
        emp_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")
        apiKey = DynamicApi('HOLIDAY').get_api(tracker)
        holiday_type = tracker.get_slot('holiday_type')
        page = 1
        get_url= 'https://'+comp_code+'.honohr.com/sapi/EventMaster/upcomingPastHoliday_New_v2?'
        bal_key = get_url + 'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&page='+str(page)+'&token='+access_token
        encryptedKey = base64.b64encode(bal_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        balance_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        balance_url= get_url +'encryption_key=' + balance_key + '&type=ios'
        r = requests.get(balance_url)

        if r.status_code == 200:
            try:
                data = r.json()[holiday_type]
                if len(data) != 0:
                    dispatcher.utter_message('Getting your holiday list.')
                    data_holiday = [{'key':i['holiday_name'], 'value':i['holiday_date']} for i in data]
                    data_holidays = {"data_type":"key_value","data": data_holiday}
                    dispatcher.utter_attachment(data_holidays)
                else:
                    dispatcher.utter_message("No Holidays for this time stamp.")
                return []
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime.")


class view_leave(Action):
    
    def name(self):
        
        return "get_leave_balance"  
    
    
    def run(self,dispatcher,tracker,domain):
        # comp_code = tracker.get_slot("comp_code")
        # if comp_code == "orientbell":
        #     dispatcher.utter_message("Sorry, I'm not authorised to show leave balances for your company.")
        #     return []
        # else:
        dispatcher.utter_message("Getting your leave balance.")
        apiKey = DynamicApi('LEAVE').get_api(tracker)
        data, req = getLeaveBalances_v2(apiKey).get_data(tracker)

        if req.status_code == 200:
            try:
                data = data['leave_balance']
                dispatcher.utter_message("Below is the summary of all available leave balance in your account:")
                ls = [{'key':i['lv_Type'], 'value':i['lv_Value']} for i in data]
                data_leave = {"data_type": "key_value", "data" : ls}
                dispatcher.utter_attachment(data_leave)
                return []
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime.")


"""view applied leaves"""
class ActionGetLeaveRequest(Action):

    def name(self):
        return 'get_leave_request'

    def run(self, dispatcher, tracker, domain):

        comp_code = tracker.get_slot("comp_code")
        emp_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")
        apiKey = DynamicApi('LEAVE').get_api(tracker)
        page = 1
        get_trans_url = 'https://'+comp_code+'.honohr.com/sapi/LeaveMaster/getLeaveTransactionsNew_v2?'
        get_trans_key = get_trans_url+'comp_code='+comp_code+'&emp_code='+emp_code+'&api_key='+apiKey+'&token='+access_token+'&declareText=&page='+str(page)+'&type=ios'
        encryptedKey = base64.b64encode(get_trans_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        trans_url = get_trans_url + 'encryption_key=' + trans_key + '&type=ios'
        r = requests.get(trans_url)

        if r.status_code == 200:
            try:
                data = r.json()['leave_transactions']
                dispatcher.utter_message('Please find the summary of all applied leaves:')

                count = dict(collections.Counter([i['Status'] for i in data]))
                leave_db = [i for i in count]
                status_list =  ['Pending for Approval','Cancelled','Approved','Rejected']
                for i in status_list:
                    if i not in leave_db:
                        count.update({i:0})
                ls=[{"key":i,"value":count[i]} for i in status_list]
                data_summary = {"data_type":"key_value", "data":ls}

                dispatcher.utter_attachment(data_summary)
                return [SlotSet("leave_transactions", data)]
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("something went wrong, please try after sometime.")

class ActionViewLeaveStatus(FormAction):
    def name(self):
        return "view_leave_status"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        return ["view_leave_text"]

    def slot_mappings(self):
        return {
            "view_leave_text":[
                self.from_text(not_intent=['stop','reset_bot'])],
            }


    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'view_leave_text':
                        logger.debug("Request next slot '{}'".format(slot))
                        status_buttons =  ['1. Pending for Approval','2. Cancelled','3. Approved','4. Rejected']
                        buttons = []
                        for t in status_buttons:
                            payload = "/view_leave_status{\"view_leave_text\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        text = "Please Select One of the following Leave Status."
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)] 
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_view_leave_text(self, value, dispatcher, tracker, domain):
        if value != "":
            if value.lower() in ["1","pending for approval","pending","1. pending for approval"]:
                return {"view_leave_text":"Pending for Approval"}
            elif value.lower() in ["2","cancelled","cancelled leaves","cancelled leave","2. cancelled"]:
                return {"view_leave_text":"Cancelled"}
            elif value.lower() in ["3","approved","approved leaves","approved leave","3. approved"]:
                return {"view_leave_text":"Approved"}
            elif value.lower() in ["4","rejected","rejected leaves","rejected leave","4. rejected"]:
                return {"view_leave_text":"Rejected"}
            else:
                dispatcher.utter_message("That's an invalid Leave Status")
        else:
            dispatcher.utter_message('Leave Status cannot be blank.')


    def submit(self, dispatcher, tracker, domain):
        # dispatcher.utter_template('utter_check_details', tracker)
        return []

class ActionShowLeaveTransactions(Action):

    def name(self):
        return 'show_leave_transaction'

    def run(self, dispatcher, tracker, domain):
        data = tracker.get_slot("leave_transactions")
        leave_status = tracker.get_slot("view_leave_text")
        count = dict(collections.Counter([i['Status'] for i in data]))
        leave_db = [i for i in count]
        if leave_status not in leave_db:
            status_text = "No Record found for this Leave Status"
            dispatcher.utter_message(status_text)
        else:
            leave_text = 'Below are the details of all {} leave requests:'.format(leave_status)
            dispatcher.utter_message(leave_text)
            ks = []
            n = 0
            for i in data:
                if i['Status']==leave_status:
                    n+=1
                    ks.append({"SNo": "S No", "n": n,"leave_type": "Leave Type", "Leave_type": i['Leave_type'],
                            "applied_date": "Applied Date","Applied_Date_Time": i['Applied_Date_Time'], 
                            "from_date": "From Date", "From_date": i['From_date'], 
                            "to_date": "To Date", "To_date": i['To_date'], 
                            "reason": "Reason", "Not_marking_reason": i['Reason']})
            data_detail = {"data_type":"leave_transaction_detail", "data":ks}
            dispatcher.utter_attachment(data_detail)        
        return []



# A form action to fetch news from the internet
class getNews(FormAction):
    def name(self):
        return "get_news"
    
    @staticmethod
    def required_slots(tracker: Tracker):

        return ["topic_news"]

    def slot_mappings(self):
        return {"topic_news": [self.from_entity(entity='topic_news',intent='getNews'),
                                self.from_text(not_intent=['reset_bot'])]
                }

    def validate_topic_news(self, value, dispatcher, tracker, domain):
        if value != "":
            
            pageSize = '5' # Set the number to how many news articles you want to fetch 
            
            url = "https://newsapi.org/v2/everything?q=" + value + "&apiKey=" + NEWS_API_KEY + "&pageSize=" + pageSize
            
            r = requests.get(url = url)
            try:
                data = r.json() # extracting data in json format
                data = data['articles']
                if len(data) != 0:

                    dispatcher.utter_message("Here is the top 5 news I found!")

                    for i in range(len(data)):
                        title = '<strong>' + '{}.'.format(i+1) + '</strong>' + '<br>' + '<strong>' + 'Title:' + '</strong>' + '<br>' + data[i]['title'] + \
                            '<br>' + '<strong>' + 'Description:' + '</strong>' + '<br>' + data[i]['description'] + '<br>' + \
                                '<strong>' + 'Link:' + '</strong>' + '<br>' + '<a href="{}" target="_blank">Click Here To Read More.</a>'.format(data[i]['url']) + '<br>'
                        dispatcher.utter_message(title)

                    dispatcher.utter_template("utter_confirm_if_service_is_correct", tracker)
                    return {"topic_news":value}

                else:
                    dispatcher.utter_message("Try Another Topic, Couldn't find anything on this topic.")

            except: 
                dispatcher.utter_message("Try Another Topic, Couldn't find anything on this topic ") 
        else:
            dispatcher.utter_message('Topic cannot be empty.')

    def submit(self, dispatcher, tracker, domain):
        return []


class getHealines(FormAction):
    def name(self):
        return "get_headlines"
    
    @staticmethod
    def required_slots(tracker: Tracker):

        return ["headline_country"]

    def slot_mappings(self):
        return {"headline_country": [
                                self.from_entity(entity='headline_country',intent='getHeadlines'),
                                self.from_text(not_intent=['reset_bot'])]
                }

    def validate_headline_country(self, value, dispatcher, tracker, domain):
        if value != "":
            with open('./data/lookup/country_json.txt') as json_file:
                country_list = json.load(json_file)
            count_found = 0
            for i in country_list['country_data']:
                if value in i['Name']:
                    return {"headline_country":i['Code']}
                    count_found += 1
                elif value in i['Code']:
                    return {"headline_country":i['Code']}
                    count_found += 1
            if count_found == 0:
                dispatcher.utter_message("Try Another Country, Couldn't find anything on this Country.")

        else:
            dispatcher.utter_message('Country Name cannot be empty.')

    def submit(self, dispatcher, tracker, domain):
        return []


class actionheadlines(Action):
    def name(self):

        return 'show_headlines'

    def run(self, dispatcher, tracker, domain):
        pageSize = '5'
        country_code = tracker.get_slot("headline_country")
        url = "https://newsapi.org/v2/top-headlines?country=" + country_code + "&apiKey=" + NEWS_API_KEY + "&pageSize=" + pageSize
        
        r = requests.get(url = url)
        try:
            data = r.json() # extracting data in json format
            data = data['articles']
            if len(data) != 0:
                dispatcher.utter_message("Here is the top headlines I found!")

                for i in range(len(data)):
                    title = '<strong>' + '{}.'.format(i+1) + '</strong>' + '<br>' + '<strong>' + 'Title:' + '</strong>' + '<br>' + data[i]['title'] + \
                        '<br>' + '<strong>' + 'Description:' + '</strong>' + '<br>' + data[i]['description'] + '<br>' + \
                            '<strong>' + 'Link:' + '</strong>' + '<br>' + '<a href="{}" target="_blank">Click Here To Read More.</a>'.format(data[i]['url']) + '<br>'
                    dispatcher.utter_message(title)
            else:
                dispatcher.utter_message("Try Another , Couldn't find anything on this Country.")

        except: 
            dispatcher.utter_message("Try Another Country, Couldn't find anything on this Country ") 


"""view applied od/out for duty"""
class ActionGetODRequest(Action):
    def name(self):
        return 'get_od_request'

    def run(self, dispatcher, tracker, domain):

        comp_code = tracker.get_slot("comp_code")
        emp_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")
        apiKey = DynamicApi('ATTENDANCE').get_api(tracker)
        page='1'
        base_url='https://'+comp_code+'.honohr.com/sapi/AttendanceMaster/ODTransactions_New_v3?'
        od_trans_key= base_url+'comp_code='+comp_code+'&api_key='+apiKey+'&emp_code='+emp_code+'&page='+page+'&token='+access_token
        encryptedKey = base64.b64encode(od_trans_key.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        od_trans_url = base_url + 'encryption_key=' + trans_key + '&type=ios'
        r = requests.get(od_trans_url)

        if r.status_code == 200:
            try:
                data = r.json()['OD_transactions']
                dispatcher.utter_message('Please find the summary of all Out On Duty requests:')

                count = dict(collections.Counter(i['Status'] for i in data))
                od_db = [i for i in count]
                status_list =  ['Pending for Approval','Cancelled','Approved','Rejected']
                for i in status_list:
                    if i not in od_db:
                        count.update({i:0})
                ls = [{"type":i,"number_of_days":count[i]} for i in status_list]
                data_od_summary = {"data_type": "pending_ar_od_summary", "data": ls}

                dispatcher.utter_attachment(data_od_summary)
                return [SlotSet('OD_transactions', data)]
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime.")

class ActionViewODStatus(FormAction):
    def name(self):
        return "view_od_status"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        return ["view_od_text"]

    def slot_mappings(self):
        return {
            "view_od_text":[
                self.from_text(not_intent=['stop','reset_bot'])],
            }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'view_od_text':
                        logger.debug("Request next slot '{}'".format(slot))
                        status_buttons =  ['1. Pending for Approval','2. Cancelled','3. Approved','4. Rejected']
                        buttons = []
                        for t in status_buttons:
                            payload = "/view_od_status{\"view_od_text\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        text = "Please Select One of the following OD Status."
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)] 
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_view_od_text(self, value, dispatcher, tracker, domain):
        if value != "":
            if value.lower() in ["1","pending for approval","pending","1. pending for approval"]:
                return {"view_od_text":"Pending for Approval"}
            elif value.lower() in ["2","cancelled","cancelled leaves","cancelled leave","2. cancelled"]:
                return {"view_od_text":"Cancelled"}
            elif value.lower() in ["3","approved","approved leaves","approved leave","3. approved"]:
                return {"view_od_text":"Approved"}
            elif value.lower() in ["4","rejected","rejected leaves","rejected leave","4. rejected"]:
                return {"view_od_text":"Rejected"}
            else:
                dispatcher.utter_message("That's an invalid OD Status")
        else:
            dispatcher.utter_message('OD Status cannot be blank.')


    def submit(self, dispatcher, tracker, domain):
        # dispatcher.utter_template('utter_check_details', tracker)

        return []

class ActionViewODTransaction(Action):
    def name(self):
        return 'get_od_transaction'

    def run(self, dispatcher, tracker, domain):
        data = tracker.get_slot("OD_transactions")
        od_status = tracker.get_slot("view_od_text")
        count = dict(collections.Counter([i['Status'] for i in data]))
        od_db = [i for i in count]
        if od_status not in od_db:
            status_text = "No Record found for this OD Status"
            dispatcher.utter_message(status_text)
        else:
            od_text = 'Below are the details of all {} Out On Duty requests:'.format(od_status)
            dispatcher.utter_message(od_text)

            ks = []
            n=0
            for i in data:
                if i['Status']==od_status:
                    n+=1
                    ks.append({"SNo": "S No", "n": n,"applied_date": "Applied Date","Applied_Date_Time": i['Applied_Date_Time'], 
                            "from_date": "From Date", "From_date": i['From_date'], "to_date": "To Date", "To_date": i['To_date']})

            data_od_detail = {"data_type": "pending_od_details", "data": ks}
            dispatcher.utter_attachment(data_od_detail)
        return []

"""view team details for manager, view team"""
class view_myteam(Action):
    
    def name(self):
        
        return "get_myteam_list"  
    
    def run(self,dispatcher,tracker,domain):
        comp_code = tracker.get_slot("comp_code")
        mngr_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")

        """to check if user has manager role"""
        api_key = DynamicApi('EMPLOYEE').get_api(tracker)
        base_url = 'https://'+comp_code+'.honohr.com/sapi/OrganisationChart/OrgChart_v2?'
        chart_url = base_url+'comp_code='+comp_code+'&api_key='+api_key+'&emp_code='+mngr_code+'&token='+access_token
        encryptedKey = base64.b64encode(chart_url.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        chart_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        api_trans_url = base_url + 'encryption_key=' + chart_key + '&type=ios'
        r = requests.get(api_trans_url)

        if r.status_code == 200:
            try:
                data = r.json()['data']

                if len(data['subchild']) > 0:
                    manager_role = True
                elif len(data['subchild']) == 0:
                    manager_role = False
                else:
                    manager_role = False
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime.")
            return []

        if manager_role == True:
            apiKey = DynamicApi('MY_TEAM_DETAILS').get_api(tracker)
            get_url= 'https://'+comp_code+'.honohr.com/sapi/Service/myTeamDetails_New_v2?'
            team_key = get_url + 'comp_code='+comp_code+'&mngr_code='+mngr_code+'&api_key='+apiKey+'&token='+access_token
            encryptedKey = base64.b64encode(team_key.encode('utf-8'))
            prefix = RandomDigits.random_characters(3)
            suffix = RandomDigits.random_characters(3)
            myteam_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
            myteam_url= get_url +'encryption_key=' + myteam_key + '&type=ios'
            r = requests.get(myteam_url)
            abc = tracker.latest_message['entities']
            if len(abc) != 0:
                for i in abc:
                    emp_status = i['value']
            else:
                emp_status = None

            if r.status_code == 200:
                try:
                    data = r.json()['team_details']
                    count = dict(collections.Counter([i['status'] for i in data]))
                    status_db = [i for i in count]
                    status_list = ['Present', 'Absent']
                    for i in status_list:
                        if i not in status_db:
                            count.update({i:0})
                    ls = [{"key":i, "value":count[i]} for i in status_list]
                    dispatcher.utter_message("Please find the summary of your team's attendance.")
                    data_summary = {"data_type": "key_value", "data": ls}
                    dispatcher.utter_attachment(data_summary)
                    ks = [{'key':i['emp_name'], 'value':i['mobile_no']} for i in data]
                    dispatcher.utter_message("Below is the list of your team members.")
                    data_details = {"data_type": "key_value", "data": ks}
                    dispatcher.utter_attachment(data_details)
                    return [SlotSet('team_detail_slot',data), SlotSet('view_team_text', emp_status)]
                except:
                    dispatcher.utter_message("Something went wrong, please try after sometime.")
            else:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        elif manager_role == False:
            # dispatcher.utter_message("You don't have any team yet.")
            return [SlotSet('view_team_text', 'not_manager'), SlotSet('team_detail_slot', None)]
        else:
            pass

""" for gettin api for company"""
class ActionGetSalaryCompany(Action):

    def name(self):
        return "company_for_salary"
    
    def run(self, dispatcher, tracker, domain):

        comp_code = tracker.get_slot("comp_code")
        apiKey = DynamicApi('PAYROLL').get_api(tracker)
        
        if apiKey == '':
            dispatcher.utter_message("Sorry, I'm not authorised to access salary details for your company.")
            return [SlotSet("FromMonth", "no_api")]
        else:
            try:
                month = tracker.latest_message['entities']
                for i in month:
                    if i['entity'] == 'FromMonth':
                        from_month = i['value']
                        return[SlotSet("FromMonth", from_month)]
                    else:
                        return []
            except:
                return []

"""form to get and validate month and year for salary details"""
class ActionSalaryForm(FormAction):
    def name(self):

        return "salary_form"

    @staticmethod
    def required_slots(tracker: Tracker):
        if tracker.get_slot('FromMonth') == "no_api":
            return []
        else:
            return ['FromMonth']

    def slot_mappings(self):
        return {
            "FromMonth":[self.from_entity(entity = 'FromMonth', intent = 'get_salary'),
                self.from_text(not_intent=['deny','stop','reset_bot'])]
            }

    def validate_FromMonth(self,value, dispatcher, tracker, domain):

        """slot setting for both month and year"""
        pdt = parsedatetime.Calendar()
        mnth, stamp = pdt.parseDT(value)
        month = mnth.date().month
        given_year = mnth.date().year
        current_year = datetime.datetime.now().date().year
        
        if stamp == 0:
            dispatcher.utter_message("That's an invalid month, try using formats march, jan, oct 2019 etc.")
        elif given_year >= current_year:
            given_year = given_year-1
            return {"FromMonth": month, "FromYear": given_year}
        else:
            return {"FromMonth": month, "FromYear": given_year}


    def submit(self, dispatcher, tracker, domain):
        return []

"""to get salary details"""
class ActionGetSalaryDetails(Action):

    def name(self):
        return "get_salary_details"

    def run(self, dispatcher, tracker, domain):

        comp_code = tracker.get_slot("comp_code")
        emp_code = tracker.get_slot("emp_code")
        action = "encrypt"
        month = tracker.get_slot("FromMonth")
        apiKey = DynamicApi('PAYROLL').get_api(tracker)
        if month != 'no_api':
            base_url = "https://"+comp_code+".honohr.com/sapi/PayrollData/payrollEncryption?"
            ekey_url = base_url+'comp_code='+comp_code+'&emp_code='+emp_code+'&api_key='+apiKey+'&action='+action
            req = requests.get(ekey_url)
            if req.status_code == 200:
                try:
                    data = req.json()
                    if data['result'] in ['true', True]:
                        ekey = req.json()['data']
                    else:
                        dispatcher.utter_message(data['error'])
                        return []
                except:
                    dispatcher.utter_message("Something went wrong, please try after sometime.")

            month = tracker.get_slot("FromMonth")
            year = tracker.get_slot("FromYear")
            month = month if len(str(month))==2 else '0'+str(month)
            get_salary_url = base_url+'PayrollData/getEmpSalary?comp_code='+comp_code+'&api_key=' + apiKey + '&emp_code='+ekey+'&month='+str(month)+'&year='+str(year)
            r = requests.get(get_salary_url)
            if r.status_code == 200:
                try:
                    data = r.json()
                    if data['result'] in ['false', False]:
                        dispatcher.utter_message(data['error'])
                    else:
                        dispatcher.utter_message("Getting your salary details.")
                        for key,value in data.items():

                            if key == 'salary':
                                salary =[]
                                salary.append({'key':'NETPAY','value': value['NETPAY']})
                                salary.append({'key':'GROSSPAY','value': value['GROSSPAY']})
                                if len(salary) != 0:
                                    salary_data = {'data_type': 'key_value', 'data': salary}
                                    dispatcher.utter_message("Please find the summary of your salary breakup.")
                                    dispatcher.utter_attachment(salary_data)
                                else:
                                    pass


                            elif key in 'Earning':
                                earning = []
                                if len(value) != 0:
                                    for i in value:
                                        earning.append({'key':i['Payhead'],'value':i['Value']})
                                else:
                                    pass
                                if len(earning) != 0:
                                    earning_data = {'data_type': 'key_value', 'data': earning}
                                    dispatcher.utter_message("Below are the details of your earnings.")
                                    dispatcher.utter_attachment(earning_data)
                                else:
                                    pass


                            elif key == 'Deduction':
                                deduction = []
                                if len(value) != 0:
                                    for i in value:
                                        deduction.append({'key':i['Payhead'],'value':i['Value']})
                                else:
                                    pass
                                if len(deduction) != 0:
                                    deduction_data = {'data_type': 'key_value', 'data': deduction}
                                    dispatcher.utter_message("Below are the details of deductions.")
                                    dispatcher.utter_attachment(deduction_data)
                                else:
                                    pass


                            elif key == 'Reimbursement':
                                reimbursement = []
                                if len(value) != 0:
                                    for i in value:
                                        reimbursement.append({'key':i['Payhead'],'value':i['Value']})
                                else:
                                    pass
                                if len(reimbursement) != 0:
                                    reimbursement_data = {'data_type': 'key_value', 'data': reimbursement}
                                    dispatcher.utter_message("Below are the details of your reimbursements.")
                                    dispatcher.utter_attachment(reimbursement_data)
                                else:
                                    pass


                            elif key == 'Arrear':
                                arrear = []
                                if len(value) != 0:
                                    for i in value():
                                        arrear.append({'key':i['Payhead'],'value':i['Value']})
                                else:
                                    pass
                                if len(arrear) != 0:
                                    arrear_data = {'data_type': 'key_value', 'data': arrear}
                                    dispatcher.utter_message("Below are the details of your arrear reimbursements.")
                                    dispatcher.utter_attachment(arrear_data)
                                else:
                                    pass

                            else:
                                pass
                        else:
                            pass
                except:
                    dispatcher.utter_message("Something went wrong, please try after sometime.")
            else:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
            return []
        else:
            return []


"""need to add after get_myteam_list in view_team_manager, for getting details"""
class ActionViewTeamDetails(FormAction):
    def name(self):
        return "view_team_status"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        if tracker.get_slot("view_team_text") == 'not_manager':
            return []
        else:
            return ["view_team_text"]

    def slot_mappings(self):
        return {
            "view_team_text":[
                self.from_text(not_intent=['deny','stop','reset_bot'])]
            }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'view_team_text':
                        logger.debug("Request next slot '{}'".format(slot))
                        # data = tracker.get_slot('team_detail_slot')
                        # count = dict(collections.Counter([i['status'] for i in data]))
                        # ls = [i for i in count]
                        status_list = ['Absent','Present']
                        buttons = []
                        for i in status_list:
                            payload = "/view_team_status{\"Status\": \"" + i.lower() + "\"}"
                            buttons.append({"title":i, "payload":payload})

                        text = "Please Select One of the following button to view details."
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)] 
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_view_team_text(self, value, dispatcher, tracker, domain):

        data = tracker.get_slot('team_detail_slot')
        try:
            ls = [i['status'] for i in data]
        except:
            ls = []

        if value != "":
            # wrong_value = False
            ks = ['Present','Absent']
            if value.lower() in [i.lower() for i in ls]:
                # wrong_value = True
                return {"view_team_text":value.strip().lower()}
            elif value == 'not_manager':
                return {"view_team_text": 'not_manager'}
            elif value in ks and value not in ls:
                # dispatcher.utter_message("Sorry, no record found for {} status.".format(value.lower()))
                return {"view_team_text":value.strip().lower()}
            else:
                 dispatcher.utter_message("Status type not found.")     
        else:
            dispatcher.utter_message("Status type can't be empty.")

        
    def submit(self, dispatcher, tracker, domain):
        return []

class ActionGetTeamDetails(Action):
    
    def name(self):
        return "get_team_details"

    def run(self, dispatcher, tracker, domain):

        # ks = ['present','absent']
        status = tracker.get_slot("view_team_text")
        if status == 'not_manager':
            dispatcher.utter_message("You don't have any team yet.")
        # elif status not in ks:
        #     dispatcher.utter_message("Sorry, no record found for {} status.".format(status.lower()))
        else:
            data = tracker.get_slot('team_detail_slot')
            if data != '':
                js = [i['status'].lower() for i in data]
                ls = ['present','absent']
                if status not in js and status in ls:
                    dispatcher.utter_message("Sorry, no record found for {} status.".format(status.lower()))
                else:
                    try:
                        ks = []
                        for i in data:
                            if i['status'].lower() == status:
                                ks.append({'key':i['emp_name'], 'value':i['mobile_no']})
                        data_team_details = {"data_type": "key_value", "data": ks}
                        dispatcher.utter_message("Please find the detials of all {} employees.".format(status))
                        dispatcher.utter_attachment(data_team_details)
                        return []
                    except:
                        dispatcher.utter_message("Something went wrong, please try after sometime.")
            else:
                dispatcher.utter_message("Something went wrong, please try after sometime.")


"""view manager todo list, manager pending tasks"""

class PutSpace:
    def __init__(self,WordInput):
        self.WordInput = WordInput

    def putSpace(self):   
        words = re.findall('[A-Z][a-z]*', self.WordInput) 
        result = [] 
        for word in words: 
            word = chr( ord (word[0]) + 32) + word[1:] 
            result.append(word.title()) 
        word_created =  ' '.join(result)
        return word_created 

class actionTodolist(Action):
    def name(self):

        return 'get_todo_list'

    def run(self, dispatcher, tracker, domain):
        
        comp_code = tracker.get_slot("comp_code")
        emp_code =  tracker.get_slot("emp_code")
        access_token = tracker.get_slot("access_token")


        """to check if user has manager role"""
        api_key = DynamicApi('EMPLOYEE').get_api(tracker)
        base_url = 'https://'+comp_code+'.honohr.com/sapi/OrganisationChart/OrgChart_v2?'
        chart_url = base_url+'comp_code='+comp_code+'&api_key='+api_key+'&emp_code='+emp_code+'&token='+access_token
        encryptedKey = base64.b64encode(chart_url.encode('utf-8'))
        prefix = RandomDigits.random_characters(3)
        suffix = RandomDigits.random_characters(3)
        chart_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        api_trans_url = base_url + 'encryption_key=' + chart_key + '&type=ios'
        r = requests.get(api_trans_url)

        if r.status_code == 200:
            try:
                data = r.json()['data']

                if len(data['subchild']) > 0:
                    manager_role = True
                else:
                    manager_role = False
            except:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            dispatcher.utter_message("Something went wrong, please try after sometime.")
            return [SlotSet('move_forward_todo', 'not_manager')]

        if manager_role == True:
            apikey = DynamicApi('LEAVE').get_api(tracker)
            get_trans_url = 'https://'+comp_code+'.honohr.com/sapi/LeaveRequestApproval/getToDoList_Confirm_v3?'
            get_trans_key = get_trans_url+'comp_code='+comp_code+'&emp_code='+emp_code+'&api_key='+apikey+'&token='+access_token
            encryptedKey = base64.b64encode(get_trans_key.encode('utf-8'))
            prefix = RandomDigits.random_characters(3)
            suffix = RandomDigits.random_characters(3)
            trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
            trans_url = get_trans_url + 'encryption_key=' + trans_key + '&type=ios'
            r = requests.get(trans_url)
            if r.status_code == 200:
                try:
                    data = r.json()['data']
                    ls = [{'key': key.replace(key, PutSpace(key).putSpace()),
                            'value': len(value)} for key, value in data.items() if type(value) == list]
                    data_manager = {"data_type": "key_value", "data": ls}
                    dispatcher.utter_message("Please find the summary of tasks in your todo list.")
                    dispatcher.utter_attachment(data_manager)
                    
                    return [SlotSet('todo_data', ls), SlotSet('todo_all_data', data)]
                except:
                    dispatcher.utter_message("Something went wrong, please try after sometime.")
            else:
                dispatcher.utter_message("Something went wrong, please try after sometime.")
        else:
            return [SlotSet('move_forward_todo', 'not_manager')]

class DetailedTodoTask(FormAction):
    def name(self):
        return "detailed_todo_task"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        if tracker.get_slot('move_forward_todo') == 'not_manager':
            return[]
        elif tracker.get_slot('move_forward_todo') == 'no':
            return ["move_forward_todo"]
        else: 
            return ["move_forward_todo","todo_list_text"]

    def slot_mappings(self):
        return {
            "move_forward_todo":[
                self.from_text(not_intent=['stop','reset_bot'])],
            "todo_list_text":[
                self.from_text(not_intent=['stop','reset_bot'])]
            }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'todo_list_text':
                        logger.debug("Request next slot '{}'".format(slot))
                        # ls = tracker.get_slot('todo_data')
                        ls = ['Leave Pending Request','Mark Past Attendance','Out On Duty']
                        buttons = []
                        for t in ls:
                            # payload = "/detailed_todo_task{\"todo_list_text\": \"" + t['key'] + "\"}"
                            # buttons.append({"title": "{0}. {1}".format(ls.index(t)+1,t['key']), "payload": payload})
                            payload = "/detailed_todo_task{\"todo_list_text\": \"" + t + "\"}"
                            buttons.append({"title": "{0}. {1}".format(ls.index(t)+1,t), "payload": payload})
                        text = "Kindly select one of the following request type to proceed:"
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)]
                    elif slot == 'move_forward_todo':
                        logger.debug("Request next slot '{}'".format(slot))
                        status_buttons =  ['1. Yes','2. No']
                        buttons = []
                        for t in status_buttons:
                            payload = "/detailed_todo_task{\"move_forward_todo\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        text = "Do you want to approve or cancel any request?"
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)]
                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_move_forward_todo(self,value, dispatcher, tracker, domain):
        if value != "":
            if value.lower() in ["1","yes","1. yes"]:
                return {"move_forward_todo":"yes"}
            elif value.lower() in ["2","no","2. no"]:
                return {"move_forward_todo":"no"}
            elif value.lower() == 'not_manager':
                return {"move_forward_todo":"not_manager"}
            else:
                text = "That's an invalid input."
                dispatcher.utter_button_message(text)
        else:
            text = "Input cannot be blank."
            dispatcher.utter_button_message(text)

    def validate_todo_list_text(self,value, dispatcher, tracker, domain):
        if value != "":
            # ls = tracker.get_slot('todo_data')
            ls = ['Leave Pending Request','Mark Past Attendance','Out On Duty']
            wrong_value = False
            for t in ls:
                # if value.lower() in [t['key'].lower(),str(ls.index(t)+1),"{0}. {1}".format(ls.index(t)+1,t['key'].lower())]:
                #     wrong_value = True
                #     return {"todo_list_text":t['key']}
                if value.lower() in [t.lower(),str(ls.index(t)+1),"{0}. {1}".format(ls.index(t)+1,t.lower())]:
                    wrong_value = True
                    return {"todo_list_text":t}

            if wrong_value == False:
                if value.lower() == 'not_manager':
                    return {"todo_list_text":"not_manager"}
                else:
                    dispatcher.utter_message("That's an invalid approval type value.")
        else:
            dispatcher.utter_message("Approval type can't be empty.")

    def submit(self, dispatcher, tracker, domain):
        return []

class GetTodoList(Action):
    def name(self):
        return "get_todo_list_data"

    def run(self, dispatcher, tracker, domain):
        affirm_deny = tracker.get_slot('move_forward_todo')
        if affirm_deny in ['no','not_manager']:
            return []
        else:
            approval_data = tracker.get_slot("todo_list_text").replace(" ","")
            data = tracker.get_slot('todo_all_data')
            for key, value in data.items():
                if type(value) == list:
                    if approval_data == key:
                        if len(value) == 0:
                            dispatcher.utter_message('No Record Found.')
                            return [SlotSet('move_forward_todo','no')]
                        else:
                            if key == 'OutOnDuty':
                                ks = []
                                n = 0
                                for i in value:
                                    n += 1
                                    ks.append({"SNo": "S No","n": n,"emp_name": "Emp Name","Emp_Name": i['emp_name'],
                                    "no_of_days": "No. of Days","No_Of_Days": i['no_of_days'],"from_date": "From Date",
                                    "From_date": i['date_from'], "to_date": "To Date", "To_date": i['date_to'],
                                    "req_id": i['outWorkId']})
                                data_todo_detail = {"data_type": "todo_od_details", "data": ks}
                                dispatcher.utter_attachment(data_todo_detail)
                                return [SlotSet('emp_todo_data', ks)]  
                            elif key == 'MarkPastAttendance':
                                MarkPastIds = []
                                ks = []
                                n = 0
                                for i in value:
                                    for a,b in i.items():
                                        if a == 'markPastId':
                                            MarkPastIds.append(b)
                                comp_code = tracker.get_slot("comp_code")
                                apiKey = DynamicApi('ATTENDANCE').get_api(tracker)
                                access_token = tracker.get_slot("access_token")
                                for i in MarkPastIds:
                                    markpastid = i
                                    get_trans_url = 'https://'+comp_code+'.honohr.com/sapi/MarkPastAttendance/getMarkPastPopupData_v2?'
                                    get_trans_key = get_trans_url+'comp_code='+comp_code+'&api_key='+apiKey+'&markPastId='+str(markpastid)+'&token='+access_token
                                    encryptedKey = base64.b64encode(get_trans_key.encode('utf-8'))
                                    prefix = RandomDigits.random_characters(3)
                                    suffix = RandomDigits.random_characters(3)
                                    trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                                    trans_url = get_trans_url + 'encryption_key=' + trans_key + '&type=ios'
                                    r = requests.get(trans_url)
                                    data = r.json()['popup_data']
                                    n += 1
                                    ks.append({"SNo": "S No","n": n,"emp_name": "Emp Name","Emp_Name": data['requested_by'],
                                    "from_date": "From Date", "From_date": data['date_from'], "to_date": "To Date", 
                                    "To_date": data['date_to'], "req_id": i, "in_time": "In Time", "In_time": data['intime'],
                                    "out_time": "Out Time", "Out_time": data['outtime'], "actual_in_time": "Actual in Time","Actual_in_time": data['actual_in_time'],
                                    "actual_out_time": "Actual out Time", "Actual_out_time": data['actual_out_time']})
                                data_todo_detail = {"data_type": "todo_ar_details", "data": ks}
                                dispatcher.utter_attachment(data_todo_detail)
                                return [SlotSet('emp_todo_data', ks)]
                            elif key == 'LeavePendingRequest':
                                ks = []
                                n = 0
                                for i in value:
                                    n += 1
                                    ks.append({"SNo": "S No","n": n,"emp_name": "Emp Name","Emp_Name": i['emp_name'],
                                    "no_of_days": "No. of Days","No_Of_Days": i['LvDays'],"from_date": "From Date",
                                    "From_date": i['LvFrom'], "to_date": "To Date", "To_date": i['LvTo'], 
                                    "leave_type": "Leave Type", "Leave_Type": i['lvtype'], "req_id": i['leaveID']})
                                data_todo_detail = {"data_type": "todo_leave_details", "data": ks}
                                dispatcher.utter_attachment(data_todo_detail)
                                return [SlotSet('emp_todo_data', ks)]
                            else:
                                ks = []
                                n = 0
                                for i in value:
                                    n += 1
                                    ks.append({"SNo": "S No","n": n,"emp_name": "Emp Name","Emp_Name": i['emp_name'],
                                    "no_of_days": "No. of Days","No_Of_Days": i['no_of_days'],"from_date": "From Date",
                                    "From_date": i['date_from'], "to_date": "To Date", "To_date": i['date_to'],
                                    "req_id": i['outWorkId']})
                                data_todo_detail = {"data_type": "todo_od_details", "data": ks}
                                dispatcher.utter_attachment(data_todo_detail)
                                return [SlotSet('emp_todo_data', ks)]


class TakeActionTodo(FormAction):
    def name(self):
        return "take_todo_action"
    
    @staticmethod
    def required_slots(tracker: Tracker):
        if tracker.get_slot('move_forward_todo') in ['not_manager','no']:
            return []
        else:
            return ["serial_no_todo", "manager_decision","remark_todo","affirm_deny_todo"]

    def slot_mappings(self):
        return {
            "serial_no_todo":[
                self.from_text(not_intent=['stop','reset_bot'])],
            "remark_todo":[                    
                self.from_text()],
            "manager_decision":[                    
                self.from_text(not_intent=['stop','reset_bot'])],
            "affirm_deny_todo":[                    
                self.from_text(not_intent=['stop','reset_bot'])]
            }

    def request_next_slot(self,
                            dispatcher,  # type: CollectingDispatcher
                            tracker,  # type: Tracker
                            domain  # type: Dict[Text, Any]
                            ):
            # type: (...) -> Optional[List[Dict]]
            """Request the next slot and utter template if needed,
                else return None"""

            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if slot == 'manager_decision':
                        logger.debug("Request next slot '{}'".format(slot))
                        approval_data = tracker.get_slot("todo_list_text").replace(" ","")
                        if approval_data == 'LeavePendingRequest':
                            status_button1 =  ['1. Approve','2. Reject', '3. Reconsider']
                            buttons = []
                            for t in status_button1:
                                payload = "/take_todo_action{\"manager_decision\": \"" + t + "\"}"
                                buttons.append({"title": "{}".format(t), "payload": payload})
                            text = "Kindly select the type action you want to take:"
                            dispatcher.utter_button_message(text, buttons)
                            return [SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            status_button1 =  ['1. Approve','2. Reject']
                            buttons = []
                            for t in status_button1:
                                payload = "/take_todo_action{\"manager_decision\": \"" + t + "\"}"
                                buttons.append({"title": "{}".format(t), "payload": payload})
                            text = "Kindly select the type action you want to take:"
                            dispatcher.utter_button_message(text, buttons)
                            return [SlotSet(REQUESTED_SLOT, slot)]
                    elif slot == 'affirm_deny_todo':
                        logger.debug("Request next slot '{}'".format(slot))
                        status_buttons =  ['1. Yes','2. No']
                        buttons = []
                        for t in status_buttons:
                            payload = "/take_todo_action{\"affirm_deny_todo\": \"" + t + "\"}"
                            buttons.append({"title": "{}".format(t), "payload": payload})
                        text = "Do you want to move forward with your request?"
                        dispatcher.utter_button_message(text, buttons)
                        return [SlotSet(REQUESTED_SLOT, slot)] 

                    else:
                        logger.debug("Request next slot '{}'".format(slot))
                        dispatcher.utter_template("utter_ask_{}".format(slot),
                                          tracker,
                                          silent_fail=False,
                                          **tracker.slots)
                        return [SlotSet(REQUESTED_SLOT, slot)]

    def validate_serial_no_todo(self,value, dispatcher, tracker, domain):
        if value != "":
            if value == 'not_manager':
                return {"serial_no_todo": "not_manager"}
            else:
                data = tracker.get_slot('emp_todo_data')
                count_number = len(data)
                try:
                    sn = w2n.word_to_num(value)
                    if 0< sn <= count_number:
                        return {"serial_no_todo":sn}
                    else:
                        dispatcher.utter_message('No record found for this serial number.')

                except:
                    dispatcher.utter_message('Kindly provide a valid pending serial number.')
        else:
            dispatcher.utter_message('Kindly provide a serial number.')

    def validate_manager_decision(self,value, dispatcher, tracker, domain):
        if value != "":
            if value == 'not_manager':
                return {"manager_decision": 'not_manager'}
            else:
                approval_data = tracker.get_slot("todo_list_text").replace(" ","")
                if approval_data == 'LeavePendingRequest':
                    if value.lower() in ["1","approve","1. approve"]:
                        return {"manager_decision": '1'}
                    elif value.lower() in ["2","reject","2. reject"]:
                        return {"manager_decision": '3'}
                    elif value.lower() in ["3","reconsider","3. reconsider"]:
                        return {"manager_decision": '8'}
                    else:
                        dispatcher.utter_message("That's an invalid decision")
                else:
                    if value.lower() in ["1","approve","1. approve"]:
                        return {"manager_decision": '2'}
                    elif value.lower() in ["2","reject","2. reject"]:
                        return {"manager_decision": '3'}
                    else:
                        dispatcher.utter_message("That's an invalid decision")
        else:
            dispatcher.utter_message('Kindly provide your decision.')

    def validate_affirm_deny_todo(self,value, dispatcher, tracker, domain):
        if value != "":
            if value == 'not_manager':
                return {"affirm_deny_todo":"not_manager"}
            else:
                if value.lower() in ["1","yes","1. yes"]:
                    return {"affirm_deny_todo":"yes"}
                elif value.lower() in ["2","no","2. no"]:
                    return {"affirm_deny_todo":"no"}
                else:
                    text = "That's an invalid input."
                    dispatcher.utter_button_message(text)
        else:
            text = "Input cannot be blank."
            dispatcher.utter_button_message(text)

    def submit(self, dispatcher, tracker, domain):
        return []


class ManagerDecisionDone(Action):
    def name(self):
        return "manager_decision_final"

    def run(self, dispatcher, tracker, domain):
        if tracker.get_slot('move_forward_todo') == 'no':
            return []
        elif tracker.get_slot('move_forward_todo') == 'not_manager':
            dispatcher.utter_message("You don't have any team yet.")
        else:
            if tracker.get_slot('affirm_deny_todo') == 'no':
                dispatcher.utter_message('Alright, removing your application.')
            else:
                comp_code = tracker.get_slot("comp_code")
                emp_code =  tracker.get_slot("emp_code")
                access_token = tracker.get_slot("access_token")

                SerialNoUser = tracker.get_slot('serial_no_todo')
                action_flag = tracker.get_slot('manager_decision')
                remark = tracker.get_slot('remark_todo')
                reasons = tracker.get_slot('remark_todo')
                planned_unplanned = '1'
                combo_reason = '1'
                approval_data = tracker.get_slot("todo_list_text").replace(" ","")

                if approval_data == 'LeavePendingRequest':
                    api_key = DynamicApi('LEAVE').get_api(tracker)
                    data = tracker.get_slot('emp_todo_data')
                    for i in data:
                        if SerialNoUser == i['n']:
                            RequestID = i['req_id']
                    base_url = 'https://'+comp_code+'.honohr.com/sapi/LeaveRequestApproval/LeaveApproval_v2?'
                    cancel_key = base_url+'comp_code='+comp_code+'&api_key='+api_key+'&emp_code='+emp_code+'&leave_id='+str(RequestID)+'&action_flag='+action_flag+'&remarks='+remark+'&planned_unplanned='+planned_unplanned+'&combo_reason='+combo_reason+'&reasons='+reasons+'&token='+access_token
                    encryptedKey = base64.b64encode(cancel_key.encode('utf-8'))
                    prefix = RandomDigits.random_characters(3)
                    suffix = RandomDigits.random_characters(3)        
                    trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                    trans_url = base_url + 'encryption_key=' + trans_key + '&type=ios'
                    r = requests.get(trans_url)
                    if r.status_code == 200:
                        try:
                            response = r.json()
                            if response['result'] in ['true', True]:
                                dispatcher.utter_message(response['message'])
                            elif response['result'] in ['false', False]:
                                dispatcher.utter_message(response['error'])
                            else:
                                dispatcher.utter_message('Something went wrong.')
                        except:
                            dispatcher.utter_message('Something went wrong.')
                    elif r.status_code == 400:
                        dispatcher.utter_message('Something went wrong, please try again after sometime.')
                    else:
                        dispatcher.utter_message('Something went wrong.')

                elif approval_data == 'OutOnDuty':
                    api_key = DynamicApi('ATTENDANCE').get_api(tracker)
                    data = tracker.get_slot('emp_todo_data')
                    for i in data:
                        if SerialNoUser == i['n']:
                            RequestID = i['req_id']
                    base_url = 'https://'+comp_code+'.honohr.com/sapi/MarkPastAttendance/approveOutOnDuty_v2?'
                    od_key = base_url+'comp_code='+comp_code+'&api_key='+api_key+'&emp_code='+emp_code+'&outWorkId='+str(RequestID)+'&status_flag='+action_flag+'&user_code='+emp_code+'&remarks='+remark+'&token='+access_token
                    encryptedKey = base64.b64encode(od_key.encode('utf-8'))
                    prefix = RandomDigits.random_characters(3)
                    suffix = RandomDigits.random_characters(3)        
                    trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                    data = {'encryption_key':trans_key, 'type':'ios'}
                    r = requests.post(url = base_url, data= data)
                    if r.status_code == 200:
                        try:
                            response = r.json()
                            if response['result'] in ['true', True]:
                                dispatcher.utter_message(response['message'])
                            elif response['result'] in ['false', False]:
                                dispatcher.utter_message(response['error'])
                            else:
                                dispatcher.utter_message('Something went wrong.')
                        except:
                            dispatcher.utter_message('Something went wrong.')
                    elif r.status_code == 400:
                        dispatcher.utter_message('Something went wrong, please try again after sometime.')
                    else:
                        dispatcher.utter_message('Something went wrong.')

                elif approval_data == 'MarkPastAttendance':
                    api_key = DynamicApi('ATTENDANCE').get_api(tracker)
                    data = tracker.get_slot('emp_todo_data')
                    for i in data:
                        if SerialNoUser == i['n']:
                            RequestID = i['req_id']
                    base_url = 'https://'+comp_code+'.honohr.com/sapi/MarkPastAttendance/approveMarkPastAttendance_v2?'
                    ar_key = base_url+'comp_code='+comp_code+'&api_key='+api_key+'&emp_code='+emp_code+'&markPastId='+str(RequestID)+'&status_flag='+action_flag+'&user_code='+emp_code+'&remarks='+remark+'&token='+access_token
                    encryptedKey = base64.b64encode(ar_key.encode('utf-8'))
                    prefix = RandomDigits.random_characters(3)
                    suffix = RandomDigits.random_characters(3)        
                    trans_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
                    data = {'encryption_key':trans_key, 'type':'ios'}
                    r = requests.post(url = base_url, data= data)
                    if r.status_code == 200:
                        try:
                            response = r.json()
                            if response['result'] in ['true', True]:
                                dispatcher.utter_message(response['message'])
                            elif response['result'] in ['false', False]:
                                dispatcher.utter_message(response['error'])
                            else:
                                dispatcher.utter_message('Something went wrong.')
                        except:
                            dispatcher.utter_message('Something went wrong.')
                    elif r.status_code == 400:
                        dispatcher.utter_message('Something went wrong, please try again after sometime.')
                    else:
                        dispatcher.utter_message('Something went wrong.')


'''Get "action_weather" data'''
class ActionWeather(FormAction):
    def name(self):
        return 'action_weather'

    @staticmethod
    def required_slots(tracker: Tracker):
        return ["location"]

    def slot_mappings(self):
        return {
            "location":[self.from_entity(entity = 'location', intent = 'ask_weather'),
                self.from_text(not_intent=['reset_bot'])],
            }

    def validate_location(self, value, dispatcher, tracker, domain):
        if value != "":
            api_key = "ce60c6e5bb715a1e344771614895b8c2"
            base_url = "https://api.openweathermap.org/data/2.5/weather?"

            Final_url = base_url + "q=" + value + "&appid=" + api_key + "&units=metric"
    
            weather_data = requests.get(Final_url).json()

            if weather_data["cod"] != "404": 
            
                y = weather_data["main"] 

                current_temperature = y["temp"] 

                pressure = y["pressure"] 

                humidiy = y["humidity"] 
                
                wind = weather_data["wind"]['speed']

                z = weather_data["weather"] 

                desc = z[0]["description"] 
                response = """ It is {} in {} at this moment. The temperature is {} degree and the wind speed is {} m/s. """. format(desc, value, current_temperature, wind)
                dispatcher.utter_message(response)
                return {"location":value}
            else: 
                dispatcher.utter_message(" City Not Found ") 
        else:
            dispatcher.utter_message('Location cannot be empty.')


    def submit(self, dispatcher, tracker, domain):
        return []
 

'''Get "action_temp" data'''
class ActionTemperature(FormAction):
    def name(self):
        return 'action_temp'

    @staticmethod
    def required_slots(tracker: Tracker):
        return ["location"]

    def slot_mappings(self):
        return {
            "location":[self.from_entity(entity = 'location', intent = 'ask_temperature'),
                self.from_text(not_intent=['reset_bot'])],
            }

    def validate_location(self, value, dispatcher, tracker, domain):

        if value != "":
            api_key = "ce60c6e5bb715a1e344771614895b8c2"
            base_url = "https://api.openweathermap.org/data/2.5/weather?"
    
            Final_url = base_url + "q=" + value + "&appid=" + api_key + "&units=metric"
    
            weather_data = requests.get(Final_url).json()

            if weather_data["cod"] != "404": 
            
                y = weather_data["main"] 

                current_temperature = y["temp"] 

                response = """ The temperature in {} is {} degree currently """. format(value, current_temperature)
                dispatcher.utter_message(response)
                return {"location":value}
            else:
                dispatcher.utter_message("City Not Found ")  
        else:
            dispatcher.utter_message('Location cannot be empty.')

    def submit(self, dispatcher, tracker, domain):
        return []



# class ActionDefaultAskAffirmation(Action):

#     def name(self):
#         return "action_default_ask_affirmation"

#     def __init__(self):
#         self.intent_mapping = {}
#         with open('intent_mapping.csv', newline='', encoding='utf-8') as file:
#             csv_reader = csv.reader(file)
#             for row in csv_reader:
#                 self.intent_mapping[row[0]] = row[1]


#     def run(self, dispatcher, tracker, domain):
#         last_intent_name = tracker.latest_message['intent']['name']
#         # print("trackerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", tracker.current_state())
#         intent_prompt = self.intent_mapping[last_intent_name]
#         buttons = [{'title': 'Yes',
#                     'payload': "/last_intent_name{'last_intent_name'}"},
#                     {'title': 'No',
#                     'payload': "/out_of_scope{'out_of_scope'}"}]
#         # print("ddddddddddddddddddddddddddddddd", buttons)
#         dispatcher.utter_button_message(intent_prompt, buttons = buttons)
#         return []


# class ActionDefaultAskAffirmation(Action):
#     """Default implementation which asks the user to affirm his intent.
#        It is suggested to overwrite this default action with a custom action
#        to have more meaningful prompts for the affirmations. E.g. have a
#        description of the intent instead of its identifier name.
#     """

#     def name(self) -> Text:
#         return 'ACTION_DEFAULT_ASK_AFFIRMATION_NAME'

#     async def run(
#         self,
#         dispatcher,
#         output_channel: "OutputChannel",
#         nlg: "NaturalLanguageGenerator",
#         tracker: "DialogueStateTracker",
#         domain: "Domain",
#     ):
#         intent_to_affirm = tracker.latest_message.intent.get("name")
#         print("intenttttttttttttttttttttttttttt", intent_to_affirm)
#         affirmation_message = f"Do you want to '{intent_to_affirm}'?"

#         buttons = [
#             {"title": "Yes", "payload": "/intent_to_affirm"},
#             {"title": "No", "payload": "/out_of_scope"}]
#         dispatcher.utter_button_message(affirmation_message, buttons = buttons)

#         return []

