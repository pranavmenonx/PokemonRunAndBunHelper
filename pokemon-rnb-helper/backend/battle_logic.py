from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
import copy

# Type effectiveness chart
TYPE_CHART = {
    "Normal": {"Ghost": 0, "Rock": 0.5, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water": {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5},
    "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0, "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison": {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2},
    "Ground": {"Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2, "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2},
    "Flying": {"Electric": 0.5, "Grass": 2, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0, "Steel": 0.5},
    "Bug": {"Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Dark": 2, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Bug": 2, "Steel": 0.5},
    "Ghost": {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark": {"Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5, "Fairy": 0.5},
    "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2, "Rock": 2, "Steel": 0.5, "Fairy": 2},
    "Fairy": {"Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2, "Dark": 2, "Steel": 0.5}
}

@dataclass
class BattleAction:
    """Represents a single action in battle."""
    action_type: str  # "move" or "switch"
    user: str  # "player" or "opponent"
    index: int  # move index or pokemon index
    target_index: Optional[int] = None  # for multi-target moves

@dataclass
class Turn:
    """Represents a single turn in battle."""
    player_action: Optional[BattleAction]
    opponent_action: Optional[BattleAction]
    results: List[Dict]  # List of action results in order of execution

def calculate_type_effectiveness(move_type: str, defender_types: List[str]) -> float:
    """Calculate type effectiveness of a move against a Pokémon."""
    multiplier = 1.0
    for def_type in defender_types:
        if move_type in TYPE_CHART and def_type in TYPE_CHART[move_type]:
            multiplier *= TYPE_CHART[move_type][def_type]
    return multiplier

def calculate_damage(move: Dict, attacker: Dict, defender: Dict, weather: Optional[str] = None) -> Tuple[int, int]:
    """Calculate damage range (min, max) for a move."""
    if move["power"] is None:
        return (0, 0)
    
    # Get base power and relevant stats
    base_power = move["power"]
    
    # Apply STAB (Same Type Attack Bonus)
    stab = 1.5 if move["type"] in attacker["types"] else 1.0
    
    # Calculate type effectiveness
    type_effect = calculate_type_effectiveness(move["type"], defender["types"])
    
    # Get attack and defense stats
    if move["category"] == "Physical":
        atk = attacker["stats"]["Attack"]
        def_ = defender["stats"]["Defense"]
    else:  # Special
        atk = attacker["stats"]["Sp. Attack"]
        def_ = defender["stats"]["Sp. Defense"]
    
    # Basic damage formula
    # ((2 * Level / 5 + 2) * BasePower * Attack / Defense / 50 + 2) * Modifiers
    base_damage = ((2 * attacker["level"] / 5 + 2) * base_power * atk / def_ / 50 + 2)
    
    # Apply modifiers
    modifiers = stab * type_effect
    
    # Weather effects
    if weather:
        if weather == "Sun" and move["type"] == "Fire":
            modifiers *= 1.5
        elif weather == "Rain" and move["type"] == "Water":
            modifiers *= 1.5
        
    # Calculate damage range (85-100% random factor)
    min_damage = math.floor(base_damage * modifiers * 0.85)
    max_damage = math.floor(base_damage * modifiers)
    
    return (min_damage, max_damage)

def evaluate_position(battle_state: Dict) -> float:
    """Evaluate the current battle position, returns a score between -1 and 1."""
    player_score = 0
    opponent_score = 0
    
    # Calculate total remaining HP percentage for each team
    for pokemon in battle_state["player_team"]["pokemon"]:
        max_hp = pokemon["stats"]["HP"]
        if "current_hp" not in pokemon:
            pokemon["current_hp"] = max_hp
        current_hp = pokemon["current_hp"]
        player_score += current_hp / max_hp
    
    for pokemon in battle_state["opponent_team"]["pokemon"]:
        max_hp = pokemon["stats"]["HP"]
        if "current_hp" not in pokemon:
            pokemon["current_hp"] = max_hp
        current_hp = pokemon["current_hp"]
        opponent_score += current_hp / max_hp
    
    # Normalize scores
    player_score /= len(battle_state["player_team"]["pokemon"])
    opponent_score /= len(battle_state["opponent_team"]["pokemon"])
    
    return player_score - opponent_score

def find_best_move(battle_state: Dict, depth: int = 3) -> List[BattleAction]:
    """Find the best sequence of moves using minimax with alpha-beta pruning."""
    def minimax(state: Dict, depth: int, alpha: float, beta: float, is_maximizing: bool) -> Tuple[float, Optional[BattleAction]]:
        if depth == 0:
            return evaluate_position(state), None
        
        best_action = None
        if is_maximizing:
            max_eval = float('-inf')
            # Try each possible move
            active_pokemon = state["player_team"]["pokemon"][state["player_team"]["active_pokemon_index"]]
            for i, move in enumerate(active_pokemon["moves"]):
                # Simulate move
                new_state = simulate_move(state, BattleAction("move", "player", i))
                eval_, _ = minimax(new_state, depth - 1, alpha, beta, False)
                
                if eval_ > max_eval:
                    max_eval = eval_
                    best_action = BattleAction("move", "player", i)
                
                alpha = max(alpha, eval_)
                if beta <= alpha:
                    break
            
            return max_eval, best_action
        else:
            min_eval = float('inf')
            # Try each possible opponent move
            active_pokemon = state["opponent_team"]["pokemon"][state["opponent_team"]["active_pokemon_index"]]
            for i, move in enumerate(active_pokemon["moves"]):
                # Simulate move
                new_state = simulate_move(state, BattleAction("move", "opponent", i))
                eval_, _ = minimax(new_state, depth - 1, alpha, beta, True)
                
                if eval_ < min_eval:
                    min_eval = eval_
                    best_action = BattleAction("move", "opponent", i)
                
                beta = min(beta, eval_)
                if beta <= alpha:
                    break
            
            return min_eval, best_action
    
    # Start minimax search
    best_moves = []
    current_state = battle_state.copy()
    
    for _ in range(depth):
        _, best_action = minimax(current_state, depth, float('-inf'), float('inf'), True)
        if best_action:
            best_moves.append(best_action)
            current_state = simulate_move(current_state, best_action)
    
    return best_moves

def simulate_move(battle_state: Dict, action: BattleAction) -> Dict:
    """Simulate a move and return the resulting battle state."""
    # Deep copy the battle state
    new_state = copy.deepcopy(battle_state)
    
    if action.action_type == "move":
        attacker_team = "player_team" if action.user == "player" else "opponent_team"
        defender_team = "opponent_team" if action.user == "player" else "player_team"
        
        attacker = new_state[attacker_team]["pokemon"][new_state[attacker_team]["active_pokemon_index"]]
        defender = new_state[defender_team]["pokemon"][new_state[defender_team]["active_pokemon_index"]]
        
        move = attacker["moves"][action.index]
        
        # Calculate and apply damage
        min_damage, max_damage = calculate_damage(move, attacker, defender, new_state.get("weather"))
        # For simulation, use average damage
        damage = (min_damage + max_damage) // 2
        
        # Initialize current_hp if not set
        if "current_hp" not in defender:
            defender["current_hp"] = defender["stats"]["HP"]
        
        # Update defender's HP
        defender["current_hp"] = max(0, defender["current_hp"] - damage)
        
        # Update stats HP to match current_hp for compatibility
        defender["stats"]["HP"] = defender["current_hp"]
    
    return new_state

def determine_best_action(battle_state: Dict, user: str) -> Optional[BattleAction]:
    """Determine the best action for a player."""
    team_key = "player_team" if user == "player" else "opponent_team"
    active_pokemon = battle_state[team_key]["pokemon"][battle_state[team_key]["active_pokemon_index"]]
    
    print(f"\nDetermining action for {user}'s {active_pokemon['name']}")
    print(f"Current HP: {active_pokemon['stats'].get('HP', 0)}")
    
    # Check if current Pokémon is fainted
    if active_pokemon["stats"].get("HP", 0) <= 0:
        print(f"{active_pokemon['name']} is fainted, looking for a switch")
        # Find a valid switch-in
        for i, pokemon in enumerate(battle_state[team_key]["pokemon"]):
            if pokemon["stats"].get("HP", 0) > 0 and i != battle_state[team_key]["active_pokemon_index"]:
                print(f"Found valid switch to {pokemon['name']}")
                return BattleAction(action_type="switch", user=user, index=i)
        print("No valid switches found!")
        return None
    
    # Evaluate each move
    best_move_score = float('-inf')
    best_move_index = 0
    
    for i, move in enumerate(active_pokemon["moves"]):
        score = evaluate_move(move, battle_state, user)
        if score > best_move_score:
            best_move_score = score
            best_move_index = i
    
    # Check if switching would be better
    best_switch_score = evaluate_switches(battle_state, user)
    if best_switch_score > best_move_score + 20:  # Threshold to prefer switching
        for i, pokemon in enumerate(battle_state[team_key]["pokemon"]):
            if pokemon["stats"].get("HP", 0) > 0 and i != battle_state[team_key]["active_pokemon_index"]:
                print(f"Switching to {pokemon['name']} is better")
                return BattleAction(action_type="switch", user=user, index=i)
    
    print(f"Using move {active_pokemon['moves'][best_move_index]['name']}")
    return BattleAction(action_type="move", user=user, index=best_move_index)

def evaluate_move(move: Dict, battle_state: Dict, user: str) -> float:
    """Evaluate how good a move would be in the current situation."""
    score = 0.0
    team_key = "player_team" if user == "player" else "opponent_team"
    opp_key = "opponent_team" if user == "player" else "player_team"
    
    attacker = battle_state[team_key]["pokemon"][battle_state[team_key]["active_pokemon_index"]]
    defender = battle_state[opp_key]["pokemon"][battle_state[opp_key]["active_pokemon_index"]]
    
    # Calculate damage
    min_damage, max_damage = calculate_damage(move, attacker, defender, battle_state.get("weather"))
    avg_damage = (min_damage + max_damage) / 2
    
    # Base score on damage percentage
    if defender["stats"]["HP"] > 0:
        damage_percent = avg_damage / defender["stats"]["HP"]
        score += damage_percent * 100
    
    # Bonus for STAB moves
    if move["type"] in attacker["types"]:
        score += 20
    
    # Bonus for super effective moves
    effectiveness = calculate_type_effectiveness(move["type"], defender["types"])
    if effectiveness > 1:
        score += 30 * effectiveness
    
    # Bonus for priority moves when at low HP
    if move.get("priority", 0) > 0 and attacker["stats"]["HP"] < attacker["stats"]["HP"] * 0.3:
        score += 40
    
    return score

def evaluate_switches(battle_state: Dict, user: str) -> float:
    """Evaluate how beneficial switching would be."""
    team_key = "player_team" if user == "player" else "opponent_team"
    opp_key = "opponent_team" if user == "player" else "player_team"
    
    current_pokemon = battle_state[team_key]["pokemon"][battle_state[team_key]["active_pokemon_index"]]
    opponent = battle_state[opp_key]["pokemon"][battle_state[opp_key]["active_pokemon_index"]]
    
    # Base switch score
    best_score = 0.0
    
    # Check each potential switch-in
    for pokemon in battle_state[team_key]["pokemon"]:
        if pokemon["stats"]["HP"] <= 0:
            continue
        
        score = 0.0
        
        # Resist opponent's moves
        for move in opponent["moves"]:
            effectiveness = calculate_type_effectiveness(move["type"], pokemon["types"])
            if effectiveness < 1:
                score += 30 * (1 - effectiveness)
        
        # Good matchup against opponent's types
        for type_ in pokemon["types"]:
            effectiveness = calculate_type_effectiveness(type_, opponent["types"])
            if effectiveness > 1:
                score += 20 * effectiveness
        
        best_score = max(best_score, score)
    
    return best_score

def sort_actions(actions: List[BattleAction], battle_state: Dict) -> List[BattleAction]:
    """Sort actions by priority and speed."""
    def get_action_priority(action: BattleAction) -> Tuple[int, int]:
        if not action:
            return (-999, -999)
        
        team_key = "player_team" if action.user == "player" else "opponent_team"
        pokemon = battle_state[team_key]["pokemon"][battle_state[team_key]["active_pokemon_index"]]
        
        if action.action_type == "switch":
            return (6, pokemon["stats"]["Speed"])  # Switches happen before moves
        else:
            move = pokemon["moves"][action.index]
            return (move.get("priority", 0), pokemon["stats"]["Speed"])
    
    return sorted(actions, key=get_action_priority, reverse=True)

def apply_action(battle_state: Dict, action: BattleAction) -> Dict:
    """Apply an action and return the results."""
    if not action:
        return {
            "action_desc": "No action",
            "effects": [],
            "log": ["No valid action available"],
            "new_state": battle_state
        }
    
    new_state = battle_state.copy()  # Deep copy needed in real implementation
    effects = []
    log = []
    
    if action.action_type == "switch":
        result = apply_switch(new_state, action)
    else:
        result = apply_move(new_state, action)
    
    return {
        "action_desc": result["desc"],
        "effects": result["effects"],
        "log": result["log"],
        "new_state": result["new_state"]
    }

def apply_switch(battle_state: Dict, action: BattleAction) -> Dict:
    """Apply a switch action."""
    print(f"\nApplying switch for {action.user}")
    
    team_key = "player_team" if action.user == "player" else "opponent_team"
    current_pokemon = battle_state[team_key]["pokemon"][battle_state[team_key]["active_pokemon_index"]]
    new_pokemon = battle_state[team_key]["pokemon"][action.index]
    
    # Check if the switch is valid
    if new_pokemon["stats"].get("HP", 0) <= 0:
        print(f"Cannot switch to fainted {new_pokemon['name']}")
        return {
            "action_desc": "Invalid switch",
            "effects": [],
            "log": [f"Cannot switch to fainted {new_pokemon['name']}"]
        }
    
    if action.index == battle_state[team_key]["active_pokemon_index"]:
        print(f"Cannot switch to already active {new_pokemon['name']}")
        return {
            "action_desc": "Invalid switch",
            "effects": [],
            "log": [f"Cannot switch to already active {new_pokemon['name']}"]
        }
    
    # Perform the switch
    battle_state[team_key]["active_pokemon_index"] = action.index
    print(f"Switched from {current_pokemon['name']} to {new_pokemon['name']}")
    
    return {
        "action_desc": f"Switched to {new_pokemon['name']}",
        "effects": ["switch"],
        "log": [f"{current_pokemon['name']} was withdrawn!", f"Go! {new_pokemon['name']}!"]
    }

def apply_move(battle_state: Dict, action: BattleAction) -> Dict:
    """Apply a move action."""
    print(f"\nApplying move for {action.user}")
    
    team_key = "player_team" if action.user == "player" else "opponent_team"
    opp_key = "opponent_team" if action.user == "player" else "player_team"
    
    attacker = battle_state[team_key]["pokemon"][battle_state[team_key]["active_pokemon_index"]]
    defender = battle_state[opp_key]["pokemon"][battle_state[opp_key]["active_pokemon_index"]]
    
    # If either Pokémon is fainted, return without applying move
    if attacker["stats"].get("HP", 0) <= 0:
        print(f"{attacker['name']} is fainted and cannot move")
        return {
            "action_desc": "Invalid move",
            "effects": [],
            "log": [f"{attacker['name']} cannot move because it is fainted"]
        }
    
    if defender["stats"].get("HP", 0) <= 0:
        print(f"{defender['name']} is already fainted")
        return {
            "action_desc": "Invalid move",
            "effects": [],
            "log": [f"{defender['name']} is already fainted"]
        }
    
    move = attacker["moves"][action.index]
    print(f"Using move {move['name']}")
    
    # Calculate damage
    min_damage, max_damage = calculate_damage(move, attacker, defender, battle_state.get("weather"))
    damage = (min_damage + max_damage) // 2  # Use average damage for simulation
    
    # Apply damage
    old_hp = defender["stats"].get("HP", defender["stats"].get("hp", 0))
    defender["stats"]["HP"] = max(0, old_hp - damage)
    actual_damage = old_hp - defender["stats"]["HP"]
    
    # Generate battle log
    effectiveness = calculate_type_effectiveness(move["type"], defender["types"])
    effectiveness_text = ""
    if effectiveness > 1:
        effectiveness_text = "It's super effective!"
    elif effectiveness < 1:
        effectiveness_text = "It's not very effective..."
    elif effectiveness == 0:
        effectiveness_text = "It doesn't affect the opposing Pokémon..."
    
    log = [
        f"{attacker['name']} used {move['name']}!",
        effectiveness_text if effectiveness_text else None,
        f"Dealt {actual_damage} damage!" if actual_damage > 0 else None
    ]
    log = [msg for msg in log if msg]
    
    if defender["stats"]["HP"] <= 0:
        log.append(f"{defender['name']} fainted!")
    
    return {
        "action_desc": f"{attacker['name']} used {move['name']}",
        "effects": [effectiveness_text] if effectiveness_text else [],
        "log": log
    }

def apply_end_turn_effects(battle_state: Dict) -> Dict:
    """Apply end of turn effects like weather, status conditions, etc."""
    # For now, just return the state unchanged
    return {
        "effects": [],
        "log": [],
        "new_state": battle_state
    }

def simulate_turn(battle_state: Dict) -> Dict:
    """Simulate one full turn of battle."""
    print("\nStarting turn simulation...")
    
    # Deep copy the battle state to avoid modifying the original
    battle_state = copy.deepcopy(battle_state)
    print("Created deep copy of battle state")
    
    # Initialize current_hp for all Pokemon if not set
    for team in ["player_team", "opponent_team"]:
        for pokemon in battle_state[team]["pokemon"]:
            if "current_hp" not in pokemon:
                pokemon["current_hp"] = pokemon["stats"]["HP"]
                print(f"Initialized current_hp for {pokemon['name']}: {pokemon['current_hp']}")
    
    # Get active Pokemon
    player_active = battle_state["player_team"]["pokemon"][battle_state["player_team"]["active_pokemon_index"]]
    opponent_active = battle_state["opponent_team"]["pokemon"][battle_state["opponent_team"]["active_pokemon_index"]]
    print(f"Active Pokemon - Player: {player_active['name']}, Opponent: {opponent_active['name']}")
    
    # Determine actions for both sides
    print("Determining actions...")
    player_action = determine_best_action(battle_state, "player")
    opponent_action = determine_best_action(battle_state, "opponent")
    print(f"Player action: {player_action}")
    print(f"Opponent action: {opponent_action}")
    
    # Execute actions in order of priority
    actions = [
        (player_action, "player"),
        (opponent_action, "opponent")
    ]
    actions.sort(key=lambda x: get_action_priority(x[0]))
    print(f"Sorted actions: {actions}")
    
    turn_log = []
    for action, user in actions:
        print(f"\nExecuting action for {user}...")
        # Skip if the user's active Pokemon has fainted
        active_pokemon = player_active if user == "player" else opponent_active
        if active_pokemon["current_hp"] <= 0:
            print(f"Skipping action - {active_pokemon['name']} has fainted")
            continue
            
        # Apply the action
        print(f"Applying action: {action}")
        try:
            result = apply_move(battle_state, action)
            print(f"Action result: {result}")
            turn_log.extend(result["log"])
            
            # Check if either side has fainted
            if "faint" in result["effects"]:
                print("Pokemon fainted - ending turn")
                break
        except Exception as e:
            print(f"Error applying action: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    # Apply end of turn effects here (weather, status, etc.)
    print("Turn simulation complete")
    
    return {
        "log": turn_log,
        "new_state": battle_state
    } 