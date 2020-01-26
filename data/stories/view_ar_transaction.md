## view ar status
* view_ar_transaction
  - utter_getting_ar_status
  - get_ar_request
  - view_ar_status
  - form{"name": "view_ar_status"}
  - form{"name": null}
  - view_ar_request
  - reset_slot
  - utter_ask_continue

## view ar status + deny + deny
* view_ar_transaction
  - utter_getting_ar_status
  - get_ar_request
  - view_ar_status
  - form{"name": "view_ar_status"}
* deny OR stop
  - utter_ask_cancel_view_ar
* deny
  - view_ar_status
  - form{"name": null}
  - view_ar_request
  - reset_slot
  - utter_ask_continue

## view ar status + deny + affirm
* view_ar_transaction
  - utter_getting_ar_status
  - get_ar_request
  - view_ar_status
  - form{"name": "view_ar_status"}
* deny OR stop
  - utter_ask_cancel_view_ar
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_ask_continue