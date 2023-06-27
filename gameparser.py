import re
import random


def parse_pronouns(string, character):
    # takes string, returns string with pronouns replaced
    return string.format(
        Name = character.name,
        name = character.name,
        sub = character.sub,
        Sub = character.sub.capitalize(),
        obj = character.obj,
        Obj = character.obj.capitalize(),
        pos = character.pos,
        Pos = character.pos.capitalize()
    )

def parse_effects(string):

    # for things like: "gainOne(skills: farming, plants_and_herbs), gainOne(motivations: dutiful, industrious, traditional, humble)"
    result = {
        'gain': {
            'skills': [],
            'traits': [],
            'abilities': [],
            'motivations': [],
            'keepsakes': [],
            'lifepaths': [],
            'appearances': []
        },
        'lose': {
            'skills': [],
            'traits': [],
            'abilities': [],
            'motivations': [],
            'keepsakes': [],
            'lifepaths': [],
            'appearances': []
        }
    }
    
    # divide string into list of words
    words_list = re.split(r'\(|\)|:\s|,\s', string)

    # get sublists per command
    command_words = ["gain", "gainOne", "lose", "loseOne"]
    subsections_by_commands = divide_list_at_keywords(words_list, command_words)

    # get subsublists per type of effect
    type_words = ["skills", "motivations", "traits", "abilities", "lifepaths", "keepsakes", "appearances"]
    for command_subsection in subsections_by_commands:

        command = command_subsection[0]
        subsections_by_type = divide_list_at_keywords(command_subsection, type_words)

        # if gain or lose, add everything that follows
        if command in ('gain', 'lose'):
            for type_subsection in subsections_by_type:
                item_type = type_subsection[0]

                for index in range(len(type_subsection)):
                    if index == 0:
                        continue # skip the first item in each list, ie 'skills' or 'motivations'
                    else:
                        item_id = type_subsection[index]
                        result[command][item_type].append(item_id) # add item to appropriate place in result dict
        
        # if gainOne or loseOne, add a random one from the following list
        elif command in ('gainOne', 'loseOne'):
            try:
                # get total number of options
                total_options = 0
                for type_subsection in subsections_by_type:
                    total_options += len(type_subsection)-1

                # choose option number
                chosen_option = random.randint(1, total_options)

                # count forward to get option and type
                count = 0
                for type_subsection in subsections_by_type:
                    for index in range(len(type_subsection)):
                        if index == 0:
                            continue # skip the first item in each list, ie 'skills' or 'motivations'
                        else:
                            count += 1
                            if count == chosen_option: # if it's the right option, add it to the result dict in the right spot
                                item_type = type_subsection[0]
                                item_id = type_subsection[index]
                                if command == 'gainOne':
                                    result['gain'][item_type].append(item_id)
                                elif command == 'loseOne':
                                    result['lose'][item_type].append(item_id)

            except Exception as e: (f"Error while parsing command {command}: {format(e)}")

        else: 
            raise Exception(f"Error while parsing effect: Unexpected command {command}")
        

    return result



def parse_prereqs(string):
    # for things like: "lifepaths: baby, skills: farming"
    result = {
        'skills': [],
        'traits': [],
        'abilities': [],
        'motivations': [],
        'keepsakes': [],
        'lifepaths': [],
        'settings': []
    }

    # divide string into list of words, then into sublists by type
    words_list = re.split(r'\(|\)|:\s|,\s', string)
    type_words = ["skills", "traits", "abilities", "motivations", "keepsakes", "lifepaths", "settings"]
    subsections_by_type = divide_list_at_keywords(words_list, type_words)

    for type_subsection in subsections_by_type:
        item_type = type_subsection[0]

        for index in range(len(type_subsection)):
            if index == 0:
                continue # skip the first item in each list, ie 'skills' or 'motivations'
            else:
                item_id = type_subsection[index]
                result[item_type].append(item_id) # add item to appropriate place in result dict

    return result


def parse_comma_lists( 
        skills = [],
        traits = [],
        abilities = [],
        motivations = [],
        keepsakes = [],
        lifepaths = [],
        settings = [],
        opportunities = []
        ):
    
    # for individual lists like "strength, toughness, stamina", where the type is already known
    # call function like: parse_comma_lists(abilities="strength, toughness, stamina", skills="farming")
    string_list = [skills, traits, abilities, motivations, keepsakes, lifepaths, settings, opportunities]
    parsed_list = []
    for item in string_list:
        if isinstance(item, str):
            parsed_item = re.split(r'\(|\)|:\s|,\s', item) # split into list of words
        else:
            parsed_item = item
        parsed_list.append(parsed_item)

    result = {
        'skills': parsed_list[0],
        'traits': parsed_list[1],
        'abilities': parsed_list[2],
        'motivations': parsed_list[3],
        'keepsakes': parsed_list[4],
        'lifepaths': parsed_list[5],
        'settings': parsed_list[6],
        'opportunities': parsed_list[7]
    }

    return result

    
############# HELPER FUNCTIONS ##############

def divide_list_at_keywords(words_list, keywords_list):
    keywords_indices = []
    for index, word in enumerate(words_list):
        if word in keywords_list:
            keywords_indices.append(index)
    keywords_indices.append(len(words_list)) # adding final cutoff for last section

    # split word list by those indices, into one list per command
    sections = []
    for index in range(len(keywords_indices)-1):
        sub_list = words_list[keywords_indices[index]:keywords_indices[index+1]]
        if '' in sub_list:
            sub_list.remove('') # removing trailing '' from lists
        sections.append(sub_list)
    
    return sections


    

if __name__ == "__main__":
    # print(parse_effects("gainOne(motivations: adventurous, lazy, rebellious, skills: farming), loseOne(skills: herding, animal_handling), gain(traits: jolly)"))
    # print(parse_prereqs("motivations: adventurous, lazy, rebellious, skills: farming, lifepaths: peasant_farmer, kid_peasant, settings: peasant"))
    # print(parse_comma_lists(abilities="strength, toughness, stamina", skills="farming"))
    print(parse_effects("gainOne(skills: intimidation, abilities: resolve, social_sense), gainOne(motivations: loyal, social, adventurous)"))
    print(parse_comma_lists("gainOne(skills: intimidation, abilities: resolve, social_sense), gainOne(motivations: loyal, social, adventurous)"))