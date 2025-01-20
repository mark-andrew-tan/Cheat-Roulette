import random


# Define a Table class
class Table:
    def __init__(self):
        self.allcards = []
        self.lasthand = []

    def receive_hand(self, cards):
        self.lasthand = (cards)
        self.allcards.extend(cards)

    def get_total_cards(self):
        return len(self.allcards)

    def show_last_hand(self):
        return print(f"last hand: {self.lasthand}")

    def show_lasthand_len(self):
        return print(f"Played {len(self.lasthand)} card(s)\n")
    
    def clear_table(self):
        self.allcards = []

# Define a Card class
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank}{self.suit}"

# Define a Deck class
class Deck:
    def __init__(self):
        self.suits = ['H', 'D', 'S']
        self.ranks = ['2', '3', '4', '5', '6', '7']
        # Create the deck with x of each suit plus two Jokers

    def new_deck(self):
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks] + [Card('', 'J'), Card('', 'J')]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards):
        # Deals the specified number of cards
        return [self.cards.pop() for _ in range(num_cards) if self.cards]

# Define a Player class
class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.position = 0
        self.hand = []
        self.bullets = 4
        self.survive_bullet = False
        self.safe = False
        self.truth = False
        self.must_call = False
        self.is_human = is_human  # Determines if the player is human

    def receive_cards(self, cards):
        self.hand.extend(cards)

    def count_suit(self, suit):
        return sum(1 for card in self.hand if card.suit == suit)

    def show_hand(self):
        return ', '.join(map(str, self.hand))

    def shoot_bullet(self):
        if self.bullets > 1:
            return random.randint(1, self.bullets) == 1
        else:
            return 1
        
    def reload(self):
        self.bullets -= 1

    def remove_truth_cards(self, suit, count):
        removed_cards = []
        for card in self.hand:
            if len(removed_cards) < count:
                if card.suit == suit or card.suit == 'J':
                    removed_cards.append(card)
        self.hand = [card for card in self.hand if card not in removed_cards]
        return removed_cards

    def remove_lie_cards(self, suit, count):
        removed_cards = []
        for card in self.hand:
            if len(removed_cards) < count:
                if card.suit != suit and card.suit != 'J':
                    removed_cards.append(card)
        self.hand = [card for card in self.hand if card not in removed_cards]
        return removed_cards

    def make_ai_decision(self, round_suit, total_table_cards, round_turn, safe_players):
        # AI decision based on probability
        win_suit_count = self.count_suit(round_suit)
        joker_count = self.count_suit('J')
        total_count = win_suit_count + joker_count
        lie_count = len(self.hand) - total_count

        # Basic probability-based decision: higher win_suit_count increases chance of truth
        if round_turn == 0 and safe_players < 3 or total_count >= lie_count and safe_players < 3:
            return "play"
        else:
            return "call"

    def ai_play(self, round_suit, total_table_cards):
        # AI decision based on probability
        win_suit_count = self.count_suit(round_suit)
        joker_count = self.count_suit('J')
        total_count = win_suit_count + joker_count
        lie_count = len(self.hand) - total_count

        # Basic probability-based decision: higher win_suit_count increases chance of truth
        if total_count > lie_count:
            # truth
            if total_count >= 3:
                # print("AI: Truth\n")
                self.truth = True
                return self.remove_truth_cards(round_suit, random.randint(1,3))
            else:
                # print("AI: Truth\n")
                self.truth = True
                return self.remove_truth_cards(round_suit, random.randint(1,total_count))
        elif lie_count >= 0:
            if lie_count >= 3:
                # print("AI: Lie\n")
                self.truth = False
                return self.remove_lie_cards(round_suit, random.randint(1,3))
            else:
                # print("AI: Lie\n")
                print(f"lie_count: {lie_count}")
                self.truth = False
                return self.remove_lie_cards(round_suit, random.randint(1,lie_count))
        else:
            return "c"  # "Call"


###########################################################################    
###########################################################################                
###########################################################################
# Game setup 
table = Table()
deck = Deck()
start_players = 4
cards_per_player = 5

# Create players, setting Player 1 as human
players = [Player("Pla 1", is_human=True)] + [Player(f"Com {i}") for i in range(2, start_players + 1)]

random.shuffle(players)


###########################################################################    
###########################################################################                
###########################################################################
# Start of game
game_active = True

round_active = True

############### start of each new round ###################
while game_active: 
    round_active = True
    round_turn = 0
    deck.new_deck()
    deck.shuffle()
    table.clear_table()
    round_suit = random.choice(deck.suits)
    print(f"***** Round suit: {round_suit} ******")
    print(f"{len(players)} player(s) remaining\n")

    # Deal 5 cards to each player
    for player in players:
        player.receive_cards(deck.deal(cards_per_player))
        player.safe = False

    # starting safe count is 0 if all alive, 1 if 1 dead, 2 if 2 dead etc.
    safe_count = start_players - len(players) 

    ### Gameplay ###
    while round_active: 

        # update position variables for reordering players
        for index2, pla in enumerate(players):
            pla.position = index2

        # reorder player that takes shot to the front.
        for player in players:
            if player.survive_bullet:
                players = [players[player.position]] + players[:player.position] + players[player.position + 1:]
                player.survive_bullet = False

        # game.update_player_display()

        print("## Order ##")
        for z in players:
            if not z.safe:
                print(z.name)
        print("###########")
        
        for index, player in enumerate(players):
            if player.safe: # skip player if safe
                print(f"index: {index} : player safe loop")
                continue

                     
            else:
                print(f"\n --->>> {player.name}'s turn <<<---")
    
                win_suit_count = player.count_suit(round_suit)
                joker_count = player.count_suit('J')
                total_count = win_suit_count + joker_count
                lie_count = len(player.hand) - total_count
    
                # Player 1 (human) decision
                if player.is_human:
                    print(f"Hand: {player.show_hand()}\n")

                    if safe_count >= 3:
                        action = "c"

                    elif(round_turn == 0):
                        action = input("Truth, or lie ('t', 'l')").strip().lower()
                        
                    else:
                        action = input("Truth, lie, or call? ('t', 'l', 'c')").strip().lower()
    
                    # Process the action
                    if action == "t":
                        print(f"You can play up to {total_count} truth cards")
                        num_truth_cards = int(input())                        
                        table.receive_hand(player.remove_truth_cards(round_suit, num_truth_cards))
                        print(f"Updated hand: {player.show_hand()}\n")
                        print(f"Table: {table.get_total_cards()} card(s)")
                        player.truth = True
                        round_turn += 1
                        # Check if the player is safe, add to safe count
                        if len(player.hand) <= 0:
                            player.safe = True
                            safe_count += 1
                    elif action == "l":
                        print(f"You can play up to {lie_count} lie cards")
                        num_lie_cards = int(input())
                        table.receive_hand(player.remove_lie_cards(round_suit, num_lie_cards))
                        print(f"Updated hand: {player.show_hand()}\n")
                        print(f"Table: {table.get_total_cards()} card(s)")
                        player.truth = False
                        round_turn += 1
                        # Check if the player is safe, add to safe count
                        if len(player.hand) <= 0:
                            player.safe = True
                            safe_count += 1
                    elif action == "c":
                        print(f"{player.name} is calling the previous player a liar!")
                        table.show_last_hand()
                        if (index == 0):
                            temp_index = len(players)-1
                        else:
                            temp_index = index-1
                        if (players[temp_index].truth):
                            print(f"{players[temp_index].name} truth! Player 1 must take a shot!")
                            if player.shoot_bullet():
                                print(f"{player.name} is out of the game!")
                                players.remove(player)

                                if len(players) == 1:
                                    print(f"\n ###### {players[0].name} is the winner! ######")
                                    round_active = False
                                    game_active = False
                                    break
                                    
                            else:
                                print(f"Fired Blank! {player.name} survived!")
                                player.survive_bullet = True
                                player.reload
                                
                            round_active = False
                            break
                        else:
                            print(f"{players[temp_index].name} lied and must take a shot!")
                            if players[temp_index].shoot_bullet():
                                print(f"!!BANG!! {players[temp_index].name} is out of the game!")
                                players.remove(players[temp_index])


                                if len(players) == 1:
                                    print(f"{players[0].name} is the winner!")
                                    round_active = False
                                    game_active = False
                                    break
                            else:
                                print(f"Fired Blank! {players[temp_index].name} survived!")
                                players[temp_index].survive_bullet = True
                                players[temp_index].reload
                                
                            round_active = False
                            break
                    elif action == "end":
                        round_active = False
                        game_active = False
                        print("Ending the game.")
                        break
    
                    else:
                        print("Invalid action. Please choose a valid action.")
                        
                # if not human, do computer AI decision:
                else:
                    # Computer decision

                    # notes for better implementation:
                    # we will break it into two choices: Play, or Call
                    # If Play:
                    # AI will execute in player class
                    # If Call,
                    # execute action here

                    # also check if there are 2 players remaining, AND previous player has no cards, player must call
                    print(f"Hand: |?| X {len(player.hand)}\n")
                    if player.make_ai_decision(round_suit, table.get_total_cards(), round_turn, safe_count) == "play":                 # AI plays card  
                        table.receive_hand(player.ai_play(round_suit,table.get_total_cards()))
                        table.show_lasthand_len()
                        print(f"Updated hand: |?| X {len(player.hand)}\n")
                        print(f"Table: {table.get_total_cards()} card(s)")
                        round_turn += 1
                        # Check if the player is safe, add to safe count
                        if len(player.hand) <= 0:
                            player.safe = True
                            safe_count += 1
                            
                    elif player.make_ai_decision(round_suit, table.get_total_cards(), round_turn, safe_count) == "call":
                        # AI makes call
                        print(f"{player.name} is calling the previous player a liar!")
                        table.show_last_hand()
                        if (index == 0):
                            temp_index = len(players)-1
                        else:
                            temp_index = index-1
                        if (players[temp_index].truth): # check if previous player truth
                            print(f"{players[temp_index].name} truth! {player.name} must take a shot!")                     # AI must shoot self if previous player is truth
                            if player.shoot_bullet():
                                print(f"{player.name} is out of the game!")
                                players.remove(player)

                                if len(players) == 1: # winner if last standing
                                    print(f"\n ###### {players[0].name} is the winner! ######")
                                    round_active = False
                                    game_active = False
                                    break
                            else:
                                # surviving the shot
                                print(f"Fired Blank! {player.name} survived!")
                                player.survive_bullet = True
                                player.reload

                            round_active = False
                            break
                        else:
                            # if prev player lie, prev player must take shot
                            print(f"{players[temp_index].name} lied and must take a shot!")
                            if players[temp_index].shoot_bullet():
                                print(f"!!BANG!! {players[temp_index].name} is out of the game!")
                                players.remove(players[temp_index])

                                if len(players) == 1:
                                    print(f"\n ###### {players[0].name} is the winner! ######")
                                    round_active = False
                                    game_active = False
                                    break
                            else:
                                print(f"Fired Blank! {players[temp_index].name} survived!")
                                players[temp_index].survive_bullet = True
                                players[temp_index].reload
                            round_active = False
                            break
         

    # Round over. Remove all player cards from the game
    for player in players:
        player.hand = []
    if (game_active):
        print("\n!!! new round !!!\n")
        input("Press any key + 'enter' to continue...\n")



