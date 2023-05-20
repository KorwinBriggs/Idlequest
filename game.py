'''
For now, this will just call game functions and show them to the command line
Later on, i'll convert it all to a flask server/api so i can run a front-end of my choice


character class holds character stuff: name, skills, history, etc
life class has static methods that take a character and produces events/decisions, modifying the character
    OR, nope, just jam those methods into the character class.
game class has static functions to create a character, starts a clock, calls life events, and reports changes to front end
    and then the main() runs a game loop using those functions
'''


import sqlite3
import random
import time
import datetime
import numpy as np
import pandas as pd
import argparse
from character import character

parser = argparse.ArgumentParser(
    prog='program name',
    description='description',
    epilog='text at end of help'
)

parser.add_argument('-m', '--mode', choices=['cli', 'web'], default='cli')
# if mode is cli, it pushes updates there; otherwise, it establishes webhook and pushes there

args = parser.parse_args()
mode = args.mode


def create_character(**args):
    if mode == 'cli':
        return __create_character_cli()
    elif mode == 'web':
        return __create_character_web()

def __create_character_cli():
    # Prompts for sex, name, and setting, and returns a character with those attributes
    
    write('Screaming, quiet, a light slap, and a long, high-pitched cry. A baby is born!')
    sex, name, setting = None, None, None

    while sex == None:
        sex_input = read('But what is the sex? M/F ')
        if sex_input == 'm' or sex_input == 'M' or sex_input == 'male' or sex_input == 'Male':
            write('Aha! A boy!')
            sex = 'male'
        elif sex_input == 'f' or sex_input == 'F' or sex_input == 'female' or sex_input == 'Female':
            write('Aha! A girl!')
            sex = 'female'
        else: write('...')

    while name == None:
        name_input = read(f'Hmm...what shall we call ' + ('him' if sex == 'male' else 'her') + '?').strip()
        # name_input = read(f'Hmm...and what will your name be, little one?')
        if not name_input == '':
            name = name_input.capitalize()
            write(f'Yes, ' + ('he' if sex == 'male' else 'she') + f' looks like a {name}.')
        else:
            write('...')

    while setting == None:
        write(f'And into what sort of life has {name} been born? (Choose by entering a number)')
        write('1. A community of peasants?')
        write('2. A small town in the countryside?')
        write('3. A large, bustling city?')
        write('4. A nomadic band of herders?')
        write('5. A powerful noble family?')
        write('6. Alone and impoverished?')
        setting_input = read('')
        if setting_input == '1' or setting_input == '2' or setting_input == '3' or setting_input == '4' or setting_input == '5' or setting_input == '6' :
            if setting_input == '1':
                setting = 'peasant'
                write("A simple beginning, to be sure, but even the great old oak started life toiling in the dirt.")
            else:
                write('(Sorry - only the first option is available for now)')
        else:
            write('...')

    return character(name, sex, setting)

def __create_character_web(**args):
    # Like create_character_cli, but sends and returns json instead of cli prompts
    0


def get_game_length():
    if mode == 'cli':
        return __get_game_length_cli()
    elif mode == 'web':
        return __get_game_length_web()
    
def __get_game_length_cli():
    
    game_length = None
    while game_length == None:
        length_input = read(f"Choose game length (6, 8, 10, or 12 hours)")
        if length_input == '6':
            game_length = 6 * 60
            write("6 hour game started.")
        elif length_input == '8':
            game_length = 8 * 60
            write("8 hour game started.")
        elif length_input == '10':
            game_length = 10 * 60
            write("10 hour game started.")
        elif length_input == '12':
            game_length = 12 * 60
            write("12 hour game started.")
        else:
            write("...")

def __get_game_length_web():
    0


def get_character_description(character):
    if mode == 'cli':
        return __get_character_description_cli(character)
    elif mode == 'web':
        return __get_character_description_web(character)
    
def __get_character_description_cli(character):

    description = (f"{character.name} is {character.age} years old."
          + f"\n{character.sub.capitalize()} has {character.appearanceToString()}."
    )
    return description

def __get_character_description_web(character):
    0




def event(character):



    if mode == 'cli':
        return __event_cli(character)
    elif mode == 'web':
        return __event_web(character)

def __event_cli(character):
    
    # get list of possible event ids
    db_events_query = f"SELECT * FROM events WHERE "
    db_events_query += f"prereq = 'setting:{character.setting}' "
    db_events_query += f"OR prereq = 'career:{character.career}' "

    db_possible_events = pd.read_sql_query(db_events_query, db)
    possible_events = db_possible_events.values.tolist()

    # choose one -- might also be in character
    event_choice = random.choice(possible_events)

    # run it
    # change character based on that event (including adding 1 to age)

def __event_web(character):
    0


def decision(character):
    0
    # logic for calling and resolving decisions
    # each should increase age by 1
    # 
    # get list of possible decisions based on character setting, and choose one
    # get default options
    # get list of possible other options, based on character career/skills/traits/etc
    # choose one or two of these
    # present all as options

    # player picks one. push changes to character. keep new career option new list
    # get list of possible next careers based on character setting, and add a few of them to the list
    # present list of career choices
    # player picks one
    # push change to character
    # end decision


# write and read are helper functions.
# they write and read to cli or webhooks, depending on the program's mode
def write(message):
    if mode == 'cli':
        print('\n' + message)
    elif mode == 'web':
        0

def read(message):
    if mode == 'cli':
        return input('\n' + message + ' ')
    elif mode == 'web':
        0
    
def end_game():
    write("Game Shutting Down...")
    return False


# ---------------- GAME START ---------------- #

if __name__ == "__main__":

    db = sqlite3.connect("db/gamedata") 
    game_running = True
    while game_running == True:

# ---------------- INTRO TEXT ---------------- #

        write("Game Starting...")
        if mode == 'cli':
            write("Mode: CLI")
        if mode == 'web':
            write("Mode: Web")

# ---------------- CHARACTER CREATION ---------------- #

        main_character = create_character()
        event(main_character)

# ---------------- CLOCK START ---------------- #

        game_length = get_game_length()

        write(get_character_description(main_character))

        interval = 60 # 1 minute
        elapsed = 0
        clock_running = True

        while clock_running == True: 

            time.sleep(interval - time.monotonic() % interval) # sleep until next interval
            write(time.strftime("%H:%M:%S") + f" - {elapsed} minutes elapsed.")
            elapsed += 1
            # if (time.strftime('%S') == '00'): # at top of minute, reset interval to each minute
            #     interval = 60 

# ---------------- CALLING EVENTS ---------------- #

            

# ---------------- GAME END ---------------- #
        game_running = end_game()