from kivy.app import App
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup

from kivy.graphics.context_instructions import PopMatrix, PushMatrix
from kivy.graphics import Rotate
from kivy.graphics import Color, Ellipse, Rectangle

from kivy.uix.label import Label

from kivy.uix.behaviors import ToggleButtonBehavior

from random import random, randint 
import os
from time import sleep

from kivy.config import Config
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '576')




class SnapFloatLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(FloatLayout, self).__init__(**kwargs)
        self.guess = "None"
    def newGuess(self, guess):
        if self.guess == "None":
            self.guess = guess
            return "New Guess"
        else:
            if self.guess == guess:
                text = "Sucess!"
            else:
                text = "Failure!"
            self.guess = "None"
            return text
            

    def clearGuess(self, guess):
        self.guess = "None"
        return "New Guess"


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
        app= App.get_running_app()
        

        if value == 'down':
            self.source = widget.img_dn
            guess_result = app.root.newGuess(self.card_number)        
        else:
            self.source = widget.img_up
            guess_result = app.root.clearGuess(self.card_number)        
        if guess_result == "New Guess":
            pass
        else:
            popup = Popup(title='Splendid Snap App',
                      content=Label(text=guess_result), auto_dismiss=True)
            popup.bind(on_touch_down=popup.dismiss)
            popup.open() 


class SnapArrayButtonClass:
    def __init__(self):
        self.rbuttons = []
    def newRButton(self, w, h, x, y, size, img_up, img_dn, card_number):
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
        btn.img_dn = img_dn
        btn.source = img_up
        btn.card_number = card_number
        rbutton.add_widget(btn)
        self.rbuttons.append(rbutton)
#        with rbutton.canvas:
#            Color(random(), random(), random(), 0.24)
#            Rectangle(pos=(0,0), size=rbutton.size)

        return rbutton


class IconPosition:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size        

class IconPositions:
    def __init__(self):
        self.config = []
    def newPosition(self, x, y, size):
        p = IconPosition(x,y,size)
        self.config.append(p)
    def newSet(self, x1, y1, size1, 
                     x2, y2, size2, 
                     x3, y3, size3, 
                     x4, y4, size4, 
                     x5, y5, size5, 
                     x6, y6, size6, 
                     x7, y7, size7, 
                     x8, y8, size8):
        self.newPosition(x1,y1,size1)
        self.newPosition(x2,y2,size2)
        self.newPosition(x3,y3,size3)
        self.newPosition(x4,y4,size4)
        self.newPosition(x5,y5,size5)
        self.newPosition(x6,y6,size6)
        self.newPosition(x7,y7,size7)
        self.newPosition(x8,y8,size8)
    def positions(self):
        return self.config
    
class IconPositionsGroup:
    def __init__(self):
        self.group = []
        self.populate()
    def newGroup(self, iconPositions):
        self.group.append(iconPositions)
    def groups(self):
        return self.group
    def randomGroup(self):
        i = randint(0,len(self.group)-1)
        return self.group[i]
    def populate(self):
        p = IconPositions()
        p.newSet(0,5,4, 
                 6,7,2,
                 4,6,2,
                 5,3,3,
                 2,2,3,
                 5,1,2,
                 0,1,2,
                 3,0,2)
        self.newGroup(p)
        p = IconPositions()
        p.newSet(0,0,4, 
                 5,0,3,
                 0,6,3,
                 1,4,2,
                 4,3,2,
                 3,5,2,
                 3,7,2,
                 5,5,2)
        self.newGroup(p)
        p = IconPositions()
        p.newSet(0,0,3, 
                 0,6,3,
                 5,6,3,
                 5,0,3,
                 2,3,3,
                 3,1,2,
                 3,6,2,
                 5,3,2)
        self.newGroup(p)
        p = IconPositions()
        p.newSet(0,0,3, 
                 2,3,4,
                 3,0,3,
                 6,3,2,
                 6,7,2,
                 3,7,2,
                 0,7,2,
                 0,5,2)
        self.newGroup(p)


#http://stackoverflow.com/questions/6240113/what-are-the-mathematical-computational-principles-behind-this-game
def simple_card_list(p):
    cards = []
    for i in range(p):
        pictures=[]
        for j in range(p):
            pictures.append(i * p + j)
        pictures.append(p*p)
        cards.append(pictures)
    for i in range(p):
        for j in range(p):
            pictures=[]
            for k in range(p):
                pictures.append(k * p + (j + i * k) % p)
            pictures.append(p * p + 1 + i)
            cards.append(pictures)
     
    pictures=[]
    for i in range(p+1):
        pictures.append(p * p + i)
    cards.append(pictures)
    return cards, p * p + p +1

    

class TestApp(App):

    def build(self):
        layout = SnapFloatLayout(size=(1024,576))

        rbuttons = SnapArrayButtonClass()
        positions = IconPositionsGroup()
        
        cards, num_pictures = simple_card_list(7)
        left_card = randint(0,len(cards)-1)
        right_card = randint(0,len(cards)-1)
        while left_card == right_card:
            right_card = randint(0,len(cards))
        card = cards[left_card]
        
        index = 0
        randomGroup = positions.randomGroup()
        images = os.listdir("../images/signs/")
        for i in range(0,8):
            rbutton = rbuttons.newRButton(layout.width, 
                                          layout.height,
                                          randomGroup.config[index].x, 
                                          randomGroup.config[index].y,
                                          randomGroup.config[index].size,
                                          "../images/signs/" + images[card[i]],
                                          "../images/signs/invert/"+ images[card[i]],
                                          card[i]
                                          )
            index = index + 1
            layout.add_widget(rbutton)

        index = 0
        randomGroup = positions.randomGroup()
        card = cards[right_card]
        for i in range(0,8):
            rbutton = rbuttons.newRButton(layout.width, 
                                          layout.height,
                                          randomGroup.config[index].x+8, 
                                          randomGroup.config[index].y,
                                          randomGroup.config[index].size,
                                          "../images/signs/" + images[card[i]],
                                          "../images/signs/invert/"+ images[card[i]],
                                          card[i]
                                          )
            index = index + 1
            layout.add_widget(rbutton)


        return layout


if __name__ == '__main__':
    TestApp().run()

