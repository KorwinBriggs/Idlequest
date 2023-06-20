import sqlite3
import random
import numpy as np
import pandas as pd

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

    def update_stats(self, stats_dict):
        return_list = []

        if 'gain' in stats_dict:
            gain = stats_dict['gain']
            if 'abilities' in gain:
                for ability in gain['abilities']:
                    return_list.append(self.gain_ability(ability))
            if 'skills' in gain:
                for skill in gain['skills']:
                    return_list.append(self.gain_skill(skill))
            if 'traits' in gain:
                for trait in gain['traits']:
                    return_list.append(self.gain_trait(trait))
            if 'motivations' in gain:
                for motivation in gain['motivations']:
                    return_list.append(self.gain_motivation(motivation))
            if 'keepsakes' in gain:
                for keepsake in gain['keepsakes']:
                    return_list.append(self.gain_keepsake(keepsake))
            if 'appearances' in gain:
                for appearance in gain['appearances']:
                    return_list.append(self.gain_appearance(appearance))

        if 'lose' in stats_dict:
            lose = stats_dict['lose']
            if 'abilities' in lose:
                for ability in lose['abilities']:
                    return_list.append(self.lose_ability(ability))
            if 'skills' in lose:
                for skill in lose['skills']:
                    return_list.append(self.lose_skill(skill))
            if 'traits' in lose:
                for trait in lose['traits']:
                    return_list.append(self.lose_trait(trait))
            if 'motivations' in lose:
                for motivation in lose['motivations']:
                    return_list.append(self.lose_motivation(motivation))
            if 'keepsakes' in lose:
                for keepsake in lose['keepsakes']:
                    return_list.append(self.lose_keepsake(keepsake))
            if 'appearances' in lose:
                for appearance in lose['appearances']:
                    return_list.append(self.lose_appearance(appearance))

        return return_list


    def gain_skill(self, skill_id, num = 1):
        if skill_id not in self.skills:
            raise Exception(f"Could not find skill: {skill_id}")
        
        stat, change, success, message = 'skill', 'gain', True, ''
        self.skills[skill_id]['rank'] += num
        
        if self.skills[skill_id]['rank'] > 10:
            self.skills[skill_id]['rank'] = 10
            success = False
            message = f"Skill: {self.skills[skill_id]['name'].capitalize()} can't go higher!"
        else:
            message = f"+ Skill: {self.skills[skill_id]['name'].capitalize()}"

        return {'stat': stat, 'change': change, 'success': success, 'message': message}

    def lose_skill(self, skill_id, num = 1):
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

    def gain_ability(self, ability_id, num = 1):
        if ability_id not in self.abilities:
            raise Exception(f"Could not find skill: {ability_id}")

        stat, change, success, message = 'ability', 'gain', True, ''
        self.abilities[ability_id]['rank'] += num

        if self.abilities[ability_id]['rank'] > 10:
            self.abilities[ability_id]['rank'] = 10
            success = False
            message = f"Ability: {self.abilities['ability_id']['name'].capitalize()} can't go higher!"
        else:
            message = f"+ Ability: {self.abilities['ability_id']['name'].capitalize()}"

        return {'stat': stat, 'change': change, 'success': success, 'message': message}

    def lose_ability(self, ability_id, num = 1):
        if ability_id not in self.abilities:
            raise Exception(f"Could not find skill: {ability_id}")
        
        stat, change, success, message = 'ability', 'loss', True, ''
        self.abilities[ability_id]['rank'] -= num
        
        if self.abilities[ability_id]['rank'] < 0:
            self.abilities[ability_id]['rank'] = 0
            success = False
            message = f"Ability: {self.abilities['ability_id']['name'].capitalize()} can't go lower!"
        else:
            message = f"- Ability: {self.abilities['ability_id']['name'].capitalize()}"

        return {'stat': stat, 'change': change, 'success': success, 'message': message}

    def gain_motivation(self, motivation, num = 1):
        # find line in db with motivation name as high or low value
        motivation_db = pd.read_sql_query(f"SELECT * FROM motivations WHERE low = '{motivation}' OR high = '{motivation}'", db)
        if len(motivation_db) == 0:
            raise Exception(f"Could not find motivation: {motivation}")
        
        stat, change, success, message = 'motivation', 'gain', True, ''
        motivation_dict = motivation_db.to_dict(orient="records")[0]
        motivation_id = motivation_dict['id']

        # add or remove, as needed
        if motivation == motivation_dict['high']:
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

    def lose_motivation(self, motivation, num = 1):
        # find line in db with motivation name as high or low value
        motivation_db = pd.read_sql_query(f"SELECT * FROM motivations WHERE low = '{motivation}' OR high = '{motivation}'", db)
        if len(motivation_db) == 0:
            raise Exception(f"Could not find motivation: {motivation}")
        
        stat, change, success, message = 'motivation', 'loss', True, ''
        motivation_dict = motivation_db.to_dict(orient="records")[0]
        motivation_id = motivation_dict['id']

        # add or remove, as needed
        if motivation == motivation_dict['high']:
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
        
    def gain_trait(self, trait_id):
        stat, change, success, message = 'trait', 'gain', True, ''

        if trait_id not in self.traits:
            db_trait = pd.read_sql_query(f"SELECT * FROM traits WHERE id = '{trait_id}'", db)
            if len(db_trait) == 0:
                raise Exception(f"Could not find trait: {trait_id}")
            
            trait_dict = db_trait.to_dict(orient='records')[0]
            self.traits[trait_id] = trait_dict
            message = f"Trait gained: {self.traits[trait_id]['name'].capitalize()}"
        else:
            message = f"Already had trait: {self.traits[trait_id]['name'].capitalize()}"
            success = False
        
        return {'stat': stat, 'change': change, 'success': success, 'message': message}

    def lose_trait(self, trait_id):
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

    def gain_keepsake(self, keepsake_id):
        
        stat, change, success, message = 'keepsake', 'gain', True, ''

        if keepsake_id not in self.keepsakes:
            db_keepsake = pd.read_sql_query(f"SELECT * FROM keepsakes WHERE id = '{keepsake_id}'", db)
            if len(db_keepsake) == 0:
                raise Exception(f"Could not find keepsake: {keepsake_id}")
            
            keepsake_dict = db_keepsake.to_dict(orient='records')[0]
            self.keepsakes[keepsake_id] = keepsake_dict
            message = f"Keepsake gained: {self.keepsake[keepsake_id]['name'].capitalize()}"
        else:
            message = f"Already had keepsake: {self.traits[keepsake_id]['name'].capitalize()}"
            success = False

        return {'stat': stat, 'change': change, 'success': success, 'message': message}

    def lose_keepsake(self, keepsake_id):
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

    def gain_appearance(self, appearance_id):
        
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
            message = f"Already had trait: {self.appearances[appearance_id]['name'].capitalize()}"
            success = False

        return {'stat': stat, 'change': change, 'success': success, 'message': message}

    def lose_appearance(self, appearance_id):
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


    def change_lifepath(self, lifepath_id):
        # push old lifepath details into history
        # ...later

        # load new lifepath details from db
        db_lifepath = pd.read_sql_query(f"SELECT * FROM lifepaths WHERE id = '{lifepath_id}'", db)
        if len(db_lifepath) == 0:
            raise Exception(f"Could not find lifepath: {lifepath}")
        lifepath = db_lifepath.iloc[0].to_dict()
        self.lifepath = lifepath
        self.setting = lifepath['setting']
        

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
        raise Exception("Problem assigning pronouns")
    
    def __character_creation_load_default_values(self, table):
        db_dataframe = pd.read_sql_query(f"SELECT * FROM {table} WHERE id IS NOT NULL", db)
        if len(db_dataframe) == 0:
            raise Exception(f"Could not find table: {table}.")
        db_dict = db_dataframe.to_dict(orient='records')
        result_dict = {}
        for entry in db_dict:
            result_dict[entry['id']] = entry
            result_dict[entry['id']]['rank'] = 0
        return result_dict
            
    def __check_if_in_db(self, table, id):
        # check that the skill is in the db
        db_skill = pd.read_sql_query(f"SELECT * FROM {table} WHERE id = '{id}'", db)
        if len(db_skill) == 0:
            return None
        return True
    
    def __stat_return_dict(self, stat_type, up_down_none, message):
        return {
            'stat': stat_type,
            'direction': up_down_none,
            'message': message
        }

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