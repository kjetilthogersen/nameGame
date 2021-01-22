"""
Simple name game (tournament format) to help decide which name to give the newborn. run with python run.py yourname.
Reads the txt file nameLists/navn.txt which containts the list of all names that enter the tournament
Click the name you like the most, or use left/right arrows. Exit with Esc
will create output folder youname with lists of names that have reached different rounds for further discussion
"""

import arcade
import random
import os
import math
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# These numbers represent "states" that the game can be in.
ROUND = 0
HEAD2HEAD = 1
FINISHED = 2

# Colors
BG_COLOR = arcade.color.BLACK
BG_COLOR2 = arcade.color.WHITE
NUMBERING_COLOR = arcade.color.GRAY


BG_COLOR_ROUND = arcade.color.PINK
TEXT_COLOR_ROUND = arcade.color.PURPLE

BG_COLOR_FINISHED = arcade.color.PINK
TEXT_COLOR_FINISHED = arcade.color.PURPLE

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height, fullscreen = True)
        width, height = self.get_size()
        self.set_viewport(0, width, 0, height)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)


        #Set up folder for saving        
        self.foldername = sys.argv[1]
        os.system("mkdir "+str(self.foldername))

        # Set the background color
        arcade.set_background_color(BG_COLOR)

        # Start 'state' will be showing the first page of instructions.
        self.current_state = ROUND
        namelist = list()

        # Set up list of players and create games (head 2 head).
        f = open("nameLists/navn.txt","r")
        lines = [line.rstrip('\n') for line in open("nameLists/jentenavn.txt")]
        for name in lines:
        	player = Player(name)
        	namelist.append(player)

        random.shuffle(namelist)
        self.list_of_finished_rounds = list()
        
        self.numberOfRounds = math.ceil(math.log(len(namelist))/math.log(2))
        NSeeded = 2**(self.numberOfRounds) - len(namelist)

        self.round = Round(player_list = namelist,numberOfSeededPlayers = NSeeded)


    def drawRound(self):
        arcade.start_render()
        width, height = self.get_size()
        arcade.draw_rectangle_filled(width/2, height/2 , width, height, BG_COLOR_ROUND)
        arcade.draw_text("Runde "+str(self.round.roundNumber)+" av "+str(self.numberOfRounds), width/2, height/2, TEXT_COLOR_ROUND, 70, align="center", anchor_x="center", anchor_y="center")

    def draw_head2head(self, game):
        arcade.start_render()
        width, height = self.get_size()
        arcade.draw_rectangle_filled(width/4, height/2 , width/2, height, BG_COLOR2)

        arcade.draw_text(game.player1.name, width/4, height/2, BG_COLOR, 54, align="center", anchor_x="center", anchor_y="center")
        arcade.draw_text(game.player2.name, width/2+width/4, height/2, BG_COLOR2, 54, align="center", anchor_x="center", anchor_y="center")

        arcade.draw_text(str(self.round.roundNumber)+"/"+str(self.numberOfRounds)+": "+str(self.round.game_number+1)+"/"+str(self.round.number_of_games), width-25, 25, NUMBERING_COLOR, 12, align="right", anchor_x="right", anchor_y="bottom")

    def draw_final_screen(self):
    	arcade.start_render()
    	width, height = self.get_size()
    	arcade.draw_rectangle_filled(width/2, height/2 , width, height, BG_COLOR_FINISHED)
    	arcade.draw_text("Og vinneren er:", width/2, 2*height/3, TEXT_COLOR_FINISHED, 54, align="center", anchor_x="center", anchor_y="center")
    	arcade.draw_text(self.round.games[0].winner.name, width/2, height/2, TEXT_COLOR_FINISHED, 108, align="center", anchor_x="center", anchor_y="center")

    def on_draw(self):
        arcade.start_render()

        if self.current_state == ROUND:
            self.drawRound()

        elif self.current_state == HEAD2HEAD:
        	self.draw_head2head(self.round.games[self.round.game_number])

        elif self.current_state==FINISHED:
        	self.draw_final_screen()

    def check_if_round_over(self):
    	if self.round.game_number > self.round.number_of_games-1:

    		self.list_of_finished_rounds.append(self.round)
    		self.round.print_round_to_file(self.foldername)
    		
    		if len(self.round.games)==1:
    			self.current_state = FINISHED
    		else:
    			self.current_state = ROUND
    			winners = self.round.getWinners()
    			self.round = Round(player_list = winners, roundNumber = self.round.roundNumber)
    			#self.round.initialize_round(self.player_list)

    def on_mouse_press(self, x, y, button, modifiers):
    	if self.current_state == ROUND:
    		self.current_state = HEAD2HEAD
    		if self.round.roundNumber > 1:
    			self.round.game_number = 0
    	elif self.current_state == HEAD2HEAD:

    		if round(x/SCREEN_WIDTH)==0:
    			self.round.games[self.round.game_number].winner = self.round.games[self.round.game_number].player1
    		else:
    			self.round.games[self.round.game_number].winner = self.round.games[self.round.game_number].player2

    		self.round.game_number += 1
    	
    		self.check_if_round_over()

    def on_key_press(self, key, modifiers):
    	if self.current_state == ROUND:
    		self.current_state = HEAD2HEAD
    		if self.round.roundNumber > 1:
    			self.round.game_number = 0
    	elif self.current_state == HEAD2HEAD and (key == arcade.key.LEFT or key==arcade.key.RIGHT) :
    		if key == arcade.key.LEFT:
    			self.round.games[self.round.game_number].winner = self.round.games[self.round.game_number].player1
    		elif key == arcade.key.RIGHT:
    			self.round.games[self.round.game_number].winner = self.round.games[self.round.game_number].player2

    		self.round.game_number += 1

    	elif key==arcade.key.ESCAPE:
    		arcade.close_window()
    	
    	self.check_if_round_over()

class Player:
	def __init__(self, name: str=None):
		self.name = name

class Game:
	def __init__(self,player1: Player=None, player2: Player=None, winner: Player=None):
		self.player1 = player1
		self.player2 = player2
		self.winner = winner

class Round:
	def __init__(self,roundNumber: int=0,games: list=list(), player_list: list=list(),numberOfSeededPlayers: int=0, game_number: int=0):
		self.games = games
		self.roundNumber = roundNumber
		self.game_number = game_number
		self.games = list()

		for i in range(0,numberOfSeededPlayers):
			game = Game(player_list[i],player_list[i])
			game.winner = player_list[i]
			self.games.append(game)
			game.seeded = True

		for i in range(numberOfSeededPlayers,len(player_list),2):
			game = Game(player_list[i],player_list[i+1])
			self.games.append(game)
			game.seeded = False
		
		self.roundNumber += 1
		self.number_of_games = len(self.games)
		self.game_number = numberOfSeededPlayers

	def print_round_to_file(self,foldername: str=None):
		f = open(foldername+"/round_"+str(self.roundNumber)+".txt","w")
		for game in self.games:
			if game.seeded:
				f.write(game.winner.name+" (seeded)"+"\n")
			else:
				f.write(game.winner.name+"\n")

	def getWinners(self):
		winners = list()
		for game in self.games:
			winners.append(game.winner)
		return winners


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()

if __name__ == "__main__":
    main()