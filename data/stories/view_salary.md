## view salary + without slot
* get_salary
  - company_for_salary
  - salary_form
  - form{"name": "salary_form"}
  - form{"name": null}
  - get_salary_details
  - reset_slot
  - utter_ask_continue

## view salary + deny + deny
* get_salary
  - company_for_salary
  - salary_form
  - form{"name": "salary_form"}
* deny OR stop
  - utter_ask_stop_view_salary
* deny OR get_salary
  - salary_form
  - form{"name": null}
  - get_salary_details
  - reset_slot
  - utter_ask_continue

## view salary + deny + affirm
* get_salary
  - company_for_salary
  - salary_form
  - form{"name": "salary_form"}
* deny OR stop
  - utter_ask_stop_view_salary
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_ask_continue
