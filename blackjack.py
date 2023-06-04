import copy
import random
import pygame

pygame.init()
WIDTH, HEIGHT, fps = 450, 600, 60
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Blackjack")
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 25)
fontUnderline = pygame.font.Font('freesansbold.ttf', 25)
fontUnderline.set_underline(True)

ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
cval = dict(zip(ranks, [1]*5+[0]*3+[-1]*5))
val = dict(zip(ranks, [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]))
cards = [suit + rank for rank in ranks for suit in ('C', 'D', 'H', 'S')]
cardimages = dict(zip(cards, [pygame.image.load("images/"+card+".png").convert() for card in cards]))
face_down = pygame.image.load("images/card_face_down.png")
deck = copy.deepcopy(2 * cards)
cut, curr, count = 0, 0, 0
flatHands, options = [], []
running, active, firstDeal, editBet = True, False, True, False
n = 2 # num players
minbet = 5
newBet = minbet
bet, chips = minbet, [100 for _ in range(n)]
hand = [[] for _ in range(n+1)]
topOffset = [50, 16, 8]
turn = 1
messages = ['' for _ in range(n+1)]
prevCount = count
prevChips = chips.copy()

def shuffle():
    global cut, deck, curr, count, messages
    cut, curr, count = random.randrange(len(deck) * 1//2, len(deck) * 2//3), 0, 0
    random.shuffle(deck)
    messages[0] = "Deck Shuffled!"

def calc_total(hand):
    global val
    total, aces = 0, 0
    for card in hand:
        total += val[card[1]]
        if card[1] == 'A': aces += 1
    while aces > 0 and total > 21:
        aces -= 1; total -= 10
    return total

def draw_card(hand, n=1):
    global curr, deck
    for _ in range(n): 
        hand.append(deck[curr])
        curr += 1
    return hand

def is_blackjack(hand):
    return len(hand) == 2 and calc_total(hand) == 21

def compare_hand(player, dealer, num):
    global bet, chips, prevChips
    player_total, dealer_total = calc_total(player), calc_total(dealer)
    mult, message = 0, ''
    if is_blackjack(player): 
        if is_blackjack(dealer): message = "BJ Push."
        else: mult = 1.5; message = "Player BJ!"
    elif is_blackjack(dealer) or player_total > 21: message = "Player Lose"; mult = -1
    else:
        if dealer_total > 21: message = "Player Win"; mult = 1
        else:
            if player_total > dealer_total: message = "Player Win"; mult = 1
            elif player_total < dealer_total: message = "Player Lose"; mult = -1
            else: message = "Push"
            
    chips[num-1] = prevChips[num-1] + bet * mult
    return message

def flattenHands(hand):
    global flatHands
    for i in hand:
        if type(i) == list: flattenHands(i)
        else: flatHands.append(i)

def draw_game():
    global hand, active, options, topOffset, messages, turn, chips
    buttons = []
    if active and turn > 0 and turn <= n: resetOptions(hand[turn])
    elif editBet: options = ['confirm', '1', '5', '25', 'clear']
    else: options = ['deal', 'reveal count', 'change bet'] 
    for i in range(len(options)):
        length = (WIDTH-20-6*len(options))/len(options) 
        height = HEIGHT - HEIGHT/5
        button = pygame.draw.rect(screen, 'white', [13+i*(length+6), height - 15, length, HEIGHT/5], 0, 5)
        pygame.draw.rect(screen, 'black', [13+i*(length+6), height - 15, length, HEIGHT/5], 3, 5)
        
        words = options[i].split()
        if 'confirm' in words: words = ['con', 'firm']
        for j in range(len(words)):
            offset = 0
            if len(words) > 1:
                offset = height/30 * len(words)
            text = font.render(words[j], True, 'black') 
            text_rect = text.get_rect(center=(13+i*(length+6) + length/2, height+height/10 + offset*(j - 1/2)))
            screen.blit(text, text_rect)
        buttons.append(button)

        if editBet and (i >= 1 and i <= 3):
            image = pygame.image.load("images/chip" + str(options[i]) + ".png")
            image = pygame.transform.scale(image, (60, 60))
            screen.blit(image, (13+i*(length+6)+10, height+15))

    height = (440) / (n+1)
    card_height = min(height - 30, 100)
    card_width = card_height / face_down.get_height() * face_down.get_width()

    screen.blit(font.render("Dealer's Hand", True, 'black'), (10, 10))
    screen.blit(font.render(messages[0], True, 'black'), (200, 10))
    for i, card in enumerate(hand[0]):
        image = cardimages[card]
        if active and i == 1:
            image = face_down
        image = pygame.transform.scale(image, (card_width, card_height))
        screen.blit(image, (i*card_width+10, 30 + topOffset[n-1]))

    for player in range(1, n+1):
        if player == turn and active: screen.blit(fontUnderline.render(f"Player {player}'s Hand", True, 'black'), (10, 10+(height)*player))
        else: screen.blit(font.render(f"Player {player}'s Hand", True, 'black'), (10, 10+(height)*player))
        screen.blit(font.render("$" + str(chips[player-1]) + " " + messages[player], True, 'black'), (215, 10+(height)*player))
        for i, card in enumerate(hand[player]):
            image = cardimages[card]
            image = pygame.transform.scale(image, (card_width, card_height))
            screen.blit(image, (i*card_width+10, (height)*player+30 + topOffset[n-1]))

    return buttons

def resetOptions(hand):
    global options
    options = ['hit', 'stand']
    if len(hand) == 2 and hand[0][1] == hand[1][1]: options.append('split')
    if (calc_total(hand) == 10 or calc_total(hand) == 11) and len(hand) == 2: options.append('double down')

# when new hand
def reset():
    global hand, curr, cut, bet, active, firstDeal, n, messages, turn, prevCount, prevChips, newBet
    turn = 1
    active, firstDeal = True, False
    bet = newBet
    messages = ['' for _ in range(n+1)]

    if curr >= cut: shuffle()

    prevCount = count
    prevChips = chips.copy()

    #bets here
    # use var minbet
    # if bet > minbet or bet > #chips then default to minbet

    hand = [[] for _ in range(n+1)]
    for i in range(n+1):
        hand[i] = draw_card(hand[i], 2)

    resetOptions(hand[1])

    # insurance here

    if calc_total(hand[0]) == 21:
        active = False

while running:
    timer.tick(fps)
    screen.fill('white')
    buttons = draw_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONUP:
            if not active and not editBet:
                if buttons[0].collidepoint(event.pos): reset()
                elif buttons[1].collidepoint(event.pos):
                    messages[0] = "Count: " + str(count)
                elif buttons[2].collidepoint(event.pos):
                    editBet = True
                    newBet = bet
            elif editBet:
                if buttons[0].collidepoint(event.pos): editBet = False
                elif buttons[1].collidepoint(event.pos): newBet += 1
                elif buttons[2].collidepoint(event.pos): newBet += 5
                elif buttons[3].collidepoint(event.pos): newBet += 25
                elif buttons[4].collidepoint(event.pos): newBet = minbet
            else:
                messages[0] = ''
                if buttons[0].collidepoint(event.pos):
                    hand[turn] = draw_card(hand[turn])
                    if calc_total(hand[turn]) > 21: messages[turn] = "bust"; turn += 1
                elif buttons[1].collidepoint(event.pos): messages[turn] = "stand"; turn += 1
                elif (len(buttons) > 2 and buttons[2].collidepoint(event.pos) and options[2] == 'split'):
                    #split
                    pass
                elif (len(buttons) > 2 and buttons[2].collidepoint(event.pos) and options[2] == 'double down') or (len(buttons) > 3 and buttons[3].collidepoint(event.pos) and options[3] == 'double down'):
                    bet *= 2
                    hand[turn] = draw_card(hand[turn])
                    messages[turn] = "double down"
                    turn += 1
    
    if turn > n: active = False

    if (active and is_blackjack(hand[turn])): messages[turn] = 'blackjack!'; turn += 1

    if editBet: messages[0] = "New Bet: $" + str(newBet)

    if not active and not firstDeal:
        while calc_total(hand[0]) < 17: hand[0] = draw_card(hand[0])
        for i in range(1, n+1):
            result = compare_hand(hand[i], hand[0], i)
            messages[i] = result
        flatHands = []
        flattenHands(hand)
        count = prevCount + sum([cval[card[1]] for card in flatHands])

    pygame.display.flip()

# god splits is going to be a pain

pygame.quit()

#todo
# split - idea maybe make n seperate between num players and num hands to display
# bc the draw hands area is nice with n=num hands counting splits but all the other stuff should be n=num players

# fix dd bet = isdoubledown array