import random
from os import system

class Card():
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit
    
    def __repr__(self):
        return(self.number + self.suit)

class Deck():
    def __init__(self):
        self.numbers = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.suits = ['♠', '♡', '♢', '♣']

    def populate(self):
        self.cards = []
        for number in self.numbers:
            for suit in self.suits:
                self.cards.append(Card(number, suit))
    
    def deal(self, players):
        number_of_cards = 13
        self.populate()
        random.shuffle(self.cards)
        for player in players:
            player.hand = self.cards[:number_of_cards]
            player.sort_hand()
            self.cards = self.cards[number_of_cards:]
    
class Player():
    def __init__(self, name=None):
        self.name = name or self._random_name()
        self.hand = []
        self.tricks = []

    def _random_name(self):
        names = ['Adam', 'Ahmet', 'Alessandro', 'Alexandre', 'Alfie', 'Daniel', 'Efaz', 'Isaac', 'Jess', 'Johannes', 'Matt', 'Mercy', 'Patrick', 'Rahnel', 'Shaeera', 'Taha', 'Tobi', 'Valeria', 'Will']
        return random.choice(names)

    def sort_hand(self):
        self.hand.sort(key = lambda card: (card.suit, card.number))

    def cards(self):
        return [card.number + card.suit for card in self.hand]

class Game():
    def __init__(self):
        self.players = [Player() for i in range(4)]
        self.deck = Deck()
        self.view = View(self)
    
    def new_game(self):
        self.deck.deal(self.players)
        self.turn = 0
        self.move()

    def move(self):
        move = self.view.prompt_for_move(self.players[self.turn])

class View():
    def __init__(self, game):
        self.game = game
    
    def prompt_for_move(self, lead_player):
        system('clear')
        response = None
        print(f"It's {lead_player.name}'s turn to lead:\n")
        for player in self.game.players:
            print(player.name, player.hand)
        while not response:
            response = input(f"\nWhich card will {lead_player.name} play? ")
            if response in lead_player.cards():
                print(f"{lead_player.name} plays {response}.")
            else:
                print(f"Sorry, {lead_player.name} isn't holding that card.")
                response = None


game = Game()
game.new_game()
