
import json

settings_json = json.dumps([
    {'type': 'title',
     'title': 'Splendid App Settings'},
    {'type': 'string',
     'title': 'Player Name',
     'desc': 'Set you play name for Multi-player',
     'section': 'main_settings',
     'key': 'playername'},
    {'type': 'numeric',
     'title': 'Rounds',
     'desc': 'Number of correct matches per solo game',
     'section': 'main_settings',
     'key': 'totaltowinsolo'},
    {'type': 'scrolloptions',
     'title': 'Cards',
     'desc': 'Choose which set of cards',
     'section': 'main_settings',
     'key': 'optionsimages',
     'options': ['traffic', 'doodle',  
                 'flags', 'hipster', 'monster', 
                'railway', 'round', 'social']},
     ])

  
