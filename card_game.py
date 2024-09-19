import random
from os import system

class Card():
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit
        self.is_the_black_lady = number == 'Q' and suit == '♠'
        self.sort_value = self._fetch_sort_value() # for sorting
        self.score = self._fetch_score() # for scoring
    
    def __repr__(self):
        return(self.number + self.suit)
    
    def _fetch_sort_value(self):
        if self.number in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
            return int(self.number)
        else:
            return ['J', 'Q', 'K', 'A'].index(self.number) + 11
    
    def _fetch_score(self):
        if self.suit == '♡':
            return 1
        elif self.is_the_black_lady:
            return 13
        else:
            return 0

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
        self.hand.sort(key = lambda card: (card.suit, card.sort_value))

    def cards(self):
        return [card.number + card.suit for card in self.hand]
    
    def make_move(self, move=None, suit=None, previous_plays=[], hearts_broken=False):
        options = self._define_options(suit, hearts_broken)

        move = move or (self.game.view.prompt_for_move(self, options) if self.playable else Computer(suit, options, previous_plays).choose())
        self.hand.remove(move)
        return move
    
    def trade_three_cards(self):
        trades = self.game.view.prompt_for_trade(self) if self.playable else random.sample(self.hand, 3)
        self.hand = [card for card in self.hand if card not in trades]
        return trades

    def _define_options(self, suit, hearts_broken):
        if not suit:
            return self.hand if hearts_broken else [card for card in self.hand if card.suit != '♡'] or self.hand
        
        options = [card for card in self.hand if card.suit == suit]
        return options or self.hand
    
    def identify_card(self, card_value):
        return next(iter(card for card in self.hand if card.number + card.suit == card_value), None)
    
    def shot_the_moon(self):
        return self.score == 26
    
class Computer():
    def __init__(self, suit, options, previous_plays):
        self.suit = suit
        self.previous_plays = previous_plays
        self.high_card = self._fetch_high_card()
        self.options = options
        self.leading = not any(previous_plays)
    
    def choose(self):
        print(f"Computer's options are: ", self.options) # for testing
        if self.leading:
            self._avoids_leading_high()
        elif self._can_dump_black_lady():
            self._dumps_black_lady()
        elif self._smells_blood():
            self._avoids_trick()
        elif self._notices_leading_spades():
            self._retains_black_lady_if_possible()
        
        return random.choice(self.options)
        
    def _fetch_high_card(self):
        return None if not self.previous_plays else max([card.sort_value for card in self.previous_plays if card.suit == self.suit])
        
    def _avoids_leading_high(self):
        print('avoiding leading high...') # for testing
        self.options = [card for card in self.options if card.sort_value < 11] or [min(self.options, key=lambda card: card.sort_value)]
        
    def _smells_blood(self):
        return self.suit == '♡' or any([card for card in self.previous_plays if card.is_the_black_lady])
    
    def _notices_leading_spades(self):
        return self.suit == '♠' and self.high_card < 13
    
    def _avoids_trick(self):
        print('avoiding trick...') # for testing
        good_options = [card for card in self.options if card.sort_value < self.high_card]
        self.options = [max(good_options, key=lambda card: card.sort_value)] if any(good_options) else [min(self.options, key=lambda card: card.sort_value)]

    def _can_dump_black_lady(self):
        return any(card for card in self.options if card.is_the_black_lady) and (self.suit != '♠' or self.high_card > 12)

    def _retains_black_lady_if_possible(self):
        print('retaining black lady if possible...') # for testing
        good_options = [card for card in self.options if not card.is_the_black_lady]
        if any(good_options):
            self.options = good_options
    
    def _dumps_black_lady(self):
        print('dumping black lady...') # for testing
        self.options = [card for card in self.options if card.is_the_black_lady]

class Game():
    def __init__(self):
        self.deck = Deck()
        self.view = View(self)
        self._fetch_players()
    
    def new_game(self):
        self.deck.deal(self.players)
        self.hearts_broken = False
        self._trade_three_cards()
        for player in self.players:
            player.sort_hand()
        self.turn = self._player_with_two_of_clubs()
        for i in range(13):
            plays = self._move()
            self._resolve_trick(plays)
        self._conclude_game()

    def _fetch_players(self):
        player_name = self.view.prompt_for_name()
        self.players = [Player(self, player_name, True)]
        for i in range(3):
            self.players.append(Player(self))
    
    def player_names(self):
        return [player.name for player in self.players]
    
    def _trade_three_cards(self):
        trades = []
        for (i, player) in enumerate(self.players):
            trades.append(((i + 1) % 4, player.trade_three_cards()))
        for (i, cards) in trades:
            self.players[i].hand += cards

    def _move(self):
        lead_player, other_players = self._identify_lead_player(self.turn)
        lead_player_move = self._lead_player_move(lead_player)
        lead_suit = lead_player_move.suit

        plays = [(lead_player, lead_player_move)]
        for player in other_players:
            play = player.make_move(suit=lead_suit, previous_plays=[play for (player, play) in plays])
            self.view.report_move(player.name, play)
            plays.append((player, play))

        return plays
    
    def _lead_player_move(self, lead_player):
        self.view.show_cards_and_tricks(lead_player)
        move = lead_player.make_move(lead_player.identify_card('2♣')) if '2♣' in lead_player.cards() else lead_player.make_move(hearts_broken=self.hearts_broken)

        self.view.report_move(lead_player.name, move)
        return move
    
    def _resolve_trick(self, plays, hearts_were_broken=False):
        cards, trump_card, trick_taker = self._parse_trick(plays)
        trick_taker.tricks += cards
        trick_taker.score += self._compute_trick(cards)
        self.turn = self.players.index(trick_taker)
        if not self.hearts_broken and '♡' in [card.suit for card in cards]:
            hearts_were_broken = True
            self.hearts_broken = True
        self.view.resolve_trick(trump_card, trick_taker.name, hearts_were_broken)

    def _parse_trick(self, plays):
        cards = [card for (player, card) in plays]
        lead_suit = cards[0].suit
        cards_of_lead_suit = [card for card in cards if card.suit == lead_suit]
        trump_card = max(cards_of_lead_suit, key=lambda card: card.sort_value)
        trick_taker = next(player for (player, card) in plays if card == trump_card)
        return (cards, trump_card, trick_taker)
    
    def _compute_trick(self, trick):
        return sum([card.score for card in trick])
    
    def _conclude_game(self):
        tally = self._fetch_card_tally()
        self.view.game_over(tally, self.moon_shooter)

    def _fetch_card_tally(self):
        self.moon_shooter = self._identify_moon_shooter()
        if self.moon_shooter:
            for schmuck in [player for player in self.players if not player == self.moon_shooter]:
                schmuck.score = 26
            self.moon_shooter.score = 0

        return [(player.name, [card for card in player.tricks if card.score], player.score) for player in self.players]

    def _identify_moon_shooter(self):
        moon_shooters = [player for player in self.players if player.shot_the_moon()] or [None]
        return next(iter(moon_shooters))

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
    
    def prompt_for_trade(self, player, previous_choices=[]):
        system('clear')
        print(f"Here's your current hand, {player.name}:", [card for card in player.hand if card not in previous_choices])
        print("\nSelect three cards to swap with your neighbor.\n")
        if previous_choices:
            print('Already chosen:', previous_choices)

        ordinals = ['First', 'Second', 'Third']
        response = None
        while not response:
            response = player.identify_card(
                input(f"{ordinals[len(previous_choices)]} card: ")
            )
            if not response:
                print("Sorry, you aren't holding that card.")
            elif response in previous_choices:
                response = None
                print("Sorry, you chose that one already.")
            else:
                previous_choices.append(response)
                return self.prompt_for_trade(player, previous_choices) if len(previous_choices) < 3 else previous_choices

    
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
        print('')
        # for player in [p for p in self.game.players if p.playable]:
        #     print(f"\n{player.name}'s score: {player.score}")
    
    def resolve_trick(self, trump_card, trick_taker, hearts_were_broken):
        print(f"The highest card of the lead suit was {trump_card}")
        print(f"{trick_taker} takes the trick.")
        if hearts_were_broken:
            print("Also, hearts have now been broken!")
        input("OK? ")
    
    def game_over(self, tally, moon_shooter):
        system('clear')
        scorecard = ""
        if moon_shooter:
            print(f"You schmucks, {moon_shooter.name} shot the moon!\n")
        else:
            print(f"Good game, everybody, good game!\n")
        for t in tally:
            print(t[0], t[1])
            scorecard += f"{t[0]}: {t[2]} "
        print("\nFinal scores: " + scorecard)
        print('Game Over')

game = Game().new_game()
