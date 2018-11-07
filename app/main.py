from kivy.app import App
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

from kivy.graphics.context_instructions import PopMatrix, PushMatrix
from kivy.graphics import Rotate
from kivy.graphics import Color, Ellipse, Rectangle

from kivy.uix.label import Label

from kivy.uix.behaviors import ToggleButtonBehavior

from random import random, randint 
import os

from kivy.config import Config
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '576')



class IconButton(ToggleButtonBehavior, Image):

    def __init__(self, angle=0, **kwargs):
        super(IconButton, self).__init__(**kwargs)

        self.rotate = Rotate(angle = angle)

        self.canvas.before.add(PushMatrix())
        self.canvas.before.add(self.rotate)
        self.canvas.after.add(PopMatrix())

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

    def update_canvas(self, *args):
        self.rotate.origin = self.center
        

    def on_state(self, widget, value):
        if value == 'down':
            self.source = widget.img_dn
        else:
            self.source = widget.img_up

#lass phaseArrayClass:

class SnapArrayButtonClass:
    def __init__(self):
        self.rbuttons = []
    def newRButton(self, w, h, x, y, size, img_up, img_dn):
        '''
        Images need to be bigger than canvas, so biggger than rotated button
        ''' 
        print(w,h,x,y,size)
        rbutton = RelativeLayout(size_hint=(None, None), 
                                 size=(0.7*w*size/16, 0.7*h*size/9), 
                                 pos=(w*x/16 + 0.15*w*size/16, 
                                      h*y/9  + 0.15*h*size/9 )
                                 )
        btn = IconButton(angle=randint(0,360))
        btn.img_up = img_up
        btn.img_dn = img_dn
        btn.source = img_up
        rbutton.add_widget(btn)
        self.rbuttons.append(rbutton)
        with rbutton.canvas:
            Color(random(), random(), random(), 0.24)
            Rectangle(pos=(0,0), size=rbutton.size)

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
    def populate(self):
        p = IconPositions()
        '''
        p.newSet(0,0,6, 
                 0,0,3,
                 6,3,3,
                 4,6,5,
                 1,6,3,
                 0,9,3,
                 0,12,5,
                 5,8,4)
        '''
        p.newSet(0,0,6, 
                 0,6,3,
                 3,6,3,
                 6,4,5,
                 6,1,3,
                 9,0,3,
                 12,0,4,
                 11,5,4)
        self.newGroup(p)


class TestApp(App):

    def build(self):
        layout = FloatLayout(size=(1024,576))
        print(layout.size, layout.pos)
        
        rbuttons = SnapArrayButtonClass()
        positions = IconPositionsGroup()
        
        x = 0
        y = 0
        for i in os.listdir("../images/signs/")[:8]:
            '''
            rbutton = rbuttons.newRButton(layout.width, 
                                          layout.height,
                                          x*3, y*3,
                                          3,
                                          "../images/signs/" + i,
                                          "../images/signs/invert/"+ i
                                          )
            '''

            rbutton = rbuttons.newRButton(layout.width, 
                                          layout.height,
                                          positions.group[0].config[x].x, 
                                          positions.group[0].config[x].y,
                                          positions.group[0].config[x].size,
                                          "../images/signs/" + i,
                                          "../images/signs/invert/"+ i
                                          )
            


            x = x + 1

            layout.add_widget(rbutton)
        return layout

class MainApp(App):
    def build(self):
        layout = Builder.load_string(src)
        return layout


if __name__ == '__main__':
    TestApp().run()

