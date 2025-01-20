"""

MOST STABLE VERSION.

BUGS:

ISSUE WHERE PLAYER PLAYS REMAINING CARDS AND THE NEXT COM CALLS ON PLAYER:
COM BEFORE THE PLAYER IS CHECKED INSTEAD OF THE PLAYER.
(COM BEFORE PLAYER WAS DEAD PRIOR TO EVENT)

EDIT:

LOOKS LIKE THIS OCCURS WHEN ANY PLAYER/COM GETS RID OF CARDS, AND THE COM AFTER THEM IMMEDAIETLY CALLS THEM.

IT SHOULD CALL THE PLAYER/COM WITH THE EMPTY HAND, BUT IT INSTEAD CALLS THE PLAYER WITH A HAND

IDEAS FOR FIX: 

Another variable that stores the order_index of the current player before they are removed (for player safe)

then this previous player is used for comparison when called. Instead of calculating previous player later
_______________________
FUTURE IDEAS:

Powerups:

- see 3 cards of other players choosing
     - how to balance?
        - player that chooses to peek at other player will be skipped

"""
#region Notes
"""
Command = ... (lambda:)

In Tkinter, when you assign a function to the command argument of a button, you provide a reference to the function, 
not the result of calling it. If you include the parentheses (()), the function is called immediately, and the result 
(if any) is assigned to command. This is not what you want in this case.

Explanation Without Parentheses

btn_increase = tk.Button(master=window, text="+", command=increase)

Here, the increase function is passed by reference to the command argument. 
Tkinter will call the increase function later, when the button is clicked.

What Happens With Parentheses

btn_increase = tk.Button(master=window, text="+", command=increase())

The increase() function is called immediately when this line is executed.
The return value of the increase() function (if any) is assigned to command. 
Since increase() doesn't return anything (None), this effectively sets command=None, which disables the button's functionality.

How Tkinter Executes the Command
When you click the button, Tkinter internally calls the function you passed to command. 
If you pass increase without parentheses, Tkinter knows to call it later, ensuring the function runs only when the button is clicked.

If You Need Arguments
If you want to pass arguments to the function, use a lambda function to wrap the call.

"""
#endregion

import random
import tkinter as tk
from pygame import mixer
mixer.init()



# Define a Player class
class Player:
    def __init__(self, name, position):
        self.name = name
        self.turns = 0
        self.hand = []
        self.bullets = 3
        self.survive_bullet = False
        self.safe = False
        self.truth = False
        self.truth_count = 0
        self.lie_count = 0
        self.call = False
        self.must_call = False
        self.alive = True
        self.position = position  # position 1 = HUMAN. ELSE = AI

        # the positioning/turns is based on the players/AI's index in the array


    def receive_cards(self, cards):
        self.hand.extend(cards)
    
    def clear_hand(self):
        self.hand = []

    def count_valid_cards(self, suit):
        sum = 0
                   
        for card in self.hand:
            if card == suit or card == 'J':
                sum += 1
        
        return sum
                       
    def check_choices(self, round_suit):
        truth_count = self.count_valid_cards(round_suit)
        lie_count = len(self.hand) - truth_count

        return {"truth_count": truth_count, "lie_count": lie_count}  # Returns a dictionary

    def check_safe(self):
        if len(self.hand) == 0:
            self.safe = True
            return True
        else:
            return False

    def show_hand(self):
        return f"|{'|'.join(map(str, self.hand))}|"
    
    def get_hand_len(self):
        return len(self.hand)

    def shoot_bullet(self):
        if self.bullets > 1:
            return random.randint(1, self.bullets) == 1
        else:
            return 1
        
    def reload(self):
        self.bullets -= 1

    def remove_truth_cards(self, round_card, count):
        removed_cards = []
        found = 0
        index = 0
        while found < count:

            if self.hand[index] == round_card or self.hand[index] == "J":
                removed_cards.append(self.hand[index])
                self.hand.remove(self.hand[index])
                found += 1
            else:
                index += 1
        return removed_cards

    def remove_lie_cards(self, round_card, count):
        removed_cards = []
        found = 0
        index = 0
        while found < count:

            if self.hand[index] != round_card and self.hand[index] != "J":
                removed_cards.append(self.hand[index])
                self.hand.remove(self.hand[index])
                found += 1
            else:
                index += 1
        return removed_cards

    def make_ai_decision(self, round_suit, total_table_cards, round_turns, remaining_players):
        # AI decision based on probability
        truth_count = self.count_valid_cards(round_suit)        
        lie_count = len(self.hand) - truth_count

        # Basic probability-based decision: higher truth_count increases chance of truth
        print(f"make_ai_dec_ remaining players: {remaining_players}\n")
        # print(f"truth = {truth_count}\n")
        # print(f"round_turns = {round_turns}\n")
        if round_turns == 0 or truth_count >= 2 and remaining_players >= 2:
            print("AI DECIDED TO PLAY!")
            return "play"
        else:
            print("AI DECIDED TO CALL!")

            return "call"

    def ai_play(self, round_suit, total_table_cards):
        # AI decision based on probability
        truth_count = self.count_valid_cards(round_suit)
        
        
        lie_count = len(self.hand) - truth_count

        print(f"truth_count = {truth_count}")
        # Basic probability-based decision: higher truth_count increases chance of truth
        if truth_count > lie_count:
            # truth
            if truth_count >= 3:
                print("AI: TruthA")
                self.truth = True
                return self.remove_truth_cards(round_suit, random.randint(1,3))
            else:
                print("AI: TruthB")
                self.truth = True
                return self.remove_truth_cards(round_suit, random.randint(1,truth_count))
        elif lie_count >= 0:
            if lie_count >= 3:
                print("AI: LieA")
                self.truth = False
                return self.remove_lie_cards(round_suit, random.randint(1,3))
            else:
                print("AI: LieB")
                self.truth = False
                return self.remove_lie_cards(round_suit, random.randint(1,lie_count))

    def ai_call(self):
        return True
        


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
    
    def get_all_cards(self):
        return self.allcards

    def show_last_hand(self):
        return f"{self.lasthand}"

    def get_lasthand_len(self):
        return len(self.lasthand)
    
    def clear_table(self):
        self.allcards = []

# Define a Deck class
class Deck:
    
    def __init__(self):
        self.cards = ["J","J","A","A","A","A","A","A","Q","Q","Q","Q","Q","Q","K","K","K","K","K","K"]
        # Create the deck with 6 of each suit plus two Jokers
        self.suits = ['A', 'Q', 'K']
    def new_deck(self):
        self.cards = ["J","J","A","A","A","A","A","A","Q","Q","Q","Q","Q","Q","K","K","K","K","K","K"]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards):
        # Deals the specified number of cards
        return [self.cards.pop() for _ in range(num_cards) if self.cards]

# Game class
class Game:
    def __init__(self, PLAYER_frame, INFO_frame_top, INFO_frame_right, COM_frame_left, COM_frame_right, COM_frame_top, p1_color, AI_color):
        
        self.com_death_canvas_list = [] # List to store canvas references

        # importing graphic frames made in main section
        self.player_frame = PLAYER_frame
        self.com_frame_left = COM_frame_left
        self.com_frame_right = COM_frame_right
        self.com_frame_top = COM_frame_top
        self.info_frame_top = INFO_frame_top
        self.info_frame_right = INFO_frame_right
        self.player_color = p1_color
        self.com_color = AI_color

        self.start_bullets = 3

        self.dead_color = "#880808"
        

        self.table = Table()
        self.deck = Deck()
        self.start_players = 4
        # Create players, setting Player 1 as human
        self.players = [Player("Pla 1", 1)] + [Player(f"Com {i-1}", i) for i in range(2, self.start_players + 1)]

        # Create player kill canvas (initially hidden)
        self.fading_canvas = tk.Canvas(window, bg="white")   
        # button for restart
        self.restart_button = tk.Button(master=window, text="RETRY?", command=self.prior_start, font=("Verdana", 45, "bold"))
        self.restart_button.forget()

        self.btn_new_game= tk.Button(master=INFO_frame_right, text="[NEW GAME]", font=("Verdana", 20, "bold"), command=self.prior_start ,borderwidth=8,relief="raised")
        self.btn_new_game.forget()

        self.game_active = True
        self.round_active = True
        self.cards_per_player = 5

        ############## LABELS  #############
        # ROUND SUIT LABEL
        self.lbl_roundsuit = tk.Label(master=self.info_frame_top, text="", font=("Verdana", 24, "bold"), bg="orange")
        self.lbl_roundsuit.place(relx=0.5, rely=0.5, anchor="center")

        # CALL RESULT LABEL
        self.lbl_call_result = tk.Label(master=self.info_frame_top, text="", font=("Verdana", 20, "bold"), bg="orange")
        self.lbl_call_result.place(relx=0.5, rely=0.8, anchor="center")

        # Shoot label
        self.lbl_shoot = tk.Label(master=self.info_frame_right, text="GOOD LUCK :)", font=("Verdana", 24, "bold"), bg="orange")
        self.lbl_shoot.place(relx=0.5, rely=0.5, anchor="center")

        # display hands
        self.lbl_hand_player = tk.Label(master=player_frame, text="", font=("Verdana", 16, "bold"),borderwidth=3,relief="groove",highlightthickness=5,highlightbackground="blue",bg=self.player_color)
        self.lbl_hand_player.place(relx=0.5, rely=0.2, anchor="center")
    
        self.lbl_hand_COM1 = tk.Label(master=COM_frame_left, text="", font=("Verdana", 16, "bold"))
        self.lbl_hand_COM1.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_hand_COM2 = tk.Label(master=COM_frame_top, text="", font=("Verdana", 16, "bold"))
        self.lbl_hand_COM2.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_hand_COM3 = tk.Label(master=COM_frame_right, text="", font=("Verdana", 16, "bold"))
        self.lbl_hand_COM3.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_table_value = tk.Label(master=TABLE_frame, text=f"", font=("Verdana", 16, "bold"))
        self.lbl_table_value.place(relx=0.5, rely=0.5, anchor="center")

        # ARROW INDICATORS
        self.lbl_table_COM1 = tk.Label(master=TABLE_frame, text=f"", font=("Verdana", 48, "bold"), bg="#315025", fg="yellow")
        self.lbl_table_COM1.place(relx=0.2, rely=0.5, anchor="center")

        self.lbl_table_COM2 = tk.Label(master=TABLE_frame, text=f"", font=("Verdana", 48, "bold"), bg="#315025", fg="yellow")
        self.lbl_table_COM2.place(relx=0.5, rely=0.2, anchor="center")

        self.lbl_table_COM3 = tk.Label(master=TABLE_frame, text=f"", font=("Verdana", 48, "bold"), bg="#315025", fg="yellow")
        self.lbl_table_COM3.place(relx=0.8, rely=0.5, anchor="center")

        self.lbl_table_PLAYER = tk.Label(master=TABLE_frame, text=f"", font=("Verdana", 48, "bold"), bg="#315025", fg="yellow")
        self.lbl_table_PLAYER.place(relx=0.5, rely=0.8, anchor="center")

        # display COM played info label for future

        self.lbl_turn_COM1 = tk.Label(master=COM_frame_left, text=f"", font=("Verdana", 12, "bold"), bg="yellow")
        self.lbl_turn_COM1.place(relx=0.5, rely=0.2, anchor="center")
  
        self.lbl_played_COM1 = tk.Label(master=COM_frame_left, text=f"", font=("Verdana", 12, "bold"))
        self.lbl_played_COM1.place(relx=0.5, rely=0.7, anchor="center")

        self.lbl_turn_COM2 = tk.Label(master=COM_frame_top, text=f"", font=("Verdana", 12, "bold"), bg="yellow")
        self.lbl_turn_COM2.place(relx=0.5, rely=0.2, anchor="center")

        self.lbl_played_COM2 = tk.Label(master=COM_frame_top, text=f"", font=("Verdana", 12, "bold"))
        self.lbl_played_COM2.place(relx=0.5, rely=0.7, anchor="center")

        self.lbl_turn_COM3 = tk.Label(master=COM_frame_right, text=f"", font=("Verdana", 12, "bold"), bg="yellow")
        self.lbl_turn_COM3.place(relx=0.5, rely=0.2, anchor="center")

        self.lbl_played_COM3 = tk.Label(master=COM_frame_right, text=f"", font=("Verdana", 12, "bold"))
        self.lbl_played_COM3.place(relx=0.5, rely=0.7, anchor="center")
      
        # display player 1 truth/lie cards count

        self.lbl_turn_player = tk.Label(master=player_frame, text=f"", font=("Verdana", 12, "bold"), bg="yellow")
        self.lbl_turn_player.place(relx=0.85, rely=0.1, anchor="center")

        self.lbl_p1_truth_count = tk.Label(master=player_frame, text="", font=("Verdana", 10, "bold"))
        self.lbl_p1_truth_count.place(relx=0.1, rely=0.7, anchor="center")

        self.lbl_p1_lie_count = tk.Label(master=player_frame, text="", font=("Verdana", 10, "bold"))
        self.lbl_p1_lie_count.place(relx=0.1, rely=0.9, anchor="center")

        self.lbl_play_choice = tk.Label(master=player_frame, text="", font=("Verdana", 12, "bold"))
        self.lbl_play_choice.place(relx=0.5, rely=0.71, anchor="center")
        
        self.lbl_play_value = tk.Label(master=player_frame, text="", font=("Verdana", 12, "bold"))
        self.lbl_play_value.place(relx=0.5, rely=0.9, anchor="center")

        self.btn_next= tk.Button(master=player_frame, text="[next]", font=("Verdana", 14, "bold"), command=self.update_table_ai)
        self.btn_next.place(relx=0.85, rely=0.8, anchor="center")
        self.btn_next.place_forget()

        self.btn_newround= tk.Button(master=INFO_frame_right, text="[NEW ROUND]", font=("Verdana", 20, "bold"), command=self.new_round)
        self.btn_newround.place(relx=0.5, rely=0.8, anchor="center")
        self.btn_newround.place_forget()

        # display bullet counts

        self.lbl_bullet_PLAYER = tk.Label(master=self.info_frame_right, text="", font=("Verdana", 20, "bold"), bg="red")
        self.lbl_bullet_PLAYER.place(relx=0.5, rely=0.2, anchor="center")
        self.lbl_bullet_COM1 = tk.Label(master=COM_frame_left, text="", font=("Verdana", 13, "bold"), bg="red")
        self.lbl_bullet_COM1.place(relx=0.85, rely=0.2, anchor="center")
        self.lbl_bullet_COM2 = tk.Label(master=COM_frame_top, text="", font=("Verdana", 13, "bold"), bg="red")
        self.lbl_bullet_COM2.place(relx=0.85, rely=0.2, anchor="center")
        self.lbl_bullet_COM3 = tk.Label(master=COM_frame_right, text="", font=("Verdana", 13, "bold"), bg="red")
        self.lbl_bullet_COM3.place(relx=0.85, rely=0.2, anchor="center")
            

    def prior_start(self):
        # each integer represents the index in the Players list.
        # This is purely for easier turn and call calculations.
        # iterate through each element to get the index of the current/next players turn.
        # This way we don't have to worry about removal of players in the main list. 
        # players safe and dead will be removed from turns_list during game. 
        # players safe will be added back into the game.
        """
        Note:
        we should make a temporary copy of the initial order before the round.
        That way we can add back the players who became safe during the round.
        But minus the player (if) that became dead. (some insertion algorithm?)
        """
        self.order_list = [0,1,2,3] # each integer represents the index in the Players list. 
        self.order_index = random.randint(0,3) # randomizing the turn

        for player in self.players:
            player.bullets = self.start_bullets

        self.init_kill_overlay()

        self.clear_com_death_canvas()

        if self.restart_button.winfo_ismapped(): # hide restart button
            self.restart_button.place_forget()

        if self.btn_new_game.winfo_ismapped(): # hide restart button
            self.btn_new_game.place_forget()

        self.boss_music_play = False
        self.win = False

        # btn_create = tk.Button(window, text="Create Canvas", command=lambda: self.create_com_death_canvas(COM_frame_left))
        # btn_create.place(relx=0.5, rely=0.8, anchor="center")  

        # btn_clear = tk.Button(window, text="Clear All Canvases", command=self.clear_com_death_canvas)
        # btn_clear.place(relx=0.5, rely=0.2, anchor="center")  

        # Add a button to the player_frame
        self.start_button = tk.Button(master=player_frame, text=" - Click to Begin - ", command=lambda: self.initial_start(self.start_button), font=("Verdana", 28, "bold"),borderwidth=8,relief="raised", bg="#d3d3d3")
        self.start_button.place(relx=0.5, rely=0.76, anchor="center")  


    def initial_start(self, button): # Add all button/labels creations here. we will not be looping back here.
        # ROUND SUIT LABEL
        self.lbl_roundsuit["text"] = ""
        # CALL RESULT LABEL
        self.lbl_call_result["text"] = ""
        # Shoot label
        self.lbl_shoot["text"] = "GOOD LUCK :)"
        # display hands
        self.lbl_hand_player["text"] = ""
        self.lbl_hand_COM1["text"] = ""
        self.lbl_hand_COM2["text"] = ""
        self.lbl_hand_COM3["text"] = ""
        self.lbl_table_value["text"] = ""

        # ARROW INDICATORS
        self.lbl_table_COM1["text"] = ""
        self.lbl_table_COM2["text"] = ""
        self.lbl_table_COM3["text"] = ""
        self.lbl_table_PLAYER["text"] = ""

        # display COM played info label for future
        self.lbl_turn_COM1["text"] = ""
        self.lbl_played_COM1["text"] = ""
        self.lbl_turn_COM2["text"] = ""
        self.lbl_played_COM2["text"] = ""
        self.lbl_turn_COM3["text"] = ""
        self.lbl_played_COM3["text"] = ""
      
        # display player 1 truth/lie cards count
        self.lbl_turn_player["text"] = ""
        self.lbl_p1_truth_count["text"] = ""
        self.lbl_p1_lie_count["text"] = ""
        self.lbl_play_choice["text"] = ""
        self.lbl_play_value["text"] = ""

        self.btn_next= tk.Button(master=player_frame, text="[next]", font=("Verdana", 14, "bold"), command=self.update_table_ai)
        self.btn_next.place(relx=0.85, rely=0.8, anchor="center")
        self.btn_next.place_forget()

        self.btn_newround= tk.Button(master=INFO_frame_right, text="[NEW ROUND]", font=("Verdana", 20, "bold"), command=self.new_round)
        self.btn_newround.place(relx=0.5, rely=0.8, anchor="center")
        self.btn_newround.place_forget()

        # display bullet counts

        self.lbl_bullet_PLAYER["text"] = ""
        self.lbl_bullet_COM1["text"] = ""
        self.lbl_bullet_COM2["text"] = ""
        self.lbl_bullet_COM3["text"] = ""

        # Reset alive flags
        for player in self.players:
            player.alive = True

        self.play_background_sound()
            
        # remove start button
        self.remove_button(self.start_button)
        # starting new round
        self.new_round()

    def remove_button(self, button): # Remove the button from the frame
        button.destroy()

    def new_round(self):  
        self.round_active = True
        self.round_turns = 0
        self.call_stage = 0 # for call loop button stepping
        self.deck.new_deck()
        self.deck.shuffle()
        self.table.clear_table()
        self.round_suit = random.choice(self.deck.suits)

        self.order_list = [] # each integer represents the index in the Players list. 
        
        if self.get_dead() == 2 and not self.boss_music_play:
            self.boss_music_play = True
            self.background_sound.stop()
            self.play_boss_sound()
            window.after(37000, self.stop_music)

        # ADDING ALIVE PLAYERS BACK TO ORDER LIST:
        if self.get_dead() > 0:
            for index, player in enumerate(self.players):
                if player.alive:
                    self.order_list.append(index)

        else:
            self.order_list = [0,1,2,3] # each integer represents the index in the Players list. 

        print("########## new round!!! #######")
        print(f"### order list: {self.order_list} ###\n ")
        if self.btn_newround.winfo_ismapped(): # hide next button if active
            self.btn_newround.place_forget()
        
        self.lbl_shoot["text"] = "Good Luck :)"
        self.lbl_call_result["text"] = "---"
       
        # initial label
        self.lbl_roundsuit["text"] = f"ROUND CARD: {self.round_suit}"

        # clear hands to all players
        for player in self.players:
            player.clear_hand()

        # deal cards to all players
        for player in self.players:
            player.receive_cards(self.deck.deal(self.cards_per_player))
            player.safe = False

        # reset labels for sequential rounds
        self.lbl_played_COM1["text"] = "Action: "
        self.lbl_played_COM2["text"] = "Action: "
        self.lbl_played_COM3["text"] = "Action: "

        self.lbl_table_value["text"] = f"Cards: |?| X 0"
        self.lbl_play_choice["text"] = ""

        self.previous = []

        self.round()
   
    
    def round(self):

        self.confirmed = False # flag for confirm button apperance
        self.next = False # flag for 'next' button apperance

        self.remaining_players = len(self.order_list)
        
        self.player_index = self.order_list[self.order_index]

        self.ai_decision = ""

        # getting truth and lie counts
        for plx in self.players:
            result = plx.check_choices(self.round_suit)
            plx.truth_count = result["truth_count"]
            plx.lie_count = result["lie_count"]

            # display hands and bullets
            if plx.position == 1: # human
                self.lbl_hand_player["text"] = f"{plx.show_hand()}"
                self.lbl_bullet_PLAYER["text"] = f"/̵͇̿̿/’̿’̿ ̿ ̿̿ ̿̿ ̿̿ \nCHAMBER:\n ∩ X {plx.bullets}/3"

            if plx.position == 2:
                self.lbl_hand_COM1["text"] = f"Cards: |?| X {plx.get_hand_len()}"
                self.lbl_bullet_COM1["text"] = f"/̵͇̿̿/’̿’̿ ̿ ̿̿ ̿̿ ̿̿ \nCHAMBER:\n ∩ X {plx.bullets}/3"
            if plx.position == 3:
                self.lbl_hand_COM2["text"] = f"Cards: |?| X {plx.get_hand_len()}"
                self.lbl_bullet_COM2["text"] = f"/̵͇̿̿/’̿’̿ ̿ ̿̿ ̿̿ ̿̿ \nCHAMBER:\n ∩ X {plx.bullets}/3"
            if plx.position == 4:
                self.lbl_hand_COM3["text"] = f"Cards: |?| X {plx.get_hand_len()}"
                self.lbl_bullet_COM3["text"] = f"/̵͇̿̿/’̿’̿ ̿ ̿̿ ̿̿ ̿̿ \nCHAMBER:\n ∩ X {plx.bullets}/3"
                

        # check for case where one player remaining in round
        if self.remaining_players > 1:
            # display player 1 truth/lie cards count
            
            if self.players[self.player_index].position == 1:
                print(f"ROUND LOOP player loop:: round_turn: {self.round_turns}")
                print(f"ROUND LOOP player loop:: order_index = {self.order_index}\n")

                if self.btn_next.winfo_ismapped() and self.round_turns > 0: # hide next button if active
                    self.btn_next.place_forget()

                self.lbl_turn_player["text"] = f"YOUR TURN"

                player_human = self.players[self.player_index]

                self.lbl_p1_truth_count["text"] = f"# Truth: {player_human.truth_count}"

                self.lbl_p1_lie_count["text"] = f"# Lie: {player_human.lie_count}"

                # display truth/lie/call options
                if (player_human.truth_count > 0):
                    # Add a truth button to the player_frame
                    self.button_player_t = tk.Button(master=player_frame, text="TRUTH", font=("Verdana", 12, "bold"), command=lambda: self.player_truth(player_human),borderwidth=8,relief="raised", bg="#d3d3d3")
                    self.button_player_t.place(relx=0.3, rely=0.5, anchor="center")

                if (player_human.lie_count > 0):
                    # Add a button to the player_frame
                    self.button_player_l = tk.Button(master=player_frame, text="LIE", font=("Verdana", 12, "bold"), command=lambda: self.player_lie(player_human),borderwidth=8,relief="raised", bg="#d3d3d3")
                    self.button_player_l.place(relx=0.5, rely=0.5, anchor="center")   
                
                if self.round_turns != 0:
                # Add a button to the player_frame
                    self.button_player_c = tk.Button(master=player_frame, text="CALL", font=("Verdana", 12, "bold"), command=lambda: self.player_call(player_human),borderwidth=8,relief="raised", bg="#d3d3d3")
                    self.button_player_c.place(relx=0.7, rely=0.5, anchor="center")   

                self.lbl_play_choice["text"] = "Playing ???"
                
                self.lbl_play_value["text"] = "1"
                
                self.btn_decrease = tk.Button(master=player_frame, text="-", font=("Verdana", 12, "bold"), command=self.decrease,borderwidth=8,relief="raised", bg="#d3d3d3")
                self.btn_decrease.place(relx=0.42, rely=0.9, anchor="center")

                self.btn_increase = tk.Button(master=player_frame, text="+", font=("Verdana", 12, "bold"), command=self.increase,borderwidth=8,relief="raised", bg="#d3d3d3")
                self.btn_increase.place(relx=0.58, rely=0.9, anchor="center")
        
            # it is the AI's turn
            else:
                print(f"from player to prior_update_ai. position: {self.players[self.player_index].position}")
                print(f"from player to prior_update_ai. player_index = {self.player_index}")
                print(f"from player to prior_update_ai. order_index = {self.order_index}\n")

                self.prior_update_table_ai()

        # forced call with 1 player remaining
        else:
            if self.players[self.player_index].position == 1:
                player_human = self.players[self.player_index]
                self.call_output(player_human, self.previous)
            else:
                self.ai_decision = "Call"
                self.update_table_ai() # will need to update this


    # player has played thier cards. Give to table and update table 
    def update_table_player(self, player_human):
        
        # call, if not, play hand
        if player_human.call:
            print(f"!!! HUMAN CALL IF $$$ POSITION -> {self.previous.position}")
            self.call_output(player_human, self.previous)    
        else:
            
            self.previous = player_human # keep track previous for call check

            # hide unnecessary buttons
            # if self.button_player_c.winfo_ismapped() and self.round_turns > 0: # hide next button if active
            #     self.button_player_c.place_forget()
            # if  self.button_player_l.winfo_ismapped():
            #     self.button_player_l.place_forget()
            # if  self.button_player_t.winfo_ismapped():
            #     self.button_player_t.place_forget()
            
            # hide unnecessary buttons
            if (self.round_turns != 0):
                self.button_player_c.place_forget()
            if (self.players[0].lie_count > 0):
                self.button_player_l.place_forget()
            if (self.players[0].truth_count > 0):
                self.button_player_t.place_forget()

            # hiding buttons
            self.btn_decrease.place_forget()
            self.btn_increase.place_forget()
            self.btn_confirm.place_forget()

            # give cards to table

            if player_human.truth:
                num_truth_played = int(self.lbl_play_value["text"])
                self.table.receive_hand(player_human.remove_truth_cards(self.round_suit, num_truth_played))
            else:
                num_truth_played = int(self.lbl_play_value["text"])
                self.table.receive_hand(player_human.remove_lie_cards(self.round_suit, num_truth_played))

            # show/update table cards
            self.lbl_table_value["text"] = f"Cards: |?| X {self.table.get_total_cards()}"
            # show updated hand
            self.lbl_hand_player["text"] = f"{player_human.show_hand()}"

            # arrow indicator
            self.lbl_table_PLAYER["text"] = "⇧"

            if player_human.check_safe(): # will update player safe status depending on # cards 
                self.order_list.remove(self.order_list[self.order_index])
                self.order_index -= 1 # to account for list size decrease

            # increment order and round turn before moving turn to next AI
            self.order_index += 1
            self.round_turns += 1       
            self.prior_update_table_ai()

            """
            At this point, we want to click 'next' to cycle through the ai decisions.

            We have (for each 'next')
                - display: AI played 2X cards. ALSO, update the table table to 8X cards.
                - move on to next AI
                - display: AI played 2X cards. ALSO, update the table table to 8X cards.


            """
    

    # clicking 'next' to cycle through the AI turns
    def prior_update_table_ai(self):

        if not self.next:
            self.btn_next= tk.Button(master=player_frame, text="[next]", font=("Verdana", 14, "bold"), command=self.update_table_ai,borderwidth=8,relief="raised", bg="#d3d3d3")
            self.btn_next.place(relx=0.85, rely=0.8, anchor="center")
            self.next = True
            
    # AI turns; For order_index [1,... len players]. COM's postion 2,3,4
    # NOTE: ORDER INDEX ENTERING HERE IS NEVER ZERO, SINCE THIS LOOP IS ONLY FOR COM'S.
    # ORDER INDEX 1,2,3 (COM). ORDER INDEX 0 (HUMAN)
    def update_table_ai(self):
        
        print("***** UPDATE_TABLE_AI LOOP ENTER *******")

        self.remaining_players = len(self.order_list)

        self.lbl_table_PLAYER["text"] = ""
        self.lbl_table_COM1["text"] = ""
        self.lbl_table_COM2["text"] = ""
        self.lbl_table_COM3["text"] = ""

        self.lbl_turn_COM1["text"] = ""
        self.lbl_turn_COM2["text"] = ""
        self.lbl_turn_COM3["text"] = ""

        self.lbl_turn_player["text"] = ""
        # loop back to players turn if we have went through remaining players. Check if index 0 is player
        if self.order_index == 0 and self.players[self.order_list[self.order_index]].position == 1:

            self.btn_next.place_forget() # remove next button, players turn is next
            print(f" ## ORDER LIST (before ret back)-> {self.order_list}\n")
            print("WENT BACK TO ROUND FOR PLAYER LOOP")
            self.round() 

        else:
            # AI decision, play or lie
            # first check if AI is alive and NOT SAFE (skip player if safe when cards = 0):

            print(f"update_table_ai. order_index = {self.order_index}\n")
            print(f" ## ORDER LIST (AI_DECISION) -> {self.order_list}\n")

            self.com_index = self.order_list[self.order_index]
            self.player_com = self.players[self.com_index]
            
            

            self.ai_decision = self.player_com.make_ai_decision(self.round_suit, self.table.get_total_cards(), self.round_turns, self.remaining_players)
        
            ### FOR DEBUGGING, AI ALWAYS PLAY. REMEMBER TO CHANGE ###

            if self.ai_decision == "play":
                print("AI PLAYED\n")
                # give table the AI cards played
                self.table.receive_hand(self.player_com.ai_play(self.round_suit, self.table.get_total_cards()))
                # update table cards
                self.lbl_table_value["text"] = f"Cards: |?| X {self.table.get_total_cards()}"

                if self.player_com.position == 2:
                    self.lbl_turn_COM1["text"] = f"COM 1'S TURN"

                    self.lbl_played_COM1["text"] = f"Action: Played {self.table.get_lasthand_len()} X cards"
                    self.lbl_hand_COM1["text"] = f"Cards: |?| X {self.player_com.get_hand_len()}"
                    self.lbl_table_COM1["text"] = "⇨"

                if self.player_com.position == 3:
                    self.lbl_turn_COM2["text"] = f"COM 2'S TURN"

                    self.lbl_played_COM2["text"] = f"Action: Played {self.table.get_lasthand_len()} X cards "
                    self.lbl_hand_COM2["text"] = f"Cards: |?| X {self.player_com.get_hand_len()}"
                    self.lbl_table_COM2["text"] = "⇩"

                if self.player_com.position == 4:
                    self.lbl_turn_COM3["text"] = f"COM 3'S TURN"

                    self.lbl_played_COM3["text"] = f"Action: Played {self.table.get_lasthand_len()} X cards"
                    self.lbl_hand_COM3["text"] = f"Cards: |?| X {self.player_com.get_hand_len()}"
                    self.lbl_table_COM3["text"] = "⇦"          
                

                self.previous = self.player_com # keep track previous for call check
                print(f"!!! AI IS SELF PREVIOUS $$$ POSITION -> {self.previous.position}")

                # reset order_index to zero for player_human index if at end of list
                if self.order_index == self.remaining_players-1:
                    # CHECK SAFE
                    if self.player_com.check_safe(): # will update player safe status depending on # cards 
                        self.order_list.remove(self.order_list[self.order_index])
                    
                    self.order_index = 0
                    self.round_turns += 1
                
                else:

                    # CHECK SAFE
                    if self.player_com.check_safe(): # will update player safe status depending on # cards 
                        self.order_list.remove(self.order_list[self.order_index])
                        self.order_index -= 1 # to account for list size decrease


                    # # update for next AI turn on 'next' click
                    self.order_index += 1 # go to the next player
                    self.round_turns += 1
           
            else: # AI is calling previous player
                self.call_output(self.player_com, self.previous)   
           

    def increase(self):
        self.value = int(self.lbl_play_value["text"])
        if self.players[0].truth:
            if self.value < self.players[0].truth_count and self.value < 3:
                self.lbl_play_value["text"] = f"{self.value + 1}"
        else:
            if self.value < self.players[0].lie_count and self.value < 3:
                self.lbl_play_value["text"] = f"{self.value + 1}"            

    def decrease(self):
        self.value = int(self.lbl_play_value["text"])
        if self.value > 1:
            self.lbl_play_value["text"] = f"{self.value - 1}"

    
    def hide_button(self, target_button):
        """Hides the target button."""
        target_button.place_forget()  # Remove the button from the layout

    
    def player_truth(self, player):
        if not self.confirmed:
            self.btn_confirm= tk.Button(master=player_frame, text="[confirm]", font=("Verdana", 14, "bold"), command=lambda: self.update_table_player(player),borderwidth=8,relief="raised", bg="#d3d3d3")
            self.btn_confirm.place(relx=0.85, rely=0.8, anchor="center")    
        player.truth = True
        player.call = False
        self.confirmed = True
        self.lbl_play_choice["text"] = "Playing Truth"
        self.lbl_play_value["text"] = "1"


    def player_lie(self, player):
        if not self.confirmed:
            self.btn_confirm= tk.Button(master=player_frame, text="[confirm]", font=("Verdana", 14, "bold"), command=lambda: self.update_table_player(player),borderwidth=8,relief="raised", bg="#d3d3d3")
            self.btn_confirm.place(relx=0.85, rely=0.8, anchor="center")  
        player.truth = False
        player.call = False
        self.confirmed = True
        self.lbl_play_choice["text"] = "Playing Lie"
        self.lbl_play_value["text"] = "1"

    def player_call(self, player):
        if not self.confirmed:
            self.btn_confirm= tk.Button(master=player_frame, text="[confirm]", font=("Verdana", 14, "bold"), command=lambda: self.update_table_player(player),borderwidth=8,relief="raised", bg="#d3d3d3")
            self.btn_confirm.place(relx=0.85, rely=0.8, anchor="center")    
        player.call = True
        self.confirmed = True
        self.lbl_play_choice["text"] = "Calling Liar"
        self.lbl_play_value["text"] = "0"

    def call_output(self, c_player, p_player):

        print("CALL_OUTPUT METHOD RUN")
        current_player = c_player
        previous_player = p_player
        
         
        if current_player.position == 1:
            self.lbl_hand_player["text"] = "CALLING PREVIOUS PLAYER LIAR!"
            
            # hide unnecessary buttons
            if (self.round_turns != 0):
                self.button_player_c.place_forget()
            if (self.players[0].lie_count > 0):
                self.button_player_l.place_forget()
            if (self.players[0].truth_count > 0):
                self.button_player_t.place_forget()
            self.btn_decrease.place_forget()
            self.btn_increase.place_forget()
            self.btn_confirm.place_forget()
            self.button_player_c.place_forget()

        if current_player.position == 2:
            self.lbl_hand_COM1["text"] = "CALLING PREVIOUS PLAYER LIAR!"


        if current_player.position == 3:
            self.lbl_hand_COM2["text"] = "CALLING PREVIOUS PLAYER LIAR!"

        if current_player.position == 4:
            self.lbl_hand_COM3["text"] = "CALLING PREVIOUS PLAYER LIAR!"

        if previous_player.position == 1:
            self.lbl_play_choice["text"] = f"Previous play: {self.table.show_last_hand()}"

        if previous_player.position == 2:
            self.lbl_played_COM1["text"] = f"Previous play: {self.table.show_last_hand()}"

        if previous_player.position == 3:
            self.lbl_played_COM2["text"] = f"Previous play: {self.table.show_last_hand()}"

        if previous_player.position == 4:
            self.lbl_played_COM3["text"] = f"Previous play: {self.table.show_last_hand()}"
        
        self.check_truth_output(current_player, previous_player)

    """
    TODO: for truth logic and output graphic logic: (maybe)
        - do calculations first
        - use call_stage to loop through the logic and display desired variables/buttons

    """
    
    def check_truth_output(self, current_player, previous_player):
        
        self.btn_next.place_forget()

        # THESE ARE CASES WHERE PLAYER MAY TAKE SHOT
        if current_player.position == 1: # this is player call output
            if (previous_player.truth):
                print("TRUTH OUTPUT CASE PLAYER CALL A\n")
                self.lbl_call_result["text"] = f"{previous_player.name} TRUTH ! {current_player.name} must take a shot!"
                self.lbl_shoot["text"] = "WHY YOU SNITCH? :("
                self.btn_shoot= tk.Button(master=INFO_frame_right, text="[TAKE SHOT]", font=("Verdana", 20, "bold"), command=lambda: self.check_shoot_output(current_player, is_previous=False),borderwidth=8,relief="raised")
                self.btn_shoot.place(relx=0.5, rely=0.8, anchor="center")

            else:
                print("LIE OUTPUT CASE PLAYER CALL B\n")
                
                self.lbl_call_result["text"] = f"{previous_player.name} LIE ! They must take a shot!"
                self.lbl_shoot["text"] = "YOU GOT EM! :)"

                self.btn_shoot= tk.Button(master=INFO_frame_right, text="[COM. TAKE SHOT]", font=("Verdana", 20, "bold"), command=lambda: self.check_shoot_output(previous_player, is_previous=True),borderwidth=8,relief="raised")
                self.btn_shoot.place(relx=0.5, rely=0.8, anchor="center")
        
        elif previous_player.position == 1:
                if (previous_player.truth): # COM CALLING PLAYER, PLAYER PLAYED TRUTH
                    print("TRUTH OUTPUT CASE COM CALL A\n")
                    
                    self.lbl_call_result["text"] = f"{previous_player.name} TRUTH ! {current_player.name} must take a shot!"
                    self.lbl_shoot["text"] = "U ARE HONEST :)"
                    self.btn_shoot= tk.Button(master=INFO_frame_right, text="[COM. TAKE SHOT]", font=("Verdana", 20, "bold"), command=lambda: self.check_shoot_output(current_player, is_previous=False),borderwidth=8,relief="raised")
                    self.btn_shoot.place(relx=0.5, rely=0.8, anchor="center")
                else: # COM CALLING PLAYER, PLAYER LIE
                    print("LIE OUTPUT CASE COM CALL B\n")

                    self.lbl_call_result["text"] = f"{previous_player.name} LIE ! They must take a shot!"
                    self.lbl_shoot["text"] = "WHY U LIE ?? :("

                    self.btn_shoot= tk.Button(master=INFO_frame_right, text="[TAKE SHOT]", font=("Verdana", 20, "bold"), command=lambda: self.check_shoot_output(previous_player, is_previous=True),borderwidth=8,relief="raised")
                    self.btn_shoot.place(relx=0.5, rely=0.8, anchor="center")
        
        # THESE ARE CASES WHERE ITS ONLY COM CALLING COM
        else:
                if (previous_player.truth):
                    self.lbl_call_result["text"] = f"{previous_player.name} TRUTH ! {current_player.name} must take a shot!"
                    self.lbl_shoot["text"] = "COM. IS HONEST :)"

                    self.btn_shoot= tk.Button(master=INFO_frame_right, text="[COM. TAKE SHOT]", font=("Verdana", 20, "bold"), command=lambda: self.check_shoot_output(current_player, is_previous=False),borderwidth=8,relief="raised")
                    self.btn_shoot.place(relx=0.5, rely=0.8, anchor="center")

                else:
                    self.lbl_call_result["text"] = f"{previous_player.name} LIE ! {previous_player.name} must take a shot!"
                    self.lbl_shoot["text"] = "COM. IS HONEST :)"

                    self.btn_shoot= tk.Button(master=INFO_frame_right, text="[COM. TAKE SHOT]", font=("Verdana", 20, "bold"), command=lambda: self.check_shoot_output(previous_player, is_previous=True),borderwidth=8,relief="raised")
                    self.btn_shoot.place(relx=0.5, rely=0.8, anchor="center")  




    def check_shoot_output(self, player, is_previous):

        self.lbl_turn_COM1["text"] = ""
        self.lbl_turn_COM2["text"] = ""
        self.lbl_turn_COM3["text"] = ""

        self.remaining_players = len(self.order_list)

        #need to call shoot bullet to check if survive
        
        if player.shoot_bullet(): # CHECK PLAYER DEAD
            if player.position == 1:
                if self.boss_music_play:
                    self.boss_sound.stop()
                self.background_sound.stop()
                self.play_fire_sound()
                self.btn_shoot.place_forget()
                self.show_kill_overlay()

                self.btn_shoot.after(2800, self.show_restart_btn)
                self.play_lose_sound_delay()
            else: # COM DEAD
                self.play_fire_sound()
                player.alive = False
                if player.position == 2:
                    frame_var = COM_frame_left
                elif player.position == 3:
                    frame_var = COM_frame_top
                elif player.position == 4:
                    frame_var = COM_frame_right

                if is_previous and self.order_index != 0:
                    self.order_index -= 1
                
                else: 
                    # order_index remain same unless = remaining players -1
                    if self.order_index == self.remaining_players-1:
                        self.order_index = 0

                print(f"{player.name} GOT SHOT. ORDER INDEX: {self.order_index} ")

                # death canvas
                self.create_com_death_canvas(frame_var)

                self.lbl_shoot["text"] = f"{player.name} is DEAD"
                self.btn_shoot.place_forget()

                if self.get_dead() == 3:

                    self.btn_shoot.place_forget()
                    self.win_screen()
                else:
                    self.btn_newround= tk.Button(master=INFO_frame_right, text="[NEW ROUND]", font=("Verdana", 20, "bold"), command=self.new_round,borderwidth=8,relief="raised")
                    self.btn_newround.place(relx=0.5, rely=0.8, anchor="center")

        # FIRED BLANK
        else:
            self.play_blank_sound()
            if player.position == 2:
                self.lbl_played_COM1["text"] = "FIRED BLANK"
            elif player.position == 3:
                self.lbl_played_COM2["text"] = "FIRED BLANK"
            elif player.position == 4:
                self.lbl_played_COM3["text"] = "FIRED BLANK"

            player.reload() # subtract bullet

            self.lbl_shoot["text"] = "WHEW... FIRED BLANK"
            self.btn_shoot.place_forget()

            if is_previous and self.order_index != 0:
                self.order_index -= 1
         
            print(f"WHEW... FIRED BLANK. ORDER INDEX: {self.order_index} ")

            self.btn_newround= tk.Button(master=INFO_frame_right, text="[NEW ROUND]", font=("Verdana", 20, "bold"), command=self.new_round,borderwidth=8,relief="raised")
            self.btn_newround.place(relx=0.5, rely=0.8, anchor="center")

    def stop_music(self):
        print("MUSIC SHOULD HAVE STOPPED!")
        self.boss_sound.stop() 
        self.background_sound.stop()

    def win_screen(self):
        self.win = True
        self.stop_music()
        self.win_label_flash()

        window.after(1100, self.play_win_sound)
        window.after(5500, self.new_game_option)
    
    def new_game_option(self):
        self.btn_new_game= tk.Button(master=INFO_frame_right, text="[PLAY AGAIN?]", font=("Verdana", 20, "bold"), command=self.prior_start ,borderwidth=8,relief="raised")
        self.btn_new_game.place(relx=0.5, rely=0.65, anchor="center")

    def win_label_flash(self):
        if self.win:
            self.lbl_shoot["text"] = "!! YOU WIN !!"
            if self.lbl_shoot.winfo_viewable():
                self.lbl_shoot.place_forget()
            else:
                self.lbl_shoot.place(relx=0.5, rely=0.5, anchor="center")
            
            self.lbl_shoot.after(500, self.win_label_flash)


    def create_com_death_canvas(self,frame_var):
        #death background
        com_death_canvas = tk.Canvas(master=frame_var, bg=self.dead_color)
        com_death_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.com_death_canvas_list.append(com_death_canvas)
        print(f"ADDING TO COM DEATH LIST: {self.com_death_canvas_list}")

        self.apply_fade_effect(com_death_canvas, (255, 255, 255), (120, 6, 6))

    def clear_com_death_canvas(self):
        print(f"CANVAS LIST PRIOR: {self.com_death_canvas_list}")
        # Remove all death canvases
        for canvas in self.com_death_canvas_list:
            canvas.destroy()
        self.com_death_canvas_list.clear()  # Clear the list after destroying
        print(f"CANVAS LIST AFTER CLEAR: {self.com_death_canvas_list}")
        
    def init_kill_overlay(self):
        # custom kill frame
        self.fading_canvas.place_forget()

    def show_kill_overlay(self):
        # Place the canvas to cover the entire window
        self.fading_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Trigger the fade effect
        self.apply_fade_effect(self.fading_canvas, (255, 255, 255), (120, 6, 6))


    def apply_fade_effect(self, canvas, start_color, end_color, steps=20, delay=50):
        """
        Fades the canvas background color from start_color to end_color.

        Args:
            canvas: The Canvas widget to update.
            start_color: Starting color as an RGB tuple, e.g., (255, 255, 255).
            end_color: Ending color as an RGB tuple, e.g., (255, 0, 0).
            steps: Number of steps in the fade effect.
            delay: Delay between each step in milliseconds.
        """
        def interpolate_color(start, end, step, max_steps):
            return tuple(
                int(start[i] + (end[i] - start[i]) * (step / max_steps)) for i in range(3)
            )

        def update_color(step=0):
            if step <= steps:
                # Calculate interpolated color
                new_color = interpolate_color(start_color, end_color, step, steps)
                hex_color = f"#{new_color[0]:02x}{new_color[1]:02x}{new_color[2]:02x}"
                
                # Apply the new color to the canvas
                canvas.config(bg=hex_color)
                
                # Schedule the next update
                canvas.after(delay, update_color, step + 1)

        # Start the fade effect
        update_color()

    def get_dead(self):
        total = 0
        for player in self.players:
            if not player.alive:
                total += 1
        return total
    
    def show_restart_btn(self):
        self.restart_button.place(relx=0.5, rely=0.7, anchor="center") 
    
    def play_boss_sound(self):
        # Load and play sound
        self.boss_sound = mixer.Sound(r"C:\Users\User\Documents\Personal Python\Cheat-Roulette\boss_sound.mp3")  # Replace with your sound file
        self.boss_sound.play()

    def play_blank_sound(self):
        # Load and play sound
        blank_sound = mixer.Sound(r"C:\Users\User\Documents\Personal Python\Cheat-Roulette\fire_blank.mp3")  # Replace with your sound file
        blank_sound.play()
    def play_fire_sound(self):
        # Load and play sound
        fire_sound = mixer.Sound(r"C:\Users\User\Documents\Personal Python\Cheat-Roulette\fire_bullet.mp3")  # Replace with your sound file
        fire_sound.play()
    def play_win_sound(self):
        # Load and play sound
        win_sound = mixer.Sound(r"C:\Users\User\Documents\Personal Python\Cheat-Roulette\win_sound.mp3")  # Replace with your sound file
        win_sound.play()
    def play_lose_sound(self):
        # Use mixer.Sound for short sound effects
        lose_sound = mixer.Sound(r"C:\Users\User\Documents\Personal Python\Cheat-Roulette\lose_sound.mp3")
        lose_sound.play()  # Plays asynchronously
    def play_lose_sound_delay(self):
        window.after(500,self.play_lose_sound)


    def play_background_sound(self):
        # Load and play sound
        self.background_sound = mixer.Sound(r"C:\Users\User\Documents\Personal Python\Cheat-Roulette\background_sound.mp3")  # Replace with your sound file
        self.background_sound.play()
        self.background_sound.set_volume(0.5)


"""
#############################

WINDOW SETUP 

#############################

"""   

player_color = "#1B848E"
AI_color = "#124AA0"
dead_color = "#880808"

window = tk.Tk()

# Configure grid
for i in range(4):
    window.columnconfigure(i, weight=1, minsize=475)
    window.rowconfigure(i, weight=1, minsize=240)
    window.configure(bg="#40494E")  # Set the full window background color

#region window info
"""
By using .columnconfigure() and .rowconfigure() on the window object, 
you can adjust how the rows and columns of the grid grow as the window is resized. 
Remember, the grid is attached to window, even though you’re calling .grid() on each Frame widget. 
Both .columnconfigure() and .rowconfigure() take three essential arguments:

Index: The index of the grid column or row that you want to configure or a list of indices 
to configure multiple rows or columns at the same time.
Weight: A keyword argument called weight that determines how the column or row should respond to 
window resizing, relative to the other columns and rows.
Minimum Size: A keyword argument called minsize that sets the minimum size of the row height
or column width in pixels.
"""

"""
.grid() works by splitting a window or Frame into rows and columns. 
You specify the location of a widget by calling .grid() and passing 
the row and column indices to the row and column keyword arguments, respectively. 
Both row and column indices start at 0, so a row index of 1 and a column index of 2 tells 
.grid() to place a widget in the third column of the second row.
"""
#endregion

#region LOGO_FRAME_TOP_R
# Load the image (must be .png or .gif)
image = tk.PhotoImage(file=r"C:\Users\User\Documents\Personal Python\Cheat-Roulette\ece_logo.png")  

def resize_image(image, width, height):
    # Resize the image to the specified width and height
    return image.subsample(int(image.width() / width), int(image.height() / height))

# Resize the image (for example, to 150x150 pixels)
resized_image = resize_image(image, 225, 170)

# Create a INFO_frame_top_r
INFO_frame_top_r = tk.Frame(
    master=window,
    borderwidth=0
)
INFO_frame_top_r.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
canvas = tk.Canvas(master=INFO_frame_top_r, bg="#40494E")
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)


label = tk.Label(INFO_frame_top_r, image=resized_image)
label.pack()
# Add a label to the INFO_frame_top_r


#endregion

#region INFO_FRAME_TOP
# Create a INFO_frame_top
INFO_frame_top = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
INFO_frame_top.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

# Create a canvas to fill the INFO_frame_top
canvas = tk.Canvas(master=INFO_frame_top, bg="#D25A19")
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)



# Add a label to the INFO_frame_top
label = tk.Label(master=INFO_frame_top, text=f"GAME INFO", bg="white", fg="black")
label.place(x=0,y=0)

# label_cards = tk.Label(master=INFO_frame_top, text=f"{players[0].show_hand}", bg="white", fg="black")
# label_cards.place(relx=0.5, rely=0.5, anchor="center")

#endregion
#region INFO_FRAME_RIGHT
# Create a INFO_frame_right
INFO_frame_right = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
INFO_frame_right.grid(row=1, column=3, rowspan=3, padx=5, pady=5, sticky="nsew")

# Create a canvas to fill the INFO_frame_right
canvas = tk.Canvas(master=INFO_frame_right, bg="#D25A19")
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# Add a label to the INFO_frame_right
label = tk.Label(master=INFO_frame_right, text=f"PLAYER STATS", bg="white", fg="black")
label.place(x=0,y=0)

#endregion

#region COM_FRAME_TOP
# Create a COM_frame_top
COM_frame_top = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
COM_frame_top.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

# Create a canvas to fill the COM_frame_top
canvas = tk.Canvas(master=COM_frame_top, bg=AI_color)
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# Add a label to the COM_frame_top
label = tk.Label(master=COM_frame_top, text=f"COM 2", bg="white", fg="black", font=("Verdana", 12, "bold"))
label.place(x=0,y=0)

#endregion
#region COM_FRAME_LEFT 
# Create a COM_frame_left
COM_frame_left = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
COM_frame_left.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

# Create a canvas to fill the COM_frame_left
canvas = tk.Canvas(master=COM_frame_left, bg=AI_color)
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# Add a label to the COM_frame_left
label = tk.Label(master=COM_frame_left, text=f"COM 1", bg="white", fg="black", font=("Verdana", 12, "bold"))
label.place(x=0,y=0)

#endregion
#region COM_FRAME_RIGHT 
# Create a COM_frame_right
COM_frame_right = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
COM_frame_right.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")

# Create a canvas to fill the COM_frame_right
canvas = tk.Canvas(master=COM_frame_right, bg=AI_color)
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# Add a label to the COM_frame_right
label = tk.Label(master=COM_frame_right, text=f"COM 3", bg="white", fg="black", font=("Verdana", 12, "bold"))
label.place(x=0,y=0)

#endregion

#region TABLE_frame
# Create a TABLE_frame
TABLE_frame = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=1
)
TABLE_frame.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

# Create a canvas to fill the TABLE_frame
canvas = tk.Canvas(master=TABLE_frame, bg="#315025")
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# Add a label to the TABLE_frame
label = tk.Label(master=TABLE_frame, text=f"Table", bg="white", fg="black", font=("Verdana", 12, "bold"))
label.place(x=0,y=0)

#endregion

#region PLAYER_FRAME

# Create a frame
player_frame = tk.Frame(
    master=window,
    relief=tk.RAISED,
    borderwidth=3
)
player_frame.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

# Create a canvas to fill the player_frame
canvas_player = tk.Canvas(master=player_frame, bg=player_color)
canvas_player.place(relx=0, rely=0, relwidth=1, relheight=1)
# Draw a circle (oval) at a specific position
# x1, y1 = 225, 10  # Top-left corner of the bounding box
# x2, y2 = 275, 60  # Bottom-right corner of the bounding box
# canvas_player.create_oval(x1, y1, x2, y2, fill="blue", outline="black")

# Add a label to the player_frame
label = tk.Label(master=player_frame, text=f"PLAYER", bg="white", fg="black", font=("Verdana", 12, "bold"))
label.place(x=0,y=0)

# Create circles on each canvas
# circle1 = canvas_player.create_oval(x1,y1,x2,y2, fill="red")

# Coordinates for a downward-pointing triangle x,y (left) x,y (right), x,y (apex)
triangle_coords = [20, 50, 30, 50, 25, 25]
triangle1 = canvas_player.create_polygon(triangle_coords, fill="red", outline="black", width=2)


direction = 1  # 1 for down, -1 for up

  # 1 for down, -1 for up
def update_canvas_p1_animation():
    # Movement variables
    global direction
    speed = 5  # Number of pixels per step
    speed = 2

    # Get the current position
    coords = canvas_player.coords(triangle1)

    # Check boundaries
    top_y = min(coords[1], coords[3], coords[5])  # Smallest y-coordinate
    bottom_y = max(coords[1], coords[3], coords[5])  # Largest y-coordinate
    if bottom_y >= 50:  # Bottom boundary
        direction = -1
    elif top_y <= 20:  # Top boundary
        direction = 1

    # Move the circle
    canvas_player.move(triangle1, 0, direction * speed)

    # Schedule the next animation step
    canvas_player.after(100, update_canvas_p1_animation)

update_canvas_p1_animation()

#endregion


game = Game(player_frame, INFO_frame_top, INFO_frame_right, COM_frame_left, COM_frame_right, COM_frame_top, player_color, AI_color)
game.prior_start()




window.mainloop()

