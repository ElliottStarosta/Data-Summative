import random
import json
from enum import Enum
from collections import defaultdict

class Choice(Enum):
    HIGHER = "higher"
    LOWER = "lower"
    TIE = "tie"

class HighLowChallengePlus:
    # Card values
    CARD_VALUES = {
        'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
    }
    
    CARD_NAMES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    # Game settings
    COST_TO_PLAY = 2
    PAYOUT_TIE = 8
    
    # Payout table for Higher/Lower based on first card value
    PAYOUT_TABLE = {
        1: 1,    # Ace
        2: 2,    # 2
        3: 2,    # 3
        4: 3,    # 4
        5: 3,    # 5
        6: 3,    # 6
        7: 4,    # 7
        8: 3,    # 8
        9: 3,    # 9
        10: 3,   # 10
        11: 2,   # Jack
        12: 2,   # Queen
        13: 1    # King
    }
    
    def __init__(self):
        """Initialize the game."""
        self.deck = []
    
    def create_deck(self):
        """Create a standard 52-card deck."""
        self.deck = []
        for card in self.CARD_NAMES:
            self.deck.extend([card] * 4)  # 4 suits
        random.shuffle(self.deck)
    
    def get_payout(self, first_value):
        """Get the payout for Higher/Lower based on first card value."""
        return self.PAYOUT_TABLE[first_value]
    
    def play_round(self, choice):
        """Play a single round."""
        # Recreate deck if needed
        if len(self.deck) < 2:
            self.create_deck()
        
        # Draw first and second cards
        first_card = self.deck.pop()
        second_card = self.deck.pop()
        
        first_value = self.CARD_VALUES[first_card]
        second_value = self.CARD_VALUES[second_card]
        
        # Determine outcome
        if second_value > first_value:
            outcome = "higher"
        elif second_value < first_value:
            outcome = "lower"
        else:
            outcome = "tie"
        
        # Determine payout
        payout = 0
        
        if choice == Choice.HIGHER and outcome == "higher":
            payout = self.get_payout(first_value)
        elif choice == Choice.LOWER and outcome == "lower":
            payout = self.get_payout(first_value)
        elif choice == Choice.TIE and outcome == "tie":
            payout = self.PAYOUT_TIE
        
        net_result = payout - self.COST_TO_PLAY
        
        return {
            "first_card": first_card,
            "first_value": first_value,
            "second_card": second_card,
            "second_value": second_value,
            "choice": choice.value,
            "outcome": outcome,
            "payout": payout,
            "net_result": net_result,
            "win": payout > 0
        }


def simulate_random_strategy(num_simulations=1000000):
    """Simulate game with random player strategy (1 million rounds)."""
    game = HighLowChallengePlus()
    
    player_wins = 0
    player_losses = 0
    total_net = 0
    
    # Track breakdown by first card
    outcomes_by_first_card = defaultdict(lambda: {"wins": 0, "losses": 0, "net": 0})
    
    # Track breakdown by choice
    outcomes_by_choice = {
        "higher": {"wins": 0, "losses": 0, "net": 0},
        "lower": {"wins": 0, "losses": 0, "net": 0},
        "tie": {"wins": 0, "losses": 0, "net": 0}
    }
    
    for _ in range(num_simulations):
        # Random choice: 33% each
        choice = random.choice([Choice.HIGHER, Choice.LOWER, Choice.TIE])
        
        # Play round
        result = game.play_round(choice)
        
        # Track results
        total_net += result["net_result"]
        
        if result["win"]:
            player_wins += 1
        else:
            player_losses += 1
        
        # Track by first card
        first_card = result["first_card"]
        outcomes_by_first_card[first_card]["net"] += result["net_result"]
        if result["win"]:
            outcomes_by_first_card[first_card]["wins"] += 1
        else:
            outcomes_by_first_card[first_card]["losses"] += 1
        
        # Track by choice
        choice_key = result["choice"]
        outcomes_by_choice[choice_key]["net"] += result["net_result"]
        if result["win"]:
            outcomes_by_choice[choice_key]["wins"] += 1
        else:
            outcomes_by_choice[choice_key]["losses"] += 1
    
    house_wins = num_simulations - player_wins
    player_win_rate = player_wins / num_simulations
    house_win_rate = house_wins / num_simulations
    house_advantage = (house_win_rate - player_win_rate) * 100
    expected_value_per_game = total_net / num_simulations
    
    # Convert breakdown to serializable dict
    breakdown_first_card = {}
    for card in game.CARD_NAMES:
        if card in outcomes_by_first_card:
            stats = outcomes_by_first_card[card]
            total_plays = stats["wins"] + stats["losses"]
            breakdown_first_card[card] = {
                "payout_for_higher_lower": game.get_payout(game.CARD_VALUES[card]),
                "total_plays": total_plays,
                "wins": stats["wins"],
                "losses": stats["losses"],
                "win_rate": f"{stats['wins'] / total_plays * 100:.2f}%",
                "net_result": stats["net"]
            }
    
    results = {
        "strategy": "Random (33% Higher, 33% Lower, 33% Tie)",
        "total_simulations": num_simulations,
        "player": {
            "wins": player_wins,
            "win_probability": player_win_rate,
            "win_percentage": f"{player_win_rate * 100:.2f}%"
        },
        "house": {
            "wins": house_wins,
            "win_probability": house_win_rate,
            "win_percentage": f"{house_win_rate * 100:.2f}%"
        },
        "house_advantage_percentage": f"{house_advantage:.2f}%",
        "total_net_winnings": total_net,
        "expected_value_per_game": f"${expected_value_per_game:.4f}",
        "roi_percentage": f"{(expected_value_per_game / 2) * 100:.2f}%",
        "breakdown_by_first_card": breakdown_first_card,
        "breakdown_by_choice": outcomes_by_choice
    }
    
    return results


def simulate_optimal_strategy(num_simulations=1000000):
    """
    Simulate game with optimal strategy:
    For each first card, choose the option with highest expected value.
    """
    game = HighLowChallengePlus()
    
    player_wins = 0
    player_losses = 0
    total_net = 0
    
    outcomes_by_first_card = defaultdict(lambda: {"wins": 0, "losses": 0, "net": 0, "optimal_choice": ""})
    outcomes_by_choice = {
        "higher": {"wins": 0, "losses": 0, "net": 0},
        "lower": {"wins": 0, "losses": 0, "net": 0},
        "tie": {"wins": 0, "losses": 0, "net": 0}
    }
    
    for _ in range(num_simulations):
        # Recreate deck if needed
        if len(game.deck) < 2:
            game.create_deck()
        
        # Peek at first card to determine optimal choice
        first_card = game.deck[-1]
        first_value = game.CARD_VALUES[first_card]
        
        # Calculate expected values for each choice
        # For higher/lower: count remaining cards higher/lower than first
        higher_count = sum(1 for v in game.CARD_VALUES.values() if v > first_value) * 4 - 1  # -1 for first card drawn
        lower_count = sum(1 for v in game.CARD_VALUES.values() if v < first_value) * 4 - 1
        tie_count = 3  # 3 remaining cards of same value (4 total - 1 drawn)
        total_remaining = 51
        
        payout_for_hl = game.get_payout(first_value)
        payout_for_tie = game.PAYOUT_TIE
        
        # Expected values (before subtracting cost)
        ev_higher = (higher_count / total_remaining) * payout_for_hl - (lower_count + tie_count) / total_remaining * 2
        ev_lower = (lower_count / total_remaining) * payout_for_hl - (higher_count + tie_count) / total_remaining * 2
        ev_tie = (tie_count / total_remaining) * payout_for_tie - (higher_count + lower_count) / total_remaining * 2
        
        # Choose option with highest expected value
        max_ev = max(ev_higher, ev_lower, ev_tie)
        if max_ev == ev_higher:
            choice = Choice.HIGHER
        elif max_ev == ev_lower:
            choice = Choice.LOWER
        else:
            choice = Choice.TIE
        
        # Play round
        result = game.play_round(choice)
        
        # Track results
        total_net += result["net_result"]
        
        if result["win"]:
            player_wins += 1
        else:
            player_losses += 1
        
        # Track by first card
        first_card_key = result["first_card"]
        outcomes_by_first_card[first_card_key]["net"] += result["net_result"]
        outcomes_by_first_card[first_card_key]["optimal_choice"] = choice.value
        if result["win"]:
            outcomes_by_first_card[first_card_key]["wins"] += 1
        else:
            outcomes_by_first_card[first_card_key]["losses"] += 1
        
        # Track by choice
        choice_key = result["choice"]
        outcomes_by_choice[choice_key]["net"] += result["net_result"]
        if result["win"]:
            outcomes_by_choice[choice_key]["wins"] += 1
        else:
            outcomes_by_choice[choice_key]["losses"] += 1
    
    house_wins = num_simulations - player_wins
    player_win_rate = player_wins / num_simulations
    house_win_rate = house_wins / num_simulations
    house_advantage = (house_win_rate - player_win_rate) * 100
    expected_value_per_game = total_net / num_simulations
    
    # Convert breakdown to serializable dict
    breakdown_first_card = {}
    for card in game.CARD_NAMES:
        if card in outcomes_by_first_card:
            stats = outcomes_by_first_card[card]
            total_plays = stats["wins"] + stats["losses"]
            breakdown_first_card[card] = {
                "payout_for_higher_lower": game.get_payout(game.CARD_VALUES[card]),
                "optimal_choice": stats["optimal_choice"],
                "total_plays": total_plays,
                "wins": stats["wins"],
                "losses": stats["losses"],
                "win_rate": f"{stats['wins'] / total_plays * 100:.2f}%",
                "net_result": stats["net"]
            }
    
    results = {
        "strategy": "Optimal (Maximize Expected Value per Card)",
        "total_simulations": num_simulations,
        "player": {
            "wins": player_wins,
            "win_probability": player_win_rate,
            "win_percentage": f"{player_win_rate * 100:.2f}%"
        },
        "house": {
            "wins": house_wins,
            "win_probability": house_win_rate,
            "win_percentage": f"{house_win_rate * 100:.2f}%"
        },
        "house_advantage_percentage": f"{house_advantage:.2f}%",
        "total_net_winnings": total_net,
        "expected_value_per_game": f"${expected_value_per_game:.4f}",
        "roi_percentage": f"{(expected_value_per_game / 2) * 100:.2f}%",
        "breakdown_by_first_card": breakdown_first_card,
        "breakdown_by_choice": outcomes_by_choice
    }
    
    return results


if __name__ == "__main__":
    print("Simulating High-Low Challenge+ (Whole-Number Version)...")
    print("Running 1 million rounds for each strategy...\n")
    
    # Random strategy
    print("1/2: Random Strategy...")
    random_results = simulate_random_strategy(num_simulations=1_000_000)
    
    # Optimal strategy
    print("2/2: Optimal Strategy...")
    optimal_results = simulate_optimal_strategy(num_simulations=1_000_000)
    
    # Save all results to JSON
    all_results = {
        "game": "High-Low Challenge+ (Whole-Number Version)",
        "cost_to_play": 2,
        "payout_table_higher_lower": {
            "A": 1, "2": 2, "3": 2, "4": 3, "5": 3, "6": 3, "7": 4,
            "8": 3, "9": 3, "10": 3, "J": 2, "Q": 2, "K": 1
        },
        "payout_tie": 8,
        "random_strategy": random_results,
        "optimal_strategy": optimal_results
    }
    
    with open("high_low_challenge_plus_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    print("\nRandom Strategy (33% Higher, 33% Lower, 33% Tie):")
    print(f"  Player Win Rate: {random_results['player']['win_percentage']}")
    print(f"  House Advantage: {random_results['house_advantage_percentage']}")
    print(f"  Expected Value: {random_results['expected_value_per_game']}")
    print(f"  ROI: {random_results['roi_percentage']}")
    print(f"  Total Net Winnings: ${random_results['total_net_winnings']}")
    
    print("\nOptimal Strategy (Maximize EV):")
    print(f"  Player Win Rate: {optimal_results['player']['win_percentage']}")
    print(f"  House Advantage: {optimal_results['house_advantage_percentage']}")
    print(f"  Expected Value: {optimal_results['expected_value_per_game']}")
    print(f"  ROI: {optimal_results['roi_percentage']}")
    print(f"  Total Net Winnings: ${optimal_results['total_net_winnings']}")
    
    print(f"\n✓ Full results saved to high_low_challenge_plus_results.json")
    print("="*70)