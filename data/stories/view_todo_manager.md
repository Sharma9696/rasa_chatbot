## view todolist complete story
* view_todo_list
  - get_todo_list
  - detailed_todo_task
  - form{"name": "detailed_todo_task"}
  - form{"name": "null"}
  - get_todo_list_data
  - take_todo_action
  - form{"name": "take_todo_action"}
  - form{"name": "null"}
  - manager_decision_final
  - reset_slot
  - utter_ask_continue

## view todolist + stop + affirm
* view_todo_list
  - get_todo_list
  - detailed_todo_task
  - form{"name": "detailed_todo_task"}
* stop
  - utter_ask_cancel_todo
* affirm
  - action_deactivate_form
  - form{"name": "null"}
  - reset_slot
  - utter_ask_todo_cancelled
  - utter_ask_continue

## view todolist + stop + deny
* view_todo_list
  - get_todo_list
  - detailed_todo_task
  - form{"name": "detailed_todo_task"}
* stop
  - utter_ask_cancel_todo
* deny OR view_todo_list
  - detailed_todo_task
  - form{"name": "null"}
  - get_todo_list_data
  - take_todo_action
  - form{"name": "take_todo_action"}
  - form{"name": "null"}
  - manager_decision_final
  - reset_slot
  - utter_ask_continue

## view todolist + stop + deny + stop + affirm
* view_todo_list
  - get_todo_list
  - detailed_todo_task
  - form{"name": "detailed_todo_task"}
* stop
  - utter_ask_cancel_todo
* deny OR view_todo_list
  - detailed_todo_task
  - form{"name": "null"}
  - get_todo_list_data
  - take_todo_action
  - form{"name": "take_todo_action"}
* stop
  - utter_ask_cancel_todo
* affirm
  - action_deactivate_form
  - form{"name": "null"}
  - reset_slot
  - utter_ask_todo_cancelled
  - utter_ask_continue

## view todolist + stop + deny + stop + deny
* view_todo_list
  - get_todo_list
  - detailed_todo_task
  - form{"name": "detailed_todo_task"}
* stop
  - utter_ask_cancel_todo
* deny OR view_todo_list
  - detailed_todo_task
  - form{"name": "null"}
  - get_todo_list_data
  - take_todo_action
  - form{"name": "take_todo_action"}
* stop
  - utter_ask_cancel_todo
* deny OR view_todo_list
  - take_todo_action
  - form{"name": "null"}
  - manager_decision_final
  - reset_slot
  - utter_ask_continue


## view todolist + stop + affrim
* view_todo_list
  - get_todo_list
  - detailed_todo_task
  - form{"name": "detailed_todo_task"}
  - form{"name": "null"}
  - get_todo_list_data
  - take_todo_action
  - form{"name": "take_todo_action"}
* stop
  - utter_ask_cancel_todo
* affirm
  - action_deactivate_form
  - form{"name": "null"}
  - reset_slot
  - utter_ask_todo_cancelled
  - utter_ask_continue

## view todolist + stop + deny
* view_todo_list
  - get_todo_list
  - detailed_todo_task
  - form{"name": "detailed_todo_task"}
  - form{"name": "null"}
  - get_todo_list_data
  - take_todo_action
  - form{"name": "take_todo_action"}
* stop
  - utter_ask_cancel_todo
* deny OR view_todo_list
  - take_todo_action
  - form{"name": "null"}
  - manager_decision_final
  - reset_slot
  - utter_ask_continue

