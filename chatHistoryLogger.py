from rasa.core.tracker_store import TrackerStore
from rasa.core.domain import Domain
from typing import Iterator, Optional, Text, Iterable, Union, Dict
from rasa.core.brokers.event_channel import EventChannel
from rasa.core.trackers import ActionExecuted, DialogueStateTracker, EventVerbosity
from rasa.core import events
from rasa_sdk import Tracker
from rasa_sdk import Action
import base64
import requests
import logging
from datetime import datetime
import chatLogger ## module to write data to json file
logger = logging.getLogger(__name__)
# requests = requests.sessions.Session()
# requests.verify = "Cyberoam_SSL_CA.pem"


class DynamicApi:
    def __init__(self,comp_code,function):
        self.comp_code = comp_code
        self.function = function
    
    def get_api(self):
        comp_code = self.comp_code
        function = self.function
        base_url = "https://"+comp_code+".honohr.com/sapi/Service/dynamicAPIKeys_v2?"
        api_url = base_url+'comp_code='+comp_code+'&api_key=b9317ab4b73bf5bf9a9ccf5a1344bb18'
        encryptedKey = base64.b64encode(api_url.encode('utf-8'))
        prefix = 'abc'
        suffix = 'cde'
        api_key = prefix + str(encryptedKey.decode('utf-8')) + suffix
        api_trans_url = base_url + 'encryption_key=' + api_key + '&type=ios'
        r = requests.get(api_trans_url)
        data = r.json()['api_keys']
        api_key = data[function]
        return api_key


class ActionGetUserName(Action):

    def GetName(self, tracker):

        name = (tracker.current_state())['sender_id']
        # name = '4937acc63a69ae4ac976c9098bf819_mial'
        # name = '9118d7508e68cb81b9dc9007a9bcc6_dev'
        # name = '42436e2f94e9e9fe4a4ea7d7f3a5bf_sequelone'
        access_token, comp_code = name.split('_')
        apiKey = DynamicApi(comp_code,'EMPLOYEE').get_api()
        # apiKey = 'f9496c1b6822510eeef0f6fc8699a67a'
        get_url= 'https://'+comp_code+'.honohr.com/api/EmpInformation/showPersonalData?'
        cal_key = get_url + 'comp_code='+comp_code+'&api_key='+apiKey+'&auth_token='+access_token
        r = requests.get(cal_key)
        user_dict = {}
        if r.status_code == 200:
            try:
                data = r.json()["personal_data"]
                user_dict['emp_code'] = data["Emp_Code"]
                user_dict['emp_name'] = data["Emp_Name"]
            except:
                user_dict['emp_code'] = None
                user_dict['emp_name'] = None
        else:
            pass
        return user_dict

class CustomTrackerStore(TrackerStore):
    """Stores conversation history"""

    def __init__(
        self, domain: Domain,url: Optional[str] = None, event_broker: Optional[EventChannel] = None
    ) -> None: 
        self.store = {}
        super(CustomTrackerStore, self).__init__(domain, event_broker)



    def save(self, tracker: DialogueStateTracker) -> None:
        """Updates and saves the current conversation state"""
        if self.event_broker:
            self.stream_events(tracker)

        ## get the current state data from tracker
        state = tracker.current_state(EventVerbosity.AFTER_RESTART)
        data_dict = {}
        data_dict['user_id'] = state['sender_id']
        data_dict['user_name'] = ActionGetUserName().GetName(tracker)['emp_name']
        data_dict['user_emp_code'] = ActionGetUserName().GetName(tracker)['emp_code']
        try:
            tracker_data = state['events']
            for i in tracker_data:
                # print("trackerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", i)
                data_dict['timestamp'] = (datetime.fromtimestamp(i['timestamp'])).strftime("%Y-%m-%d %H:%M:%S")
                if i['event'] == 'bot':
                    if i['text'] == "Want to explore more? I can help you with all your attendance and leave related queries.":
                        pass
                    else:
                        data_dict['bot_event'] = i['event']
                        data_dict['bot_event_text'] = i['text']
                        data_dict['bot_event_data'] = i['data'] 
                elif i['event'] == 'user':
                    data_dict['user_text'] = i['text']
                    data_dict['user_text_intent'] = i['parse_data']['intent']['name']
                    data_dict['user_text_intent_confidence'] = i['parse_data']['intent']['confidence']
                    data_dict['user_text_entity'] = i['parse_data']['entities']
                elif i['event'] == 'action':
                    if i['name'] not in  ["action_listen", "utter_ask_continue", "reset_slot"]:
                        data_dict['action_event'] = i['event']
                        data_dict['action_event_name'] = i['name']
                    else:
                        pass
                else:
                    pass
        except:
            data_dict['tracker_fail_all_data'] = state

        ## here you can write the code to persist your chat history data, I am saving to json file
        chatLogger.ActionGetCompCode.log(self,data_dict,tracker)

        serialised = CustomTrackerStore.serialise_tracker(tracker)
        self.store[tracker.sender_id] = serialised

    def keys(self):
        return self.store.keys()



    def retrieve(self, sender_id: Text) -> Optional[DialogueStateTracker]:
        """
        Args:
            sender_id: the message owner ID
        Returns:
            DialogueStateTracker
        """
        if sender_id in self.store:
            logger.debug("Recreating tracker for id '{}'".format(sender_id))
            return self.deserialise_tracker(sender_id, self.store[sender_id])
        else:
            logger.debug("Creating a new tracker for id '{}'.".format(sender_id))
            return None



    