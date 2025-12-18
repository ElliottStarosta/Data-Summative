# Two truths and a lie exp probability simulation
import random
import json
from collections import defaultdict

def evaluate_statements(dice):
    """Evaluate the three statements for a given dice roll."""
    d1, d2, d3 = sorted(dice)
    
    # Statement 1: At least two dice are the same
    at_least_two_same = (d1 == d2) or (d2 == d3) or (d1 == d3)
    
    # Statement 2: Sum >= 11
    sum_gte_11 = sum(dice) >= 11
    
    # Statement 3: All dice are different
    all_different = (d1 != d2) and (d2 != d3) and (d1 != d3)
    
    return at_least_two_same, sum_gte_11, all_different

def find_false_statement(dice):
    """Find which statement is false (there's always exactly one)."""
    at_least_two_same, sum_gte_11, all_different = evaluate_statements(dice)
    statements = [at_least_two_same, sum_gte_11, all_different]
    
    false_idx = statements.index(False)
    return false_idx  # 0, 1, or 2

def simulate_game(num_simulations=1000000):
    """Simulate the Two Truths and a Lie game."""
    
    player_correct = 0
    house_correct = 0
    
    # Store outcomes by false statement type
    outcomes_by_statement = defaultdict(lambda: {"player_wins": 0, "house_wins": 0})
    statement_names = ["At least 2 same", "Sum >= 11", "All different"]
    
    for _ in range(num_simulations):
        # Roll three dice
        dice = [random.randint(1, 6) for _ in range(3)]
        
        # Determine the false statement
        false_statement_idx = find_false_statement(dice)
        
        # Player makes a random guess
        player_guess = random.randint(0, 2)
        
        # Check if player is correct
        if player_guess == false_statement_idx:
            player_correct += 1
            outcomes_by_statement[false_statement_idx]["player_wins"] += 1
        else:
            house_correct += 1
            outcomes_by_statement[false_statement_idx]["house_wins"] += 1
    
    # Calculate probabilities
    player_win_rate = player_correct / num_simulations
    house_win_rate = house_correct / num_simulations
    house_advantage = (house_win_rate - player_win_rate) * 100
    
    # Prepare results
    results = {
        "game": "Two Truths and a Lie (Dice Edition)",
        "simulations": num_simulations,
        "player": {
            "wins": player_correct,
            "win_probability": player_win_rate,
            "win_percentage": f"{player_win_rate * 100:.2f}%"
        },
        "house": {
            "wins": house_correct,
            "win_probability": house_win_rate,
            "win_percentage": f"{house_win_rate * 100:.2f}%"
        },
        "house_advantage_percentage": f"{house_advantage:.2f}%",
        "breakdown_by_false_statement": {}
    }
    
    # Add breakdown
    for idx, statement_name in enumerate(statement_names):
        if idx in outcomes_by_statement:
            stats = outcomes_by_statement[idx]
            total = stats["player_wins"] + stats["house_wins"]
            results["breakdown_by_false_statement"][statement_name] = {
                "occurrences": total,
                "player_wins": stats["player_wins"],
                "house_wins": stats["house_wins"],
                "player_win_rate": f"{stats['player_wins'] / total * 100:.2f}%"
            }
    
    return results

if __name__ == "__main__":
    print("Simulating Two Truths and a Lie (Dice Edition)...")
    print("This may take a moment...\n")
    
    results = simulate_game(num_simulations=100_000_000)
    
    print(json.dumps(results, indent=2))
    
    # Save to JSON file
    with open("two_truths_lie_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Results saved to two_truths_lie_results.json")