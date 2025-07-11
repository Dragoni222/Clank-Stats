from app import run_app
from data.card_data import CARD_STATS
from logic.simulation import Deck, HandValue
from logic.card_loader import Card
if __name__ == "__main__":
    run_app()
    
    
    #test deckbuilder
    
    cards = ["basic","Explore","Mercenary","Mercenary"]
    
    card_objects = []
    basic_card_objects = []
    basic_card_objects.append(list(filter(lambda x: x.name == "Stumble", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Stumble", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Burgle", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Burgle", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Burgle", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Burgle", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Burgle", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Burgle", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Scramble", CARD_STATS))[0])
    basic_card_objects.append(list(filter(lambda x: x.name == "Sidestep", CARD_STATS))[0])
    for card in cards:
        if card == "basic":
            card_objects += basic_card_objects
        else:
            card_objects.append(list(filter(lambda x: x.name == card, CARD_STATS))[0])
        
    
    
    deck = Deck(card_objects)
    basicDeck = Deck(basic_card_objects)
    totals = HandValue(0,0,0,0,0,0,[])
    basictotals = HandValue(0,0,0,0,0,0,[])
    epochs = 50000
    hands = []
    basic_hands = []
    for i in range(epochs):
        deck.drawHand()
        basicDeck.drawHand()
        basic_hand = basicDeck.simulate_hand()
        basictotals += basic_hand
        basic_hands.append(basic_hand)
        hand = deck.simulate_hand()
        totals += hand
        hands.append(hand)
        
    
    print("custom:",cards)
    print("Average:",totals/epochs)
    print("skill distribution:")
    print("1",sum(x.skill <= 1 for x in hands)/(epochs/100),"%")
    print("2",sum(x.skill == 2 for x in hands)/(epochs/100),"%")
    print("3",sum(x.skill == 3 for x in hands)/(epochs/100),"%")
    print("4",sum(x.skill == 4 for x in hands)/(epochs/100),"%")
    print("5",sum(x.skill == 5 for x in hands)/(epochs/100),"%")
    print("6",sum(x.skill == 6 for x in hands)/(epochs/100),"%")
    print("7",sum(x.skill >= 7 for x in hands)/(epochs/100),"%")
    print("vs basic:")
    print("Average:",basictotals/epochs)
    print("skill distribution:")
    print("1",sum(x.skill <= 1 for x in basic_hands)/(epochs/100),"%")
    print("2",sum(x.skill == 2 for x in basic_hands)/(epochs/100),"%")
    print("3",sum(x.skill == 3 for x in basic_hands)/(epochs/100),"%")
    print("4",sum(x.skill == 4 for x in basic_hands)/(epochs/100),"%")
    print("5",sum(x.skill == 5 for x in basic_hands)/(epochs/100),"%")
    print("6",sum(x.skill == 6 for x in basic_hands)/(epochs/100),"%")
    print("7",sum(x.skill >= 7 for x in basic_hands)/(epochs/100),"%")
    
    
    
    
