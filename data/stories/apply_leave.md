## apply leave + affirm
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
* affirm
  - apply_leave_request
  - reset_slot
  - utter_ask_continue

## apply leave + deny
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
* deny OR cancel_leave
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + ask_cancel + affirm
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* deny OR stop
  - utter_ask_cancel_leave_form
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + ask_cancel + deny + deny
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* deny OR stop
  - utter_ask_cancel_leave_form
* deny OR apply_leave
  - leave_form
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
* deny OR cancel_leave
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + ask_cancel + deny + apply
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* deny OR stop
  - utter_ask_cancel_leave_form
* deny OR apply_leave
  - leave_form
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
* affirm
  - apply_leave_request
  - reset_slot
  - utter_ask_continue

<!-- ## apply leave + interrupt_chitchat + deny
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* deny OR cancel_leave
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + interrupt_chitchat + affirm + deny
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* affirm OR apply_leave
  - leave_form
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
  - utter_apply_leave_values
* deny OR cancel_leave
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + interrupt_chitchat + affirm + apply
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* affirm OR apply_leave
  - leave_form
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
  - utter_apply_leave_values
* affirm
  - apply_leave_request
  - reset_slot
  - utter_ask_continue

## apply leave + ask_cancel + chitchat + deny
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* deny OR stop
  - utter_ask_cancel_leave_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* deny OR cancel_leave
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + ask_cancel + chitchat + affirm + deny
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* deny OR stop
  - utter_ask_cancel_leave_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* affirm OR apply_leave
  - leave_form
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
  - utter_apply_leave_values
* deny OR cancel_leave
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + ask_cancel + chitchat + affirm + apply
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* deny OR stop
  - utter_ask_cancel_leave_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* affirm OR apply_leave
  - leave_form
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
  - utter_apply_leave_values
* affirm
  - apply_leave_request
  - reset_slot
  - utter_ask_continue

## apply leave + interrupt_chitchat + interrupt_chitchat + deny
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* deny OR cancel_leave
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + interrupt_chitchat + interrupt_chitchat + affirm + deny
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* affirm OR apply_leave
  - leave_form
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
  - utter_apply_leave_values
* deny OR cancel_leave
  - reset_slot
  - utter_cancel_leave
  - utter_ask_continue

## apply leave + interrupt_chitchat + interrupt_chitchat + affirm + apply
* apply_leave
  - leave_form
  - form{"name": "leave_form"}
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* ask_weather OR ask_builder OR ask_howdoing OR ask_whoisit OR ask_isbot OR ask_howold OR ask_languagesbot OR ask_wherefrom OR ask_whoami OR slang OR telljoke OR ask_whatismyname OR ask_howbuilt OR ask_whatspossible OR out_of_scope
  - action_chitchat
  - utter_ask_continue_leave_form
* affirm OR apply_leave
  - leave_form
  - form{"name": null}
  - day_date_parser
  - apply_leave_values
  - utter_apply_leave_values
* affirm
  - apply_leave_request
  - reset_slot
  - utter_ask_continue -->
