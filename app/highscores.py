import datetime
import pickle

class Score:
    def __init__(self, complete_time_ds, cards, date_str=None):
        self.complete_time_ds = complete_time_ds
        self.cards = cards
        if date_str:
            self.date_str = date_str
        else:
            self.date_str = datetime.datetime.today().strftime('%Y-%m-%d')
    def __lt__(self, other):
        return self.complete_time_ds < other.complete_time_ds
    def __str__(self):
        return str(self.complete_time_ds/10.) + \
               "s Using the cards '" + self.cards + \
               "' [" + self.date_str + "]"

class HighScores:
    def __init__(self):
        self.filename = "highscores.p"
        self.scores = []
        self.num = 5
        try: 
            self.load()
        except:
            print("!")
            self.save()
    def newScore(self, complete_time_ds, cards, date_str=None):
        s = Score(complete_time_ds, cards, date_str)
        self.scores.append(s)
        self.scores = sorted(self.scores, reverse=True)[:self.num]
        self.save()
    def load(self):
        with open(self.filename, 'rb') as f:
            self.__dict__.update(pickle.load(f).__dict__)
    def save(self):
        with open(self.filename, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
    def __str__(self):
        r = ""
        n = 1
        for s in self.scores:
            r = r + str(n) + ". " + s.__str__() + "\n"
        return (r)    
    

'''
#class HighScores(self):
    
s = Score("100", "signs")

h =  HighScores()
h.newScore("103", "signs")
h.newScore("100", "signs")
h.newScore("101", "signs")
print(h)

h.save()
h =  HighScores()
print(h)
'''
