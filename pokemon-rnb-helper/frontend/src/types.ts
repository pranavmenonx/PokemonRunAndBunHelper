export type Type =
  | "Normal"
  | "Fire"
  | "Water"
  | "Electric"
  | "Grass"
  | "Ice"
  | "Fighting"
  | "Poison"
  | "Ground"
  | "Flying"
  | "Psychic"
  | "Bug"
  | "Rock"
  | "Ghost"
  | "Dragon"
  | "Dark"
  | "Steel"
  | "Fairy";

export interface Move {
  name: string;
  type: Type;
  power?: number;
  accuracy?: number;
  pp: number;
  category: string;
  priority?: number;
  effects?: string;
}

export interface Pokemon {
  name: string;
  types: Type[];
  ability: string;
  moves: Move[];
  stats: {
    HP: number;
    Attack: number;
    Defense: number;
    "Sp. Attack": number;
    "Sp. Defense": number;
    Speed: number;
  };
  level: number;
  item?: string;
  status?: string;
  stat_stages: Record<string, number>;
  position?: number | null;
}

export interface Team {
  pokemon: Pokemon[];
  active_pokemon_index: number;
}

export interface BattleState {
  player_team: Team;
  opponent_team: Team;
  weather?: string;
  terrain?: string;
  screens: string[];
  hazards: string[];
} 