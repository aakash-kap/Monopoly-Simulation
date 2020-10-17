import numpy as np
from matplotlib import pyplot as plt
import random

# Define constants for the game
dice_max = 6
dice_min = 1
max_double_rolls = 3
special_positions = [0, 10, 20, 30]
total_positions = 40

# Now, create the game board with the costs of the properties and taxes on it
# ID 0 : Go
# ID 1 : Community Chest
# ID 2 : Chance
# ID 3 : Jail/Just Visiting
# ID 4 : Free Parking
# ID 5 : Go To Jail
game_board = [0, 60, 1, 60, -200, 200, 100, 2, 100, 120, 3, 140, 150, 140, 160, 200, 180, 1, 180,
              200, 4, 220, 2, 220, 240, 200, 260, 260, 150, 280, 5, 300, 300, 1, 320, 200, 2, 350, -100, 400]

# Chance and Community Chest Options : Each of them have 16 cards

# The cards are as follows : Trip to Marylebone Station (ID 5), Won Crossword, Building Loan Matures, Advance to Mayfair (ID 6), Go Back 3 spaces (ID 7), Bank Pays Dividend, Repairs on Properties (ID 8), Advance to Trafalgar Square (ID 9), Pay School Fees, Speeding Fine, Get Out of Jail (ID 2), Advance to Pall Mall (ID 11), Advance to Go (ID 3), Drunk In Charge, Go To Jail (ID 1), Street Repairs (ID 12)
chance_opts = [5, 100, 150, 6, 7, 50, 8, 9, -150, -15, 2, 11, 3, -20, 1, 12]

# The cards are as follows : Income Tax Refund, Beauty Contest, Go To Jail (ID 1), Inheritance, Pay Fine/Chance (ID/Value -10), Doctor's Fee, Get Out of Jail (ID 2), Advance to Go (ID 3), Pay Insurance Premium, Go Back to Old Kent Road (ID 4), Birthday, Annuity Matures, Sale of Stock, Pay Hospital, Bank Error in favour, Interest on Shares
community_chest_opts = [20, 10, 1, 100, -10, 50,
                        2, 3, -50, 4, 10, 100, 50, -100, 200, 25]

# User specified parameters for the simulation
num_simulations = int(input("Enter the number of simulations to be run (in multiples of 1000) \n"))
turns_per_game = int(input("Enter the number of turns per game \n"))
starting_money = int(input("Enter the starting money amount \n"))

divided_simulations = int(num_simulations/1000)

final_results = np.zeros([divided_simulations, total_positions])

def roll_dice():
    first_die_roll = random.randint(dice_min, dice_max)
    second_die_roll = random.randint(dice_min, dice_max)
    # Check if we have a double roll
    return (first_die_roll+second_die_roll), (first_die_roll == second_die_roll)


def take_chance():
    global chance_counter, heat_map, current_money, current_position, get_out_of_jail_cards, in_jail
    choice = chance_opts[chance_counter]
    chance_counter += 1
    
    # There are 16 possible options so wrap around once we reach 15
    chance_counter %= 16
    
    # Check for special chances and update money for everything else
    if choice == 5:
        # Trip to Marylebone Station : Check if we need to pass go or not
        if current_position > 5:
            current_money += 200
        current_position = 5
        heat_map[current_position] += 1
    
    elif choice == 6:
        # Advance to Mayfair
        current_position = 39
        heat_map[current_position] += 1
    
    elif choice == 7:
        # Go Back Three Spaces
        current_position -=3
        heat_map[current_position] += 1
        # We need to check if we land on Community Chest
        if game_board[current_position] == 1:
            take_community_chest()
        
    elif choice == 8:
        # Repair Properties : Cost changes. Complicated to model. Left for later
        pass
    
    elif choice == 9:
        # Advance to Trafalgar Square : Check if we need to pass go or not
        if current_position > 24:
            current_money += 200
        current_position = 24
        heat_map[current_position] += 1
    
    elif choice == 11:
        # Advance to Pall Mall : Check if we need to pass go or not
        if current_position > 11:
            current_money += 200
        current_position = 11
        heat_map[current_position] += 1
    
    elif choice == 12:
        # Street Repairs : Cost changes. Complicated to model. Left for later
        pass
    
    elif choice == 1:
        # Go To Jail
        current_position = 10
        if get_out_of_jail_cards > 0:
            get_out_of_jail_cards -= 1
        else:
            in_jail = True
    
    elif choice == 2:
        # Get out of Jail Card
        get_out_of_jail_cards += 1
    
    elif choice == 3:
        # Advance to Go
        current_position = 0
        heat_map[current_position] += 1
    
    else:
        current_money += choice

def take_community_chest():
    global community_chest_counter, heat_map, current_money, current_position, get_out_of_jail_cards, in_jail
    choice = community_chest_opts[community_chest_counter]
    community_chest_counter += 1
    # There are 16 possible options so wrap around once we reach 15
    community_chest_counter %= 16
    # Check for special chances and update money for everything else
    if choice == 1:
        # Go To Jail
        current_position = 10
        heat_map[current_position] += 1
        if get_out_of_jail_cards > 0:
            get_out_of_jail_cards -= 1
        else:
            in_jail = True
    elif choice == 2:
        # Get Out of Jail Card
        get_out_of_jail_cards += 1
    elif choice == 3:
        # Advance to Go
        current_position = 0
        heat_map[current_position] += 1
        # Receive Salary :)
        current_money += 200
    elif choice == 4:
        # Go back to Old Kent Road
        current_position = 1
        heat_map[current_position] += 1
    elif choice == -10:
        # Pay Fine or Take Chance (will be sampled as a random choice)
        fine_or_chance = random.randint(0, 1)
        if fine_or_chance == 0:
            # Take Fine
            current_money -= 10
        else:
            # Take chance
            take_chance()
    else:
        current_money += choice

def play_turn(doubles_rolled):
    global heat_map, current_money, current_position, get_out_of_jail_cards, in_jail
    if doubles_rolled > 2:
        # Three doubles, time for jail
        in_jail = True
        return 

    else:
        # Roll the dice
        dice_roll, is_double = roll_dice()

        # Update the position after the die roll
        current_position += dice_roll
        current_position %= total_positions

        # Mark this position as visited
        heat_map[current_position] += 1

        # Check if we are on Chance/Community Chest/Go To Jail
        if game_board[current_position] == 0:
            # We are on Go
            current_money += 200

        elif game_board[current_position] == 1:
            # We are on Community Chest 
            take_community_chest()

        elif game_board[current_position] == 2:
            # We are on Chance 
            take_chance()

        elif game_board[current_position] == 5:
            # We are on "Go To Jail" so update position
            current_position = 10
            heat_map[current_position] += 1
            if get_out_of_jail_cards > 0:
                get_out_of_jail_cards -= 1
            else:
                in_jail = True
                return

        # Isn't in jail and has rolled doubles so play another turn
        if is_double:
            play_turn(doubles_rolled+1)

# Run the simulation
temp_simulations = 0 
counter = 0
temp_results = np.zeros([divided_simulations, total_positions])

for sim in range(0, num_simulations):

    # Every new game starts at position 0 with an empty heat map
    current_position = 0
    heat_map = np.zeros(total_positions)
    current_money = starting_money

    # For every new game, we want a shuffled Chance and Community Chest Deck
    random.shuffle(community_chest_opts)
    random.shuffle(chance_opts)

    # Starting Community Chest and Chance pickup numbers, to be reset every game
    community_chest_counter = 0
    chance_counter = 0

    # Initially we are not in Jail and don't have a "Get Out of Jail Card"
    in_jail = False
    jail_turns_skipped = 0
    get_out_of_jail_cards = 0
    
    
    
    for turn in range(0, turns_per_game):
        # Skip turns if in Jail
        if in_jail:
            jail_turns_skipped += 1
            jail_turns_skipped %= 3
            
            # Do a dice roll and get out if it is a double
            dice_roll, is_double = roll_dice()
            if is_double:
                jail_turns_skipped = 0
                in_jail = False
            elif jail_turns_skipped == 0:
                # Has completed stay by losing three turns so pays fine
                current_money -= 50
                in_jail = False
            else:
                heat_map[current_position] += 1
                continue

        # Play the turn now : 0 is passed to indicate no doubles rolled at turn start
        play_turn(0)
    
    if temp_simulations < divided_simulations:
        temp_results[temp_simulations, :] = heat_map
        temp_simulations += 1
    else:
        temp_simulations = 0
        if counter < 1000:
            final_results[counter, :] = np.average(temp_results, axis=0)
        counter += 1

file_name = "Results_"+str(num_simulations)+".csv"
np.savetxt(file_name, final_results, delimiter=",")


