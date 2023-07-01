'''
Contains all the functions that the gameloop uses.
I moved the gameloop itself into a separate file called gameloop.py for now,
because it felt more organized to me.
And also because it made it easier to test individual functions here
if I wasn't using "if __name__ == __main__ to run the game itself.
'''


import sqlite3
# import numpy as np
import pandas as pd
import random
import time
# import datetime
import argparse
import console
import traceback

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
    try:
        db_lifepath = pd.read_sql_query( f"SELECT id FROM lifepaths WHERE setting = '{setting}' AND baby = 'true'", db)
        if len(db_lifepath) == 0:
            raise Exception(write_error("Couldn't find baby lifepath"))
        return db_lifepath['id'].values[0]
    except Exception as e:
        write_error(f"Error retrieving baby lifepath from setting {setting}: {e}") 

def kid_lifepath_from_setting(setting):
    # takes setting, returns the kid lifepath there
    try:
        db_lifepath = pd.read_sql_query( "SELECT id FROM lifepaths WHERE setting = '" + setting + "' AND kid = 'true'", db)
        if len(db_lifepath) == 0:
            raise Exception(write_error("Couldn't find kid lifepath"))
        return db_lifepath['id'].values[0]
    except Exception as e:
        write_error(f"Error retrieving kid lifepath from setting {setting}: {e}") 


def get_baby_events(character):
    try:
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
            random_appearance = random_row_to_dict(db_appearances)
            if not random_appearance['category'] in used_categories:
                events.append({
                    'id': f"baby_appearance_{random_appearance['category']}",
                    'name': f"baby appearance {random_appearance['name']}",
                    'prereq_type': f'lifepath',
                    'prereq_id': f'baby',
                    'test_type': '',
                    'test_id': '',
                    'difficulty': 0,
                    'setup': f"{appearance_setups[len(events)]} {random_appearance['name']}.",
                    'success_description': '',
                    'success_effect': f"gain(appearances: {random_appearance['id']})",
                    'failure_description': '',
                    'failure_effect': ''
                })
                used_categories.append(random_appearance['category'])

        # 1/3 chance of adding baby_normal event to list; otherwise, random trait event
        normal_chance = random.randint(1,3)
        if normal_chance == 1:
            db_baby_trait_events = pd.read_sql_query( "SELECT * FROM events WHERE id = 'baby_normal'", db)
        else:
            db_baby_trait_events = pd.read_sql_query( "SELECT * FROM events WHERE prereqs = 'lifepaths: baby'", db)
        # choose random baby trait event from list
        baby_trait_event = random_row_to_dict(db_baby_trait_events).to_dict()
        events.append(baby_trait_event)

        return events
    
    except Exception as e:
        write_error(f"Error creating list of baby events: {e}") 

def get_events(character):
    try:
        event_dicts = [] # the list of dicts to return
        used_events = [] # list of event_id's already used, for easier searching

        # get all events that match character - lifepath, settings (maybe in future, other prereqs)
        query = f'SELECT * FROM events WHERE '
        query += f'(prereq_type = "lifepath" AND prereq_id = {character.lifepath[id]})'
        query += f'(prereq_type = "setting" AND prereq_id = {character.setting})'
        db_possible_events = pd.read_sql_query(query, db)
        if len(db_possible_events) < int(character.lifepath['years']):
            raise Exception(write_error("Couldn't find enough events for character."))

        # fill events list with one event per year
        while len(event_dicts) < int(character.lifepath['years']):
            random_event = random_row_to_dict(db_possible_events)
            # check if even is already in list; if not, add it
            if not random_event['id'] in used_events:
                event_dicts.append(random_event)
                used_events.append(random_event['id'])

        return event_dicts
    except Exception as e:
        write_error(f"Error compiling list of events: {e}") 

def run_event(event_dict, character):

    try:
        event_string = event_dict['setup']
        effects = {}
        
        if event_dict['success_description'] != 'NULL' and event_dict['failure_description'] != 'NULL':

            # test -- later, add logic to test whatever is higher, relevant ability or skill
            if random.randint(1, 10) >= int(event_dict['difficulty']):
                event_string += f" {event_dict['success_description']}"
                effects = gameparser.parse_effects(event_dict['success_effect'])
            else:
                event_string += f" {event_dict['failure_description']}"
                effects = gameparser.parse_effects(event_dict['failure_effect'])

            write(gameparser.parse_pronouns(event_string, character))

            run_effects(effects, character)
    except Exception as e:
        write_error(f"Error running event {event_dict['id']}: {e}") 

def run_effects(effects, character):
    # update character stats with effects, write results
    try:
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
    except Exception as e:
        write_error(f"Error processing list of effects {effects}: {e}") 


def get_situation(setting):
    # choose random turning point from setting and return it
    try:
        db_situations = pd.read_sql_query(f"SELECT * FROM situations WHERE setting = '{setting}'", db)
        return random_row_to_dict(db_situations)
    except Exception as e:
        write_error(f"Error getting situation: {e}") 

def run_situation(situation_dict, character):
    # print situation info. Originally this was going to be more involved, 
    # but most of the remaining logic is now in get_opportunities
    try:
        write(situation_dict['headline'])
        write(gameparser.parse_pronouns(situation_dict['description'], character))
        effects = gameparser.parse_effects(situation_dict['effects'])
        run_effects(effects, character)
    except Exception as e:
        write_error(f"Error running situation {situation_dict['id']}: {e}") 


def get_opportunities(situation_dict, character):
    # Returns list of four opportunity dicts, each including a sub-dict with info on why it was picked

    number_of_choices = 4
    opportunity_choices = []

    try:  
        # Pull relevant opportunities and add character stat ranks to them
        db_continuation_opportunity = pd.read_sql_query(f"SELECT * FROM opportunities WHERE continuation = 'true'", db)
        if len(db_continuation_opportunity) > 0:
            continuation_opportunity = row_to_dict(db_continuation_opportunity)
        else:
            continuation_opportunity = {}
        continuation_opportunity['character_ranks'] = get_character_ranks_for_opportunity(continuation_opportunity, character)

        db_normal_opportunities = pd.read_sql_query(f"SELECT * FROM opportunities WHERE prereq_type = 'lifepath' AND prereq_id = '{character.lifepath['id']}' AND continuation = 'false'", db)
        if len(db_normal_opportunities) > 0:
            normal_opportunities = db_normal_opportunities.to_dict(orient='records')
        else:
            normal_opportunities = {}
        for opportunity in normal_opportunities:
            opportunity['character_ranks'] = get_character_ranks_for_opportunity(opportunity, character)

        db_situation_opportunities = pd.read_sql_query(f"SELECT * FROM opportunities WHERE prereq_type = 'situation' AND prereq_id = '{situation_dict['id']}'", db)
        if len(db_situation_opportunities) > 0:
            situation_opportunities = db_situation_opportunities.to_dict(orient='records')
        else:
            situation_opportunities = {}
        for opportunity in situation_opportunities:
            opportunity['character_ranks'] = get_character_ranks_for_opportunity(opportunity, character)

        # Get number of normal/continuation opportunities to add (the rest are situation opportunities)
        situation_opportunities_to_add = situation_dict['lifepath_replacements']
        normal_opportunities_to_add = number_of_choices - situation_opportunities_to_add
        if len(normal_opportunities) + len(continuation_opportunity) < normal_opportunities_to_add:
            raise Exception(write_error("Not enough normal/continuation opportunities to fill out list."))
    except Exception as e:
        write_error(f"Error retrieving opportunities from database: {e}") 
       
    try:
        # If there's space in the list, add a continuation opportunity, if available
        
        if normal_opportunities_to_add > 0 :
            if len(db_continuation_opportunity) > 0:
                opportunity_choices.append(continuation_opportunity)
                normal_opportunities_to_add -= 1

        # If there's still space, add best match to character skills/abilities
        if normal_opportunities_to_add > 0:
            best_skills_match = get_best_fit_opportunity(normal_opportunities)
            opportunity_choices.append(best_skills_match)
            # remove that match from the normal_opportunities list
            for index in range(len(normal_opportunities)):
                if normal_opportunities[index]['id'] == best_skills_match['id']:
                    del normal_opportunities[index]
                    break
            # subtract 1 from number of normal_opportunities_to_add
            normal_opportunities_to_add -= 1
        
        # If there's still space, add best match to character motivations
        if normal_opportunities_to_add > 0:
            best_motivations_match = get_most_desired_opportunity(normal_opportunities)
            opportunity_choices.append(best_motivations_match)
            # remove that match from the normal_opportunities list
            for index in range(len(normal_opportunities)):
                if normal_opportunities[index]['id'] == best_motivations_match['id']:
                    del normal_opportunities[index]
                    break
            # subtract 1 from number of normal_opportunities_to_add
            normal_opportunities_to_add -= 1

        # If there's STILL space, just add random opportunities until there's not
        try:
            while normal_opportunities_to_add > 0:
                random_index = normal_opportunities[random.randint(0, len(normal_opportunities)-1)]
                opportunity_choices.append(normal_opportunities[random_index])
                del normal_opportunities[random_index]
                normal_opportunities_to_add -= 1              
        except Exception as e:
            write_error(f"Error adding random opportunities to choice list: {e}")
            traceback.print_exc()
        
        # NEXT, do the same with the situation choices:
        # First, Add the one that best matches skills
        if situation_opportunities_to_add > 0:
            best_skills_match = get_best_fit_opportunity(situation_opportunities)
            opportunity_choices.append(best_skills_match)
            # remove that match from the situation_opportunities list
            for index in range(len(situation_opportunities)):
                if situation_opportunities[index]['id'] == best_skills_match['id']:
                    del situation_opportunities[index]
                    break
            # subtract 1 from number of situation_opportunities_to_add
            situation_opportunities_to_add -= 1
        
        # If there's still space, add best match to character motivations
        if situation_opportunities_to_add > 0:
            best_motivations_match = get_most_desired_opportunity(situation_opportunities)
            opportunity_choices.append(best_motivations_match)
            # remove that match from the situation_opportunities list
            for index in range(len(situation_opportunities)):
                if situation_opportunities[index]['id'] == best_motivations_match['id']:
                    del situation_opportunities[index]
                    break
            # subtract 1 from number of situation_opportunities_to_add
            situation_opportunities_to_add -= 1

        # If there's STILL space, just add random opportunities until there's not
        try:
            while situation_opportunities_to_add > 0:
                random_index = situation_opportunities[random.randint(0, len(situation_opportunities)-1)]
                opportunity_choices.append(situation_opportunities[random_index])
                del situation_opportunities[random_index]
                situation_opportunities_to_add -= 1              
        except Exception as e:
            write_error(f"Error adding random opportunities to choice list: {e}")
            traceback.print_exc()

        return opportunity_choices

    except Exception as e:
        write_error(f"Error populating list of opportunities: {e}") 
        
def get_character_ranks_for_opportunity(opportunity_dict, character):
    # parses the abilities, skills, and motivations from the opportunity_dict,
    # gets the character's ranks in those abilities, skills, and motivations,
    # and returns a dict of those ranks like {abilities: {strength: 4, speed: 2}, skills: {farming: 2}, etc}
    try:
        # split the opportunity's abilities, skills, etc into lists of ids
        abilities_list = []
        skills_list = []
        motivations_list = []
        if opportunity_dict:
            if opportunity_dict['abilities']:
                abilities_list = opportunity_dict['abilities'].split(", ")
            if opportunity_dict['skills']:
                skills_list = opportunity_dict['skills'].split(", ")
            if opportunity_dict['motivations']:
                motivations_list = opportunity_dict['motivations'].split(", ")

        # make a dict containing the ranks the character has in those abilities/skills/motivations
        character_ranks = {'abilities':{}, 'skills':{}, 'motivations':{}}
        for ability in abilities_list:
            character_ranks['abilities'][ability] = character.abilities[ability]['rank']
        for skill in skills_list:
            character_ranks['skills'][skill] = character.skills[skill]['rank']
        for motivation in motivations_list:
            for motivation_dict in character.motivations.values():
                if motivation_dict['high'] == motivation:
                    character_ranks['motivations'][motivation] = character.motivations[motivation_dict['id']]['rank']
                elif motivation_dict['low'] == motivation:
                    character_ranks['motivations'][motivation] = character.motivations[motivation_dict['id']]['rank'] * -1
        return character_ranks
    
    except Exception as e:
        write_error(f"Error getting character ranks in abilities/skills/motivations for opportunity {opportunity_dict['id']}: {e}") 


# REWRITE THE FOLLOWING TWO FUNCTIONS WHEN I'M LESS BRAINDEAD.
def get_best_fit_opportunity(opportunity_list_with_character_ranks):
    # Returns the opportunity that best matches character's abilities and skills
    # (Specifically, best average rank of top two matching abilities and/or skills)
    try:

        # Get average of top-two matching scores and save that to opportunity['skill_fit']
        for opportunity in opportunity_list_with_character_ranks:
            top_rank = {'type':None, 'id':None, 'rank':0}
            second_rank = {'type':None, 'id':None, 'rank':0}

            # populate top_rank and second_rank with top two relevant ability scores
            for id, rank in opportunity['character_ranks']['abilities'].items():
                if rank > top_rank['rank']: 
                    top_rank = {'type':'ability', 'id': id, 'rank': rank}
                elif rank >= second_rank['rank']: 
                    second_rank = {'type':'ability', 'id': id, 'rank': rank}

            # do the same as above, but now with skill scores
            for id, rank in opportunity['character_ranks']['skills'].items():
                if rank > top_rank['rank']: 
                    top_rank = {'type':'skill', 'id': id, 'rank': rank}
                elif rank >= second_rank['rank']: 
                    second_rank = {'type':'skill', 'id': id, 'rank': rank}

            # add those scores to opportunity.character_ranks, for future reference
            # opportunity['character_ranks']['top_abilities_and_skills'] = [top_rank, second_rank]
            # get average of those two scores
            opportunity['character_ranks']['skill_fit'] = (top_rank['rank'] + second_rank['rank']) / 2
        
        # compile list of opportunities with top skill_fit score (usually only one, but ties are possible)
        best_matches = []
        for opportunity in opportunity_list_with_character_ranks:
            # if best_matches is empty, add it
            if len(best_matches) == 0:
                best_matches.append(opportunity)
            else:
                # if it's higher than best_matches, replace it
                if opportunity['character_ranks']['skill_fit'] > best_matches[0]['character_ranks']['skill_fit']:
                    best_matches = [opportunity]
                # if it's tied with best_matches, append it to list
                if opportunity['character_ranks']['skill_fit'] == best_matches[0]['character_ranks']['skill_fit']:
                    best_matches.append(opportunity)

        # add random opportunity from best_matches
        best_match = best_matches[random.randint(0, len(best_matches)-1)]
        return(best_match)
    except Exception as e:
        write_error(f"Error adding best skill/ability match to list of opportunities: {e}") 

def get_most_desired_opportunity(opportunity_list_with_character_ranks):
    # Returns best match to character motivations
    # (specifically, the highest score in any relevant motivation)
    try:
        # assign each opportunity a motivation_fit score based on the highest relevant motivation
        for opportunity in opportunity_list_with_character_ranks:
            motivation_ranks = opportunity['character_ranks']['motivations'].values()
            motivation_fit = max(motivation_ranks)
            opportunity['character_ranks']['motivation_fit'] = motivation_fit
            
        # compile list of opportunities with top motivation_fit score (usually only one, but ties are possible)
        best_matches = []
        for opportunity in opportunity_list_with_character_ranks:
            # if best_matches is empty, add it
            if len(best_matches) == 0:
                best_matches.append(opportunity)
            else:
                # if it's higher than best_matches, replace it
                if opportunity['character_ranks']['motivation_fit'] > best_matches[0]['character_ranks']['motivation_fit']:
                    best_matches = [opportunity]
                # if it's tied with best_matches, append it to list
                if opportunity['character_ranks']['motivation_fit'] == best_matches[0]['character_ranks']['motivation_fit']:
                    best_matches.append(opportunity)
        
        # add random opportunity from best_matches
        best_match = best_matches[random.randint(0, len(best_matches)-1)]
        return(best_match)
    except Exception as e:
        write_error(f"Error adding best motivation match to list of opportunities: {e}") 
        

def choose_opportunity(opportunity_dict_list, character):
    0
    # lay out list

def run_opportunity(opportunity_dict, character):
    0
    # run chosen opportunity, including any changes to character.
    # should change character's lifepath, meaning the next call of
    # get_events(character) should give the right events.

    # NOTE TO SELF - rewrite choice descriptions to be more personal and evocative


def end_game():
    write("Game Shutting Down...")
    return False

#---------------- HELPER FUNCTIONS ----------------#

def event_to_dict(event_id_string):
    # returns event dict directly from id, without having to go through get_events
    try:
        db_event = pd.read_sql_query(f"SELECT * FROM events WHERE id = '{event_id_string}'", db)
        return db_event.iloc[0].to_dict()
    except Exception as e:
        write_error(f"Error retrieiving event {event_id_string}: {e}") 

def row_to_dict(dataframe):
    # takes single row dataframe, returns dict
    try:
        if len(dataframe) > 1:
            raise Exception(write_error(f'Dataframe of more than one row passed to row_to_dict:\n{dataframe}'))
        return dataframe.iloc[0].to_dict()
    except Exception as e:
        write_error(f"Error converting dataframe to dict: {e}") 

def random_row_to_dict(dataframe):
    # takes multi-row dataframe, returns single random row's dict
    try:
        random_row = random.randint(0, len(dataframe)-1)
        return dataframe.iloc[random_row].to_dict()
    except Exception as e:
        write_error(f"Error converting dataframe to dict: {e}") 

def convert_motivation(motivation, rank=0):
    db_motivation = pd.read_sql_query(f"SELECT * FROM motivations WHERE id = '{motivation}' OR low = '{motivation}' OR high = '{motivation}'")
    if len(db_motivation) == 0:
        raise Exception(write_error(f"Error converting motivation: '{motivation}' not found in database"))
    motivation_dict = db_motivation.to_dict(orient='records')
    if motivation == motivation_dict['high']:
        return motivation_dict['id'], rank
    elif motivation == motivation_dict['low']:
        return motivation_dict['id'], rank * -1
    elif motivation == motivation_dict['id']:
        if rank >= 0:
            return motivation_dict['high'], rank
        else:
            return motivation_dict['low'], rank * -1


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

def write_error(text):
    if mode == 'cli':
        console.write_error(text) 
        traceback.print_exc()




if __name__ == "__main__":

    testperson = character("Testperson", "male", "peasant")
    write(f"Name: {testperson.name}")

    testperson.change_lifepath("kid_peasant")
    write(f"Lifepath: {testperson.lifepath}")

    run_event(event_to_dict("peasant_kid_first_plant"), testperson)
    run_event(event_to_dict("peasant_kid_herding"), testperson)
    # run_event(event_to_dict("peasant_kid_church"), testperson)
    run_event(event_to_dict("peasant_kid_chores"), testperson)
    run_event(event_to_dict("peasant_kid_trapping"), testperson)
    run_event(event_to_dict("peasant_kid_bully"), testperson)
    testperson.gain_motivation('intellectual')

    write(f"Motivations: {testperson.motivations}")
    write(f"Abilities: {testperson.abilities}")
    write(f"Skills: {testperson.skills}")

    situation = get_situation("peasant") # at this time, only one possible result: peasant_fort_construction
    write(f"Situation: {situation}")
    run_situation(situation, testperson)

    opportunities = get_opportunities(situation, testperson)
    write("Opportunities:")
    for opportunity in opportunities:
        write(f"- {opportunity['id']}")