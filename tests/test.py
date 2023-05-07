
#! python3
#above thing makes it use python 3 vs some old grody python

class Character:
   
   name = "Hero"
   goal = "Retrieve word of drow"
   skills = {
      
      #body things
      "strength": 0,
      "running": 0,
      "sprinting": 0,
      "jumping": 0,
      "swimming": 0,
      "dodging": 0,
      "climbing": 0,

      #environmental skills
      "forest-wise": 0,
      "mountain-wise": 0,
      "swamp-wise": 0,

      #weapon skills
      "short blade": 0,
      "long blade": 0,
      "archery": 0,

      #tradeskills
      "pottery": 0,
      "masonry": 0,
      "farming": 0,

   }
   # note that in-game we'll make two characters -- the version at start,
   # and the version that we change throughout the game. We'll compare
   # these two to keep track of changes

   items = []

big = Character()
# print(big.skills)


class Encounter:


   success = 0

   # success starts at 0, and goes down and up based on interaction with environment
   # if it goes up to 2, achieve objective
   # if it goes down to -2, fail objective and take penalty
   # if it does neither after a few actions, mixed result

   # encounter defined by list of tokens.

   environment = ["swamp", "fog"]
   # environments, like swamp or fog, act as traversal challenges, which tend to affect the beginnings, endings, 
   # or the resolutions of other objects.

   objects = ["old-wagon", "mushrooms"]
   # objects won't do anything unless interacted with
   # some, like old-wagon, act as potential boons
   # some, like mushrooms, act as potential boons or problems

   entities = ["troll", "merchant"]
   # entities act independently each turn, and will respond differently based on your character
   # troll might attack you or attack the merchant
   # merchant might flee from troll, or die, or, if helped, sell you something

   #these tokens are assembled at encounter creation, from lists of more and less risky things
   # every object/entity has a risk and reward rating; the encounter assembles a set budget of these

   # every object/entity has inherent actions and reactions
   # these are pulled from a separate list;
   # fire will burn some things, improve others, etc. by altering their subtokens
   # for example, a firebomb might add the effect "fire" to its target
   # for example, fire might add "singed" to a cloak, "destroyed" to a paper, "overcharged" to an elemental


   # function: add/remove traits or items, make future encounters worse, or story effect to postscript
   risk = "harm"
   reward = "10g"



   introtext = ""

   options = []


class Environment:

   def __init__(self, *tags):
      self.tags = []
      taglist = list(tags)
      for tag in taglist:
         if tag not in self.tags:
            self.tags.append(tag)
      print(self.tags)

   def check_tags(self, *tags):
      taglist = list(tags)
      for tag in taglist:
         if tag not in self.tags:
            return False
      return True
      
   def add_tags(self, *tags):
      taglist = list(tags)
      for tag in taglist:
         if tag not in self.tags:
            self.tags.append(tag)

   def remove_tags(self, *tags):
      taglist = list(tags)
      for tag in taglist:
         if tag in self.tags:
            self.tags.remove(tag)

def swamp():
      return Environment("swamp")
   

         

testenv = Environment("test1", "test2")

testSwamp = swamp()

testSwamp.add_tags("wet")
print(testSwamp.tags)



