import random
import json
from statistics import mean, stdev

continute_probability_path_a = 0.5
continute_probability_path_b = 0.5

# Create deck
def create_deck():
    """Create a shuffled 52-card deck."""
    deck = []
    for value in range(1, 14):  # 1-13
        for suit in ['H', 'D', 'C', 'S']:  # 4 suits
            deck.append({'value': value, 'suit': suit})
    random.shuffle(deck)
    return deck

def get_card_name(card):
    """Return readable card name."""
    values = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 
              8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K'}
    return f"{values[card['value']]}{card['suit']}"

def get_path_a_stage1_payout(card_value):
    """Get payout for Path A Stage 1 based on Card 1 value."""
    payouts = {
        1: 1, 13: 1,      # Ace, King
        2: 2, 12: 2,      # 2, Queen
        3: 2, 11: 2,      # 3, Jack
        4: 2, 10: 2,      # 4, 10
        5: 3, 9: 3,       # 5, 9
        6: 3, 8: 3,       # 6, 8
        7: 4,             # 7
    }
    return payouts.get(card_value, 0)

def get_path_a_stage2_payout(guessed_tie):
    """Get payout for Path A Stage 2."""
    return 9 if guessed_tie else 8

def get_path_b_stage1_payout(card_value):
    """Get payout for Path B Stage 1 based on Card 1 value."""
    payouts = {
        1: 3, 13: 3,      # Ace, King
        2: 4, 12: 4,      # 2, Queen
        3: 4, 11: 4,      # 3, Jack
        4: 4, 10: 4,      # 4, 10
        5: 5, 9: 5,       # 5, 9
        6: 5, 8: 5,       # 6, 8
        7: 6,             # 7
    }
    return payouts.get(card_value, 0)

def get_path_b_stage2_payout(guessed_tie):
    """Get payout for Path B Stage 2."""
    return 11 if guessed_tie else 10

def find_best_direction_value_only(card_value, remaining_deck):
    """Find best H/L/T guess (value only) based on remaining cards."""
    higher_count = sum(1 for c in remaining_deck if c['value'] > card_value)
    lower_count = sum(1 for c in remaining_deck if c['value'] < card_value)
    tie_count = sum(1 for c in remaining_deck if c['value'] == card_value)
    
    if higher_count >= lower_count and higher_count >= tie_count:
        return 'Higher'
    elif lower_count >= tie_count:
        return 'Lower'
    else:
        return 'Tie'

def find_best_suit_and_direction(card_value, remaining_deck):
    """Find best suit and best H/L/T guess based on remaining cards."""
    best_suit = None
    best_count = 0
    best_direction = None
    
    # Try each suit
    for suit in ['H', 'D', 'C', 'S']:
        higher_count = sum(1 for c in remaining_deck if c['value'] > card_value and c['suit'] == suit)
        lower_count = sum(1 for c in remaining_deck if c['value'] < card_value and c['suit'] == suit)
        tie_count = sum(1 for c in remaining_deck if c['value'] == card_value and c['suit'] == suit)
        
        max_count = max(higher_count, lower_count, tie_count)
        
        # If this suit has more cards in best direction, choose it
        if max_count > best_count:
            best_count = max_count
            best_suit = suit
            
            if higher_count >= lower_count and higher_count >= tie_count:
                best_direction = 'Higher'
            elif lower_count >= tie_count:
                best_direction = 'Lower'
            else:
                best_direction = 'Tie'
    
    return best_suit, best_direction

def check_prediction_value_only(card1, card2, prediction):
    """Check if value-only prediction is correct."""
    if prediction == 'Higher':
        return card2['value'] > card1['value']
    elif prediction == 'Lower':
        return card2['value'] < card1['value']
    else:  # Tie
        return card2['value'] == card1['value']

def check_prediction_with_suit(card1, card2, prediction, chosen_suit):
    """Check if value+suit prediction is correct."""
    # First check value
    value_correct = False
    if prediction == 'Higher':
        value_correct = card2['value'] > card1['value']
    elif prediction == 'Lower':
        value_correct = card2['value'] < card1['value']
    else:  # Tie
        value_correct = card2['value'] == card1['value']
    
    # Then check suit
    suit_correct = card2['suit'] == chosen_suit
    
    return value_correct and suit_correct

# ============================================================================
# PATH A SIMULATIONS
# ============================================================================

def simulate_path_a_cash_out():
    """Path A Stage 1 only (cash out after winning)."""
    deck = create_deck()
    
    # Stage 1: Card 1 revealed
    card1 = deck[0]
    remaining = deck[1:]
    
    # Player makes best guess (value only)
    prediction = find_best_direction_value_only(card1['value'], remaining)
    
    # Card 2 revealed
    card2 = deck[1]
    
    # Check if correct
    if check_prediction_value_only(card1, card2, prediction):
        # Player won Stage 1
        payout = get_path_a_stage1_payout(card1['value'])
        return {'payout': payout, 'wagered': 2, 'net': payout - 2}
    else:
        # Player lost Stage 1
        return {'payout': 0, 'wagered': 2, 'net': -2}

def simulate_path_a_continue():
    """Path A Stage 1 + Stage 2 (always continue if win Stage 1)."""
    deck = create_deck()
    
    # ===== STAGE 1 =====
    card1 = deck[0]
    remaining_after_1 = deck[1:]
    
    # Player makes best guess (value only)
    prediction_s1 = find_best_direction_value_only(card1['value'], remaining_after_1)
    
    # Card 2 revealed
    card2 = deck[1]
    
    # Check if Stage 1 correct
    if not check_prediction_value_only(card1, card2, prediction_s1):
        # Lost Stage 1
        return {'payout': 0, 'wagered': 2, 'net': -2}
    
    # Stage 1 won!
    stage1_payout = get_path_a_stage1_payout(card1['value'])
    
    # Player decides to continue (60% of the time)
    if random.random() > continute_probability_path_a:
        # Cash out
        return {'payout': stage1_payout, 'wagered': 2, 'net': stage1_payout - 2}
    
    # ===== STAGE 2 =====
    # Player pays 1 DD to continue
    total_wagered = 2 + 1
    
    remaining_after_2 = deck[2:]
    
    # Player picks direction (value only for Stage 2)
    chosen_suit_s2, prediction_s2 = find_best_suit_and_direction(card2['value'], remaining_after_2)
    
    # Card 3 revealed
    card3 = deck[2]
    
    # Check if Stage 2 correct
    if check_prediction_with_suit(card2, card3, prediction_s2, chosen_suit_s2):
        # Stage 2 won!
        guessed_tie = (prediction_s2 == 'Tie')
        stage2_payout = get_path_a_stage2_payout(guessed_tie)
        total_payout = stage1_payout + stage2_payout
        return {'payout': total_payout, 'wagered': total_wagered, 'net': total_payout - total_wagered}
    else:
        # Stage 2 lost - player loses Stage 1 payout + Stage 2 cost
        return {'payout': 0, 'wagered': total_wagered, 'net': -total_wagered}

# ============================================================================
# PATH B SIMULATIONS
# ============================================================================

def simulate_path_b_cash_out():
    """Path B Stage 1 only (value + suit required)."""
    deck = create_deck()
    
    # Stage 1: Card 1 revealed
    card1 = deck[0]
    remaining = deck[1:]
    
    # Player picks BEST suit and direction
    chosen_suit, prediction = find_best_suit_and_direction(card1['value'], remaining)
    
    # Card 2 revealed
    card2 = deck[1]
    
    # Check if correct (value + suit)
    if check_prediction_with_suit(card1, card2, prediction, chosen_suit):
        # Player won Stage 1
        payout = get_path_b_stage1_payout(card1['value'])
        return {'payout': payout, 'wagered': 3, 'net': payout - 3}
    else:
        # Player lost Stage 1
        return {'payout': 0, 'wagered': 3, 'net': -3}

def simulate_path_b_continue():
    """Path B Stage 1 + Stage 2 (value + suit required both stages)."""
    deck = create_deck()
    
    # ===== STAGE 1 =====
    card1 = deck[0]
    remaining_after_1 = deck[1:]
    
    # Player picks BEST suit and direction
    chosen_suit_s1, prediction_s1 = find_best_suit_and_direction(card1['value'], remaining_after_1)
    
    # Card 2 revealed
    card2 = deck[1]
    
    # Check if Stage 1 correct
    if not check_prediction_with_suit(card1, card2, prediction_s1, chosen_suit_s1):
        # Lost Stage 1
        return {'payout': 0, 'wagered': 3, 'net': -3}
    
    # Stage 1 won!
    stage1_payout = get_path_b_stage1_payout(card1['value'])
    
    # Player decides to continue (60% of the time)
    if random.random() > continute_probability_path_b:
        # Cash out
        return {'payout': stage1_payout, 'wagered': 3, 'net': stage1_payout - 3}
    
    # ===== STAGE 2 =====
    # Player pays 1 DD to continue
    total_wagered = 3 + 1
    
    remaining_after_2 = deck[2:]
    
    # Player picks BEST suit and direction
    chosen_suit_s2, prediction_s2 = find_best_suit_and_direction(card2['value'], remaining_after_2)
    
    # Card 3 revealed
    card3 = deck[2]
    
    # Check if Stage 2 correct
    if check_prediction_with_suit(card2, card3, prediction_s2, chosen_suit_s2):
        # Stage 2 won!
        guessed_tie = (prediction_s2 == 'Tie')
        stage2_payout = get_path_b_stage2_payout(guessed_tie)
        total_payout = stage1_payout + stage2_payout
        return {'payout': total_payout, 'wagered': total_wagered, 'net': total_payout - total_wagered}
    else:
        # Stage 2 lost - player loses Stage 1 payout + Stage 2 cost
        return {'payout': 0, 'wagered': total_wagered, 'net': -total_wagered}

# ============================================================================
# STATISTICS & REPORTING
# ============================================================================

def calculate_stats(results):
    """Calculate statistics from results."""
    nets = [r['net'] for r in results]
    payouts = [r['payout'] for r in results]
    wagered = [r['wagered'] for r in results]
    
    n = len(results)
    wins = sum(1 for r in results if r['payout'] > 0)
    losses = n - wins
    win_rate = (wins / n) * 100
    
    total_net = sum(nets)
    avg_net = mean(nets)
    std_net = stdev(nets) if n > 1 else 0
    total_payout = sum(payouts)
    total_wagered = sum(wagered)
    
    return {
        'count': n,
        'total_payout': total_payout,
        'total_wagered': total_wagered,
        'total_net_profit': total_net,
        'average_net_profit': round(avg_net, 4),
        'std_dev': round(std_net, 4),
        'wins': wins,
        'losses': losses,
        'win_rate_pct': round(win_rate, 2),
    }

def run_simulation(num_games=1_000_000):
    """Run 1M games for each scenario."""
    scenarios = {
        'Path A + Cash Out': [],
        'Path A + Continue': [],
        'Path B + Cash Out': [],
        'Path B + Continue': [],
    }
    
    print(f"Running {num_games:,} games for each scenario...")
    print("=" * 80)
    
    for game_num in range(num_games):
        if (game_num + 1) % 250_000 == 0:
            print(f"Progress: {game_num + 1:,} games completed...")
        
        # Path A Cash Out
        scenarios['Path A + Cash Out'].append(simulate_path_a_cash_out())
        
        # Path A Continue
        scenarios['Path A + Continue'].append(simulate_path_a_continue())
        
        # Path B Cash Out
        
        scenarios['Path B + Cash Out'].append(simulate_path_b_cash_out())
        
        # Path B Continue
        scenarios['Path B + Continue'].append(simulate_path_b_continue())
    
    return scenarios

def print_results(scenarios):
    """Print formatted results."""
    print("\n" + "=" * 80)
    print("SIMULATION RESULTS (1,000,000 games per scenario)")
    print("=" * 80)
    
    for scenario_name, results in scenarios.items():
        stats = calculate_stats(results)
        
        print(f"\n{scenario_name}")
        print("-" * 80)
        print(f"  Total Games:          {stats['count']:,}")
        print(f"  Total Wagered:        {stats['total_wagered']:,} DD")
        print(f"  Total Payouts:        {stats['total_payout']:,} DD")
        print(f"  Total Net Profit:     {stats['total_net_profit']:,} DD")
        print(f"  Average Net/Game:     {stats['average_net_profit']:.4f} DD")
        print(f"  Std Dev:              {stats['std_dev']:.4f}")
        print(f"  Win Rate:             {stats['win_rate_pct']:.2f}%")
        print(f"  Total Wins:           {stats['wins']:,}")
        print(f"  Total Losses:         {stats['losses']:,}")

def export_to_json(scenarios, filename='hlt_ladder_results.json'):
    """Export results to JSON."""
    data = {}
    
    for scenario_name, results in scenarios.items():
        stats = calculate_stats(results)
        
        player_wins = stats['wins']
        house_wins = stats['losses']
        total_games = stats['count']
        player_win_prob = player_wins / total_games
        house_win_prob = house_wins / total_games
        
        house_advantage_pct = (house_win_prob - player_win_prob) * 100
        ev_per_game = stats['average_net_profit']
        roi_pct = (stats['total_net_profit'] / stats['total_wagered']) * 100
        
        data[scenario_name] = {
            'statistics': {
                'count': stats['count'],
                'total_wagered': stats['total_wagered'],
                'total_payouts': stats['total_payout'],
                'total_net_profit': stats['total_net_profit'],
                'average_net_profit': stats['average_net_profit'],
                'std_dev': stats['std_dev'],
                'wins': stats['wins'],
                'losses': stats['losses'],
                'win_rate_pct': stats['win_rate_pct'],
            },
            'player': {
                'wins': player_wins,
                'win_probability': round(player_win_prob, 6),
                'win_percentage': f"{player_win_prob * 100:.2f}%"
            },
            'house': {
                'wins': house_wins,
                'win_probability': round(house_win_prob, 6),
                'win_percentage': f"{house_win_prob * 100:.2f}%"
            },
            'house_advantage_percentage': f"{house_advantage_pct:.2f}%",
            'expected_value_per_game': f"${ev_per_game:.4f}",
            'roi_percentage': f"{roi_pct:.2f}%",
        }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Results exported to '{filename}'")

if __name__ == "__main__":
    scenarios = run_simulation(num_games=1_000_000)
    # print_results(scenarios)
    export_to_json(scenarios)
