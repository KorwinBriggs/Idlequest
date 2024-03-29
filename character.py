import sqlite3
import random
import numpy as np
import pandas as pd

import console
import gameparser
from dbhelpers import row_to_dict, random_row_to_dict

db = sqlite3.connect("db/gamedata.db")

class character:

    def __init__(self, name, gender, setting):

        self.name = name

        self.age = 0

        self.gender = gender

        self.pronouns = self.__character_creation_pronouns(name, gender)
        self.sub = self.pronouns["subjective"]
        self.obj = self.pronouns["objective"]
        self.pos = self.pronouns["possessive"]


        self.appearances = {}
        # dict of appearances by id.

        self.ABILITY_MAX = 5
        self.ABILITY_MIN = 0
        self.abilities = self.__character_creation_abilities()
        # dict of abilities by id, range 0 to 5

        self.SKILL_MAX = 10
        self.SKILL_MIN = 0
        self.skills = self.__character_creation_skills()
        # dict of all skills by id and their levels. range 0 to 10

        self.MOTIVATION_MAX = 5
        self.MOTIVATION_MIN = -5
        self.motivations = self.__character_creation_motivations()
        # dict of motivations by id, range -5 to 5

        self.traits = {}
        # dicts of traits with key of trait_id. includes modifiers

        self.keepsakes = {}
        # like traits, but keepsakes

        self.relationships = {}
        # like traits, but relationships (includes ages and names)

        self.setting = setting
        # current setting id

        self.lifepath = {
        # current lifepath id
            "id": "newborn",
            "name": "newborn",
            "years": "0",
        }

        self.history = []
        # list of dictionaries, like, 
        #   {
        #       age: 6
        #       event: stairs_fall
        #       change: add trait hurty_foot
        #       string: "Harald fell down the stairs and broke his little footsie wootsie."
        #   }
        # this is added to throughout gameplay and used afterwords to make a log/postscript

        self.seen_opportunities = []

    def update_stats(self, stats_dict = {}):
        # go through stats dict from parse_effects or parse_prereqs and update stats
        # if called without dict, simply updates stats

        result = {
        'skills': {},
        'traits': {},
        'abilities': {},
        'motivations': {},
        'keepsakes': {},
        'relationships': {},
        'lifepaths': {},
        'settings': {},
        'appearances': {}
        }
        try:
            return_list = []
            if 'skills' in stats_dict:
                for skill, mod in stats_dict['skills'].items(): # ex {'farming': 3}
                    if mod > 0:
                        return_list.append(self.gain_skill(skill, mod))
                    elif mod < 0:
                        return_list.append(self.lose_skill(skill, mod))
            if 'abiltiies' in stats_dict:
                for ability, mod in stats_dict['abilities'].items():
                    if mod > 0:
                        return_list.append(self.gain_ability(ability, mod))
                    elif mod < 0:
                        return_list.append(self.lose_ability(ability, mod))
            if 'motivations' in stats_dict:
                for motivation, mod in stats_dict['motivations'].items():
                    if mod > 0:
                        return_list.append(self.gain_motivation(motivation, mod))
                    elif mod < 0:
                        return_list.append(self.lose_motivation(motivation, mod))
            if 'traits' in stats_dict:
                for trait, mod in stats_dict['traits'].items():
                    if isinstance(mod, int):
                        if mod > 0:
                            return_list.append(self.gain_trait(trait))
                        elif mod < 0:
                            return_list.append(self.lose_trait(trait))
                    else:
                        return_list.append(self.change_trait(trait, mod))
            if 'keepsakes' in stats_dict:
                for keepsake, mod in stats_dict['keepsakes'].items():
                    if isinstance(mod, int):
                        if mod > 0:
                            return_list.append(self.gain_keepsake(keepsake))
                        elif mod < 0:
                            return_list.append(self.lose_keepsake(keepsake))
                    else:
                        return_list.append(self.change_keepsake(keepsake, mod))
            if 'relationships' in stats_dict:
                for relationship, mod in stats_dict['relationships'].items():
                    if isinstance(mod, int):
                        if mod > 0:
                            return_list.append(self.gain_relationship(relationship))
                        elif mod < 0:
                            return_list.append(self.lose_relationship(relationship))
                    else:
                        return_list.append(self.change_relationship(relationship, mod))
            if 'appearances' in stats_dict:
                for appearance, mod in stats_dict['appearances'].items():
                    if isinstance(mod, int):
                        if mod > 0:
                            return_list.append(self.gain_appearance(appearance))
                        elif mod < 0:
                            return_list.append(self.lose_appearance(appearance))
                    else:
                        return_list.append(self.change_appearance(appearance, mod))
            if 'lifepaths' in stats_dict:
                self.change_lifepath(stats_dict['lifepaths'][0]['id'])
            return return_list
        except Exception as e:
            console.write_error(f"Error updating character stats: {e}")

    def get_skill(self, skill_id):
        # returns skill dict like
        # {'farming': { ((id, name, etc)), 'rank': 1, 'modifiers': {traits: {green_thumb: 2}, keepsakes: {family_farm:1} }, 'total': 4 }
        try:
            # check that skill exists
            if skill_id not in self.skills:
                raise Exception(console.write_error(f'Error getting skill: {skill_id} not found in character skills.'))
            else:
                # establish return_dict, add empty traits/keepsakes sections, default total to character skill ranks
                return_dict = self.skills[skill_id]
                return_dict['modifiers'] = {'abilities': {}, 'traits': {}, 'keepsakes': {}}
                return_dict['total'] = return_dict['rank'] 

                # go through each trait and compile relevant modifiers
                for trait in self.traits: # ie 'green_thumb'
                    if 'skills' in self.traits[trait]['modifiers']: # check it has a skills section
                        if skill_id in self.traits[trait]['modifiers']['skills']: # ie farming
                            # if trait modifies the skill in question, add ie {'green_thumb': 1} to return_dict modifiers trait list
                            return_dict['modifiers']['traits'][trait] = self.traits[trait]['modifiers']['skills'][skill_id]
                            # and update the total
                            return_dict['total'] += self.traits[trait]['modifiers']['skills'][skill_id]

                # do same for keepsakes
                for keepsake in self.keepsakes: # ie 'family_farm'
                    if 'skills' in self.keepsakes[keepsake]['modifiers']: # check it has a skills section
                        if skill_id in self.keepsakes[keepsake]['modifiers']['skills']: # ie farming
                            # if trait modifies the skill in question, add ie {'family_farm': 1} to return_dict modifiers trait list
                            return_dict['modifiers']['keepsakes'][keepsake] = self.keepsakes[keepsake]['modifiers']['skills'][skill_id]
                            # and update the total
                            return_dict['total'] += self.keepsakes[keepsake]['modifiers']['skills'][skill_id]
                
                # get relevant abilities and their average
                ability1 = self.skills[skill_id]['ability1']
                ability2 = self.skills[skill_id]['ability2']
                return_dict['modifiers']['abilities'][ability1] = self.get_ability(ability1)['total']
                return_dict['modifiers']['abilities'][ability2] = self.get_ability(ability2)['total']
                return_dict['modifiers']['abilities']['average'] = (return_dict['modifiers']['abilities'][ability1] + return_dict['modifiers']['abilities'][ability2]) / 2
                # if 'total' is less than the relevant ability average, use the average
                if return_dict['total'] < return_dict['modifiers']['abilities']['average']:
                    return_dict['total'] = return_dict['modifiers']['abilities']['average']

                return return_dict
            
        except Exception as e:
            console.write_error(f"Error getting character skill level for {skill_id}: {e}")             

    def gain_skill(self, skill_id, num = 1):
        try:
            if skill_id not in self.skills:
                raise Exception(f"Could not find skill: {skill_id}")
        
            stat, change, success, message = 'skill', 'gain', True, ''
            self.skills[skill_id]['rank'] += num
            
            if self.skills[skill_id]['rank'] > self.SKILL_MAX:
                self.skills[skill_id]['rank'] = self.SKILL_MAX
                success = False
                message = f"Skill: {self.skills[skill_id]['name'].capitalize()} can't go higher!"
            else:
                # message = ''
                # message.append('+') for i in range(num)
                message = f"+ Skill: {self.skills[skill_id]['name'].capitalize()}"

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        except Exception as e:
            console.write_error(f"Error adding skill {skill_id} to character: {e}")

    def lose_skill(self, skill_id, num = 1):
        try:
            if skill_id not in self.skills:
                raise Exception(f"Could not find skill: {skill_id}")
            
            stat, change, success, message = 'skill', 'loss', True, ''
            self.skills[skill_id]['rank'] -= num
            
            if self.skills[skill_id]['rank'] < self.SKILL_MIN:
                self.skills[skill_id]['rank'] = self.SKILL_MIN
                success = False
                message = f"Skill: {self.skills[skill_id]['name'].capitalize()} can't go lower!"
            else:
                message = f"- Skill: {self.skills[skill_id]['name'].capitalize()}"

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
    
        except Exception as e:
            console.write_error(f"Error removing skill {skill_id} from character: {e}")

    def get_ability(self, ability_id):
        # returns ability dict like
        # {'farming': { ((id, name, etc)), 'rank': 1, 'modifiers': {traits: {green_thumb: 2}, keepsakes: {family_farm:1} }, 'total': 4 }
        try:
            # check that ability exists
            if ability_id not in self.abilities:
                raise Exception(console.write_error(f'Error getting ability: {ability_id} not found in character abilitys.'))
            else:
                # establish return_dict, add empty traits/keepsakes sections, default total to character ability ranks
                return_dict = self.abilities[ability_id]
                return_dict['modifiers'] = {'traits': {}, 'keepsakes': {}}
                return_dict['total'] = return_dict['rank'] 

                # go through each trait and compile relevant modifiers
                for trait in self.traits: # ie 'green_thumb'
                    if 'abilities' in self.traits[trait]['modifiers']: # check it has a abilities section
                        if ability_id in self.traits[trait]['modifiers']['abilities']: # ie farming
                            # if trait modifies the ability in question, add ie {'green_thumb': 1} to return_dict modifiers trait list
                            return_dict['modifiers']['traits'][trait] = self.traits[trait]['modifiers']['abilities'][ability_id]
                            # and update the total
                            return_dict['total'] += self.traits[trait]['modifiers']['abilities'][ability_id]

                # do same for keepsakes
                for keepsake in self.keepsakes: # ie 'family_farm'
                    if 'abilities' in self.keepsakes[keepsake]['modifiers']: # check it has a abilities section
                        if ability_id in self.keepsakes[keepsake]['modifiers']['abilities']: # ie farming
                            # if trait modifies the ability in question, add ie {'family_farm': 1} to return_dict modifiers trait list
                            return_dict['modifiers']['keepsakes'][keepsake] = self.keepsakes[keepsake]['modifiers']['abilities'][ability_id]
                            # and update the total
                            return_dict['total'] += self.keepsakes[keepsake]['modifiers']['abilities'][ability_id]
                
                return return_dict
            
        except Exception as e:
            console.write_error(f"Error getting character ability level for {ability_id}: {e}")             

    def gain_ability(self, ability_id, num = 1):
        try:
            if ability_id not in self.abilities:
                raise Exception(f"Could not find ability: {ability_id}")

            stat, change, success, message = 'ability', 'gain', True, ''
            self.abilities[ability_id]['rank'] += num

            if self.abilities[ability_id]['rank'] > self.ABILITY_MAX:
                self.abilities[ability_id]['rank'] = self.ABILITY_MAX
                success = False
                message = f"Ability: {self.abilities[ability_id]['name'].capitalize()} can't go higher!"
            else:
                message = f"+ Ability: {self.abilities[ability_id]['name'].capitalize()}"

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        except Exception as e:
            console.write_error(f"Error adding ability {ability_id} to character: {e}")

    def lose_ability(self, ability_id, num = 1):
        try:
            if ability_id not in self.abilities:
                raise Exception(f"Could not find ability: {ability_id}")
            
            stat, change, success, message = 'ability', 'loss', True, ''
            self.abilities[ability_id]['rank'] -= num
            
            if self.abilities[ability_id]['rank'] < self.ABILITY_MIN:
                self.abilities[ability_id]['rank'] = self.ABILITY_MIN
                success = False
                message = f"Ability: {self.abilities['ability_id']['name'].capitalize()} can't go lower!"
            else:
                message = f"- Ability: {self.abilities[ability_id]['name'].capitalize()}"

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        except Exception as e:
            console.write_error(f"Error removing ability {ability_id} from character: {e}")

    def get_motivation(self, motivation):
        # returns relevant motivation dict like
        # {'farming': { ((id, name, etc)), 'rank': 1, 'modifiers': {traits: {green_thumb: 2}, keepsakes: {family_farm:1} }, 'total': 4 }
        try:
            # get motivation_id from motivation name
            db_motivation = pd.read_sql_query(f"SELECT * FROM motivations WHERE id = '{motivation}' OR low = '{motivation}' OR high = '{motivation}'", db)
            if len(db_motivation) == 0:
                raise Exception(f"Could not find motivation: {motivation}")
            motivation_dict = row_to_dict(db_motivation)
            motivation_id = motivation_dict['id']
            motivation_low = motivation_dict['low']
            motivation_high = motivation_dict['high']

            # establish return_dict, add empty traits/keepsakes sections, default total to character motivation rank
            return_dict = self.motivations[motivation_id]
            return_dict['modifiers'] = {'traits': {}, 'keepsakes': {}}
            return_dict['total'] = return_dict['rank']

            # go through each trait and compile relevant modifiers
            for trait in self.traits: # ie 'shy'
                if 'motivations' in self.traits[trait]['modifiers']: # if it has a motivations section
                    # if that contains the id or high level (ie 'socialbility' or 'social')
                    if (motivation_id in self.traits[trait]['modifiers']['motivations']) or (motivation_high in self.traits[trait]['modifiers']['motivations']):
                        # then add ie {'sociability': 1} to return_dict modifiers
                        return_dict['modifiers']['traits'][trait] = self.traits[trait]['modifiers']['motivations'][motivation_id]
                        # and add it to the total
                        return_dict['total'] += self.traits[trait]['modifiers']['motivations'][motivation_id]
                    # if it contains the low level version (ie 'solitary')
                    elif (motivation_low in self.traits[trait]['modifiers']['motivations']):
                        # do as above, but turn plusses to minuses and vice versa
                        return_dict['modifiers']['traits'][trait] = self.traits[trait]['modifiers']['motivations'][motivation_id] * -1
                        # and add it to the total
                        return_dict['total'] -= self.traits[trait]['modifiers']['motivations'][motivation_id]

            # then do same for keepsakes
            for keepsake in self.keepsakes: # ie 'shy'
                if 'motivations' in self.keepsakes[keepsake]['modifiers']: # if it has a motivations section
                    # if that contains the id or high level (ie 'socialbility' or 'social')
                    if (motivation_id in self.keepsakes[keepsake]['modifiers']['motivations']) or (motivation_high in self.keepsakes[keepsake]['modifiers']['motivations']):
                        # then add ie {'sociability': 1} to return_dict modifiers
                        return_dict['modifiers']['keepsakes'][keepsake] = self.keepsakes[keepsake]['modifiers']['motivations'][motivation_id]
                        # and add it to the total
                        return_dict['total'] += self.keepsakes[keepsake]['modifiers']['motivations'][motivation_id]
                    # if it contains the low level version (ie 'solitary')
                    elif (motivation_low in self.keepsakes[keepsake]['modifiers']['motivations']):
                        # do as above, but turn plusses to minuses and vice versa
                        return_dict['modifiers']['keepsakes'][keepsake] = self.keepsakes[keepsake]['modifiers']['motivations'][motivation_id] * -1
                        # and add it to the total
                        return_dict['total'] -= self.keepsakes[keepsake]['modifiers']['motivations'][motivation_id]
                
            # now translate it back
            return return_dict

        except Exception as e:
            console.write_error(f"Error getting character motivation level for {motivation_id}: {e}") 

    def gain_motivation(self, motivation, num = 1):
        try:
            # find line in db with motivation name as high or low value
            db_motivation = pd.read_sql_query(f"SELECT * FROM motivations WHERE id = '{motivation}' OR low = '{motivation}' OR high = '{motivation}'", db)
            if len(db_motivation) == 0:
                raise Exception(f"Could not find motivation: {motivation}")
            
            stat, change, success, message = 'motivation', 'gain', True, ''
            motivation_dict = row_to_dict(db_motivation)
            motivation_id = motivation_dict['id']

            # add or remove, as needed
            if motivation == motivation_dict['high'] or motivation == motivation_dict['id']:
                self.motivations[motivation_id]['rank'] += num
            elif motivation == motivation_dict['low']:
                self.motivations[motivation_id]['rank'] -= num

            # if above limit, bring down to limit
            if self.motivations[motivation_id]['rank'] > self.MOTIVATION_MAX:
                self.motivations[motivation_id]['rank'] = self.MOTIVATION_MAX
                success = False
                message = f"Motivation: {motivation.capitalize()} can't go higher!"
            elif self.motivations[motivation_id]['rank'] < self.MOTIVATION_MIN:
                self.motivations[motivation_id]['rank'] = self.MOTIVATION_MIN
                success = False
                message = f"Motivation: {motivation.capitalize()} can't go higher!"
            else:   
                message = f"+ Motivation: {motivation.capitalize()}"

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        except Exception as e:
            console.write_error(f"Error adding motivation {motivation_id} to character: {e}")

    def lose_motivation(self, motivation, num = 1):
        try:
            # find line in db with motivation name as high or low value
            motivation_db = pd.read_sql_query(f"SELECT * FROM motivations WHERE id = '{motivation}' OR low = '{motivation}' OR high = '{motivation}'", db)
            if len(motivation_db) == 0:
                raise Exception(f"Could not find motivation: {motivation}")
            
            stat, change, success, message = 'motivation', 'loss', True, ''
            motivation_dict = motivation_db.to_dict(orient="records")[0]
            motivation_id = motivation_dict['id']

            # add or remove, as needed
            if motivation == motivation_dict['high'] or motivation == motivation_dict['id']:
                self.motivations[motivation_id]['rank'] -= num
            elif motivation == motivation_dict['low']:
                self.motivations[motivation_id]['rank'] += num

            # if above limit, bring down to limit
            if self.motivations[motivation_id]['rank'] > self.MOTIVATION_MAX:
                self.motivations[motivation_id]['rank'] = self.MOTIVATION_MAX
                success = False
                message = f"Motivation: {motivation.capitalize()} can't go lower!"
            elif self.motivations[motivation_id]['rank'] < self.MOTIVATION_MIN:
                self.motivations[motivation_id]['rank'] = self.MOTIVATION_MIN
                success = False
                message = f"Motivation: {motivation.capitalize()} can't go lower!"
            # return statement
            else: 
                message = f"- Motivation: {motivation.capitalize()}"

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        except Exception as e:
            console.write_error(f"Error removing motivation {motivation_id} from character: {e}")
            
    def gain_trait(self, trait_id):
        try:
            stat, change, success, message = 'trait', 'gain', True, ''

            if trait_id not in self.traits:
                # get trait info from db
                db_trait = pd.read_sql_query(f"SELECT * FROM traits WHERE id = '{trait_id}'", db)
                if len(db_trait) == 0:
                    raise Exception(f"Could not find trait: {trait_id}")
                trait_dict = row_to_dict(db_trait)

                # get and parse modifier into trait['modifiers']
                trait_dict['modifiers'] = gameparser.parse_items(trait_dict['modifiers'])

                # save trait dict to traits
                self.traits[trait_id] = trait_dict
                message = f"Trait gained: {self.traits[trait_id]['name'].capitalize()}"
            else:
                message = f"Already had trait: {self.traits[trait_id]['name'].capitalize()}"
                success = False
            
            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error adding trait {trait_id} to character: {e}")

    def lose_trait(self, trait_id):
        try:
            stat, change, success, message = 'trait', 'loss', True, ''

            if not self.__check_if_in_db("traits", trait_id):
                raise Exception(f"Could not find trait: {trait_id}")
            
            if trait_id in self.traits:
                name = self.traits[trait_id]['name'].capitalize()
                self.traits.pop(trait_id)
                message = f"Trait lost: {name}"
            else:
                message = f"Never had trait: {name}"
                success = False

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error removing trait {trait_id} from character: {e}")

    def change_trait(self, old_trait_id, new_trait_id):
        try:
            stat, change, success, message = 'trait', 'change', True, ''

            if old_trait_id not in self.traits:
                raise Exception(f"Character does not have trait {old_trait_id}")
            else:
                old_trait_name = self.traits[old_trait_id]['name'].capitalize()
                self.lose_trait(old_trait_id)
                self.gain_trait(new_trait_id)
                new_trait_name = self.traits[new_trait_id]['name'].capitalize()
                message = f"Trait lost: {old_trait_name}; Trait gained: {new_trait_name}"
                return {'stat': stat, 'change': change, 'success': success, 'message': message}
            
        except Exception as e:
            console.write_error(f"Error updating trait {old_trait_id} to {new_trait_id}: {e}")

    def gain_relationship(self, relationship_id, name=None, age=None):
        try:
            stat, change, success, message = 'relationship', 'gain', True, ''

            if relationship_id not in self.traits:
                # get trait info from db
                db_relationship = pd.read_sql_query(f"SELECT * FROM relationships WHERE id = '{relationship_id}'", db)
                if len(db_relationship) == 0:
                    raise Exception(f"Could not find relationship: {relationship_id}")
                relationship_dict = row_to_dict(db_relationship)

                # generate name if none provided
                if name == None:
                    namegen = relationship_dict['namegen'].split(' ')
                    name = ''
                    for part in namegen:
                        db_name_part = pd.read_sql_query(f"SELECT name FROM namegen WHERE type = '{part}' and gender = '{relationship_dict['gender']}'", db)
                        if len(db_name_part) == 0:
                            name += part
                        else:
                            name += random_row_to_dict(db_name_part)['name']
                        name += ' '
                    relationship_dict['name'] = name.strip()
                else:
                    relationship_dict['name'] = name

                # generate starting age
                if age == None:
                    relationship_dict['age'] = random.randint(relationship_dict['start_age_min'], relationship_dict['start_age_max'])
                else:
                    relationship_dict['age'] = age
                relationship_dict['max_age'] = random.randint(relationship_dict['end_age_min'], relationship_dict['end_age_max'])

                # save relationship dict to traits
                self.relationships[relationship_id] = relationship_dict
                message = f"Relationship gained: {self.relationships[relationship_id]['name'].capitalize()}"
            else:
                message = f"Already had relationship: {self.relationships[relationship_id]['name'].capitalize()}"
                success = False
            
            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error adding relationship {relationship_id} to character: {e}")

    def lose_relationship(self, relationship_id):
        try:
            stat, change, success, message = 'relationship', 'loss', True, ''

            if not self.__check_if_in_db("relationships", relationship_id):
                raise Exception(f"Could not find relationship: {relationship_id}")
            
            if relationship_id in self.relationships:
                name = self.relationships[relationship_id]['name']
                self.relationships.pop(relationship_id)
                message = f"relationship lost: {name}"
            else:
                message = f"Never had relationship: {name}"
                success = False

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error removing relationship {relationship_id} from character: {e}")

    def change_relationship(self, old_relationship_id, new_relationship_id):
        try:
            stat, change, success, message = 'relationship', 'change', True, ''

            if old_relationship_id not in self.relationships:
                raise Exception(f"Character does not have relationship {old_relationship_id}")
            else:
                name = self.relationships[old_relationship_id]['name']
                age = self.relationships[old_relationship_id]['age']
                self.lose_relationship(old_relationship_id)
                self.gain_relationship(new_relationship_id, name, age)

                message = f"{name} has become a {self.relationships[new_relationship_id]['descriptor']}"
                return {'stat': stat, 'change': change, 'success': success, 'message': message}
            
        except Exception as e:
            console.write_error(f"Error updating relationship {old_relationship_id} to {new_relationship_id}: {e}")

    def gain_keepsake(self, keepsake_id):
        try:
            stat, change, success, message = 'keepsake', 'gain', True, ''

            if keepsake_id not in self.keepsakes:
                # get keepsake dict from db
                db_keepsake = pd.read_sql_query(f"SELECT * FROM keepsakes WHERE id = '{keepsake_id}'", db)
                if len(db_keepsake) == 0:
                    raise Exception(f"Could not find keepsake: {keepsake_id}")
                keepsake_dict = row_to_dict(db_keepsake)

                # get and parse modifier into trait['modifiers']
                keepsake_dict['modifiers'] = gameparser.parse_items(keepsake_dict['modifiers'])
                
                # save keepsake dict to keepsakes
                self.keepsakes[keepsake_id] = keepsake_dict
                message = f"Keepsake gained: {self.keepsake[keepsake_id]['name'].capitalize()}"
            else:
                message = f"Already had keepsake: {self.traits[keepsake_id]['name'].capitalize()}"
                success = False

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error adding keepsake {keepsake_id} to character: {e}")

    def lose_keepsake(self, keepsake_id):
        try:
            stat, change, success, message = 'keepsake', 'loss', True, ''
            
            if not self.__check_if_in_db("keepsakes", keepsake_id):
                raise Exception(f"Could not find keepsake: {keepsake_id}")
            
            if keepsake_id in self.keepsakes:
                name = self.keepsakes[keepsake_id]['name'].capitalize()
                self.keepsakes.pop(keepsake_id)
                message = f"Keepsake lost: {name}"
            else:
                message = f"Never had keepsake: {name}"
                success = False

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error removing keepsake {keepsake_id} from character: {e}")

    def change_keepsake(self, old_keepsake_id, new_keepsake_id):
        try:
            stat, change, success, message = 'keepsake', 'change', True, ''

            if old_keepsake_id not in self.keepsakes:
                raise Exception(f"Character does not have keepsake {old_keepsake_id}")
            else:
                old_keepsake_name = self.keepsakes[old_keepsake_id]['name'].capitalize()
                self.lose_keepsake(old_keepsake_id)
                self.gain_keepsake(new_keepsake_id)
                new_keepsake_name = self.keepsakes[new_keepsake_id]['name'].capitalize()
                message = f"Keepsake lost: {old_keepsake_name}; Keepsake gained: {new_keepsake_name}"
                return {'stat': stat, 'change': change, 'success': success, 'message': message}
            
        except Exception as e:
            console.write_error(f"Error updating keepsake {old_keepsake_id} to {new_keepsake_id}: {e}")

    def gain_appearance(self, appearance_id):
        try:
            # print(f'gain_appearance called: {appearance_id}')
            stat, change, success, message = 'appearance', 'gain', True, ''

            if appearance_id not in self.appearances:
                db_appearance = pd.read_sql_query(f"SELECT * FROM appearances WHERE id = '{appearance_id}'", db)
                if len(db_appearance) == 0:
                    raise Exception(f"Could not find appearance: {appearance_id}")
                
                appearance_dict = row_to_dict(db_appearance)
                self.appearances[appearance_id] = appearance_dict
                message = f"Appearance gained: {self.appearances[appearance_id]['name'].capitalize()}"
            else:
                message = f"Already had appearance: {self.appearances[appearance_id]['name'].capitalize()}"
                success = False

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error adding appearance {appearance_id} to character: {e}")

    def lose_appearance(self, appearance_id):
        try:
            stat, change, success, message = 'appearance', 'loss', True, ''
            
            if not self.__check_if_in_db("appearances", appearance_id):
                raise Exception(f"Could not find appearance: {appearance_id}")
            
            if appearance_id in self.appearances:
                self.appearances.pop(appearance_id)
                message = f"Appearance lost: {self.appearances[appearance_id]['name'].capitalize()}"
            else:
                message = f"Never had appearance: {self.appearances[appearance_id]['name'].capitalize()}"
                success = False

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error removing appearance {appearance_id} from character: {e}")

    def change_appearance(self, old_appearance_id, new_appearance_id):

        try:
            stat, change, success, message = 'appearance', 'change', True, ''

            if old_appearance_id not in self.appearances:
                raise Exception(f"Character does not have appearance {old_appearance_id}")
            else:
                old_appearance_name = self.appearances[old_appearance_id]['name'].capitalize()
                self.lose_appearance(old_appearance_id)
                self.gain_appearance(new_appearance_id)
                new_appearance_name = self.appearances[new_appearance_id]['name'].capitalize()
                message = f"appearance lost: {old_appearance_name}; appearance gained: {new_appearance_name}"
                return {'stat': stat, 'change': change, 'success': success, 'message': message}
            
        except Exception as e:
            console.write_error(f"Error updating appearance {old_appearance_id} to {new_appearance_id}: {e}")

    def change_lifepath(self, lifepath_id):
        try:
            # load new lifepath details from db
            db_lifepath = pd.read_sql_query(f"SELECT * FROM lifepaths WHERE id = '{lifepath_id}'", db)
            if len(db_lifepath) == 0:
                raise Exception(f"Could not find lifepath: {lifepath}")
            lifepath = row_to_dict(db_lifepath)
            self.lifepath = lifepath
            self.setting = lifepath['setting']
            self.abilities['wealth']['rank'] = lifepath['wealth']
            self.abilities['fame']['rank'] = lifepath['fame']
            self.update_stats(gameparser.parse_effects(self.lifepath['start_bonus']))
        except Exception as e:
            console.write_error(f"Error moving character to lifepath {lifepath_id}: {e}")

    def age(self, years):
        self.age += years
        for relationship in self.relationships:
            relationship['age'] += years

    def get_age(self):
        return int(self.age)

    def __character_creation_pronouns(self, name, gender):
        if gender == "male":
            return {
                'name': name,
                'subjective': 'he',
                'objective': 'him',
                'possessive': 'his'
            }
        if gender == "female":
            return {
                'name': name,
                'subjective': 'she',
                'objective': 'her',
                'possessive': 'her'
            }
        raise Exception(f"Problem assigning pronouns for gender {gender}")
    
    def __character_creation_skills(self):
        try:
            db_dataframe = pd.read_sql_query(f"SELECT * FROM skills WHERE id IS NOT NULL", db)
            if len(db_dataframe) == 0:
                raise Exception(f"Could not find skills table.")
            db_dict = db_dataframe.to_dict(orient='records')
            result_dict = {}
            for entry in db_dict:
                result_dict[entry['id']] = entry
                result_dict[entry['id']]['rank'] = 0
            return result_dict
        except Exception as e:
            console.write_error(f"Error adding default values from skills table: {e}")
    
    def __character_creation_abilities(self):
        try:
            db_dataframe = pd.read_sql_query(f"SELECT * FROM abilities WHERE id IS NOT NULL", db)
            if len(db_dataframe) == 0:
                raise Exception(f"Could not find abilities table.")
            db_dict = db_dataframe.to_dict(orient='records')
            result_dict = {}
            for entry in db_dict:
                result_dict[entry['id']] = entry
                result_dict[entry['id']]['rank'] = random.randint(1,3)
            result_dict['health']['rank'] = self.ABILITY_MAX
            result_dict['wealth']['rank'] = self.ABILITY_MIN
            result_dict['fame']['rank'] = self.ABILITY_MIN
            result_dict['reputation']['rank'] = self.ABILITY_MIN
            return result_dict
        except Exception as e:
            console.write_error(f"Error adding default values from skills table: {e}")

    def __character_creation_motivations(self):
        try:
            db_dataframe = pd.read_sql_query(f"SELECT * FROM motivations WHERE id IS NOT NULL", db)
            if len(db_dataframe) == 0:
                raise Exception(f"Could not find motivations table.")
            db_dict = db_dataframe.to_dict(orient='records')
            result_dict = {}
            for entry in db_dict:
                result_dict[entry['id']] = entry
                result_dict[entry['id']]['rank'] = 0
            return result_dict
        except Exception as e:
            console.write_error(f"Error adding default values from skills table: {e}")

      
    def __check_if_in_db(self, table, id):
        # check that the skill is in the db
        db_skill = pd.read_sql_query(f"SELECT * FROM {table} WHERE id = '{id}'", db)
        if len(db_skill) == 0:
            return None
        return True

    def appearanceToString(self):
        # build query from appearance ids
        query = "SELECT name FROM appearance WHERE "
        for index in range(len(self.appearances)):
            query += "id = '" + self.appearances[index] + "'"
            if index < len(self.appearances)-1:
                query += " OR "

        # query db, arrange into ___, ___, and ___ format
        db_appearance_names = pd.read_sql_query(query, db)
        return_string = ''
        for index in range(len(db_appearance_names)):
            return_string += db_appearance_names.iloc[index].values[0]
            if index < len(db_appearance_names) - 2:
                return_string += ', '
            if index == len(db_appearance_names) - 2:
                return_string += ', and '
        
        return return_string


if __name__ == "__main__":

    testchar = character("Test Character", "male", "peasant")
    # print(testchar.gain_motivation('rebellious'))
    # print(testchar.lose_motivation('pious'))

    # print(testchar.update_stats({'gain': {'skills': ['farming'], 'traits': ['jolly'], 'abilities': [], 'motivations': [], 'keepsakes': [], 'lifepaths': []}, 'lose': {'skills': ['animal_handling'], 'traits': [], 'abilities': [], 'motivations': [], 'keepsakes': [], 'lifepaths': []}}))
    # print(testchar.motivations)
    # print(testchar.skills)
    # print(testchar.abilities)
    # print(testchar.traits)
    # testchar.update_stats({'pop':'poop'})
    console.write(testchar.update_stats({'relationships': {'pet_dog': 1}}))
    console.write(testchar.relationships)
    console.write(testchar.update_stats({'relationships': {'pet_dog': 'miller'}}))
    console.write(testchar.relationships)
    console.write(testchar.update_stats({'relationships': {'miller': -1}}))
    console.write(testchar.relationships)
    # print(testchar.abilities)