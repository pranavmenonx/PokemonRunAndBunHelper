from typing import List, Dict, Optional
from main import Pokemon, Move, BattleState
import random

def calculate_damage(move: Move, attacker: Pokemon, defender: Pokemon, weather: Optional[str] = None) -> float:
    # Basic damage calculation
    if move.power is None:
        return 0.0
    
    # Get attack and defense stats based on move category
    if move.category == "Physical":
        attack = attacker.stats["Attack"] * get_stat_stage_multiplier(attacker.stat_stages.get("Attack", 0))
        defense = defender.stats["Defense"] * get_stat_stage_multiplier(defender.stat_stages.get("Defense", 0))
    else:
        attack = attacker.stats["Sp. Attack"] * get_stat_stage_multiplier(attacker.stat_stages.get("Sp. Attack", 0))
        defense = defender.stats["Sp. Defense"] * get_stat_stage_multiplier(defender.stat_stages.get("Sp. Defense", 0))
    
    # Basic damage formula
    damage = ((2 * attacker.level / 5 + 2) * move.power * attack / defense / 50 + 2)
    
    # Type effectiveness (simplified for now)
    # TODO: Implement full type effectiveness calculation
    
    return damage

def get_stat_stage_multiplier(stage: int) -> float:
    if stage >= 0:
        return (stage + 2) / 2
    return 2 / (abs(stage) + 2)

def calculate_move_score(move: Move, battle_state: BattleState) -> float:
    base_score = 6.0  # Default score for most moves
    attacker = battle_state.opponent_pokemon
    defender = battle_state.player_pokemon
    
    # Calculate if move is highest damaging
    damage = calculate_damage(move, attacker, defender, battle_state.weather)
    is_highest_damaging = True  # TODO: Compare with other moves
    
    if is_highest_damaging:
        base_score = 6.0 if random.random() < 0.8 else 8.0
    
    # Special move scoring logic based on move type
    if move.name in ["Stealth Rock", "Spikes", "Toxic Spikes"]:
        if not any(h == move.name for h in battle_state.hazards):
            base_score = 8.0 if random.random() < 0.25 else 9.0
    
    elif move.name == "Protect":
        base_score = calculate_protect_score(battle_state)
    
    elif move.name in ["Swords Dance", "Dragon Dance", "Nasty Plot"]:
        base_score = calculate_setup_move_score(move, battle_state)
    
    # Add priority move scoring
    if move.priority > 0:
        if is_threatened_by_ko(attacker, defender) and not is_faster(attacker, defender):
            base_score += 11.0
    
    return base_score

def is_threatened_by_ko(pokemon: Pokemon, opponent: Pokemon) -> bool:
    # TODO: Implement KO check logic
    return False

def is_faster(pokemon1: Pokemon, pokemon2: Pokemon) -> bool:
    return pokemon1.stats["Speed"] > pokemon2.stats["Speed"]

def calculate_protect_score(battle_state: BattleState) -> float:
    base_score = 6.0
    
    # Check for status conditions that encourage protecting
    if battle_state.opponent_pokemon.status in ["Poison", "Burn", "Curse"]:
        base_score -= 2.0
    
    if battle_state.player_pokemon.status in ["Poison", "Burn", "Curse"]:
        base_score += 1.0
    
    return base_score

def calculate_setup_move_score(move: Move, battle_state: BattleState) -> float:
    base_score = 6.0
    attacker = battle_state.opponent_pokemon
    defender = battle_state.player_pokemon
    
    # Don't setup if threatened with KO
    if is_threatened_by_ko(attacker, defender):
        return -20.0
    
    # Bonus if opponent is incapacitated
    if defender.status in ["Frozen", "Sleep"]:
        base_score += 3.0
    
    return base_score

def predict_switch(battle_state: BattleState, opponent_team: List[Pokemon]) -> Dict[Pokemon, float]:
    scores = {}
    player_pokemon = battle_state.player_pokemon
    
    for pokemon in opponent_team:
        score = 0.0
        
        # Base scoring from Post-KO Switch-in AI document
        if is_faster(pokemon, player_pokemon):
            if can_ohko(pokemon, player_pokemon):
                score += 5.0
            else:
                score += 1.0
                if deals_more_percent_damage(pokemon, player_pokemon):
                    score += 2.0
        else:
            if can_ohko(pokemon, player_pokemon) and not can_ohko(player_pokemon, pokemon):
                score += 4.0
            elif deals_more_percent_damage(pokemon, player_pokemon):
                score += 2.0
            if can_ohko(player_pokemon, pokemon):
                score -= 1.0
        
        # Special cases
        if pokemon.name == "Ditto":
            score += 2.0
        elif pokemon.name in ["Wynaut", "Wobbuffet"]:
            if not (not is_faster(pokemon, player_pokemon) and can_ohko(player_pokemon, pokemon)):
                score += 2.0
        
        scores[pokemon] = score
    
    return scores

def can_ohko(attacker: Pokemon, defender: Pokemon) -> bool:
    # TODO: Implement OHKO check
    return False

def deals_more_percent_damage(pokemon1: Pokemon, pokemon2: Pokemon) -> bool:
    # TODO: Implement percent damage comparison
    return False 