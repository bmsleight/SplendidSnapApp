
from kivy.support import install_twisted_reactor
install_twisted_reactor()


from kivy.app import App
from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Rotate
from kivy.graphics.context_instructions import PopMatrix, PushMatrix
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget

from kivy.uix.settings import Settings


import time
from random import random, randint
import os
from time import sleep
import threading


from settingsjson import settings_json
from highscores import HighScores
from cardarrangement import *
from settingscrolloptions import SettingScrollOptions
from helpscreen import HelpScreen

# Added Autobahn
from kivy.factory import Factory
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.wamp import ApplicationRunner
from twisted.internet.defer import inlineCallbacks



class ClockRect(Widget):
    def __init__(self, **kwargs):
        super(ClockRect, self).__init__(**kwargs)
        self.timer = Clock
        self.dseconds = 0
    def start(self):
        self.event = self.timer.schedule_interval(self.update, 1/10.)
    def pause(self):
        self.event.cancel()
        r = self.dseconds
        self.dseconds = 0
        return r
    def update(self, *args):
        self.dseconds = self.dseconds + 1


class SnapRelativeLayout(RelativeLayout):
    def __init__(self, **kwargs):
        super(FloatLayout, self).__init__(**kwargs)

class IconButton(ToggleButtonBehavior, Image):

    def __init__(self, angle=0, **kwargs):
        super(IconButton, self).__init__(**kwargs)
        self.rotate = Rotate(angle = angle)
        self.canvas.before.add(PushMatrix())
        self.canvas.before.add(self.rotate)
        self.canvas.after.add(PopMatrix())
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.guess = None
    def update_canvas(self, *args):
        self.rotate.origin = self.center
    def on_state(self, widget, value):
        # Better way to access SnapRelativeLayout ? than 
        #  self.parent.parent.parent ?
        # Tied too much into how kv is...
        screen = self.parent.parent.parent.parent.parent
        
        if value == 'down':
            self.source = "./assets/logo.png"
            guess_result = screen.newGuess(self.card_number)
        else:
            self.source = widget.img_up
            guess_result = screen.clearGuess(self.card_number)
        
        # Got Sucess or Now Guess from buttons
        if guess_result == "New Guess":
            pass
        else:
            if guess_result == "Success!":
                remote_set = screen.manager.get_screen('cards').remote_set
                total_correct_return = screen.removeCardsFromFLayer()
                if remote_set:
                    # Remote call
                    screen.manager.get_screen('results').ids['button'].disabled = True
                    screen.parent.get_screen('results').labelText = "Winner!"
                    screen.manager.get_screen('smpgame').multiMatch()
                else:
                    # Local sucess
                    if total_correct_return == -1:
                        # Finished game - i.e. at 10 correct
                        screen.manager.current = 'notify'
                    else:
                        if total_correct_return == 1:
                            matches_text = " You have made the first" + \
                                           " correct match"
                        else:
                            matches_text = " You have made " + \
                                            str(total_correct_return) + \
                                            " correct matches"
                        screen.parent.get_screen('results').labelText = \
                                                            guess_result + \
                                                            matches_text
                            
                        screen.manager.current = 'results'
            else:
                screen.parent.get_screen('results').labelText = \
                                                        guess_result + \
                                " Change at least one to a make a match"
                screen.manager.current = 'results'
            

class SnapArrayButtonClass:
    def __init__(self):
        self.rbuttons = []
    def newRButton(self, w, h, x, y, size, img_up, card_number, 
                   positional_offset=0):
        '''
        Images need to be bigger than canvas, so biggger than rotated button
        ''' 
        rbutton = RelativeLayout(size_hint=(None, None), 
                                 size=(0.7*w*size/16, 0.7*h*size/9), 
                                 pos=(w*x/16 + 0.15*w*size/16, 
                                      h*y/9  + 0.15*h*size/9 )
                                 )
        btn = IconButton(angle=randint(0,360))
        btn.img_up = img_up
        btn.img_dn = "./assets/logo.png"
        btn.source = img_up
        btn.card_number = card_number
        rbutton.add_widget(btn)
        self.rbuttons.append(rbutton)
        return rbutton
    def resetAllButtons(self):
        for btn in self.rbuttons:
            btn.children[0].state = 'normal'


class IntroScreen(Screen):
    pass

class CardsScreen(Screen):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.new_set = True
        self.guess = "None"
        self.total_correct = 0
        self.total_dseconds = 0
        self.remote_set = {}
        self.left_buttons = None
        self.right_buttons = None
    def newGuess(self, guess):
        if self.guess == "None":
            self.guess = guess
            return "New Guess"
        else:
            if self.guess == guess:
                text = "Success!"
            else:
                text = "Failure!"
                print("Reset All Buttons")
                
                self.left_buttons.resetAllButtons()
                self.right_buttons.resetAllButtons()
            self.guess = "None"
            return text
    def clearGuess(self, guess):
        self.guess = "None"
        return "New Guess"
    def clockStart(self):
        clock = getattr(self.ids, "clock")
        clock.start()
    def clockStop(self):
        clock = getattr(self.ids, "clock")
        self.total_dseconds = self.total_dseconds + clock.pause()
    def strTotal(self):
        return "Total time: " + str(self.total_dseconds/10.) + "s"
    def populateCards(self):
        if self.new_set:
            # clear old cards
            fl = getattr(self.ids, "SnapFloatLayoutLeft")
            fl.clear_widgets()
            fl = getattr(self.ids, "SnapFloatLayoutRight")
            fl.clear_widgets()

            # Get size informatoin 
            (max_x, max_y) = Window.size
            max_x = (max_x/16) * 8 *2 # Allow for wierd aspect ratios

            # Get set of cards for left and right
            cards = simple_card_list(7)
            if self.remote_set:
                left_card = self.remote_set['left_card']
                right_card = self.remote_set['right_card']
                oi = self.remote_set['oi']
                use_group_l = self.remote_set['use_group_l']
                use_group_r = self.remote_set['use_group_r']
            else:
                left_card = randint(0,len(cards)-1)
                right_card = randint(0,len(cards)-1)
                while left_card == right_card:
                    right_card = randint(0,len(cards)-1)
                oi = App.get_running_app().config.get('main_settings', 
                                                      'optionsimages')
                use_group_l = None
                use_group_r = None
            # Set left and rright
            self.left_buttons = self.addCardsToFLayer( \
                                  "SnapFloatLayoutLeft", max_x, max_y, 
                                  "./images/" + oi + "/", 
                                  cards[left_card],
                                  use_group_l
                                  )
            
            self.right_buttons = self.addCardsToFLayer( \
                                   "SnapFloatLayoutRight", max_x, max_y, 
                                  "./images/" + oi + "/", 
                                  cards[right_card],
                                  use_group_r
                                  )
        self.new_set = False

    def addCardsToFLayer(self, layerId, max_x, max_y,
                        img_location,
                        card,
                        use_group_i,
                        positional_offset=0):
        fl = getattr(self.ids, layerId)

        # Make buttons and get button positions
        rbuttons = SnapArrayButtonClass()
        positions = IconPositionsGroup()
        use_group = positions.getGroup(use_group_i)

         
        images = os.listdir(img_location)
        for i in range(0,8):
            rbutton = rbuttons.newRButton(max_x, 
                                          max_y,
                                          use_group.config[i].x, 
                                          use_group.config[i].y,
                                          use_group.config[i].size,
                                          img_location + images[card[i]],
                                          card[i]
                                          )
            fl.add_widget(rbutton)
        return rbuttons
        
    def removeCardsFromFLayer(self):
        total_correct_return = 0
        self.total_correct = self.total_correct + 1
        rt_win = int(App.get_running_app().config.get('main_settings', 
                                                      'totaltowinsolo'))
        if self.total_correct >= rt_win:
            # Done! 
            #Reset counters
            self.manager.current = 'notify'
            #Highscores
            if rt_win == 10:
                self.manager.get_screen('notify').labelText = self.strTotal()
                c = App.get_running_app().config.get('main_settings', 
                                                     'optionsimages')
                highscores = HighScores()
                highscores.newScore(self.total_dseconds, c)
            else:
                self.manager.get_screen('notify').labelText = \
                      self.strTotal() + \
                      " (need 10 rounds for a high score)"
            self.total_correct = 0
            total_correct_return = -1
            self.total_dseconds = 0
        else:
            total_correct_return = self.total_correct
        self.new_set = True
        self.populateCards()
        return total_correct_return

class NotifyScreen(Screen):
    labelText = StringProperty('My label')
    time_str = StringProperty('Boo')

    

class ResultsScreen(Screen):
    labelText = StringProperty('My label')


class HighScoresScreen(Screen):
    labelText = StringProperty('My label')
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.labelText = 'My labeaal'
    def populateHS(self):
        highscores = HighScores()
        self.labelText = highscores.__str__()
    def clearHS(self):
        pass


class MultiMenuScreen(Screen):
    pass


class JoinMultiPlayerGameScreen(Screen):
    game_key_text = StringProperty()
    def __init__(self, **kwargs):
        super(JoinMultiPlayerGameScreen, self).__init__(**kwargs)
        self.game_key_text = '123456'

    def joinGameKey(self):
        print(self.game_key_text)
        print(App.get_running_app().root.get_screen('smpgame').game_key )
        App.get_running_app().root.get_screen('smpgame').game_key = str(self.game_key_text)
        App.get_running_app().root.current = 'smpgame'


class GameWampComponent(ApplicationSession):
    """
    A WAMP application component which is run from the Kivy UI.
    """
    def subto(self, uicallback, short_url, game_key):
        sub_url = short_url + str(game_key)
        print("Subscribe to: ", sub_url)
        self.subscribe(uicallback, sub_url)

    def onJoin(self, details):
        print("session ready", self.config.extra)

        # get the Kivy UI component this session was started from
        ui = self.config.extra['ui']
        ui.on_session(self)
        self.subto(ui.on_join_message, 
                   u'org.splendidsnap.app.game.joined.',
                   self.config.extra['game_key']
                   )
        self.subto(ui.on_start_message, 
                   u'org.splendidsnap.app.game.start.',
                   self.config.extra['game_key']
                   )
        self.subto(ui.on_card_message, 
                   u'org.splendidsnap.app.game.card.',
                   self.config.extra['game_key']
                   )
        self.subto(ui.on_winner_message,
                   u'org.splendidsnap.app.game.winner.',
                   self.config.extra['game_key']
                   )
        self.subto(ui.on_end_message,
                   u'org.splendidsnap.app.game.end.',
                   self.config.extra['game_key']
                   )
#        
        print("Subs done")

class StartMultiPlayerGameScreen(Screen):
    server_messages = StringProperty('Contacting server ...')
    game_key_label = StringProperty('Game Key: 123456')
    button_txt = StringProperty('')
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.session = None
        self.game_key_label = "Game Key: Waiting"
        self.server_messages = ""
        self.button_txt = ""
        self.game_key = None
        self.timer = Clock
        self.trying_to_connect = False
        self.new_game = False
        self.p_name = ""
        self.winner = False

    def on_enter(self):
        self.event = self.timer.schedule_interval(self.tick,1.)
        if self.game_key:
            pass
        else:
            self.getNewGameKey()
        if self.session:
            pass
        else:
            self.connectToGame()

    def tick(self, *args):
        if self.session:
            return False
        else:
            self.server_messages += "."

    def startGame(self, *args):
        self.session.call(u'org.splendidsnap.app.game.startpush', 
                          self.game_key)
        self.session.call(u'org.splendidsnap.app.game.cardpush', 
                          self.game_key)

    def delayNewCard(self):
        sleep(5)
        self.winner = False
        self.manager.get_screen('results').ids['button'].disabled = False
        if self.session:
            self.session.call(u'org.splendidsnap.app.game.cardpush', 
                          self.game_key)

    def multiMatch(self):
        details = {}
        details['game_key'] = self.game_key
        details['player_name'] = self.p_name
        if self.session:
            self.session.call(u'org.splendidsnap.app.game.matchpush', 
                          details)
        self.winner = True
        # What a headache! - Buy the the GUI update!
        threading.Thread(target = self.delayNewCard).start()
        
    def on_start_message(self):
        print("I am starting .....")

    def on_card_message(self, remote_set):
        print("remote_set ", remote_set)
        self.manager.get_screen('cards').remote_set = remote_set
        self.manager.get_screen('cards').new_set = True        
        self.manager.current = 'cards'

    def on_winner_message(self, details):
        self.manager.get_screen('results').ids['button'].disabled = True
        print(details, details['player_name'])
        if not self.winner:
            self.manager.get_screen('results').labelText = "Loser!"  +\
                                                         "\nWinner " +\
                                            str(details['player_name'])
        self.manager.current = 'results'

    def on_end_message(self, game):
        # Un subcribe
        # disconnect
        # send results to ...
        # option for replay w/out entering number
        print("The End")
        self.manager.current = 'notify'
        

    def getNewGameKey(self):
        game_key = randint(100000, 999999)
        self.game_key = game_key
        self.game_key_label = "Game Key: " + str(game_key)
        self.new_game = True

    def connectToGame(self):
        if self.session:
            pass
        else:
            if self.trying_to_connect:
                pass
            else:
                self.trying_to_connect = True
                self.server_messages += "Contacting server ... "
                url, realm = u"ws://localhost:8080/ws", u"SpledidSnapApp"
                self.server_messages += url 
                runner = ApplicationRunner(url=url,
                                           realm=realm,
                                           extra=dict(ui=self, 
                                                      game_key=self.game_key))
                runner.run(GameWampComponent, start_reactor=False)


    def on_join_message(self, player_name):
        self.server_messages += " " + player_name + " joined \n"
        print("on_join_message")


    @inlineCallbacks
    def on_session(self, session):
        self.server_messages += " Connected to server!"
        self.session = session
        self.trying_to_connect = False
        self.p_name = App.get_running_app().config.get('main_settings', 
                                                  'playername')
        if self.new_game:
            rounds = App.get_running_app().config.get('main_settings', 
                                                  'totaltowinsolo')
            oi = App.get_running_app().config.get('main_settings', 
                                                  'optionsimages')                                                  
            yield self.session.call(u'org.splendidsnap.app.game.newgame', 
                              self.game_key, rounds, oi, self.p_name)
            self.button_txt = "Start Game with Current Players"
            self.ids['nextbutton'].disabled = False
            self.ids['nextbutton'].bind(on_press=self.startGame)

        else:
            # join exisiting game            
            yield self.session.call(u'org.splendidsnap.app.game.joingame',
                              self.game_key, self.p_name)
            self.button_txt = "Waiting for game to start"
            self.ids['nextbutton'].disabled = True
            self.game_key_label = "Game Key: " + str(self.game_key)

        self.server_messages += "\nWaiting for more players.\n"



class MyScreenManager(ScreenManager):
    blue   = ListProperty([0.19, 0.39, 0.78, 1])
    orange = ListProperty([1, 0.61, 0, 1])
    def go_back(self, screen_name):
        if screen_name == 'root':
            exit()
        else:
            self.current = 'intro'


class SplendidSnapApp(App):
    def build(self):
        self.use_kivy_settings = False
        self.bind(on_start=self.post_build_init)
        return Builder.load_file('SplendidSnap.kv')

    def post_build_init(self, *args):
        win = Window
        win.bind(on_keyboard=self.my_key_handler)
        
    def my_key_handler(self, window, keycode1, keycode2, text, 
                       modifiers):
        if keycode1 in [27, 1001]:
            self.root.go_back(screen_name=self.root.current)
            return True
        return False


    def build_config(self, config):
        config.setdefaults('main_settings', {
            'totaltowinsolo': 10,
            'optionsimages': 'doodle',
            'playername': "Player_" + str(randint(100000, 999999))
            })

    def build_settings(self, settings):
        Setting = Settings()
        settings.register_type('scrolloptions', SettingScrollOptions)        
        settings.add_json_panel('Main Settings',
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section,
                         key, value):
        if section == 'main_settings' and key == 'optionsimages':
            self.root.get_screen('cards').new_set = True

if __name__ == "__main__":
    SplendidSnapApp().run()
    
