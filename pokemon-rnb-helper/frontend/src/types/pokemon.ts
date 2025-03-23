export interface Pokemon {
  name: string;
  types: string[];
  stats: {
    HP: number;
    Attack: number;
    Defense: number;
    'Sp. Attack': number;
    'Sp. Defense': number;
    Speed: number;
  };
  moves: {
    name: string;
    type: string;
    power: number | null;
    accuracy: number | null;
    category: string;
    priority: number;
    effects: string;
  }[];
  ability: string;
  item?: string;
  level: number;
  status: string | null;
} 