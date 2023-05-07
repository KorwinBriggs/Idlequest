
import sqlite3
import random
import numpy as np
import pandas as pd

db = sqlite3.connect("db/gamedata")
db_appearances = pd.read_sql_query("SELECT id, name, category FROM appearance WHERE aging = 'false' AND scar = 'false'", db)


db_appearance_categories = pd.read_sql_query("SELECT DISTINCT category FROM appearance", db)

appearance_categories = []

for row in range(len(db_appearance_categories)): 
    # range used for for loop; len is function to take number of rows
    category_name = db_appearance_categories.iloc[row].values[0]
    # .iloc [row] narrows to the row. .values gives the value in a list; .values[0] gives the actual value
    appearance_categories += [category_name]

character_appearance = {}
# get three random numbers


while len(character_appearance) < 3:
    random_row = random.randint(0, len(db_appearances))
    if not db_appearances.iloc[random_row].values[2] in character_appearance:
        character_appearance[db_appearances.iloc[random_row].values[2]] = db_appearances.iloc[random_row].to_dict()

print(character_appearance)

appearance_string = "This character has "
for key in character_appearance:
    appearance_string += character_appearance[key].name

# + ", " + character_appearance[1].name + ", and " + character_appearance[2].name

print(appearance_string)


    
# character has appearance

# three times:
# - query list
# - choose a feature from the list
# - record the category of that feature
# - modify query to remove all items of that category
# this should leave me with 3 items from different categories

# print(db_appearances.iloc[3].values[2])