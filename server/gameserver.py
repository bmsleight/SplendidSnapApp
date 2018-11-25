###############################################################################
##
##  Copyright (C) 2014, Tavendo GmbH and/or collaborators. All rights reserved.
##
##  Redistribution and use in source and binary forms, with or without
##  modification, are permitted provided that the following conditions are met:
##
##  1. Redistributions of source code must retain the above copyright notice,
##     this list of conditions and the following disclaimer.
##
##  2. Redistributions in binary form must reproduce the above copyright notice,
##     this list of conditions and the following disclaimer in the documentation
##     and/or other materials provided with the distribution.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
##  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
##  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
##  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
##  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
##  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
##  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
##  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
##  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
##  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
##  POSSIBILITY OF SUCH DAMAGE.
##
###############################################################################

from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession

import time

class MultiplayerGameOptions:
    def __init__(self, game_key, rounds, optionsimages):
        self.game_key = game_key
        self.rounds = rounds
        self.optionsimages = optionsimages
        self.players = []
        self.start = False
        self.current_round = 0

class MultiplayerGames:
    def __init__(self):
        self.games = []
    def addGame(self, game):
        self.games.append(game)
    def joinGame(self, game_key, player_name):
        return_g = None
        for g in self.games:
            if g.game_key == game_key:
                return_g = g
                g.players.append(player_name)
                break
        return return_g
    def startGame(self, game_key):
        return_sg = False
        for g in self.games:
            if int(g.game_key) == int(game_key):
                g.start =  True
                return_sg = True
                break
        return return_sg


class GamesBackend(ApplicationSession):

    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.init()
        self.games = MultiplayerGames()
        

    def init(self):
        pass

    @wamp.register(u'org.splendidsnap.app.game.newgame')
    def getNewGame(self, game_key, rounds, optionsimages, player_name):
        game = MultiplayerGameOptions(game_key, rounds, optionsimages)
        game.players.append(player_name)
        self.games.addGame(game)
        print(game_key, rounds, optionsimages, player_name)

    @wamp.register(u'org.splendidsnap.app.game.joingame')
    def getJoinGame(self, game_key, player_name):
        game = self.games.joinGame(int(game_key), player_name)
        if game:
            publish_game_joined = u'org.splendidsnap.app.game.joined.'+\
                                  str(game_key)
            print("Publish to", publish_game_joined)
            self.publish(publish_game_joined, player_name)
            print("Joined :", game_key, player_name)
        else:
            print("Game key not valid") 

    @wamp.register(u'org.splendidsnap.app.game.startpush')
    def pushStartGame(self, game_key):
        game = self.games.startGame(int(game_key))
        if game:
            publish_game_start = u'org.splendidsnap.app.game.start.'+\
                                  str(game_key)
            print("Publish to", publish_game_start)
            self.publish(publish_game_start)
            print("start :", game_key)
        else:
            print("Game key not valid") 


    @inlineCallbacks
    def onJoin(self, details):
        res = yield self.register(self)
        print("VotesBackend: {} procedures registered!".format(len(res)))
