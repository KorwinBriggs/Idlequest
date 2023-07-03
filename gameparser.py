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
    result = {}

    # divide string into list of words
    words_list = re.split(r'\(|\)|:\s|,\s', string)

    # get sublists per command
    command_words = ["gain", "gainOne", "lose", "loseOne"]
    subsections_by_commands = divide_list_at_keywords(words_list, command_words)

    for command_subsection in subsections_by_commands:
        # get command, then delete it from list and parse the rest into parsed object
        command = command_subsection[0]
        del command_subsection[0]

        # parse subsection - ' '.join'ed list into string because parse_items requires string, not list
        items = (parse_items(' '.join(command_subsection))) 

        # add necessary item_type sections to result dict
        for item_type in items:
            if item_type not in result:
                result[item_type] = {}

        # if gain or lose, add all to result
        if command == 'lose' or command == 'gain':
            for item_type in items: # ex 'skills
                for item_id, item_mod in items[item_type].items(): # ex farming, 1
                    # if lose, make modifier negative
                    if command == 'lose':
                        item_mod *= -1
                    # if already in result, add mod to existing entry
                    if item_id in result[item_type]:
                        result[item_type][item_id] += item_mod
                    # if not, add new entry
                    else:
                        result[item_type][item_id] = item_mod

        # if gainOne or loseOne, first choose random item (and make note of its type)
        elif command == 'gainOne' or command == 'loseOne':
            # make list containing all the items like {'type': 'skills', 'id': 'farming', 'mod': 2}
            random_item_list = []
            for item_type in items: # ex 'skills'
                for item_id, item_mod in items[item_type].items(): # ex 'farming', 1
                    # if loseOne, make modifier negative
                    if command == 'loseOne':
                        item_mod *= 1
                    random_item_list.append({'type': item_type, 'id': item_id, 'mod': item_mod})
            # choose random entry from list
            random_item = random_item_list[random.randint(0, len(random_item_list)-1)]
            # if already in result, add mod to existing entry
            item_type = random_item['type']
            item_id = random_item['id']
            item_mod = random_item['mod']
            if item_id in result[item_type]:
                result[item_type][item_id] += item_mod
            # if not, add new entry
            else:
                result[item_type][item_id] = item_mod

    return result


def parse_items(string):
    # for things like: "lifepaths: baby, skills: farming"
    # should return a series of dicts like {'skills': {'farming': 2, 'mining': -1} }
    result = {}

    # divide string into list of words
    words_list = re.split(r'\(|\)|:\s|,\s|\s', string)
    # divide those lists into separate lists by keyword
    type_words = ["skills", "traits", "abilities", "motivations", "keepsakes", "lifepaths", "settings", "appearances"]
    subsections_by_type = divide_list_at_keywords(words_list, type_words)

    for type_subsection in subsections_by_type:
        # get item type, then remove it from subsection list
        item_type = type_subsection[0]

        # add item_type section to result
        if item_type not in result:
            result[item_type] = {}

        del type_subsection[0]

        # use parse_modifiers to get id and mod
        for item in type_subsection:
            parsed_item = parse_modifiers(item)
            for item_id, item_mod in parsed_item.items(): # for loop only runs 1 time; needed it because .items() is iterable
                # if already in result, add mods together
                if item_id in result[item_type]:
                    result[item_type][item_id] += item_mod
                # otherwise, add as new entry
                else:
                    result[item_type][item_id] = item_mod

    return result


def divide_list_at_keywords(words_list, keywords_list):
    # takes list of words, like ["motivations", "adventurous", "lazy", "skills", "farming"]
    # and splits by keywrods, returning ex. [['motivations', 'adventurous', 'lazy'], ['skills', 'farming']]
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


def parse_modifiers(string):
    # for things like "farming+2" or "resolve-3"; if no + or -, defaults to +1
    if '+' in string:
        split = string.split('+')
        return {split[0]: int(split[1])} # if +, {farming: 2}
    elif '-' in string:
        split = string.split('-')
        return {split[0]: int(split[1]) * -1} # if -, {farming: -2}
    else:
        return {string: 1} # if neither, default to {farming: 1}


    

if __name__ == "__main__":

    # print(parse_modifiers("resolve"))

    # words_list = ["motivations", "adventurous", "lazy", "skills", "farming"]
    # type_words = ["skills", "traits", "abilities", "motivations", "keepsakes", "lifepaths", "settings"]
    # print(divide_list_at_keywords(words_list, type_words))

    # joined_list = (' '.join(['motivations', 'adventurous', 'lazy', 'rebellious', 'skills', 'farming']))
    # print(joined_list)
    # parsed_joined_list = parse_items(joined_list)
    # print(parsed_joined_list)

    print(parse_effects("gainOne(motivations: adventurous, lazy, rebellious, skills: farming), loseOne(skills: herding, animal_handling), gain(traits: jolly+2), lose(abilities: strength, resolve)"))
    # # print(parse_items("motivations: adventurous, lazy, rebellious, skills: farming, lifepaths: peasant_farmer, kid_peasant, settings: peasant"))
    # print(parse_effects("gainOne(skills: intimidation, abilities: resolve, social_sense), gainOne(motivations: loyal, social, adventurous)"))
    

    print(parse_items("motivations: adventurous"))