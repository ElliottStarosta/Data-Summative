# 
import random
import json
from enum import Enum
from datetime import datetime
import signal
import sys

class Choice(Enum):
    HIGHER = "higher"
    LOWER = "lower"
    TIE = "tie"

class HighLowChallengePlus:
    CARD_VALUES = {
        'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
    }
    
    CARD_NAMES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    COST_TO_PLAY = 2
    PAYOUT_TIE = 8
    
    PAYOUT_TABLE = {
        1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 4,
        8: 3, 9: 3, 10: 3, 11: 2, 12: 2, 13: 1
    }
    
    def __init__(self):
        self.deck = []
        self.game_history = []
        self.balance = 0
        self.round_number = 0
        self.create_deck()
    
    def create_deck(self):
        self.deck = []
        for card in self.CARD_NAMES:
            self.deck.extend([card] * 4)
        random.shuffle(self.deck)
    
    def get_payout(self, first_value):
        return self.PAYOUT_TABLE[first_value]
    
    def play_round(self, choice, first_card, first_value):
        self.round_number += 1
        
        if len(self.deck) < 1:
            self.create_deck()
        
        second_card = self.deck.pop()
        second_value = self.CARD_VALUES[second_card]
        
        if second_value > first_value:
            outcome = "higher"
        elif second_value < first_value:
            outcome = "lower"
        else:
            outcome = "tie"
        
        payout = 0
        if choice == Choice.HIGHER and outcome == "higher":
            payout = self.get_payout(first_value)
        elif choice == Choice.LOWER and outcome == "lower":
            payout = self.get_payout(first_value)
        elif choice == Choice.TIE and outcome == "tie":
            payout = self.PAYOUT_TIE
        
        net_result = payout - self.COST_TO_PLAY
        self.balance += net_result
        
        round_result = {
            "round": self.round_number,
            "first_card": first_card,
            "first_value": first_value,
            "second_card": second_card,
            "second_value": second_value,
            "player_choice": choice.value,
            "outcome": outcome,
            "payout": payout,
            "cost": self.COST_TO_PLAY,
            "net_result": net_result,
            "balance_after": self.balance,
            "win": payout > 0
        }
        
        self.game_history.append(round_result)
        return round_result
    
    def save_results(self):
        if not self.game_history:
            print("\nNo rounds played. Nothing to save.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"high_low_challenge_game_{timestamp}.json"
        
        wins = sum(1 for r in self.game_history if r["win"])
        losses = len(self.game_history) - wins
        total_payout = sum(r["payout"] for r in self.game_history)
        total_cost = len(self.game_history) * self.COST_TO_PLAY
        
        results = {
            "game": "High-Low Challenge+ (Whole-Number Version)",
            "session_timestamp": datetime.now().isoformat(),
            "total_rounds": len(self.game_history),
            "wins": wins,
            "losses": losses,
            "win_rate": f"{(wins / len(self.game_history) * 100):.2f}%",
            "total_payout": total_payout,
            "total_cost": total_cost,
            "final_balance": self.balance,
            "game_history": self.game_history
        }
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✓ Game results saved to: {filename}")
        print(f"{'='*70}\n")


def display_header():
    print("\n" + "="*70)
    print("HIGH-LOW CHALLENGE+ (WHOLE-NUMBER VERSION)")
    print("="*70)
    print(f"Cost to play: $2")
    print(f"Payout Table (Higher/Lower):")
    print(f"  Ace, King: $1 | 2, 3, J, Q: $2 | 4-6, 8-10: $3 | 7: $4")
    print(f"Payout for Tie: $8")
    print("="*70)
    print("Press Ctrl+C at any time to exit and save your results.")
    print("="*70 + "\n")


def display_round(round_result):
    print(f"\n--- Round {round_result['round']} ---")
    print(f"First card: {round_result['first_card']} (value: {round_result['first_value']})")
    print(f"Your choice: {round_result['player_choice'].upper()}")
    print(f"Second card: {round_result['second_card']} (value: {round_result['second_value']})")
    print(f"Outcome: {round_result['outcome'].upper()}")
    
    if round_result['win']:
        print(f"✓ YOU WIN! Payout: ${round_result['payout']}")
    else:
        print(f"✗ You lose. Payout: $0")
    
    print(f"Cost: ${round_result['cost']}")
    print(f"Net result: ${round_result['net_result']:+d}")
    print(f"Balance: ${round_result['balance_after']:+d}")


def get_player_choice():
    while True:
        choice_input = input("Will the next card be (h)igher, (l)ower, or (t)ie? ").lower().strip()
        if choice_input == 'h':
            return Choice.HIGHER
        elif choice_input == 'l':
            return Choice.LOWER
        elif choice_input == 't':
            return Choice.TIE
        else:
            print("Invalid choice. Please enter 'h', 'l', or 't'.")


def handle_exit(signum, frame):
    raise KeyboardInterrupt()


def main():
    game = HighLowChallengePlus()
    signal.signal(signal.SIGINT, handle_exit)
    
    display_header()
    
    try:
        while True:
            if len(game.deck) < 2:
                game.create_deck()
            
            first_card = game.deck.pop()
            first_value = game.CARD_VALUES[first_card]
            
            print(f"\n{'='*70}")
            print(f"First card drawn: {first_card} (value: {first_value})")
            print(f"{'='*70}")
            
            choice = get_player_choice()
            
            round_result = game.play_round(choice, first_card, first_value)
            display_round(round_result)
            
    
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
    
    finally:
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        print(f"Total rounds played: {game.round_number}")
        
        if game.game_history:
            wins = sum(1 for r in game.game_history if r["win"])
            losses = game.round_number - wins
            win_rate = (wins / game.round_number) * 100 if game.round_number > 0 else 0
            
            print(f"Wins: {wins}")
            print(f"Losses: {losses}")
            print(f"Win rate: {win_rate:.2f}%")
            print(f"Final balance: ${game.balance:+d}")
            print("="*70)
        
        game.save_results()


if __name__ == "__main__":
    main()