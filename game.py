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
import numpy as np
import pandas as pd
import random
import time
import datetime
import argparse
import console

from character import character
import gameparser

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
        # sex_input = read('But what is the sex? M/F ')
        sex_input = console.read('But what is the sex? M/F')
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


def baby_lifepath_from_setting(setting):
    # takes setting, returns the kid lifepath there
    db_lifepath = pd.read_sql_query( f"SELECT id FROM lifepaths WHERE setting = '{setting}' AND baby = 'true'", db)
    if len(db_lifepath) == 0:
        raise Exception("Couldn't find baby lifepath")
    return db_lifepath['id'].values[0]

def kid_lifepath_from_setting(setting):
# takes setting, returns the kid lifepath there
    db_lifepath = pd.read_sql_query( "SELECT id FROM lifepaths WHERE setting = '" + setting + "' AND kid = 'true'", db)
    if len(db_lifepath) == 0:
        raise Exception("Couldn't find kid lifepath")
    return db_lifepath['id'].values[0]


def get_baby_events(character):
        events = []

        # take random appearance from db, check if one of its category is already in the list,
        # if not, add it to the list and its category to the used_categories list
        db_appearances = pd.read_sql_query( "SELECT id, name, category FROM appearances WHERE aging = 'false' AND scar = 'false'", db )

        appearance_setups = [
            "Even as an infant, {name} has",
            "As {sub} grows, {name} develops",
            "Little {name} grows more, gaining"
        ]

        used_categories = []

        while len(events) < int(character.lifepath['years'])-1:
            random_appearance = get_random_row(db_appearances).to_dict()
            if not random_appearance['category'] in used_categories:
                events.append({
                    'id': f"baby_appearance_{random_appearance['category']}",
                    'name': f"baby appearance {random_appearance['name']}",
                    'prereqs': f"lifepath: baby",
                    'test_skill_id': '',
                    'difficulty': 0,
                    'setup': f"{appearance_setups[len(events)]} {random_appearance['name']}.",
                    'success_description': '',
                    'success_effect': f"gain(appearances: {random_appearance['id']})",
                    'failure_description': '',
                    'failure_effect': ''
                })

        # 1/3 chance of adding baby_normal event to list; otherwise, random trait event
        normal_chance = random.randint(1,3)
        if normal_chance == 1:
            db_baby_trait_events = pd.read_sql_query( "SELECT * FROM events WHERE id = 'baby_normal'", db)
        else:
            db_baby_trait_events = pd.read_sql_query( "SELECT * FROM events WHERE prereqs = 'lifepaths: baby'", db)
        # choose random baby trait event from list
        baby_trait_event = get_random_row(db_baby_trait_events).to_dict()
        events.append(baby_trait_event)

        return events

def get_events(character):
    
    events = [] # the list of dicts to return
    used_events = [] # list of event_id's already used, for easier searching

    # get all events
    db_all_events = pd.read_sql_query(f"SELECT id, prereqs FROM events WHERE id IS NOT NULL", db)
    all_events_dict = db_all_events.to_dict(orient="records")

    # parse prereqs and make list of events whose prereqs the character has
    possible_event_ids = []
    for event in all_events_dict:
        parsed_prereqs = gameparser.parse_prereqs(event['prereqs'])
        keep_event = False
        if character.setting in parsed_prereqs['settings']: 
            keep_event = True
        if character.lifepath['id'] in parsed_prereqs['lifepaths']:
            keep_event = True
        if keep_event:
            possible_event_ids.append(event['id'])

    # check that there are enough events in the list, total
    if len(possible_event_ids) < int(character.lifepath['years']):
        raise Exception("Couldn't find enough events for character.")
    
    # get full events from db
    query = "SELECT * FROM events WHERE"
    for id in possible_event_ids:
        query += f" id = '{id}' OR"
    query = query[:-3] # chop off last " OR"
    db_possible_events = pd.read_sql_query(query, db)

    # fill events list with one event per year
    while len(events) < int(character.lifepath['years']):
        random_event = get_random_row(db_possible_events).to_dict()
        # check if even is already in list; if not, add it
        if not random_event['id'] in used_events:
            events.append(random_event)
            used_events.append(random_event['id'])

    return events


def run_event(event, character):

    event_string = event['setup']
    effects = {}
    
    if event['success_description'] != 'NULL' and event['failure_description'] != 'NULL':

        # test -- later, add logic to test whatever is higher, relevant ability or skill
        if random.randint(1, 10) >= int(event['difficulty']):
            event_string += f" {event['success_description']}"
            effects = gameparser.parse_effects(event['success_effect'])
        else:
            event_string += f" {event['failure_description']}"
            effects = gameparser.parse_effects(event['failure_effect'])

        write(gameparser.parse_pronouns(event_string, character))

        effects_results = character.update_stats(effects)
        for result in effects_results: # write in the correct color
            if result['change'] == 'gain':
                if result['success'] == True:
                    write_gain(result['message'])
                else:
                    write_gain_failed(result['message'])
            elif result['change'] == 'loss':
                if result['success'] == True:
                    write_loss(result['message'])
                else:
                    write_loss_failed(result['message'])



def decision(character):
    0
    # logic for calling and resolving decisions
    # each should increase age by 1
    # 
    # get list of possible decisions based on character setting, and choose one
    # get default options
    # get list of possible other options, based on character lifepath/skills/traits/etc
    # choose one or two of these
    # present all as options

    # player picks one. push changes to character. keep new lifepath option new list
    # get list of possible next lifepaths based on character setting, and add a few of them to the list
    # present list of lifepath choices
    # player picks one
    # push change to character
    # end decision

def end_game():
    write("Game Shutting Down...")
    return False

#---------------- HELPER FUNCTIONS ----------------#

def get_random_row(dataframe):
    random_row = random.randint(0, len(dataframe)-1)
    # write(dataframe.iloc[random_row])
    return dataframe.iloc[random_row]

# write and read are helper functions.
# they write and read to cli or webhooks, depending on the program's mode
def write(text):
    if mode == 'cli':
        return console.write(text)
    elif mode == 'web':
        0

def read(text, choices=None):
    if mode == 'cli':
        return console.read(text, choices)
    elif mode == 'web':
        0
    
def write_gain(text):
    if mode == 'cli':
        return console.write_gain(text)
    elif mode == 'web':
        0

def write_gain_failed(text):
    if mode == 'cli':
        return console.write_gain_failed(text)
    elif mode == 'web':
        0

def write_loss(text):
    if mode == 'cli':
        return console.write_loss(text)
    elif mode == 'web':
        0

def write_loss_failed(text):
    if mode == 'cli':
        return console.write_loss_failed(text)
    elif mode == 'web':
        0

# ---------------- GAME START ---------------- #

if __name__ == "__main__":

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

        # ---------------- CLOCK START ---------------- #

        game_length = get_game_length()

        # write(get_character_description(main_character))

        # interval = 1 # 1 second
        interval = 10 # 10 seconds
        # interval = 60 # 1 minute
        elapsed = 0
        clock_running = True
        events_list = []

        while clock_running == True: 

            time.sleep(interval - time.monotonic() % interval) # sleep until next interval
            write(time.strftime("%H:%M:%S") + f" - {elapsed} minutes elapsed.")
            elapsed += 1
            # if (time.strftime('%S') == '00'): # at top of minute, reset interval to each minute
            #     interval = 60 

            # ---------------- THE LOOP ---------------- #

            if len(events_list) == 0: # if no events left in list (ie, if all have run)

                # if newborn, grow to baby
                if main_character.lifepath['id'] == 'newborn':
                    baby_lifepath = baby_lifepath_from_setting(main_character.setting)
                    main_character.change_lifepath(baby_lifepath)
                    events_list = get_baby_events(main_character)
                # if baby, grow to kid  
                elif main_character.lifepath['baby'] == 'true': # if just finished being baby
                    kid_lifepath = kid_lifepath_from_setting(main_character.setting)
                    main_character.change_lifepath(kid_lifepath)
                    events_list = get_events(main_character)

                # if kid or adult, player makes decision and chooses new lifepath
                else:
                    write("Grown to adult.") # end game for now
                    game_running = end_game()
                
            # run event
            # choose first event on the list
            this_event = events_list[0]
            # run event and print output
            run_event(this_event, main_character)
            # remove first item from list
            events_list.pop(0)




            # if really old, get ending decision and end game
            # else get decision, run decision, choose next lifepath
            # choose next lifepath
            

# ---------------- GAME END ---------------- #
        game_running = end_game()