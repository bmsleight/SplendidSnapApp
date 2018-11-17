
import json

settings_json = json.dumps([
    {'type': 'title',
     'title': 'Splendid App Settings'},
    {'type': 'numeric',
     'title': 'Rounds',
     'desc': 'Number of correct matches per solo game',
     'section': 'main_settings',
     'key': 'totaltowinsolo'},
    {'type': 'options',
     'title': 'Cards',
     'desc': 'Choose which set of cards',
     'section': 'main_settings',
     'key': 'optionsimages',
     'options': ['traffic', 'doodle', 'food', 
                 'flags', 'hipster', 'monster', 
                'railway', 'round', 'social']},
     ])

  
