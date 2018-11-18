from random import random, randint

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
    def __str__(self):
        r = ""
        for c in self.config:
            r = r + "\n    "
            r = r + str(c.x) + ", " + str(c.y) + ", " + str(c.size) 
        return r
    
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
        print("Group: ", i)
        print("Arrangement: ", self.group[i])
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
                 
        p = IconPositions()
        p.newSet(3,2,5,
                 6,7,2,
                 0,0,3,
                 0,3,3,
                 0,6,3,
                 3,7,2,
                 3,0,2,
                 6,0,2)
        self.newGroup(p)

        p = IconPositions()
        p.newSet(0,0,2,
                 0,2,3,
                 0,5,4,
                 2,0,2,
                 3,3,2,
                 4,5,4,
                 4,0,2,
                 5,2,3)
        self.newGroup(p)

        p = IconPositions()
        p.newSet(0,0,3,
                 5,0,3,
                 5,6,3,
                 0,6,3,
                 4,3,3,
                 1,3,3,
                 3,1,2,
                 3,6,2)
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
