## view myteam
* view_myteam
  - get_myteam_list
  - view_team_status
  - form{"name": "view_team_status"}
  - form{"name": null}
  - get_team_details
  - reset_slot
  - utter_ask_continue

## view myteam + deny + deny
* view_myteam
  - get_myteam_list
  - view_team_status
  - form{"name": "view_team_status"}
* stop OR deny
  - utter_ask_stop_myteam
* deny OR stop
  - view_team_status
  - form{"name": null}
  - get_team_details
  - reset_slot
  - utter_ask_continue

## view myteam + deny + affirm
* view_myteam
  - get_myteam_list
  - view_team_status
  - form{"name": "view_team_status"}
* stop OR deny
  - utter_ask_stop_myteam
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_ask_continue