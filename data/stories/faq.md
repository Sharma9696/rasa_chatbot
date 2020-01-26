## faq
* faq
  - utter_start_help_desk
  - faq_form
  - form{"name": "faq_form"}
  - form{"name": "null"}
  - user_details
  - send_faq
  - reset_slot
  - utter_ask_continue

## faq + cancel + affirm
* faq
  - utter_start_help_desk
  - faq_form
  - form{"name": "faq_form"}
* deny OR stop
  - utter_stop_faq
* affirm
  - action_deactivate_form
  - form{"name": "null"}
  - user_details
  - reset_slot
  - utter_faq_cancel
  - utter_ask_continue

## faq + cancel + affirm
* faq
  - utter_start_help_desk
  - faq_form
  - form{"name": "faq_form"}
* deny OR stop
  - utter_stop_faq
* deny OR faq
  - faq_form
  - form{"name": "null"}
  - user_details
  - send_faq
  - reset_slot
  - utter_ask_continue