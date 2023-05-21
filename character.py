import sqlite3
import random
import numpy as np
import pandas as pd

db = sqlite3.connect("db/gamedata")

class character:

    def __init__(self, name, gender, setting):

        self.name = name

        self.age = 0

        self.gender = gender

        self.pronouns = self.__character_creation_pronouns(name, gender)
        self.sub = self.pronouns["subjective"]
        self.obj = self.pronouns["objective"]
        self.pos = self.pronouns["possessive"]

        self.skills = {}
        # list of all skills by id and their levels. instantiate at 0, modify through lifepaths/events

        self.skillmods = {}
        # list of skill modifiers from active appearances, traits, items, etc.
        # these are added/removed whenever appearances, traits, items, etc are added/removed.
        # these act as multipliers of skills through events.

        self.appearances = {}
        # list of appearances by id.

        self.traits = []
        # list of traits by id

        self.posessions = []
        # list of posessions by id

        self.setting = setting
        # current setting id

        self.lifepath = {
            "id": "newborn",
            "name": "newborn",
            "years": "0",
        }
        # current lifepath id

        self.history = []
        # list of dictionaries, like, 
        #   {
        #       age: 6
        #       event: stairs_fall
        #       change: add trait hurty_foot
        #       string: "Harald fell down the stairs and broke his little footsie wootsie."
        #   }
        # this is added to throughout gameplay and used afterwords to make a log/postscript


    # def addSkill(skillid, num):
    #     0
    
    # def addAppearance(appearanceid):
    #     0
        
    # def addTrait(traitid):
    #     0
        
    # def addPosession(posessionid):
    #     0
        
    # def removePosession(posessionid):
    #     0

    def change_lifepath(self, lifepath_id):
        # push old lifepath details into history
        # ...later

        # load new lifepath details from db
        db_lifepath = pd.read_sql_query(f"SELECT * FROM lifepaths WHERE id = '{lifepath_id}'", db)
        lifepath = db_lifepath.iloc[0].to_dict()
        self.lifepath = lifepath
        self.setting = lifepath['setting']
        

    # def __character_creation_appearance(self, num_appearances):
    #     # take random appearance from db, check if one of its category is already in the list,
    #     # if not, add it to the list and its category to the used_categories list
    #     db_appearances = pd.read_sql_query( "SELECT id, name, category FROM appearance WHERE aging = 'false' AND scar = 'false'", db )
    #     id_list = []
    #     used_categories = []

    #     while len(id_list) < num_appearances:
    #         random_row = random.randint(0, len(db_appearances))
    #         if not db_appearances.iloc[random_row].values[2] in used_categories:
    #             id_list += [ db_appearances.iloc[random_row].values[0] ]
    #             used_categories += [ db_appearances.iloc[random_row].values[2] ]

    #     return id_list

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
        
    # def parse_event_string(self, string):
    #     return string.format(**self.dynamic_string_words)

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

