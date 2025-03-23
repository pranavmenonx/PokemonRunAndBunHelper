from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, conlist
from typing import List, Optional, Dict, Union
from enum import Enum
from showdown_parser import parse_showdown_export
from battle_logic import (
    find_best_move,
    simulate_move,
    determine_best_action,
    BattleAction,
    apply_move,
    evaluate_position,
    sort_actions,
    calculate_damage,
    evaluate_move,
    evaluate_switches,
    calculate_type_effectiveness,
    apply_switch
)
import copy
import traceback

app = FastAPI(title="Pokemon Run and Bun Helper")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Type(str, Enum):
    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    ELECTRIC = "Electric"
    GRASS = "Grass"
    ICE = "Ice"
    FIGHTING = "Fighting"
    POISON = "Poison"
    GROUND = "Ground"
    FLYING = "Flying"
    PSYCHIC = "Psychic"
    BUG = "Bug"
    ROCK = "Rock"
    GHOST = "Ghost"
    DRAGON = "Dragon"
    DARK = "Dark"
    STEEL = "Steel"
    FAIRY = "Fairy"

class Move(BaseModel):
    name: str
    type: Type
    power: Optional[int]
    accuracy: Optional[int]
    pp: int
    category: str  # Physical, Special, or Status
    priority: int = 0
    effects: Optional[str]

class Pokemon(BaseModel):
    name: str
    types: List[Type]
    ability: str
    moves: List[Move]
    stats: Dict[str, int]  # HP, Attack, Defense, Sp. Attack, Sp. Defense, Speed
    level: int
    item: Optional[str]
    status: Optional[str]
    current_hp: Optional[int] = None  # Current HP for battle simulation
    stat_stages: Dict[str, int] = {}  # Attack, Defense, etc. stages (-6 to +6)
    position: Optional[int] = None  # Position in team (1-6)

class Team(BaseModel):
    pokemon: conlist(Pokemon, min_items=1, max_items=6)  # Ensures team size between 1 and 6
    active_pokemon_index: int = 0

class BattleState(BaseModel):
    player_team: Team
    opponent_team: Team
    weather: Optional[str]
    terrain: Optional[str]
    screens: List[str] = []  # Light Screen, Reflect, etc.
    hazards: List[str] = []  # Stealth Rock, Spikes, etc.

class ShowdownExport(BaseModel):
    export_text: str
    team_position: Optional[int] = None  # Position in team (1-6)
    is_opponent: bool = False  # Whether this is an opponent's Pokemon

class BattleStrategy(BaseModel):
    turns: List[Dict] = []  # List of turns with actions and results
    winner: Optional[str] = None  # "player" or "opponent"
    battle_log: List[str] = []  # Detailed battle log

@app.get("/")
async def root():
    return {"message": "Pokemon Run and Bun Helper API"}

@app.post("/parse-showdown")
async def parse_showdown(export: ShowdownExport):
    try:
        print(f"Received export text:\n{export.export_text}")  # Debug log
        pokemon_data = parse_showdown_export(export.export_text)
        print(f"Parsed Pokemon data:\n{pokemon_data}")  # Debug log
        
        # Set current HP to max HP initially
        pokemon_data["current_hp"] = pokemon_data["stats"]["HP"]
        
        if export.team_position is not None:
            pokemon_data["position"] = export.team_position
        return pokemon_data
    except Exception as e:
        print(f"Error parsing export: {str(e)}")  # Debug log
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/calculate-battle-strategy")
async def calculate_battle_strategy(battle_state: BattleState) -> BattleStrategy:
    """Calculate the optimal battle strategy."""
    try:
        print("\nStarting battle simulation...")
        
        # Convert BattleState to dict for easier manipulation
        current_state = battle_state.dict()
        
        # Initialize battle tracking
        turns = []
        battle_log = []
        turn_number = 1
        
        while turn_number <= 50:  # Maximum 50 turns to prevent infinite loops
            print(f"\nTurn {turn_number}")
            
            # Check if either side has no more usable Pokémon
            player_alive = any(p["stats"].get("HP", 0) > 0 for p in current_state["player_team"]["pokemon"])
            opponent_alive = any(p["stats"].get("HP", 0) > 0 for p in current_state["opponent_team"]["pokemon"])
            
            print(f"Player team alive: {player_alive}")
            print(f"Opponent team alive: {opponent_alive}")
            
            if not player_alive:
                return BattleStrategy(
                    turns=turns,
                    winner="opponent",
                    battle_log=battle_log + ["Player has no more usable Pokémon!"]
                )
            elif not opponent_alive:
                return BattleStrategy(
                    turns=turns,
                    winner="player",
                    battle_log=battle_log + ["Opponent has no more usable Pokémon!"]
                )
            
            # Simulate the turn
            print("Simulating turn...")
            turn_result = simulate_turn(current_state, turn_number)
            
            # Update battle log
            battle_log.extend(turn_result["log"])
            
            # Check for winner
            if turn_result.get("winner"):
                return BattleStrategy(
                    turns=turns,
                    winner=turn_result["winner"],
                    battle_log=battle_log
                )
            
            # Update state and continue
            current_state = turn_result["state"]
            turns.append(turn_result)
            turn_number += 1
        
        # If we reach here, it's a draw
        print("Battle reached 50 turns. Ending in a draw.")
        return BattleStrategy(
            turns=turns,
            winner=None,
            battle_log=battle_log + ["Battle ended in a draw after 50 turns."]
        )
    
    except Exception as e:
        print(f"Error in battle simulation: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def simulate_turn(battle_state: Dict, turn_number: int) -> Dict:
    """Simulate one full turn of battle."""
    print(f"\nSimulating turn {turn_number}...")
    
    # Create a deep copy of the battle state to avoid modifying the original
    current_state = copy.deepcopy(battle_state)
    
    # Get actions for both sides
    print("Determining player action...")
    player_action = determine_best_action(current_state, "player")
    if not player_action:
        print("Player has no valid actions!")
        return {
            "winner": "opponent",
            "log": ["Player has no valid moves or switches!"]
        }
    
    print("Determining opponent action...")
    opponent_action = determine_best_action(current_state, "opponent")
    if not opponent_action:
        print("Opponent has no valid actions!")
        return {
            "winner": "player",
            "log": ["Opponent has no valid moves or switches!"]
        }
    
    # Sort actions by priority (switches before moves)
    actions = []
    if player_action.action_type == "switch":
        actions.append(player_action)
    if opponent_action.action_type == "switch":
        actions.append(opponent_action)
    
    # Add move actions after switches
    if player_action.action_type == "move":
        actions.append(player_action)
    if opponent_action.action_type == "move":
        actions.append(opponent_action)
    
    turn_log = []
    
    # Execute actions in order
    for action in actions:
        if action.action_type == "move":
            result = apply_move(current_state, action)
        else:  # switch
            result = apply_switch(current_state, action)
        
        turn_log.extend(result["log"])
        
        # Check if either side has no more usable Pokémon
        player_alive = any(p["stats"].get("HP", 0) > 0 for p in current_state["player_team"]["pokemon"])
        opponent_alive = any(p["stats"].get("HP", 0) > 0 for p in current_state["opponent_team"]["pokemon"])
        
        if not player_alive:
            return {
                "winner": "opponent",
                "log": turn_log + ["Player has no more usable Pokémon!"]
            }
        elif not opponent_alive:
            return {
                "winner": "player",
                "log": turn_log + ["Opponent has no more usable Pokémon!"]
            }
    
    return {
        "winner": None,
        "log": turn_log,
        "state": current_state
    }

@app.post("/calculate-ai-move")
async def calculate_ai_move(battle_state: BattleState):
    # TODO: Implement AI move calculation logic
    return {"moves": []}

@app.post("/predict-switch")
async def predict_switch(battle_state: BattleState):
    # TODO: Implement switch prediction logic
    return {"switches": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 