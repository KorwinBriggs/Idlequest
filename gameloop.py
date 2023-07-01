

import sqlite3
# import numpy as np
# import pandas as pd
# import random
import time
import datetime
import argparse
# import console

# from character import character
import game
# import gameparser

parser = argparse.ArgumentParser(
    prog='program name',
    description='description',
    epilog='text at end of help'
)

parser.add_argument('-m', '--mode', choices=['cli', 'web'], default='cli')
# if mode is cli, it pushes updates there; otherwise, it establishes webhook and pushes there

args = parser.parse_args()
mode = args.mode

db = sqlite3.connect("db/gamedata.db") 





game_running = True
while game_running == True:

   # ---------------- INTRO TEXT ---------------- #

   game.write("Game Starting...")
   if mode == 'cli':
      game.write("Mode: CLI")
   if mode == 'web':
      game.write("Mode: Web")

   # ---------------- CHARACTER CREATION ---------------- #

   main_character = create_character()

   # ---------------- CLOCK START ---------------- #
   # ----- Runs the game-loop every interval ----- #

   # game_length = get_game_length()

   # write(get_character_description(main_character))

   interval = 1 # 1 second
   # interval = 10 # 10 seconds
   # interval = 60 # 1 minute
   elapsed = 0
   clock_running = True
   events_list = []

   while clock_running == True: 

      time.sleep(interval - time.monotonic() % interval) # sleep until next interval
      game.write(time.strftime("%H:%M:%S") + f" - {elapsed} minutes elapsed.")
      elapsed += 1
      # if (time.strftime('%S') == '00'): # at top of minute, reset interval to each minute
      #     interval = 60 


      # ---------------------------- GAME LOOP ----------------------------- #

      # If events_list has remaining events, run the events on intervals
      # If it's empty, fill it by checking lifepath:
      #   - if just started game (lifepath: newborn), set to baby and make custom baby events
      #   - next time, switch to relevatn kid lifepath, get_events for the kid lifepath
      #   - subsequent times: 
      #     - run a situation
      #     - set up opportunity list
      #     - have player pick and resolve one of those opportunities
      #     - get_events for the new lifepath
      #   - final time, if very old, go to game end and postscript

      if len(events_list) == 0: # if no events left in list (ie, if all have run)

            # if newborn, grow to baby
            if main_character.lifepath['id'] == 'newborn':
               baby_lifepath = game.baby_lifepath_from_setting(main_character.setting)
               main_character.change_lifepath(baby_lifepath)
               events_list = game.get_baby_events(main_character)
            # if baby, grow to kid  
            elif main_character.lifepath['baby'] == 'true': # if just finished being baby
               kid_lifepath = game.kid_lifepath_from_setting(main_character.setting)
               main_character.change_lifepath(kid_lifepath)
               events_list = game.get_events(main_character)
            # if age is super old, run postscript
            elif main_character.age >= 60:
               game.write("Grown to adult.") # end game for now
               game_running = game.end_game()
            # otherwise, game runs a situation and then offers a choice of opportunities
            else:
               situation = game.get_situation(main_character.setting)
               game.run_situation(situation, main_character)
               game.get_opportunities(situation, main_character)
               events_list = game.get_events(main_character)
               game.write("Grown to adult.") # end game for now
               game_running = game.end_game()
            
      # RUN EVENT: choose first event on list, run it, remove it from list
      event_to_run = events_list[0]
      game.run_event(event_to_run, main_character)
      events_list.pop(0)




      # if really old, get ending decision and end game
      # else get decision, run decision, choose next lifepath
      # choose next lifepath
      

# ---------------- GAME END ---------------- #
   game_running = game.end_game()