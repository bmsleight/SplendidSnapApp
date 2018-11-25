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

from cardarrangement import *
from random import random, randint


class MultiplayerGameOptions:
    def __init__(self, game_key, rounds, optionsimages):
        self.game_key = game_key
        self.rounds = rounds
        self.optionsimages = optionsimages
        self.players = []
        self.start = False
        self.current_round = 0
        self.winners = []
        icons = IconPositionsGroup()
        self.max_positions = icons.possiblePositions() - 1
    def cardSet(self):
        # All players get the same card set
        remote_set = {}
        cards = simple_card_list(7)
        remote_set['left_card'] = randint(0,len(cards)-1)
        remote_set['right_card'] = randint(0,len(cards)-1)
        while remote_set['left_card'] == remote_set['right_card']:
            remote_set['right_card'] = randint(0,len(cards)-1)
        remote_set['use_group_l'] = randint(0,self.max_positions)
        remote_set['use_group_r'] = randint(0,self.max_positions)
        remote_set['oi'] = self.optionsimages
        # A soem point update curent_round
        return remote_set


class MultiplayerGames:
    def __init__(self):
        self.games = []
    def addGame(self, game):
        self.games.append(game)
    def getCard(self, game_key):
        return_g = None
        for g in self.games:
            if g.game_key == game_key:
                return_g = g
                break
        return return_g
        
    def joinGame(self, game_key, player_name):
        return_g = self.getCard(game_key)
        if return_g:
            return_g.players.append(player_name)
        return return_g
    def startGame(self, game_key):
        return_sg = False
        return_g = self.getCard(game_key)
        if return_g:
            return_g.start =  True
            return_sg = True
        return return_sg
    def nextCard(self, game_key):
        remote_set = None
        return_g = self.getCard(game_key)
        if return_g:
            remote_set = return_g.cardSet()
        return remote_set


class GamesBackend(ApplicationSession):

    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.init()
        self.games = MultiplayerGames()
        

    def init(self):
        pass


    def printPublish(self, purl, r_object=None):
        print("Publish to ", purl)
        self.publish(purl, r_object)
        print("Joined ", purl, " Data :", r_object)

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
            self.printPublish(publish_game_joined, player_name)
        else:
            print("Game key not valid") 

    @wamp.register(u'org.splendidsnap.app.game.startpush')
    def pushStartGame(self, game_key):
        game = self.games.startGame(int(game_key))
        if game:
            publish_game_start = u'org.splendidsnap.app.game.start.'+\
                                  str(game_key)
            self.printPublish(publish_game_start)
        else:
            print("Game key not valid") 


    @wamp.register(u'org.splendidsnap.app.game.cardpush')
    def pushNextCard(self, game_key):
        remote_set = self.games.nextCard(game_key)
        if remote_set:
            # nextCard
            publish_game_card = u'org.splendidsnap.app.game.card.'+\
                                  str(game_key)
            self.printPublish(publish_game_card, remote_set)
        else:
            pass


    @inlineCallbacks
    def onJoin(self, details):
        res = yield self.register(self)
        print("VotesBackend: {} procedures registered!".format(len(res)))
