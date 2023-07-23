

import sqlite3
# import numpy as np
# import pandas as pd
# import random
import time
import datetime
import argparse

import console
import gamelogic
from character import character
import gameparser

# parser = argparse.ArgumentParser(
#     prog='program name',
#     description='description',
#     epilog='text at end of help'
# )

# parser.add_argument('-m', '--mode', choices=['cli', 'web'], default='cli')
# if mode is cli, it pushes updates there; otherwise, it establishes webhook and pushes there

# args = parser.parse_args()
# mode = args.mode

db = sqlite3.connect("db/gamedata.db") 




if __name__ == '__main__':


   game_running = True
   while game_running == True:

      # ---------------- INTRO TEXT ---------------- #

      console.write("Game Starting...")

      # ---------------- CHARACTER CREATION ---------------- #

      main_character = gamelogic.create_character()

      # ---------------- CLOCK START ---------------- #
      # ----- Runs the game-loop every interval ----- #

      # game_length = get_game_length()

      # console.write(get_character_description(main_character))

      interval = 1 # 1 second
      # interval = 10 # 10 seconds
      # interval = 60 # 1 minute
      elapsed = 0
      clock_running = True
      events_list = []

      while clock_running == True: 

         time.sleep(interval - time.monotonic() % interval) # sleep until next interval
         console.write(time.strftime("%H:%M:%S") + f" - {elapsed} minutes elapsed.")
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
                  baby_lifepath = gamelogic.baby_lifepath_from_setting(main_character.setting)
                  main_character.change_lifepath(baby_lifepath)
                  events_list = gamelogic.get_baby_events(main_character)
                  years_per_event = main_character.lifepath['years'] / len(events_list)

               # if baby, grow to kid  
               elif main_character.lifepath['baby'] == 'true': # if just finished being baby
                  kid_lifepath = gamelogic.kid_lifepath_from_setting(main_character.setting)
                  main_character.change_lifepath(kid_lifepath)
                  events_list = gamelogic.get_events(main_character)
                  years_per_event = main_character.lifepath['years'] / len(events_list)

               # if age is super old or sick, run postscript
               elif main_character.age >= 90 or main_character.abilities['health'] == 0:
                  console.write("End of game.") # end game for now
                  game_running = gamelogic.end_game()

               # otherwise, game runs a situation and then offers a choice of opportunities
               else:
                  situation = gamelogic.get_situation(main_character.setting)
                  gamelogic.run_situation(situation, main_character)

                  opportunities = gamelogic.get_opportunities(situation, main_character)
                  chosen_opportunity = gamelogic.choose_opportunity(opportunities)

                  new_lifepath = gamelogic.run_opportunity(chosen_opportunity, main_character)
                  main_character.change_lifepath(new_lifepath)
                  events_list = gamelogic.get_events(main_character)
                  years_per_event = main_character.lifepath['years'] / len(events_list)
               
         # RUN EVENT: choose first event on list, run it, remove it from list
         event_to_run = events_list[0]
         gamelogic.run_event(event_to_run, main_character)
         main_character.age += years_per_event
         events_list.pop(0)




         # if really old, get ending decision and end game
         # else get decision, run decision, choose next lifepath
         # choose next lifepath
         

   # ---------------- GAME END ---------------- #
      game_running = gamelogic.end_game()