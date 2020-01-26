## cancel leave + affirm/deny/norecord
* cancel_leave
  - get_leave_transaction
  - cancel_leave_remarks
  - form{"name": "cancel_leave_remarks"}
  - form{"name": null}
  - cancel_leave_request
  - reset_slot
  - utter_ask_continue

## cancel leave + interrupt + deny + affirm/deny
* cancel_leave
  - get_leave_transaction
  - cancel_leave_remarks
  - form{"name": "cancel_leave_remarks"}
* deny OR stop
  - utter_ask_continue_cancel_leave
* deny
  - cancel_leave_remarks
  - form{"name": null}
  - cancel_leave_request
  - reset_slot
  - utter_ask_continue

## cancel leave + interrupt + affirm
* cancel_leave
  - get_leave_transaction
  - cancel_leave_remarks
  - form{"name": "cancel_leave_remarks"}
* deny OR stop
  - utter_ask_continue_cancel_leave
* affirm
  - action_deactivate_form
  - form{"name": null}
  - utter_not_cancel_leave
  - reset_slot
  - utter_ask_continue