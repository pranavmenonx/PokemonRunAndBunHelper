from typing import Dict, List, Optional, Tuple
import re
import requests
import json

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

def get_pokemon_data(name: str) -> Dict:
    """Get Pokemon data from PokeAPI."""
    # Clean up the name for PokeAPI (lowercase, no special chars)
    clean_name = name.lower().split('@')[0].strip()  # Remove items
    
    try:
        response = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{clean_name}")
        if response.ok:
            data = response.json()
            return {
                "types": [t["type"]["name"].capitalize() for t in data["types"]],
                "base_stats": {
                    "HP": data["stats"][0]["base_stat"],
                    "Attack": data["stats"][1]["base_stat"],
                    "Defense": data["stats"][2]["base_stat"],
                    "Sp. Attack": data["stats"][3]["base_stat"],
                    "Sp. Defense": data["stats"][4]["base_stat"],
                    "Speed": data["stats"][5]["base_stat"]
                }
            }
        else:
            raise ValueError(f"Pokemon '{name}' not found")
    except Exception as e:
        print(f"Error fetching Pokemon data: {str(e)}")
        raise ValueError(f"Pokemon '{name}' not found")

def get_move_data(move_line: str) -> Dict:
    """Get move data from the move line."""
    # Clean up the move name by removing leading dashes and spaces
    move_name = move_line.strip('- ').strip()
    
    try:
        # Get move data from PokeAPI
        url = f"https://pokeapi.co/api/v2/move/{move_name.lower().replace(' ', '-')}/"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return {
                "name": move_name,
                "type": data["type"]["name"].capitalize(),
                "power": data["power"],
                "accuracy": data["accuracy"],
                "pp": data["pp"],
                "category": data["damage_class"]["name"].capitalize(),
                "priority": data["priority"],
                "effects": data["effect_entries"][0]["short_effect"] if data["effect_entries"] else None
            }
    except Exception as e:
        print(f"Error fetching move data for {move_name}: {str(e)}")
    
    # Fallback to basic move data if API call fails
    return {
        "name": move_name,
        "type": "Normal",  # Default type
        "power": None,
        "accuracy": None,
        "pp": 20,  # Default PP
        "category": "Physical",  # Default category
        "priority": 0,
        "effects": None
    }

def parse_showdown_export(export: str) -> Dict:
    """Parse a Pokemon Showdown export string into a Pokemon object."""
    lines = export.strip().split('\n')
    
    if not lines:
        raise ValueError("Empty export string")
    
    # Initialize default values
    pokemon_data = {
        "name": "",
        "types": ["Normal"],
        "ability": "",
        "level": 100,
        "moves": [],
        "stats": {
            "HP": 0,
            "Attack": 0,
            "Defense": 0,
            "Sp. Attack": 0,
            "Sp. Defense": 0,
            "Speed": 0
        },
        "ivs": {
            "HP": 31,  # Default max IVs
            "Attack": 31,
            "Defense": 31,
            "Sp. Attack": 31,
            "Sp. Defense": 31,
            "Speed": 31
        },
        "stat_stages": {
            "Attack": 0,
            "Defense": 0,
            "Sp. Attack": 0,
            "Sp. Defense": 0,
            "Speed": 0,
            "Accuracy": 0,
            "Evasion": 0
        },
        "item": None,
        "status": None
    }
    
    # Parse first line for name and item
    if lines:
        full_name = lines[0].strip()
        if '@' in full_name:
            name, item = full_name.split('@')
            pokemon_data["name"] = name.strip()
            pokemon_data["item"] = item.strip()
        else:
            pokemon_data["name"] = full_name

        # Get Pokemon data from PokeAPI
        api_data = get_pokemon_data(pokemon_data["name"])
        pokemon_data["types"] = api_data["types"]
        base_stats = api_data["base_stats"]
    
    nature_multipliers = {}
    
    for line in lines[1:]:  # Skip the first line (name)
        line = line.strip()
        
        if line.startswith("Ability: "):
            pokemon_data["ability"] = line.replace("Ability: ", "")
        
        elif line.startswith("Level: "):
            pokemon_data["level"] = int(line.replace("Level: ", ""))
        
        elif line.endswith("Nature"):
            nature = line.replace(" Nature", "")
            nature_multipliers = get_nature_multipliers(nature)
        
        elif line.startswith("IVs: "):
            iv_string = line.replace("IVs: ", "")
            iv_parts = iv_string.split(" / ")
            
            # Map Showdown stat names to our stat names
            stat_map = {
                "HP": "HP",
                "Atk": "Attack",
                "Def": "Defense",
                "SpA": "Sp. Attack",
                "SpD": "Sp. Defense",
                "Spe": "Speed"
            }
            
            for part in iv_parts:
                try:
                    value, stat_abbr = part.split(" ", 1)  # Split on first space
                    iv = int(value)
                    # Find the matching stat name
                    for abbr, full_name in stat_map.items():
                        if stat_abbr == abbr:
                            pokemon_data["ivs"][full_name] = iv
                            break
                except (ValueError, KeyError) as e:
                    print(f"Error parsing IV: {part} - {e}")
                    continue
        
        # Parse moves
        elif line and not line.startswith(("Ability:", "Level:", "IVs:", "EVs:", "Shiny:", "Gigantamax:", "Tera Type:")):
            if not line.endswith("Nature"):
                move_data = get_move_data(line)
                pokemon_data["moves"].append(move_data)
    
    # Calculate final stats using base stats, IVs, and nature
    for stat in pokemon_data["stats"]:
        if stat == "HP":
            pokemon_data["stats"][stat] = calculate_hp(
                base_stats[stat],
                pokemon_data["ivs"][stat],
                pokemon_data["level"]
            )
        else:
            base = base_stats[stat]
            iv = pokemon_data["ivs"][stat]
            stat_value = calculate_stat(base, iv, pokemon_data["level"])
            
            # Apply nature multiplier if applicable
            if stat == "Attack" and "Atk" in nature_multipliers:
                stat_value = int(stat_value * nature_multipliers["Atk"])
            elif stat == "Defense" and "Def" in nature_multipliers:
                stat_value = int(stat_value * nature_multipliers["Def"])
            elif stat == "Sp. Attack" and "SpA" in nature_multipliers:
                stat_value = int(stat_value * nature_multipliers["SpA"])
            elif stat == "Sp. Defense" and "SpD" in nature_multipliers:
                stat_value = int(stat_value * nature_multipliers["SpD"])
            elif stat == "Speed" and "Spe" in nature_multipliers:
                stat_value = int(stat_value * nature_multipliers["Spe"])
            
            pokemon_data["stats"][stat] = stat_value
    
    return pokemon_data

def calculate_hp(base: int, iv: int, level: int) -> int:
    """Calculate HP stat."""
    return ((2 * base + iv) * level // 100) + level + 10

def calculate_stat(base: int, iv: int, level: int) -> int:
    """Calculate non-HP stat."""
    return ((2 * base + iv) * level // 100) + 5

def get_nature_multipliers(nature: str) -> Dict[str, float]:
    """Get stat multipliers for a given nature."""
    nature_effects = {
        "Hardy": {},
        "Lonely": {"Atk": 1.1, "Def": 0.9},
        "Brave": {"Atk": 1.1, "Spe": 0.9},
        "Adamant": {"Atk": 1.1, "SpA": 0.9},
        "Naughty": {"Atk": 1.1, "SpD": 0.9},
        "Bold": {"Def": 1.1, "Atk": 0.9},
        "Docile": {},
        "Relaxed": {"Def": 1.1, "Spe": 0.9},
        "Impish": {"Def": 1.1, "SpA": 0.9},
        "Lax": {"Def": 1.1, "SpD": 0.9},
        "Timid": {"Spe": 1.1, "Atk": 0.9},
        "Hasty": {"Spe": 1.1, "Def": 0.9},
        "Serious": {},
        "Jolly": {"Spe": 1.1, "SpA": 0.9},
        "Naive": {"Spe": 1.1, "SpD": 0.9},
        "Modest": {"SpA": 1.1, "Atk": 0.9},
        "Mild": {"SpA": 1.1, "Def": 0.9},
        "Quiet": {"SpA": 1.1, "Spe": 0.9},
        "Bashful": {},
        "Rash": {"SpA": 1.1, "SpD": 0.9},
        "Calm": {"SpD": 1.1, "Atk": 0.9},
        "Gentle": {"SpD": 1.1, "Def": 0.9},
        "Sassy": {"SpD": 1.1, "Spe": 0.9},
        "Careful": {"SpD": 1.1, "SpA": 0.9},
        "Quirky": {}
    }
    return nature_effects.get(nature, {}) 