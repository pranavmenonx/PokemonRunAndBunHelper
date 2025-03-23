import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Textarea,
  useToast,
  Text,
  Button,
} from '@chakra-ui/react';
import { BattleSimulator } from './BattleSimulator';

interface Pokemon {
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
  }[];
  ability: string;
  item?: string;
}

interface BattleAction {
  action_type: string;
  user: string;
  index: number;
  move_name?: string;
  from_pokemon?: string;
  to_pokemon?: string;
}

interface BattleResult {
  action_desc: string;
  effects: string[];
  log: string[];
}

interface BattleTurn {
  player_action: BattleAction | null;
  opponent_action: BattleAction | null;
  results: BattleResult[];
}

interface BattleResults {
  winner: string | null;
  turns: BattleTurn[];
  battle_log: string[];
}

export const BattleCalculator: React.FC = () => {
  const [playerTeamText, setPlayerTeamText] = useState('');
  const [opponentTeamText, setOpponentTeamText] = useState('');
  const [playerTeam, setPlayerTeam] = useState<Pokemon[]>([]);
  const [opponentTeam, setOpponentTeam] = useState<Pokemon[]>([]);
  const [isImporting, setIsImporting] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const toast = useToast();

  const importTeam = async (text: string, isOpponent: boolean) => {
    console.log(`Importing team for ${isOpponent ? 'opponent' : 'player'}:`, text);
    try {
      const response = await fetch('http://localhost:8001/parse-showdown', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          export_text: text,
          is_opponent: isOpponent,
        }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        console.error('Import team error:', errorData);
        throw new Error(`Failed to import team: ${errorData}`);
      }

      const pokemon = await response.json();
      console.log(`Imported Pokemon:`, pokemon);

      if (isOpponent) {
        setOpponentTeam(prev => [...prev, pokemon]);
      } else {
        setPlayerTeam(prev => [...prev, pokemon]);
      }

      toast({
        title: 'Success',
        description: `Imported ${pokemon.name} to ${isOpponent ? 'opponent' : 'your'} team`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error importing team:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to import team',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleImportTeams = async () => {
    console.log('Starting team import...');
    console.log('Player team text:', playerTeamText);
    console.log('Opponent team text:', opponentTeamText);

    setIsImporting(true);
    setPlayerTeam([]);
    setOpponentTeam([]);

    try {
      // Split teams into individual Pokémon
      const playerPokemon = playerTeamText.split('\n\n').filter(text => text.trim());
      const opponentPokemon = opponentTeamText.split('\n\n').filter(text => text.trim());

      console.log('Player Pokémon count:', playerPokemon.length);
      console.log('Opponent Pokémon count:', opponentPokemon.length);

      // Import player's team
      for (const pokemon of playerPokemon) {
        await importTeam(pokemon, false);
      }

      // Import opponent's team
      for (const pokemon of opponentPokemon) {
        await importTeam(pokemon, true);
      }
    } catch (error) {
      console.error('Error in handleImportTeams:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to import teams',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsImporting(false);
    }
  };

  const simulateBattle = async () => {
    console.log('Starting battle simulation...');
    console.log('Player team:', playerTeam);
    console.log('Opponent team:', opponentTeam);

    if (playerTeam.length === 0 || opponentTeam.length === 0) {
      const message = 'Please import both teams before simulating';
      console.warn(message);
      toast({
        title: 'Teams required',
        description: message,
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return null;
    }

    setIsSimulating(true);
    try {
      const response = await fetch('http://localhost:8001/calculate-battle-strategy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_team: {
            pokemon: playerTeam,
            active_pokemon_index: 0,
          },
          opponent_team: {
            pokemon: opponentTeam,
            active_pokemon_index: 0,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to simulate battle');
      }

      const data = await response.json();
      
      // Process the battle log to extract turns
      const turns: BattleTurn[] = [];
      let currentTurn: BattleTurn = {
        player_action: null,
        opponent_action: null,
        results: [],
      };

      let currentTurnNumber = 1;

      data.battle_log.forEach((entry: string) => {
        // Check if this is a turn marker
        if (entry.startsWith('Turn')) {
          if (currentTurn.results.length > 0) {
            turns.push({ ...currentTurn });
            currentTurn = {
              player_action: null,
              opponent_action: null,
              results: [],
            };
          }
          currentTurnNumber = parseInt(entry.split(' ')[1]);
        } else {
          // Extract player action
          if (entry.toLowerCase().includes('player') && entry.includes('used')) {
            const moveName = entry.split('used')[1].trim();
            currentTurn.player_action = {
              action_type: 'move',
              user: 'player',
              index: currentTurnNumber - 1,
              move_name: moveName,
            };
            currentTurn.results.push({
              action_desc: entry,
              effects: [],
              log: [entry],
            });
          }
          // Extract opponent action
          else if (entry.toLowerCase().includes('opponent') && entry.includes('used')) {
            const moveName = entry.split('used')[1].trim();
            currentTurn.opponent_action = {
              action_type: 'move',
              user: 'opponent',
              index: currentTurnNumber - 1,
              move_name: moveName,
            };
            currentTurn.results.push({
              action_desc: entry,
              effects: [],
              log: [entry],
            });
          }
          // Handle switch actions
          else if (entry.includes('switched from')) {
            const [fromPokemon, toPokemon] = entry.split('switched from')[1].split('to').map(s => s.trim());
            const isPlayer = entry.toLowerCase().includes('player');
            const action = {
              action_type: 'switch',
              user: isPlayer ? 'player' : 'opponent',
              index: currentTurnNumber - 1,
              from_pokemon: fromPokemon,
              to_pokemon: toPokemon,
            };
            if (isPlayer) {
              currentTurn.player_action = action;
            } else {
              currentTurn.opponent_action = action;
            }
            currentTurn.results.push({
              action_desc: entry,
              effects: [],
              log: [entry],
            });
          }
          // Add damage and effect results
          else if (entry.includes('Dealt') || entry.includes('super effective') || entry.includes('not very effective')) {
            if (currentTurn.results.length > 0) {
              currentTurn.results[currentTurn.results.length - 1].effects.push(entry);
            }
          }
          // Add faint results
          else if (entry.includes('fainted')) {
            currentTurn.results.push({
              action_desc: entry,
              effects: [],
              log: [entry],
            });
          }
        }
      });

      // Add the last turn if it has results
      if (currentTurn.results.length > 0) {
        turns.push(currentTurn);
      }

      setIsSimulating(false);
      return {
        winner: data.winner || null,
        turns: turns,
        battle_log: data.battle_log,
      };
    } catch (error) {
      console.error('Error simulating battle:', error);
      setIsSimulating(false);
      return null;
    }
  };

  return (
    <Box p={6}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>Pokémon Battle Simulator</Heading>
          <Text mb={4}>
            Paste your team's Pokémon Showdown export format below. Each Pokémon should be separated by a blank line.
          </Text>
        </Box>

        <VStack spacing={4} align="stretch">
          <Box>
            <Heading size="md" mb={2}>Your Team</Heading>
            <Textarea
              value={playerTeamText}
              onChange={(e) => setPlayerTeamText(e.target.value)}
              placeholder="Paste your team here..."
              height="200px"
              fontFamily="monospace"
            />
          </Box>

          <Box>
            <Heading size="md" mb={2}>Opponent's Team</Heading>
            <Textarea
              value={opponentTeamText}
              onChange={(e) => setOpponentTeamText(e.target.value)}
              placeholder="Paste opponent's team here..."
              height="200px"
              fontFamily="monospace"
            />
          </Box>

          <Button
            colorScheme="blue"
            onClick={handleImportTeams}
            isLoading={isImporting}
            loadingText="Importing..."
            size="lg"
          >
            Import Teams
          </Button>
        </VStack>

        {playerTeam.length > 0 && opponentTeam.length > 0 && (
          <BattleSimulator
            playerTeam={playerTeam}
            opponentTeam={opponentTeam}
            onSimulate={simulateBattle}
            isSimulating={isSimulating}
          />
        )}
      </VStack>
    </Box>
  );
}; 