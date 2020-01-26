## apply ar + apply
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
  - form{"name": null}
  - apply_ar_values
* affirm
  - apply_ar_request
  - reset_slot
  - utter_ask_continue

## apply ar + deny
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
  - form{"name": null}
  - apply_ar_values
* deny
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + ask_cancel + affirm
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* deny OR stop
  - utter_ask_cancel_ar_form
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + ask_cancel + deny + deny
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* deny OR stop
  - utter_ask_cancel_ar_form
* deny OR apply_ar
  - ar_form
  - form{"name": null}
  - apply_ar_values
* deny
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + ask_cancel + deny + apply
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* deny OR stop
  - utter_ask_cancel_ar_form
* deny OR apply_ar
  - ar_form
  - form{"name": null}
  - apply_ar_values
* affirm
  - apply_ar_request
  - reset_slot
  - utter_ask_continue

<!-- ## apply ar + interrupt_chitchat + deny
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* deny
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + interrupt_chitchat + affirm + deny
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* affirm OR apply_ar
  - ar_form
  - form{"name": null}
  - apply_ar_values
  - utter_ar_details
* deny
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + interrupt_chitchat + affirm + apply
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* affirm OR apply_ar
  - ar_form
  - form{"name": null}
  - apply_ar_values
  - utter_ar_details
* affirm
  - apply_ar_request
  - reset_slot
  - utter_ask_continue

## apply ar + ask_cancel + chitchat + deny
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* deny OR stop
  - utter_ask_cancel_ar_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* deny
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + ask_cancel + chitchat + affirm + deny
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* deny OR stop
  - utter_ask_cancel_ar_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* affirm OR apply_ar
  - ar_form
  - form{"name": null}
  - apply_ar_values
  - utter_ar_details
* deny
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + ask_cancel + chitchat + affirm + apply
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* deny OR stop
  - utter_ask_cancel_ar_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* affirm OR apply_ar
  - ar_form
  - form{"name": null}
  - apply_ar_values
  - utter_ar_details
* affirm
  - apply_ar_request
  - reset_slot
  - utter_ask_continue

## apply ar + interrupt_chitchat + interrupt_chitchat + deny
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* deny
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + interrupt_chitchat + interrupt_chitchat + affirm + deny
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* affirm OR apply_ar
  - ar_form
  - form{"name": null}
  - apply_ar_values
  - utter_ar_details
* deny
  - reset_slot
  - utter_cancel_ar
  - utter_ask_continue

## apply ar + interrupt_chitchat + interrupt_chitchat + affirm + apply
* apply_ar
  - ar_form
  - form{"name": "ar_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_ar_form
* affirm OR apply_ar
  - ar_form
  - form{"name": null}
  - apply_ar_values
  - utter_ar_details
* affirm
  - apply_ar_request
  - reset_slot
  - utter_ask_continue -->
