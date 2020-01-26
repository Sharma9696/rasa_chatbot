## cancel ar + affirm/deny/norecord
* cancel_ar_request
  - show_pending_ar_request
  - cancel_ar_remarks
  - form{"name": "cancel_ar_remarks"}
  - form{"name": null}
  - cancel_pending_ar_request
  - reset_slot
  - utter_ask_continue

## cancel ar + interrupt + affirm
* cancel_ar_request
  - show_pending_ar_request
  - cancel_ar_remarks
  - form{"name": "cancel_ar_remarks"}
* deny OR stop
  - utter_ask_continue_cancel_ar
* affirm
  - action_deactivate_form
  - form{"name": null}
  - utter_not_cancel_ar
  - reset_slot
  - utter_ask_continue

## cancel ar + interrupt + deny + affirm/deny
* cancel_ar_request
  - show_pending_ar_request
  - cancel_ar_remarks
  - form{"name": "cancel_ar_remarks"}
* deny OR stop
  - utter_ask_continue_cancel_ar
* deny
  - cancel_ar_remarks
  - form{"name": null}
  - cancel_pending_ar_request
  - reset_slot
  - utter_ask_continue