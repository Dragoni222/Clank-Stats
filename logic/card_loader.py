


def card_name_to_filename(card_name):
    return card_name.replace(" ", "").replace("'", "") + ".png"


class Card:
    def __init__(self, name, cost, skill, boots=0, swords=0, clank=0, draw=0, gold=0, teleports=0, green=0, addedValue=0):
        self.name = name
        self.filename = card_name_to_filename(name)
        self.cost = cost
        self.skill = skill
        self.boots = boots
        self.swords = swords
        self.clank = clank
        self.draw = draw
        self.gold = gold
        self.teleports = teleports
        self.green = green
        self.addedValue = addedValue


    def __gt__(self, other):
        return self.value() > other.value()

    def __lt__(self, other):
        return self.value() < other.value()

    def __le__(self, other):
        return self.value() <= other.value()

    def __ge__(self, other):
        return self.value() >= other.value()

    
    def __copy__(self):
        return Card(self.name, self.cost, self.skill, self.boots, self.swords, self.clank, self.draw, self.gold, self.teleports, self.green, self.addedValue)
    
    def __str__(self):
        return self.name
    def value(self):
        return self.addedValue + self.draw * 2 + self.gold * 1 + (self.clank * -1 if self.clank > 0 else self.clank * -0.6) + self.teleports * 1.2 + self.boots * 0.6 + self.swords * 0.5 + (((self.skill*0.9)) ** 1.3)
