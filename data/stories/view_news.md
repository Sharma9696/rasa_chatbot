## story 1
* getNews
  - get_news
  - form{"name": "get_news"}
  - form{"name": null}
  - reset_slot
  - utter_ask_continue

## story 1 + deny + deny
* getNews
  - get_news
  - form{"name": "get_news"}
* deny OR stop
  - utter_ask_stop_news
* deny OR getNews
  - get_news
  - form{"name": null}
  - reset_slot
  - utter_ask_continue

## story 1 + deny + affirm
* getNews
  - get_news
  - form{"name": "get_news"}
* stop OR deny
  - utter_ask_stop_news
* affirm
  - action_deactivate_form
  - form{"name": null}
  - reset_slot
  - utter_ask_continue

## story 2
* getHeadlines
  - get_headlines
  - form{"name": "get_headlines"}
  - form{"name": null}
  - show_headlines
  - reset_slot
  - utter_ask_continue

## story 2 + deny + deny
* getHeadlines
  - get_headlines
  - form{"name": "get_headlines"}
* stop OR deny
  - utter_ask_stop_headlines
* deny OR getHeadlines
  - get_headlines
  - form{"name": null}
  - show_headlines
  - reset_slot
  - utter_ask_continue

## story 2 + deny + affirm
* getHeadlines
  - get_headlines
  - form{"name": "get_headlines"}
* stop OR deny
  - utter_ask_stop_headlines
* affirm
  - action_deactivate_form
  - form{"name": null}
  - show_headlines
  - reset_slot
  - utter_ask_continue