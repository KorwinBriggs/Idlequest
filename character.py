import sqlite3
import random
import numpy as np
import pandas as pd
import console
import gameparser

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
        # list of appearances by id.

        self.abilities = self.__character_creation_load_default_values('abilities')
        # list of abilities by id, range 0 to 10

        self.skills = self.__character_creation_load_default_values('skills')
        # list of all skills by id and their levels. range 0 to 10

        self.motivations = self.__character_creation_load_default_values('motivations')
        # list of motivations by id, range -5 to 5

        self.traits = {}
        # list of traits by id

        self.keepsakes = {}
        # list of posessions by id

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
                    if mod > 0:
                        return_list.append(self.gain_trait(trait))
                    elif mod < 0:
                        return_list.append(self.lose_trait(trait))
            if 'keepsakes' in stats_dict:
                for keepsakes, mod in stats_dict['keepsakes'].items():
                    if mod > 0:
                        return_list.append(self.gain_keepsake(keepsakes))
                    elif mod < 0:
                        return_list.append(self.lose_keepsake(keepsakes))
            if 'appearances' in stats_dict:
                for appearance, mod in stats_dict['appearances'].items():
                    if mod > 0:
                        return_list.append(self.gain_appearance(appearance))
                    elif mod < 0:
                        return_list.append(self.lose_appearance(appearance))
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
                return_dict['modifiers'] = {'traits': {}, 'keepsakes': {}}
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
                
                return return_dict
            
        except Exception as e:
            console.write_error(f"Error getting character skill level for {skill_id}: {e}")             

    def gain_skill(self, skill_id, num = 1):
        try:
            if skill_id not in self.skills:
                raise Exception(f"Could not find skill: {skill_id}")
        
            stat, change, success, message = 'skill', 'gain', True, ''
            self.skills[skill_id]['rank'] += num
            
            if self.skills[skill_id]['rank'] > 10:
                self.skills[skill_id]['rank'] = 10
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
            
            if self.skills[skill_id]['rank'] < 0:
                self.skills[skill_id]['rank'] = 0
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

            if self.abilities[ability_id]['rank'] > 10:
                self.abilities[ability_id]['rank'] = 10
                success = False
                message = f"Ability: {self.abilities['ability_id']['name'].capitalize()} can't go higher!"
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
            
            if self.abilities[ability_id]['rank'] < 0:
                self.abilities[ability_id]['rank'] = 0
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
            motivation_db = pd.read_sql_query(f"SELECT * FROM motivations WHERE id = '{motivation}' OR low = '{motivation}' OR high = '{motivation}'", db)
            if len(motivation_db) == 0:
                raise Exception(f"Could not find motivation: {motivation}")
            motivation_dict = motivation_db.to_dict(orient="records")[0]
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
            motivation_db = pd.read_sql_query(f"SELECT * FROM motivations WHERE id = '{motivation}' OR low = '{motivation}' OR high = '{motivation}'", db)
            if len(motivation_db) == 0:
                raise Exception(f"Could not find motivation: {motivation}")
            
            stat, change, success, message = 'motivation', 'gain', True, ''
            motivation_dict = motivation_db.to_dict(orient="records")[0]
            motivation_id = motivation_dict['id']

            # add or remove, as needed
            if motivation == motivation_dict['high'] or motivation == motivation_dict['id']:
                self.motivations[motivation_id]['rank'] += num
            elif motivation == motivation_dict['low']:
                self.motivations[motivation_id]['rank'] -= num

            # if above limit, bring down to limit
            if self.motivations[motivation_id]['rank'] > 5:
                self.motivations[motivation_id]['rank'] = 5
                success = False
                message = f"Motivation: {motivation.capitalize()} can't go higher!"
            elif self.motivations[motivation_id]['rank'] < -5:
                self.motivations[motivation_id]['rank'] = -5
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
            if self.motivations[motivation_id]['rank'] > 5:
                self.motivations[motivation_id]['rank'] = 5
                success = False
                message = f"Motivation: {motivation.capitalize()} can't go lower!"
            elif self.motivations[motivation_id]['rank'] < -5:
                self.motivations[motivation_id]['rank'] = -5
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
                trait_dict = db_trait.to_dict(orient='records')[0]

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
                self.traits.pop(trait_id)
                message = f"Trait lost: {self.traits[trait_id]['name'].capitalize()}"
            else:
                message = f"Never had trait: {self.traits[trait_id]['name'].capitalize()}"
                success = False

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error removing trait {trait_id} from character: {e}")

    def gain_keepsake(self, keepsake_id):
        try:
            stat, change, success, message = 'keepsake', 'gain', True, ''

            if keepsake_id not in self.keepsakes:
                # get keepsake dict from db
                db_keepsake = pd.read_sql_query(f"SELECT * FROM keepsakes WHERE id = '{keepsake_id}'", db)
                if len(db_keepsake) == 0:
                    raise Exception(f"Could not find keepsake: {keepsake_id}")
                keepsake_dict = db_keepsake.to_dict(orient='records')[0]

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
                self.keepsakes.pop(keepsake_id)
                message = f"Keepsake lost: {self.keepsakes[keepsake_id]['name'].capitalize()}"
            else:
                message = f"Never had keepsake: {self.keepsakes[keepsake_id]['name'].capitalize()}"
                success = False

            return {'stat': stat, 'change': change, 'success': success, 'message': message}
        
        except Exception as e:
            console.write_error(f"Error removing keepsake {keepsake_id} from character: {e}")

    def gain_appearance(self, appearance_id):
        try:
            # print(f'gain_appearance called: {appearance_id}')
            stat, change, success, message = 'appearance', 'gain', True, ''

            if appearance_id not in self.appearances:
                db_appearance = pd.read_sql_query(f"SELECT * FROM appearances WHERE id = '{appearance_id}'", db)
                if len(db_appearance) == 0:
                    raise Exception(f"Could not find appearance: {appearance_id}")
                
                appearance_dict = db_appearance.to_dict(orient='records')[0]
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

    def change_lifepath(self, lifepath_id):
        try:
            # push old lifepath details into history
            # ...later

            # load new lifepath details from db
            db_lifepath = pd.read_sql_query(f"SELECT * FROM lifepaths WHERE id = '{lifepath_id}'", db)
            if len(db_lifepath) == 0:
                raise Exception(f"Could not find lifepath: {lifepath}")
            lifepath = db_lifepath.iloc[0].to_dict()
            self.lifepath = lifepath
            self.setting = lifepath['setting']

        except Exception as e:
            console.write_error(f"Error moving character to lifepath {lifepath_id}: {e}")

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
    
    def __character_creation_load_default_values(self, table):
        try:
            db_dataframe = pd.read_sql_query(f"SELECT * FROM {table} WHERE id IS NOT NULL", db)
            if len(db_dataframe) == 0:
                raise Exception(f"Could not find table: {table}.")
            db_dict = db_dataframe.to_dict(orient='records')
            result_dict = {}
            for entry in db_dict:
                result_dict[entry['id']] = entry
                result_dict[entry['id']]['rank'] = 0
            return result_dict
        except Exception as e:
            console.write_error(f"Error adding default values from table {table}: {e}")
            
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
    print(testchar.gain_motivation('rebellious'))
    print(testchar.lose_motivation('pious'))
    print(testchar.update_stats({'gain': {'skills': ['farming'], 'traits': ['jolly'], 'abilities': [], 'motivations': [], 'keepsakes': [], 'lifepaths': []}, 'lose': {'skills': ['animal_handling'], 'traits': [], 'abilities': [], 'motivations': [], 'keepsakes': [], 'lifepaths': []}}))
    # print(testchar.motivations)
    # print(testchar.skills)
    # print(testchar.abilities)
    # print(testchar.traits)
    testchar.update_stats({'pop':'poop'})