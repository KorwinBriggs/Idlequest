
import random
import console
import pandas as pd



def row_to_dict(dataframe):
    # takes single row dataframe, returns dict
    try:
        if len(dataframe) > 1:
            raise Exception(console.write_error(f'Dataframe of more than one row passed to row_to_dict:\n{dataframe}'))
        return dataframe.iloc[0].to_dict()
    except Exception as e:
        console.write_error(f"Error converting dataframe to dict: {e}") 

def random_row_to_dict(dataframe):
    # takes multi-row dataframe, returns single random row's dict
    try:
        random_row = random.randint(0, len(dataframe)-1)
        return dataframe.iloc[random_row].to_dict()
    except Exception as e:
        console.write_error(f"Error converting dataframe to dict: {e}") 