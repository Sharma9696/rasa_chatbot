## story 1
* ask_weather
  - action_weather
  - form{"name": "action_weather"}
  - form{"name": null}
  - reset_slot
  - utter_ask_continue

## story 1 + deny + deny
* ask_weather
  - action_weather
  - form{"name": "action_weather"}
* stop OR deny
  - utter_ask_stop_weather
* deny OR ask_weather
  - action_weather
  - form{"name": null}
  - reset_slot
  - utter_ask_continue

## story 1 + deny + affirm
* ask_weather
  - action_weather
  - form{"name": "action_weather"}
* stop OR deny
  - utter_ask_stop_weather
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_ask_continue

## story 2
* ask_temperature
  - action_temp
  - form{"name": "action_temp"}
  - form{"name": null}
  - reset_slot
  - utter_ask_continue

## story 2 + deny + deny
* ask_temperature
  - action_temp
  - form{"name": "action_temp"}
* deny OR stop
  - utter_ask_stop_temp
* deny OR ask_temperature
  - action_temp
  - form{"name": null}
  - reset_slot
  - utter_ask_continue

## story 2 + deny + affirm
* ask_temperature
  - action_temp
  - form{"name": "action_temp"}
* deny OR stop
  - utter_ask_stop_temp
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_ask_continue
