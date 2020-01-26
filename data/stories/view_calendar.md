## view calendar
* view_calendar
 - calendar_date_form
 - form{"name": "calendar_date_form"}
 - form{"name": null}
 - calendar_form
 - form{"name": "calendar_form"}
 - form{"name": null}
 - get_attendance_details
 - reset_slot
 - utter_ask_continue

## view calendar + deny + affirm
* view_calendar
 - calendar_date_form
 - form{"name": "calendar_date_form"}
* stop OR deny
 - utter_ask_stop_calendar
* affirm
 - action_deactivate_form
 - form{"name": null}
 - reset_slot
 - utter_ask_continue

## view calendar + deny + deny
* view_calendar
 - calendar_date_form
 - form{"name": "calendar_date_form"}
* stop OR deny
 - utter_ask_stop_calendar
* deny OR view_calendar
 - calendar_date_form
 - form{"name": null}
 - calendar_form
 - form{"name": "calendar_form"}
 - form{"name": null}
 - get_attendance_details
 - reset_slot
 - utter_ask_continue