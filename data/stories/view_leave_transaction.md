## view leave transaction
* leave_transaction
  - utter_getting_leave_transaction
  - get_leave_request
  - view_leave_status
  - form{"name": "view_leave_status"}
  - form{"name": null}
  - show_leave_transaction
  - reset_slot
  - utter_ask_continue

## view leave transaction + deny + deny
* leave_transaction
  - utter_getting_leave_transaction
  - get_leave_request
  - view_leave_status
  - form{"name": "view_leave_status"}
* deny OR stop
  - utter_ask_cancel_view_leave
* deny
  - view_leave_status
  - form{"name": null}
  - show_leave_transaction
  - reset_slot
  - utter_ask_continue

## view leave transaction + deny + affirm
* leave_transaction
  - utter_getting_leave_transaction
  - get_leave_request
  - view_leave_status
  - form{"name": "view_leave_status"}
* deny OR stop
  - utter_ask_cancel_view_leave
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_ask_continue
