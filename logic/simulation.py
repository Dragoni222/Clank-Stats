import random
from collections import namedtuple
from copy import copy

from logic.card_loader import Card


class Deck:
    def __init__(self, cards, draw, discard, hand, hasCrown=False, hasArtifact=False):
        self.cards = cards
        self.draw = draw  # <-- Make a shallow copy here
        self.discard = discard
        self.hand = hand
        self.hasCrown = hasCrown
        self.hasArtifact = hasArtifact
        self.cardID = 0

    def drawHand(self):
        self.discard += self.hand
        self.hand.clear()
        self._draw_cards(5)

    def simulate_hands(self, count):
        all_hands = []
        test_deck = copy(self)
        
        for i in range(count):
            test_deck.drawHand()
            all_hands.append(test_deck.value_this_hand())

        return all_hands

    def simulate_next_hands(self,count):
        all_hands = []
        for i in range(count):
            test_deck = copy(self)
            test_deck.discard_hand()
            test_deck.drawHand()
            all_hands.append(test_deck.value_this_hand())

        return all_hands
    
    def simulate_this_hand(self, count):
        current_value = HandValue(0, 0, 0, 0, 0, 0, [])
        for i in range(count):
            test_deck = copy(self)
            test_deck._undiscard_hand()
            test_deck.drawHand()
            current_value += test_deck.value_this_hand()

        return current_value/count
    
    def value_this_hand(self):
        current_value = HandValue(0, 0, 0, 0, 0, 0, [])
        while len(self.hand) > 0:
            current_value += self.simulate_card(sorted(self.hand)[-1])
        return current_value
    def simulate_card(self, card):
        self.hand.remove(card)
        current_value = HandValue(card.skill, card.boots, card.swords, card.clank, card.gold, card.teleports, [card])
        match card.name:
            case 'Sleight Of Hand':
                self._discard_cards(1)
            case 'Apothecary':
                #add branches here 
                self._discard_cards(1)
            case 'Mountain King':
                if self.hasCrown:
                    current_value.boots += 1
                    current_value.swords += 1
            #case 'The Queen of Hearts':
            #healing todo

        self._draw_cards(card.draw)

        self.discard.append(card)
        return current_value

    def _draw_cards(self, count):
        for i in range(count):
            if len(self.draw) != 0:
                card = random.choice(self.draw)
                self.hand.append(card)
                self.draw.remove(card)
            elif len(self.cards) < 5:
                self.hand = copy(self.cards)
                return 
            else:
                self.shuffle_deck()
                card = random.choice(self.draw)
                self.hand.append(card)
                self.draw.remove(card)

    def _discard_cards(self, count):

        for i in range(count):
            chosen = sorted(self.hand)[0]
            self.discard.append(chosen)
            self.hand.remove(chosen)
    
    def _undiscard_hand(self, count):
        self.draw += self.hand
        self.hand.clear()
    def discard_hand(self):
        self.discard += self.hand
        self.hand.clear()

    def shuffle_deck(self):
        self.draw += self.discard
        self.discard = []

    def __copy__(self):
        return Deck(copy(self.cards), copy(self.draw), copy(self.discard), copy(self.hand), self.hasCrown,
                    self.hasArtifact)

    def add_to_deck(self, card):
        new_card = copy(card)
        self.discard.append(new_card)
        self.cards = self.draw + self.discard + self.hand

    def remove_from_deck(self, card):
        # Remove button from UI list
        if card in self.draw:
            self.draw.remove(card)
        elif card in self.hand:
            self.hand.remove(card)
        elif card in self.discard:
            self.discard.remove(card)

        self.cards = self.draw + self.discard + self.hand


    def move_card(self, card):
        if card in self.draw:
            self.hand.append(card)
            self.draw.remove(card)
        elif card in self.hand:
            self.discard.append(card)
            self.hand.remove(card)
        elif card in self.discard:
            self.draw.append(card)
            self.discard.remove(card)
        self.cards = self.draw + self.discard + self.hand


class HandValue:
    def __init__(self, skill, boots, swords, clank, gold, teleports, cards):
        self.skill = skill
        self.boots = boots
        self.swords = swords
        self.clank = clank
        self.gold = gold
        self.teleports = teleports
        self.cards = cards

    def __add__(self, other):
        if isinstance(other, HandValue):
            return HandValue(self.skill + other.skill, self.boots + other.boots, self.swords + other.swords,
                             self.clank + other.clank, self.gold + other.gold, self.teleports + other.teleports,
                             self.cards + other.cards if (len(other.cards) == 1 or len(self.cards) == 1) else [])
        else:
            return HandValue(self.skill + other, self.boots + other, self.swords + other,
                             self.clank + other, self.gold + other, self.teleports + other,
                             [])

    def __sub__(self, other):
        if isinstance(other, HandValue):
            return HandValue(self.skill - other.skill, self.boots - other.boots, self.swords - other.swords,
                             self.clank - other.clank, self.gold - other.gold, self.teleports - other.teleports,
                             [])
        else:
            return HandValue(self.skill - other, self.boots - other, self.swords - other,
                             self.clank - other, self.gold - other, self.teleports - other,
                             [])

    def __mul__(self, other):
        if isinstance(other, HandValue):
            return HandValue(self.skill * other.skill, self.boots * other.boots, self.swords * other.swords,
                             self.clank * other.clank, self.gold * other.gold, self.teleports * other.teleports,
                             [])
        else:
            return HandValue(self.skill * other, self.boots * other, self.swords * other,
                             self.clank * other, self.gold * other, self.teleports * other,
                             [])

    def __truediv__(self, other):
        if isinstance(other, HandValue):
            return HandValue(self.skill / other.skill, self.boots / other.boots, self.swords / other.swords,
                             self.clank / other.clank, self.gold / other.gold, self.teleports / other.teleports,
                             [])
        else:
            return HandValue(self.skill / other, self.boots / other, self.swords / other,
                             self.clank / other, self.gold / other, self.teleports / other,
                             [])

    def __str__(self):
        return (str(self.skill) + " skill " + str(self.boots) + " boots " + str(self.swords) + " swords " + str(
            self.clank) +
                " clank " + str(self.gold) + " gold " + str(self.teleports) + " teleports")
    
    
def flatten_handvalues(handvalues):
    total = HandValue(0, 0, 0, 0, 0, 0, [])
    for hv in handvalues:
        total += hv
    return total
