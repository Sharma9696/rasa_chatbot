## apply od + affirm 
* apply_od
  - od_form
  - form{"name": "od_form"}
  - form{"name": null}
  - apply_od_values
* affirm
  - apply_od_request
  - reset_slot
  - utter_ask_continue

## apply od + deny 
* apply_od
  - od_form
  - form{"name": "od_form"}
  - form{"name": null}
  - apply_od_values
* deny
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + ask_cancel + affirm
* apply_od
  - od_form
  - form{"name": "od_form"}
* deny OR stop
  - utter_ask_cancel_od_form
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + ask_cancel + deny + deny
* apply_od
  - od_form
  - form{"name": "od_form"}
* deny OR stop
  - utter_ask_cancel_od_form
* deny OR apply_od
  - od_form
  - form{"name": null}
  - apply_od_values
* deny
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + ask_cancel + deny + apply
* apply_od
  - od_form
  - form{"name": "od_form"}
* deny OR stop
  - utter_ask_cancel_od_form
* deny OR apply_od
  - od_form
  - form{"name": null}
  - apply_od_values
* affirm
  - apply_od_request
  - reset_slot
  - utter_ask_continue

<!-- ## apply od + interrupt_chitchat + deny
* apply_od
  - od_form
  - form{"name": "od_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* deny
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + interrupt_chitchat + affirm + deny
* apply_od
  - od_form
  - form{"name": "od_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* affirm OR apply_od
  - od_form
  - form{"name": null}
  - apply_od_values
  - utter_od_details
* deny
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + interrupt_chitchat + affirm + apply
* apply_od
  - od_form
  - form{"name": "od_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* affirm OR apply_od
  - od_form
  - form{"name": null}
  - apply_od_values
  - utter_od_details
* affirm
  - apply_od_request
  - reset_slot
  - utter_ask_continue

## apply od + ask_cancel + chitchat + deny
* apply_od
  - od_form
  - form{"name": "od_form"}
* deny OR stop
  - utter_ask_cancel_od_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* deny
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + ask_cancel + chitchat + affirm + deny
* apply_od
  - od_form
  - form{"name": "od_form"}
* deny OR stop
  - utter_ask_cancel_od_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* affirm OR apply_od
  - od_form
  - form{"name": null}
  - apply_od_values
  - utter_od_details
* deny
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + ask_cancel + chitchat + affirm + apply
* apply_od
  - od_form
  - form{"name": "od_form"}
* deny OR stop
  - utter_ask_cancel_od_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* affirm OR apply_od
  - od_form
  - form{"name": null}
  - apply_od_values
  - utter_od_details
* affirm
  - apply_od_request
  - reset_slot
  - utter_ask_continue

## apply od + interrupt_chitchat + interrupt_chitchat + deny
* apply_od
  - od_form
  - form{"name": "od_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* deny
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + interrupt_chitchat + interrupt_chitchat + affirm + deny
* apply_od
  - od_form
  - form{"name": "od_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* affirm OR apply_od
  - od_form
  - form{"name": null}
  - apply_od_values
  - utter_od_details
* deny
  - reset_slot
  - utter_cancel_od
  - utter_ask_continue

## apply od + interrupt_chitchat + interrupt_chitchat + affirm + apply
* apply_od
  - od_form
  - form{"name": "od_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_od_form
* affirm OR apply_od
  - od_form
  - form{"name": null}
  - apply_od_values
  - utter_od_details
* affirm
  - apply_od_request
  - reset_slot
  - utter_ask_continue -->