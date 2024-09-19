import random
from os import system

class Card():
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit
        self.value = self._fetch_value()
        self.is_the_black_lady = number == 'Q' and suit == '♠'
    
    def __repr__(self):
        return(self.number + self.suit)
    
    def _fetch_value(self):
        if self.number in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
            return int(self.number)
        else:
            return ['J', 'Q', 'K', 'A'].index(self.number) + 11

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
    def __init__(self, game, name=None, playable=False):
        self.game = game
        self.name = name or self._random_name()
        self.playable = playable
        self.hand = []
        self.tricks = []
        self.score = 0

    def _random_name(self):
        names = ['Adam', 'Ahmet', 'Alessandro', 'Alexandre', 'Alfie', 'Daniel', 'Efaz', 'Isaac', 'Jess', 'Johannes', 'Matt', 'Mercy', 'Patrick', 'Rahnel', 'Shaeera', 'Taha', 'Tobi', 'Valeria', 'Will']
        choices = [name for name in names if name not in self.game.player_names()]
        return random.choice(choices)

    def sort_hand(self):
        self.hand.sort(key = lambda card: (card.suit, card.value))

    def cards(self):
        return [card.number + card.suit for card in self.hand]
    
    def make_move(self, move=None, suit=None, hearts_broken=False):
        options = self._define_options(suit, hearts_broken)

        move = self.game.view.prompt_for_move(self, options) if self.playable else move or random.choice(options)
        self.hand.remove(move)
        return move
    
    def _define_options(self, suit, hearts_broken):
        if not suit:
            return self.hand if hearts_broken else [card for card in self.hand if card.suit != '♡'] or self.hand
        
        options = [card for card in self.hand if card.suit == suit]
        return options or self.hand
    
    def identify_card(self, card_value):
        return next(iter(card for card in self.hand if card.number + card.suit == card_value), None)

class Game():
    def __init__(self):
        self.deck = Deck()
        self.view = View(self)
    
    def new_game(self):
        self.fetch_players()
        self.deck.deal(self.players)
        self.hearts_broken = False
        self.turn = self._player_with_two_of_clubs()
        for i in range(13):
            plays = self.move()
            self.resolve_trick(plays)
    
    def fetch_players(self):
        player_name = self.view.prompt_for_name()
        self.players = [Player(self, player_name, True)]
        for i in range(3):
            self.players.append(Player(self))
    
    def player_names(self):
        return [player.name for player in self.players]

    def move(self):
        lead_player, other_players = self._identify_lead_player(self.turn)
        lead_player_move = self._lead_player_move(lead_player)
        lead_suit = lead_player_move.suit

        plays = [(lead_player, lead_player_move)]
        for player in other_players:
            play = player.make_move(suit=lead_suit)
            self.view.report_move(player.name, play)
            plays.append((player, play))

        return plays
    
    def _lead_player_move(self, lead_player):
        self.view.show_cards_and_tricks(lead_player)
        move = lead_player.identify_card('2♣') if '2♣' in lead_player.cards() else lead_player.make_move(hearts_broken=self.hearts_broken)
        self.view.report_move(lead_player.name, move)
        return move
    
    def resolve_trick(self, plays):
        cards = [card for (player, card) in plays]
        lead_suit = cards[0].suit
        cards_of_lead_suit = [card for card in cards if card.suit == lead_suit]
        trump_card = max(cards_of_lead_suit, key=lambda card: card.value)
        print(f"The highest card of the lead suit was {trump_card}")
        trick_taker = next(player for (player, card) in plays if card == trump_card)
        print(f"{trick_taker.name} takes the trick.")
        trick_taker.tricks.append(cards)
        trick_taker.score += self.compute_trick(cards)
        self.turn = self.players.index(trick_taker)
        if not self.hearts_broken and '♡' in [card.suit for card in cards]:
            print("Also, hearts have now been broken!")
            self.hearts_broken = True
        return input("OK? ")
    
    def compute_trick(self, trick):
        result = len([card for card in trick if card.suit == '♡'])
        if any([card for card in trick if card.is_the_black_lady]):
            result += 13
        return result

    def _identify_lead_player(self, turn):
        lead_player = self.players[turn]
        other_players = []
        for i in range(1, 4):
            i = (turn + i) % 4
            other_players.append(self.players[i])
        return [lead_player, other_players]
    
    def _player_with_two_of_clubs(self):
        return next(self.players.index(player) for player in self.players if '2♣' in player.cards())

class View():
    def __init__(self, game):
        self.game = game

    def prompt_for_name(self):
        system('clear')
        response = None
        print("Hey there, how'd you like to play a game of Hearts?\n")
        return input("Please enter your name: ")
    
    def prompt_for_move(self, player, options):
        response = None
        while not response:
            response = player.identify_card(
                input(f"\nWhich card you gonna play, {player.name}? ")
            )
            if not response:
                print(f"Sorry, {player.name}, you aren't holding that card.")
            elif not response in options:
                print("Sorry, that's not a legal move.")
                response = None
        return response
    
    def report_move(self, player, play):
        print(f"{player} plays {play}.")
    
    def show_cards_and_tricks(self, lead_player):
        system('clear')
        print(f"It's {lead_player.name}'s turn to lead:\n")
        for player in self.game.players:
            print(player.name, player.hand)
        for player in [p for p in self.game.players if p.playable]:
            print(f"\n{player.name}'s score: {player.score}")

game = Game()
game.new_game()
