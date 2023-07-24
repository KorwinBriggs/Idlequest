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
import traceback

from character import character
import gameparser
import console
from dbhelpers import row_to_dict, random_row_to_dict

# parser = argparse.ArgumentParser(
#     prog='program name',
#     description='description',
#     epilog='text at end of help'
# )

# parser.add_argument('-m', '--mode', choices=['cli', 'web'], default='cli')
# # if mode is cli, it pushes updates there; otherwise, it establishes webhook and pushes there
# # actually, scratch that -- i'm planning to rewrite this whole thing for phones in kotlin multiplatform.

# args = parser.parse_args()
# mode = args.mode


# CONSTANTS

db = sqlite3.connect("db/gamedata.db") 


def create_character():
    # Prompts for sex, name, and setting, and returns a character with those attributes
    
    console.write('Screaming, quiet, a light slap, and a long, high-pitched cry. A baby is born!')
    sex, name, setting = None, None, None

    while sex == None:
        # sex_input = console.read('But what is the sex? M/F ')
        sex_input = console.read('But what is the sex? M/F')
        console.write(sex_input)
        if sex_input == 'm' or sex_input == 'M' or sex_input == 'male' or sex_input == 'Male':
            console.write('Aha! A boy!')
            sex = 'male'
        elif sex_input == 'f' or sex_input == 'F' or sex_input == 'female' or sex_input == 'Female':
            console.write('Aha! A girl!')
            sex = 'female'
        else: console.write('...')

    while name == None:
        name_input = console.read(f'Hmm...what shall we call ' + ('him' if sex == 'male' else 'her') + '?').strip()
        # name_input = console.read(f'Hmm...and what will your name be, little one?')
        if not name_input == '':
            name = name_input.capitalize()
            console.write(f'Yes, ' + ('he' if sex == 'male' else 'she') + f' looks like a {name}.')
        else:
            console.write('...')

    while setting == None:
        console.write(f'And into what sort of life has {name} been born? (Choose by entering a number)')
        console.write('1. A community of peasants?')
        console.write('2. A small town in the countryside?')
        console.write('3. A large, bustling city?')
        console.write('4. A nomadic band of herders?')
        console.write('5. A powerful noble family?')
        console.write('6. Alone and impoverished?')
        setting_input = console.read('')
        if setting_input == '1' or setting_input == '2' or setting_input == '3' or setting_input == '4' or setting_input == '5' or setting_input == '6' :
            if setting_input == '1':
                setting = 'peasant'
                console.write("A simple beginning, to be sure, but even the great old oak started life toiling in the dirt.")
            else:
                console.write('(Sorry - only the first option is available for now)')
        else:
            console.write('...')

    return character(name, sex, setting)

def get_game_length():
    game_length = None
    while game_length == None:
        length_input = console.read(f"Choose game length (6, 8, 10, or 12 hours)")
        if length_input == '6':
            game_length = 6 * 60
            console.write("6 hour game started.")
        elif length_input == '8':
            game_length = 8 * 60
            console.write("8 hour game started.")
        elif length_input == '10':
            game_length = 10 * 60
            console.write("10 hour game started.")
        elif length_input == '12':
            game_length = 12 * 60
            console.write("12 hour game started.")
        else:
            console.write("...")

def get_character_description(character):
    description = (f"{character.name} is {character.age} years old."
          + f"\n{character.sub.capitalize()} has {character.appearanceToString()}."
    )
    return description

def baby_lifepath_from_setting(setting):
    # takes setting, returns the kid lifepath there
    try:
        db_lifepath = pd.read_sql_query( f"SELECT id FROM lifepaths WHERE setting = '{setting}' AND baby = 'true'", db)
        if len(db_lifepath) == 0:
            raise Exception(console.write_error("Couldn't find baby lifepath"))
        return db_lifepath['id'].values[0]
    except Exception as e:
        console.write_error(f"Error retrieving baby lifepath from setting {setting}: {e}") 

def kid_lifepath_from_setting(setting):
    # takes setting, returns the kid lifepath there
    try:
        db_lifepath = pd.read_sql_query( "SELECT id FROM lifepaths WHERE setting = '" + setting + "' AND kid = 'true'", db)
        if len(db_lifepath) == 0:
            raise Exception(console.write_error("Couldn't find kid lifepath"))
        return db_lifepath['id'].values[0]
    except Exception as e:
        console.write_error(f"Error retrieving kid lifepath from setting {setting}: {e}") 

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
                    'event_type': 'gain',
                    'test_type': '',
                    'test_id': '',
                    'test_min': 0,
                    'age_min': 0,
                    'age_max': 4,
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
            db_baby_trait_events = pd.read_sql_query( "SELECT * FROM events WHERE prereq_type = 'lifepath' AND prereq_id = 'baby'", db)
        # choose random baby trait event from list
        baby_trait_event = random_row_to_dict(db_baby_trait_events)
        events.append(baby_trait_event)

        return events
    
    except Exception as e:
        console.write_error(f"Error creating list of baby events: {e}") 

def get_kid_events(character):
    0 # Should be like get_events but only use kid lifepath (to avoid any weird adult things)

def get_events(character):
    # This returns a randomized list of events:
    # 1 relationship conclusion event for every ending relationship (should usually be 1-2 max)
    # 1 relationship event for every continuing relationship (should usually be 3 max)
    # 1 relationship start event if below relationship limit
    # 1 aging event, if any apply
    # 1 trait event
    # 1 keepsake event
    # 4 lifepath events
    # 4 setting events
    RELATIONSHIP_LIMIT = 3
    LIFEPATH_EVENTS_LIMIT = 4
    SETTING_EVENTS_LIMIT = 3

    # each lifepath should wind up with around 10-14 events, depending on relationships 


    # CONSTRUCT QUERIES
    try:
        setting_query = f"SELECT * FROM events WHERE prereq_type = 'setting' AND prereq_id = '{character.setting}'"
        lifepath_query = f"SELECT * FROM events WHERE prereq_type = 'lifepath' AND prereq_id = '{character.lifepath}'"
        age_query = f"SELECT * FROM events WHERE prereq_type = 'age' AND age_min < {character.age} AND age_max > {character.age}"

        # relationship queries as lists (to make it easier to select by individual rleationship), including separate list for any dying/ending characters
        starting_relationship_query = f"SELECT * FROM events WHERE event_type = 'relationship_start' AND ( (prereq_type = 'setting' AND prereq_id = '{character.setting}') OR (prereq_type = 'lifepath' AND prereq_id = '{character.lifepath}') )"
        existing_relationship_queries = []
        ending_relationship_queries = []
        if len(character.relationships > 0):
            relationship_query = "SELECT * FROM events WHERE "
            for relationship in character.relationships:
                # if relationship character will reach max_age during this lifepath, add conclusion event
                if relationship['age'] + character.lifepath['years'] >= relationship['max_age']:
                    ending_relationship_queries.append(f"SELECT * FROM events WHERE event_type = 'relationship_end' AND prereq_id = '{relationship['id']}'")
                # otherwise, add normal event
                else:
                    existing_relationship_queries.append(f"SELECT * FROM events WHERE prereq_type = 'relationship' AND event_type NOT 'relationship_end' AND prereq_id = '{relationship['id']}'")

        # trait query
        trait_query = None
        if len(character.traits > 0):
            trait_query = "SELECT * FROM events WHERE "
            for trait in character.traits:
                trait_query += f"prereq_type = 'trait' AND prereq_id = '{trait['id']}' OR '"
            trait_query = trait_query[0:-3]

        # keepsake query
        keepsake_query = None
        if len(character.keepsakes > 0):
            keepsake_query = "SELECT * FROM events WHERE "
            for keepsake in character.keepsakes:
                keepsake_query += f"prereq_type = 'keepsake' AND prereq_id = '{keepsake['id']}' OR '"
            keepsake_query = keepsake_query[0:-3]

    except Exception as e:
        console.write_error(f"Error constructing event queries: {e}")

    # MAKE QUERIES AND FILL EVENT LIST
    try:
        event_dicts = []

        # add a relationship-end event for each relationship that will end
        try:
            if len(ending_relationship_queries) > 0:
                for query in ending_relationship_queries:
                    db_relationship_end = pd.read_sql_query(query, db)
                    event_dicts.append(random_row_to_dict(db_relationship_end))
        except Exception as e:
            console.write_error(f"Error getting relationship conclusion event: {e}") 

        # add relationship event for each relationship
        try:
            if len(existing_relationship_queries) > 0:
                for query in existing_relationship_queries:
                    db_relationship = pd.read_sql_query(query, db)
                    event_dicts.append(random_row_to_dict(db_relationship))
        except Exception as e:
            console.write_error(f"Error getting relationship event: {e}") 

        # add new relationship if below relationship limit
        try:
            if len(character.relationships) < RELATIONSHIP_LIMIT:
                db_new_relationship = pd.read_sql_query(starting_relationship_query, db)
                event_dicts.append(random_row_to_dict(db_new_relationship))
        except Exception as e:
            console.write_error(f"Error getting relationship start event: {e}") 

        # add an aging event if any
        try:
            db_age_events = pd.read_sql_query(age_query, db)
            if len(db_age_events) > 0:
                event_dicts.append(random_row_to_dict(db_age_events))
        except Exception as e:
            console.write_error(f"Error getting aging event: {e}") 

        # add a trait event
        try:
            if len(character.traits) > 0:
                db_trait_events = pd.read_sql_query(trait_query, db)
                event_dicts.append(random_row_to_dict(db_trait_events))
        except Exception as e:
            console.write_error(f"Error getting trait event: {e}")

        # add a keepsake event
        try:
            if len(character.keepsakes) > 0:
                db_keepsake_events = pd.read_sql_query(keepsake_query, db)
                event_dicts.append(random_row_to_dict(db_keepsake_events))
        except Exception as e:
            console.write_error(f"Error getting keepsake event: {e}")

        # add lifepath events to limit
        try:
            db_lifepath_events = pd.read_sql_query(lifepath_query, db)
            lifepath_event_dicts = db_lifepath_events.to_dict(orient='records')
            # check that there are enough lifepath events
            if len(lifepath_event_dicts) < LIFEPATH_EVENTS_LIMIT:
                raise Exception(f"Couldn't find enough events for lifepath {character.lifepath['id']}")
            # populate list of random lifepath events
            chosen_dicts = []
            while len(chosen_dicts) < LIFEPATH_EVENTS_LIMIT:
                random_index = random.randint(len(lifepath_event_dicts))
                chosen_dicts.append(lifepath_event_dicts.pop(random_index))
            # add those events to event list
            event_dicts.extend(chosen_dicts)
        except Exception as e:
            console.write_error(f"Error getting lifepath events: {e}")

        # add setting events to limit
        try:
            db_setting_events = pd.read_sql_query(setting_query, db)
            setting_event_dicts = db_setting_events.to_dict(orient='records')
            # check that there are enough setting events
            if len(setting_event_dicts) < SETTING_EVENTS_LIMIT:
                raise Exception(f"Couldn't find enough events for setting {character.setting['id']}")
            # populate list of random setting events
            chosen_dicts = []
            while len(chosen_dicts) < SETTING_EVENTS_LIMIT:
                random_index = random.randint(len(setting_event_dicts))
                chosen_dicts.append(setting_event_dicts.pop(random_index))
            # add those events to event list
            event_dicts.extend(chosen_dicts)
        except Exception as e:
            console.write_error(f"Error getting setting events: {e}")

        # randomize event order and return list
        random.shuffle(event_dicts)
        return event_dicts
    
    except Exception as e:
        console.write_error(f"Error compiling list of events: {e}") 

def run_event(event_dict, character):
    # rewrite to make test non-random -- skill is above or below threshhold
    try:

        success = True

        # write setup
        console.write(gameparser.parse_pronouns(event_dict['setup'], character))

        # if a test, check score and note whether successful
        if (event_dict['test_type']) == 'ability':
            if character.get_ability(event_dict['test_id'])['total'] > event_dict['test_min']:
                console.write_gain(f"Ability: {event_dict['test_id']} - success!")
            else:
                console.write_loss(f"Ability: {event_dict['test_id']} - failed!")
                success = False

        elif (event_dict['test_type']) == 'skill':
            if character.get_skill(event_dict['test_id'])['total'] > event_dict['test_min']:
                console.write_gain(f"Skill: {event_dict['test_id']} - success!")
            else:
                console.write_loss(f"Skill: {event_dict['test_id']} - failed!")
                success = False

        elif (event_dict['test_type']) == 'motivation':
            if character.get_motivation(event_dict['test_id'])['total'] > event_dict['test_min']:
                console.write_gain(f"Motivation: {event_dict['test_id']} - success!")
            else:
                console.write_loss(f"Motivation: {event_dict['test_id']} - failed!")
                success = False

        # write results
        if success:
            console.write(gameparser.parse_pronouns(event_dict['success_description'], character))
            run_effects(gameparser.parse_effects(event_dict['success_effect']), character)
        else:
            console.write(gameparser.parse_pronouns(event_dict['failure_description'], character))
            run_effects(gameparser.parse_effects(event_dict['failure_effect']), character)

        # if event_dict['success_description'] != 'NULL' and event_dict['failure_description'] != 'NULL':

        #     # test -- later, add logic to test whatever is higher, relevant ability or skill
        #     if random.randint(1, 10) >= int(event_dict['difficulty']):
        #         event_string += f" {event_dict['success_description']}"
        #         effects = gameparser.parse_effects(event_dict['success_effect'])
        #     else:
        #         event_string += f" {event_dict['failure_description']}"
        #         effects = gameparser.parse_effects(event_dict['failure_effect'])

        #     console.write(gameparser.parse_pronouns(event_string, character))

        #     run_effects(effects, character)

    except Exception as e:
        console.write_error(f"Error running event {event_dict['id']}: {e}") 

def run_effects(effects, character):
    # update character stats with effects, console.write results
    try:
        effects_results = character.update_stats(effects)
        for result in effects_results: # console.write in the correct color
            if result['change'] == 'gain':
                if result['success'] == True:
                    console.write_gain(result['message'])
                else:
                    console.write_gain_failed(result['message'])
            elif result['change'] == 'loss':
                if result['success'] == True:
                    console.write_loss(result['message'])
                else:
                    console.write_loss_failed(result['message'])
    except Exception as e:
        console.write_error(f"Error processing list of effects {effects}: {e}") 

def get_situation(setting):
    # choose random turning point from setting and return it
    try:
        db_situations = pd.read_sql_query(f"SELECT * FROM situations WHERE setting = '{setting}'", db)
        return random_row_to_dict(db_situations)
    except Exception as e:
        console.write_error(f"Error getting situation: {e}") 

def run_situation(situation_dict, character):
    # print situation info. Originally this was going to be more involved, 
    # but most of the remaining logic is now in get_opportunities
    try:
        console.write(situation_dict['headline'])
        console.write(gameparser.parse_pronouns(situation_dict['description'], character))
        effects = gameparser.parse_effects(situation_dict['effects'])
        run_effects(effects, character)
    except Exception as e:
        console.write_error(f"Error running situation {situation_dict['id']}: {e}") 

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
            raise Exception(console.write_error("Not enough normal/continuation opportunities to fill out list."))
    except Exception as e:
        console.write_error(f"Error retrieving opportunities from database: {e}") 
       
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
            console.write_error(f"Error adding random opportunities to choice list: {e}")
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
            console.write_error(f"Error adding random opportunities to choice list: {e}")
            traceback.print_exc()

        return opportunity_choices

    except Exception as e:
        console.write_error(f"Error populating list of opportunities: {e}") 
        
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
            character_ranks['abilities'][ability] = character.get_ability(ability)['total']
        for skill in skills_list:
            character_ranks['skills'][skill] = character.get_skill(skill)['total']
        for motivation in motivations_list:
            for motivation_dict in character.motivations.values():
                if motivation_dict['high'] == motivation:
                    character_ranks['motivations'][motivation] = character.get_motivation(motivation_dict['id'])['total']
                elif motivation_dict['low'] == motivation:
                    character_ranks['motivations'][motivation] = character.get_motivation(motivation_dict['id'])['total'] * -1
        return character_ranks
    
    except Exception as e:
        console.write_error(f"Error getting character ranks in abilities/skills/motivations for opportunity {opportunity_dict['id']}: {e}") 

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
        console.write_error(f"Error adding best skill/ability match to list of opportunities: {e}") 

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
        console.write_error(f"Error adding best motivation match to list of opportunities: {e}") 
        
def choose_opportunity(opportunity_dict_list, character):
    # takes opportunity_dict_list, prints choices to screen, and returns the choice dict
    
    try:
        intro_text = gameparser.parse_pronouns("{Name} considers the opportunities before {obj}...", character)

        choices = []

        # for each choice, compile text
        for index in range(len(opportunity_dict_list)):
            opportunity_dict = opportunity_dict_list[index]
            console.write(opportunity_dict)
            choice_text = ''
            # add description
            choice_text += f"{index+1}: {gameparser.parse_pronouns(opportunity_dict['choice_prompt'], character)}"
            # add risk
            choice_text += f"\n   Risk: {opportunity_dict['risk'].capitalize()}"
            # list bonuses
            bonuses = '\n   Bonuses:'
            for item_type in opportunity_dict['character_ranks']: # ie 'abilities'
                # check if there are abilities/skills/motivations in character_ranks
                if item_type in ('abilities', 'skills', 'motivations'):
                    relevant_bonuses = []
                    if len(opportunity_dict['character_ranks'][item_type]) > 0:
                        # if there are, color and add the non-zero ones to a relevant_bonuses list
                        for item, value in opportunity_dict['character_ranks'][item_type].items():
                            if value > 0:
                                relevant_bonuses.append(f"[green]{item.capitalize()}: {value}[/green], ")
                            elif value < 0:
                                relevant_bonuses.append(f"[red]{item.capitalize()}: {value}[/red], ")
                    # if there were relevant_bonuses, add a printed list of them, including category name
                    if len(relevant_bonuses) > 0:
                        bonuses += f" {item_type.capitalize()}: "
                        for bonus in relevant_bonuses:
                            bonuses += bonus
            # add bonuses to choice_text
            choice_text += bonuses
            # add choice_text to choices
            choices.append(choice_text)

        # write the choice options, and take 1, 2, 3, or 4 as responses
        valid_choice = False
        while valid_choice == False:
            console.write(intro_text)
            for choice in choices:
                console.write(choice)
            choice = console.read(gameparser.parse_pronouns('Which does {Name} choose?', character))
            if choice in ('1','2','3','4'):
                valid_choice = True
            else:
                console.write('...')

        return opportunity_dict_list[int(choice)-1]
    
    except Exception as e:
        console.write_error(f"Error choosing opportunities: {e}") 

def run_opportunity(opportunity_dict, character):
    # run chosen opportunity, including any changes to character.
    # returns opportunity's lifepath id, 
    try:

        success = True

        # write setup
        console.write(gameparser.parse_pronouns(opportunity_dict['setup'], character))

        # if a test, check score and note whether successful
        if (opportunity_dict['test_type']) == 'ability':
            if character.get_ability(opportunity_dict['test_id'])['total'] > opportunity_dict['test_min']:
                console.write_gain(f"Ability: {opportunity_dict['test_id']} - success!")
            else:
                console.write_loss(f"Ability: {opportunity_dict['test_id']} - failed!")
                success = False

        elif (opportunity_dict['test_type']) == 'skill':
            if character.get_skill(opportunity_dict['test_id'])['total'] > opportunity_dict['test_min']:
                console.write_gain(f"Skill: {opportunity_dict['test_id']} - success!")
            else:
                console.write_loss(f"Skill: {opportunity_dict['test_id']} - failed!")
                success = False

        elif (opportunity_dict['test_type']) == 'motivation':
            if character.get_motivation(opportunity_dict['test_id'])['total'] > opportunity_dict['test_min']:
                console.write_gain(f"Motivation: {opportunity_dict['test_id']} - success!")
            else:
                console.write_loss(f"Motivation: {opportunity_dict['test_id']} - failed!")
                success = False

        # write results
        if success:
            console.write(gameparser.parse_pronouns(opportunity_dict['success_description'], character))
            run_effects(gameparser.parse_effects(opportunity_dict['success_effect']), character)
        else:
            console.write(gameparser.parse_pronouns(opportunity_dict['failure_description'], character))
            run_effects(gameparser.parse_effects(opportunity_dict['failure_effect']), character)

    except Exception as e:
        console.write_error(f"Error running opportunity {opportunity_dict['id']}: {e}")    

    # NOTE TO SELF - reconsole.write choice descriptions to be more personal and evocative


def end_game():
    console.write("Game Shutting Down...")
    return False, False

#---------------- HELPER FUNCTIONS ----------------#

def event_to_dict(event_id_string):
    # returns event dict directly from id, without having to go through get_events
    try:
        db_event = pd.read_sql_query(f"SELECT * FROM events WHERE id = '{event_id_string}'", db)
        return db_event.iloc[0].to_dict()
    except Exception as e:
        console.write_error(f"Error retrieiving event {event_id_string}: {e}") 

def convert_motivation(motivation, rank=0):
    db_motivation = pd.read_sql_query(f"SELECT * FROM motivations WHERE id = '{motivation}' OR low = '{motivation}' OR high = '{motivation}'")
    if len(db_motivation) == 0:
        raise Exception(console.write_error(f"Error converting motivation: '{motivation}' not found in database"))
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


# console.write and console.read are helper functions.
# they console.write and console.read to cli or webhooks, depending on the program's mode


if __name__ == "__main__":

    testperson = character("Testperson", "male", "peasant")
    console.write(f"Name: {testperson.name}")

    testperson.change_lifepath("kid_peasant")
    console.write(f"Lifepath: {testperson.lifepath}")

    run_event(event_to_dict("baby_adventurous"), testperson)
    run_event(event_to_dict("peasant_kid_first_plant"), testperson)
    run_event(event_to_dict("peasant_kid_herding"), testperson)
    # run_event(event_to_dict("peasant_kid_church"), testperson)
    run_event(event_to_dict("peasant_kid_chores"), testperson)
    run_event(event_to_dict("peasant_kid_trapping"), testperson)
    run_event(event_to_dict("peasant_kid_bully"), testperson)
    testperson.gain_motivation('intellectual')
    testperson.gain_ability('intellect')
    testperson.gain_ability('intellect')
    testperson.gain_ability('intellect')
    testperson.gain_ability('intellect')
    testperson.gain_ability('strength')
    testperson.gain_trait('strong')
    testperson.gain_trait('shy')

    console.write(f"Motivations: {testperson.motivations}")
    console.write(f"Abilities: {testperson.abilities}")
    console.write(f"Skills: {testperson.skills}")
    console.write(f"Traits: {testperson.traits}")

    console.write(f"Current Strength: {testperson.get_ability('strength')}")
    console.write(f"Current Sociability: {testperson.get_motivation('social')}")
    console.write(f"Current Solitariness: {testperson.get_motivation('solitary')}")

    situation = get_situation("peasant") # at this time, only one possible result: peasant_fort_construction
    console.write(f"Situation: {situation}")
    run_situation(situation, testperson)

    opportunities = get_opportunities(situation, testperson)
    console.write("Opportunities:")
    choice = choose_opportunity(opportunities, testperson)
