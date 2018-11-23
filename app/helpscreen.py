from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

class HelpScreen(Screen):
    labelText = StringProperty('My label')

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.labelText = 'My labeaal'

#    labelText = StringProperty('My label')
    def populate(self):
        self.labelText = """Playing snap has never been such splendid \
fun! No need to carry a pack of cards with you. No need to find an \
opponent. You can play whenever, wherever, Splendid!

Choose a set of cards you wish to play with, including transport, \
monsters, or world flags. Many more being added. Watch as a split \
screen appears before you. Find two matching icons to move to the next \
screen.  You won't think there's a match... but there always will be!

Once you click 'start game' a split screen will appear with 8 \
icons on each side. You need to find a matching icon on both sides \
and touch them on the screen.

You won't think there's a match... but there always will be!

        """
