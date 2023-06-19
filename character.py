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


        self.appearances = []
        # list of appearances by id.

        self.abilities = {}
        # list of abilities by id, range 0 to 10

        self.skills = {}
        # list of all skills by id and their levels. range 0 to 10

        self.motivations = {}
        # list of motivations, range -5 to 5

        self.traits = []
        # list of traits by id

        self.keepsakes = []
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

    def gain_and_lose(self, json_data):
        gain = json_data['gain']
        lose = json_data['lose']
        for ability in gain['abilities']:
            self.gain_ability(ability)
        for ability in lose['abilities']:
            self.lose_ability(ability)
        for skill in gain['skills']:
            self.gain_skill(skill)
        for skill in lose['skills']:
            self.lose_skill(skill)
        for trait in gain['traits']:
            self.gain_trait(trait)
        for trait in lose['traits']:
            self.lose_trait(trait)
        for motivation in gain['motivations']:
            self.gain_motivation(motivation)
        for motivation in lose['motivations']:
            self.lose_motivation(motivation)
        for keepsake in gain['keepsakes']:
            self.gain_keepsake(keepsake)
        for keepsake in lose['keepsakes']:
            self.lose_keepsake(keepsake)


    def gain_skill(self, skill_id, num = 1):
        # check that the skill is in the db
        if not self.__check_if_in_db("skills", skill_id):
            raise Exception(f"Could not find skill: {skill_id}")
        # add skill to character
        if skill_id in self.skills:
            self.skills[skill_id] += num
        else: 
            self.skills[skill_id] = num
        # if over limit, bring down to limit
        if self.skills[skill_id] > 10:
            self.skills[skill_id] = 10

    def lose_skill(self, skill_id, num = 1):
        # check that the skill is in the db
        if not self.__check_if_in_db("skills", skill_id):
            raise Exception(f"Could not find skill: {skill_id}")
        # add skill to character
        if skill_id in self.skills:
            self.skills[skill_id] -= num
        else: 
            self.skills[skill_id] = 0
        # if below limit, bring up to limit
        if self.skills[skill_id] < 0:
            self.skills[skill_id] = 0

    def gain_ability(self, ability_id, num = 1):
        # check that the skill is in the db
        if not self.__check_if_in_db("abilities", ability_id):
            raise Exception(f"Could not find skill: {ability_id}")
        # add skill to character
        if ability_id in self.abilities:
            self.abilities[ability_id] += num
        else: 
            self.abilities[ability_id] = num
        # if over limit, bring down to limit
        if self.abilities[ability_id] > 10:
            self.abilities[ability_id] = 10

    def lose_ability(self, ability_id, num = 1):
        # check that the skill is in the db
        if not self.__check_if_in_db("abilities", ability_id):
            raise Exception(f"Could not find skill: {ability_id}")
        # add skill to character
        if ability_id in self.abilities:
            self.abilities[ability_id] -= num
        else: 
            self.abilities[ability_id] = 0
        # if below limit, bring up to limit
        if self.abilities[ability_id] < 0:
            self.abilities[ability_id] = 0

    def gain_motivation(self, motivation, num = 1):
        # find line in db with motivation name as high or low value
        motivation_db = pd.read_sql_query(f"SELECT * FROM motivations WHERE low = '{motivation}' OR high = '{motivation}'", db)
        if len(motivation_db) == 0:
            raise Exception(f"Could not find motivation: {motivation}")
        motivation_dict = motivation_db.to_dict(orient="records")[0]
        motivation_id = motivation_dict['id']
        # if high, add to stat
        if motivation == motivation_dict['high']:
            if motivation_id in self.motivations:
                self.motivations[motivation_id] += num
            else:
                self.motivations[motivation_id] = num
        # if low, subtract from stat
        elif motivation == motivation_dict['low']:
            if motivation_id in self.motivations:
                self.motivations[motivation_id] -= num
            else:
                self.motivations[motivation_id] = -1 * num
        # if above limit, bring down to limit
            if self.motivations[motivation_id] > 5:
                self.motivations[motivation_id] = 5
            if self.motivations[motivation_id] < -5:
                self.motivations[motivation_id] = -5

    def lose_motivation(self, motivation, num = 1):
        # find line in db with motivation name as high or low value
        motivation_db = pd.read_sql_query(f"SELECT * FROM motivations WHERE low = '{motivation}' OR high = '{motivation}'", db)
        if len(motivation_db) == 0:
            raise Exception(f"Could not find motivation: {motivation}")
        motivation_dict = motivation_db.to_dict(orient="records")[0]
        motivation_id = motivation_dict['id']
        # if high, subtract from stat
        if motivation == motivation_dict['high']:
            if motivation_id in self.motivations:
                self.motivations[motivation_id] -= num
            else:
                self.motivations[motivation_id] = -1 * num
        # if low, add to stat
        elif motivation == motivation_dict['low']:
            if motivation_id in self.motivations:
                self.motivations[motivation_id] += num
            else:
                self.motivations[motivation_id] = num
        # if above limit, bring down to limit
            if self.motivations[motivation_id] > 5:
                self.motivations[motivation_id] = 5
            if self.motivations[motivation_id] < -5:
                self.motivations[motivation_id] = -5
        
    def gain_trait(self, trait_id):
        # check that the trait is in the db
        if not self.__check_if_in_db("traits", trait_id):
            raise Exception(f"Could not find trait: {trait_id}")
        # add trait to character
        if trait_id not in self.traits:
            self.traits.append(trait_id)

    def lose_trait(self, trait_id):
        # check that the trait is in the db
        if not self.__check_if_in_db("traits", trait_id):
            raise Exception(f"Could not find trait: {trait_id}")
        # remove trait from character
        if trait_id in self.traits:
            self.traits.remove(trait_id)

    def gain_keepsake(self, keepsake_id):
        # check that the keepsake is in the db
        if not self.__check_if_in_db("keepsakes", keepsake_id):
            raise Exception(f"Could not find keepsake: {keepsake_id}")
        # add keepsake to character
        if keepsake_id not in self.keepsakes:
            self.keepsakes.append(keepsake_id)

    def lose_keepsake(self, keepsake_id):
        # check that the keepsake is in the db
        if not self.__check_if_in_db("keepsakes", keepsake_id):
            raise Exception(f"Could not find keepsake: {keepsake_id}")
        # remove keepsake from character
        if keepsake_id in self.keepsakes:
            self.keepsakes.remove(keepsake_id)


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
                'possessive': 'hers'
            }
        raise Exception("Problem assigning pronouns")
        
    def __check_if_in_db(self, table, id):
        # check that the skill is in the db
        db_skill = pd.read_sql_query(f"SELECT * FROM {table} WHERE id = '{id}'", db)
        if len(db_skill) == 0:
            return False
        return True
    
    # def __translate_motivation(self, motivation, num = 1):
    #     if motivation in ('vain', 'rebellious', 'solitary', 'greedy', 'lazy', 'traditional', )

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
    testchar.gain_motivation('rebellious')
    testchar.lose_motivation('pious')
    testchar.gain_and_lose({'gain': {'skills': ['farming'], 'traits': ['jolly'], 'abilities': [], 'motivations': [], 'keepsakes': [], 'lifepaths': []}, 'lose': {'skills': ['animal_handling'], 'traits': [], 'abilities': [], 'motivations': [], 'keepsakes': [], 'lifepaths': []}})
    print(testchar.motivations)
    print(testchar.skills)
    print(testchar.abilities)
    print(testchar.traits)