import copy
import random
import math

ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
cval = dict(zip(ranks, [1]*5+[0]*3+[-1]*5))
val = dict(zip(ranks, [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]))
cards = [suit + rank for rank in ranks for suit in ('C', 'D', 'H', 'S')]
cardimages = dict(zip(cards, [pygame.image.load("images/"+card+".png").convert() for card in cards]))
deck = copy.deepcopy(2 * cards)
numcards = len(deck)
cut, curr, count = 0, 0, 0
bet, chips = [], []
minbet = 5
hand = []
flatHands = []
isSplit = []
isDoubleDown = []

def shuffle():
    global cut, deck, curr
    cut = random.randrange(numcards * 1//3, numcards * 2//3)
    curr = 0
    random.shuffle(deck)
    print("Deck shuffled!")

def calc_total(hand):
    global val
    total = 0
    aces = 0
    for card in hand:
        total += val[card[1]]
        if card[1] == 'A': aces += 1
    while aces > 0 and total > 21:
        aces -= 1
        total -= 10
    return total

def print_hand(hand, name):
    if isinstance(hand[0], list):
        for j in range(len(hand)):
            print_hand(hand[j], name + f" Split {j+1}")
    else:
        print(f"{name}'s Hand: ", end = '')
        for i in range(len(hand)):
            if i == len(hand)-1: print(hand[i][1])
            else: print(hand[i][1], end = ' | ')

def draw_card(hand, n=1):
    global curr, deck
    for _ in range(n): 
        hand.append(deck[curr])
        curr += 1
    return hand

def is_blackjack(hand):
    return len(hand) == 2 and calc_total(hand) == 21

def print_dealer():
    global hand
    print(f"Dealer's Hand: {hand[0][0][1]} | ?")

def play_hand(hand, num, name):
    global bet, isSplit, isDoubleDown
    options = ['hit', 'stand']
    if len(hand) == 2 and hand[0][1] == hand[1][1]: options.append('split')
    if (calc_total(hand) == 10 or calc_total(hand) == 11) and len(hand) == 2: options.append('double down')
    print_dealer()
    print_hand(hand, name)
    print("Options: ", end = '')
    for i in range(len(options)):
        if i == len(options)-1: print(options[i])
        else: print(options[i], end = ' | ')
    choice = input('What would you like to do? >> ')
    while choice.lower() not in options:
        choice = input('What would you like to do? >> ')
    if choice == 'stand': pass
    elif choice == 'hit': 
        hand = draw_card(hand)
        if calc_total(hand) > 21:
            print_hand(hand, name)
            print("Bust!")
        else:
            play_hand(hand, num, name)
    elif choice == 'split': 
        isSplit[num - 1] = True
        hand = [[hand[0]], [hand[1]]]
        hand[0] = draw_card(hand[0])
        hand[1] = draw_card(hand[1])
        hand[0] = play_hand(hand[0], num, name + " Split 1")
        hand[1] = play_hand(hand[1], num, name + " Split 2")
    elif choice == 'double down': 
        isDoubleDown[num - 1] = True
        bet[num-1] *= 2
        hand = draw_card(hand) 
        print_hand(hand, name)
    print('')
    return hand

def compare_hand(player, dealer, num):
    global bet, chips, isSplit
    player_total = calc_total(player)
    dealer_total = calc_total(dealer)
    mult = 0
    print(f"Player {num}: ", end = '')
    if is_blackjack(player) and not isSplit[num-1]: 
        if is_blackjack(dealer): print("Blackjack Push. Keep Bet.")
        else: 
            mult = 1.5
            print("Blackjack, Win 1.5x Bet.")
    elif player_total > 21:
        print("Player Bust, Lose Bet.") 
        mult = -1
    else:
        if dealer_total > 21:
            print("Dealer Bust, Win Bet.")
            mult = 1
        else:
            if player_total > dealer_total:
                print("Player Win, Win Bet.")
                mult = 1
            elif player_total < dealer_total:
                print("Dealer Win, Lose Bet.")
                mult = -1
            else: print("Push. Keep Bet.")
            
    chips[num-1] += bet[num-1] * mult

def flattenHands(hand):
    global flatHands
    for i in hand:
        if type(i) == list: flattenHands(i)
        else: flatHands.append(i)


def blackjack():
    global curr, cut, count, bet, chips, hand, deck, flatHands, isSplit, isDoubleDown

    try: n = int(input("Number of Players: "))
    except: n=1
    bet = [minbet for _ in range(n)]
    chips = [100 for _ in range(n)]
    isSplit = [False for _ in range(n)]
    isDoubleDown = [False for _ in range(n)]
    shuffle()
    while True:
        if curr >= cut: shuffle()
        for i in range(n):
            try: newbet = int(input(f"Enter your bet, Player {i+1}. Current chips {chips[i]}. Default bet {bet[i]}: "))
            except: newbet = bet[i]
            if newbet > chips[i] or newbet < minbet: newbet = minbet
            bet[i] = newbet

        # dealer bust bet?

        hand = [[] for _ in range(n+1)] # i=0 is dealer, 1-n = players
        for i in range(n+1):
            hand[i] = draw_card(hand[i], 2)

        isSplit = [False for _ in range(n)]
        isDoubleDown = [False for _ in range(n)]

        print_dealer()
        for i in range(1, n+1):
            print_hand(hand[i], "Player " + str(i))
        print('')
        
        if hand[0][0] == 'A':
            # insurance check
            # insurance is 2 to 1 (get double money on separate bet)
            pass
        
        if calc_total(hand[0]) == 21:
            print("Dealer Blackjack!")
        else:
            for i in range(n):
                if calc_total(hand[i+1]) == 21: print("Player Blackjack!")
                else: 
                    hand[i+1] = play_hand(hand[i+1], i+1, "Player " + str(i+1))
                    print_hand(hand[i+1], "Player " + str(i+1))
                    print("")
            print_hand(hand[0], "Dealer")
            while calc_total(hand[0]) < 17:
                hand[0] = draw_card(hand[0])
                print("Dealer Hit")
                print_hand(hand[0], "Dealer")
            if calc_total(hand[0]) > 21: print("Dealer Bust!")
            else: print("Dealer Stand")
            print("")

        for i in range(1, n+1):
            if isinstance(hand[i][0], list):
                for j in range(len(hand[i])):
                    compare_hand(hand[i][j], hand[0], i)
            else: compare_hand(hand[i], hand[0], i)

        print("\nCollecting Hands ... ")
        print_hand(hand[0], "Dealer")
        for i in range(1, n+1): print_hand(hand[i], "Player " + str(i))

        flatHands = []
        flattenHands(hand)
        count += sum([cval[card[1]] for card in flatHands])
        if 'y' in input("Reveal the count? >> ").lower(): print(count)

        if 'y' in input("Would you like to quit? ").lower(): break

blackjack()
# it would be nice to refactor for dealer hand to not be in the list

# i went the lazy way and did dd = bet *= 2 but that messes up default bets
# rn either w/ isdd array or doubling bet it won't do bet payout correctly for split --> one dd one reg 
# ^^ for this i think it could be done w/ indexes instead of t/f