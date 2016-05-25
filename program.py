from collections import defaultdict as dd
import random


def bid(hand, player_no, phase_no, deck_top, reshuffled=False,
        player_data=None, suppress_player_data=True):
    '''Bid takes your hand of cards and uses player_no and deck_Top
    to accordingly simulate the win chances for each card. It then
    returns a bid of cards which are higher than the win chance specified.'''

    # Used for GROK worksheet as player_data is used in tournament.
    if suppress_player_data:
        if phase_no % 4 == 0:
            return len(hand) // 4
        if phase_no == 10:
            return 0
        else:
            return 0

    # If the deck is shuffled, then all the previously counted cards must
    # be removed.
    if phase_no == 1 or reshuffled is True:
        player_data = [(), ()]

    def clean_deck(hand, deck_top, prev_trick):
        '''This function takes a full deck and removes the already known
        cards, i.e. cards in your hand, the deck top card and any
        previous cards'''

        def make_deck():
            '''This function makes a new deck of 52 cards for the
            clean_deck function'''
            suits = 'SHCD'
            values = '234567890JQKA'
            output = []
            for suit in suits:
                for value in values:
                    card = value + suit
                    output.append(card)
            return output

        deck = make_deck()

        # Remove cards in your hand, the deck top card and any previous
        # cards from the deck.
        deck.remove(deck_top)
        for card in hand:
            if card in deck:
                deck.remove(card)
        for trick in prev_trick:
            for card in trick:
                if card in deck:
                    deck.remove(card)
        return deck

    def simulate(hand, deck):
        '''This function takes your hand and the deck and generates
        a probability of winning for each of your cards.'''

        card_chances = dd(float)
        # Trial each card 10 times to create a good average.
        for test in range(1, 10):
            card_win = 0
            total_card = 0
            for card in hand:
                plays = []

                # Randomly pick 3 other cards to represent opposing cards
                # from the cut down deck. Then insert your card as your
                # player_no position so it can be calculated whether
                # you win or not.
                for i in range(1, 3):
                    newcard = deck[random.randint(1, len(deck) - 1)]
                    if newcard in plays:
                        newcard = deck[random.randint(1, len(deck) - 1)]
                    plays.append(newcard)
                plays.insert(int(player_no), card)

                # Reorder royal cards and restrict to the trump suit/
                # player 0 suit.
                for play in plays:
                    if play[0] == '0':
                        play = 'A' + play[1]
                    elif play[0] == 'J':
                        play = 'B' + play[1]
                    elif play[0] == 'Q':
                        play = 'C' + play[1]
                    elif play[0] == 'K':
                        play = 'D' + play[1]
                    elif play[0] == 'A':
                        play = 'E' + play[1]
                    if play[1] == deck_top[-1]:
                        play = play[0] + 'B'
                    elif play[1] == plays[0][-1]:
                        play = play[0] + 'A'
                winning = plays.index(max(plays))
                result = [0, 0, 0, 0]
                result[winning] = 1

                # If the card won, increase it's chances accordingly.
                if result[player_no] == 1:
                    card_win += 1
                total_card += 1
                if card == 'A' + deck_top[1]:
                    card_chances[card] = 1
                else:
                    card_chances[card] = (card_chances[card] +
                                          card_win / total_card) / 2
        return card_chances

    # Run the above two functions to generate the card chances.

    card_chances = simulate(hand, clean_deck(hand, deck_top, player_data[1]))

    # Assign player_data to be passed onto play() the card chances and all
    # previous tricks (to be carried unto the next bid etc.).
    output_2 = (card_chances, player_data[1])

    # Return special bids for the corresponding special rounds with the
    # new player_data.
    if phase_no % 4 == 0:
        return len(hand) // 4, output_2
    if phase_no == 10:
        return 0, output_2

    # Count through each of the card chances. If there is a card chance
    # above a specified probability (found via trial and error) then
    # increase bid by 1. Also, if your hand has Ace with trump suit
    # (a.k.a. highest possible card), increase bid by 1.
    output = 0
    for i in card_chances.values():
        if i > 0.195:
            output += 1

    # Count the trumps in the hand, and add them to the output.
    for card in hand:
        if card[1] in deck_top:
            if output < len(hand):
                output += 1

    if phase_no == 1 or phase_no == 19:
        return 0, output_2
    else:
        return output, output_2


def is_valid_play(play, curr_trick, hand):
    '''Checks if a play is valid for that round.'''

    hand_suit = [card[1] for card in hand]
    flag = True

    # If you are the first player, then all cards are valid.
    # Otherwise, check if the card has a valid suit (trump suit or
    # first player suit). If not, then return False.
    if curr_trick == ():
        return True
    else:
        if play not in hand:
            return False
        elif len(hand) == 1:
            return True
        for i in hand_suit:
            if i in curr_trick[0][1] and i not in play:
                flag = False
    return flag


def score_phase(bids, tricks, deck_top, player_data=None,
                suppress_player_data=True):
    '''Score phase takes bids, tricks for this round, the deck top
    and returns the score for each player.'''

    # Redefine cards for sorting.
    cards = []
    for phase in tricks:
        phase_append = []
        for play in phase:
            if play[0] == '0':
                play = 'A' + play[1]
            elif play[0] == 'J':
                play = 'B' + play[1]
            elif play[0] == 'Q':
                play = 'C' + play[1]
            elif play[0] == 'K':
                play = 'D' + play[1]
            elif play[0] == 'A':
                play = 'E' + play[1]
            if play[1] == deck_top[-1]:
                play = play[0] + 'B'
            elif play[1] == phase[0][-1]:
                play = play[0] + 'A'
            phase_append.append(play)
        cards.append(phase_append)

    winner = 0
    player_no = 0
    score = dd(int)
    # For each phase, calculate the winning player and add 1 to the
    # corresponding position in score.
    for phase in cards:
        valid_card_values = [card[::-1] for card in phase if card[-1] in 'AB']
        # Keep each track of each of the players' positions by starting on the
        # winning position and then incrementing by one. Keep positions
        # cycling through 0-3 by using modulo 4.
        for play in phase:
            if play[::-1] == max(valid_card_values):
                score[str((player_no % 4))] += 1
                winner = player_no % 4
            else:
                score[str((player_no % 4))] += 0
            player_no += 1
        player_no = winner
    output = []

    # For each of the players' points; if they match their according
    # bid, then add 10 points.
    for player, points in sorted(score.items()):
        if bids[int(player)] == points:
            a = score[player] + 10
        else:
            a = score[player]
        output.append(a)

    if suppress_player_data:
        return tuple(output)
    return tuple(output), player_data


def play(curr_trick, hand, prev_tricks, player_no, deck_top, phase_bids,
         player_data=None, suppress_player_data=True,
         is_valid=is_valid_play, score=score_phase):
    if suppress_player_data:
        return hand[0]

    # Generate the current scores to be used in the comparison
    # to the phase_bids
    scores = score(phase_bids, prev_tricks, deck_top)
    if scores == ():
        scores = (0, 0, 0, 0)

    # Make sure function only chooses from valid cards.
    ref_hand = []
    for card in hand:
        if is_valid(card, curr_trick, hand):
            ref_hand.append(card)

    playing = ref_hand[0]
    card_probs = player_data[0]

    # If current score is lower than bid, play cards more likely to win.
    # If not, then play other cards less likely to win.
    if player_data != []:
        for card in ref_hand:
            if scores[player_no] < phase_bids[player_no]:
                if card_probs[card] > 0.5:
                    playing = card
                else:
                    playing = 'throwaway'
            else:
                if card_probs[card] < 0.5:
                    playing = card
        if playing == 'throwaway':
            value_list = [(value, card) for (card, value)
                          in card_probs.items() if card in ref_hand]
            return min(value_list)[1], (card_probs, prev_tricks)

    # Return the card as well as a 2-tuple containing card probabilities
    # (to be used in the next round if applicable) and the prev_tricks
    # to be used in the bid function.
    return playing, (card_probs, prev_tricks)






