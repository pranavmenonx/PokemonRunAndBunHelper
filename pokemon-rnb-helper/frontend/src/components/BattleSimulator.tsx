import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Button,
  VStack,
  Text,
  Heading,
  Grid,
  GridItem,
  Badge,
  Progress,
  Card,
  CardHeader,
  CardBody,
  HStack,
  useToast,
  Image,
  Spinner,
} from '@chakra-ui/react';
import axios from 'axios';

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
    effects: string;
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
  turns: BattleTurn[];
  winner: string | null;
  battle_log: string[];
}

interface BattleSimulatorProps {
  playerTeam: Pokemon[];
  opponentTeam: Pokemon[];
  isSimulating: boolean;
  onSimulate: () => Promise<BattleResults | null>;
}

interface PokemonSpecies {
  id: number;
  name: string;
  varieties: Array<{
    is_default: boolean;
    pokemon: {
      name: string;
      url: string;
    };
  }>;
}

const TYPE_COLORS: Record<string, string> = {
  Normal: 'gray.500',
  Fire: 'red.500',
  Water: 'blue.500',
  Electric: 'yellow.500',
  Grass: 'green.500',
  Ice: 'cyan.500',
  Fighting: 'orange.800',
  Poison: 'purple.500',
  Ground: 'orange.500',
  Flying: 'blue.200',
  Psychic: 'pink.500',
  Bug: 'green.600',
  Rock: 'brown.500',
  Ghost: 'purple.800',
  Dragon: 'purple.600',
  Dark: 'gray.800',
  Steel: 'gray.400',
  Fairy: 'pink.300',
};

const getStatColor = (stat: string): string => {
  switch (stat) {
    case 'HP':
      return 'green';
    case 'Attack':
      return 'red';
    case 'Defense':
      return 'orange';
    case 'Sp. Attack':
      return 'blue';
    case 'Sp. Defense':
      return 'purple';
    case 'Speed':
      return 'yellow';
    default:
      return 'gray';
  }
};

const pokemonIdCache: { [key: string]: number } = {};

async function getPokemonId(name: string): Promise<number> {
  if (pokemonIdCache[name]) {
    return pokemonIdCache[name];
  }

  try {
    const formattedName = name.toLowerCase()
      .replace('-hisui', '')
      .replace(/[^a-z0-9-]/g, '');

    const response = await axios.get<PokemonSpecies>(`https://pokeapi.co/api/v2/pokemon-species/${formattedName}`);
    
    pokemonIdCache[name] = response.data.id;
    return response.data.id;
  } catch (error) {
    console.error(`Error fetching Pokémon ID for ${name}:`, error);
    return 0;
  }
}

// Add this new component for Pokemon cards
const PokemonCard: React.FC<{ pokemon: Pokemon }> = ({ pokemon }) => {
  const [spriteId, setSpriteId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadSprite = async () => {
      setIsLoading(true);
      const id = await getPokemonId(pokemon.name);
      setSpriteId(id);
      setIsLoading(false);
    };
    loadSprite();
  }, [pokemon.name]);

  if (!pokemon || !pokemon.types || !pokemon.stats || !pokemon.moves) {
    console.error('Invalid Pokemon data:', pokemon);
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <HStack spacing={4} width="100%">
          {isLoading ? (
            <Box boxSize="96px" display="flex" alignItems="center" justifyContent="center">
              <Spinner />
            </Box>
          ) : (
            <Image
              src={`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${spriteId || 0}.png`}
              alt={pokemon.name}
              boxSize="96px"
              fallbackSrc="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png"
            />
          )}
          <VStack align="start" spacing={2} flex={1}>
            <Heading size="md">{pokemon.name}</Heading>
            <HStack>
              {pokemon.types.map((type) => (
                <Badge key={type} bg={TYPE_COLORS[type] || 'gray.500'}>
                  {type}
                </Badge>
              ))}
            </HStack>
          </VStack>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={4} align="stretch">
          <Box>
            <Text fontWeight="bold">Ability: {pokemon.ability}</Text>
            {pokemon.item && <Text>Item: {pokemon.item}</Text>}
          </Box>
          <Box>
            <Text fontWeight="bold">Stats:</Text>
            <Grid templateColumns="auto 1fr" gap={2}>
              {Object.entries(pokemon.stats).map(([stat, value]) => (
                <React.Fragment key={stat}>
                  <Text>{stat}:</Text>
                  <HStack spacing={2}>
                    <Text>{value}</Text>
                    <Progress
                      value={(value / 255) * 100}
                      size="sm"
                      width="100px"
                      colorScheme={getStatColor(stat)}
                    />
                  </HStack>
                </React.Fragment>
              ))}
            </Grid>
          </Box>
          <Box>
            <Text fontWeight="bold" mb={2}>Moves:</Text>
            <Grid templateColumns="repeat(2, 1fr)" gap={2}>
              {pokemon.moves.map((move) => (
                <Box
                  key={move.name}
                  position="relative"
                  _hover={{
                    '& > div': {
                      opacity: 1,
                      visibility: 'visible',
                    }
                  }}
                >
                  <Badge
                    width="100%"
                    p={2}
                    variant="subtle"
                    colorScheme={TYPE_COLORS[move.type]?.split('.')[0] || 'gray'}
                  >
                    {move.name}
                  </Badge>
                  <Box
                    position="absolute"
                    bottom="100%"
                    left="0"
                    right="0"
                    bg="gray.700"
                    color="white"
                    p={2}
                    borderRadius="md"
                    opacity={0}
                    visibility="hidden"
                    transition="all 0.2s"
                    zIndex={1}
                    boxShadow="lg"
                  >
                    <VStack align="start" spacing={1}>
                      <HStack>
                        <Badge colorScheme={TYPE_COLORS[move.type]?.split('.')[0] || 'gray'}>
                          {move.type}
                        </Badge>
                        <Badge colorScheme="blue">{move.category}</Badge>
                      </HStack>
                      {move.power && <Text>Power: {move.power}</Text>}
                      {move.accuracy && <Text>Accuracy: {move.accuracy}</Text>}
                      <Text fontSize="sm">{move.effects}</Text>
                    </VStack>
                  </Box>
                </Box>
              ))}
            </Grid>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export const BattleSimulator: React.FC<BattleSimulatorProps> = ({
  playerTeam,
  opponentTeam,
  onSimulate,
  isSimulating,
}) => {
  const [battleResults, setBattleResults] = useState<BattleResults | null>(null);
  const [currentTurn, setCurrentTurn] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    setBattleResults(null);
    setCurrentTurn(0);
    setError(null);
  }, [playerTeam, opponentTeam]);

  const validateBattleResults = (results: any): results is BattleResults => {
    if (!results || typeof results !== 'object') return false;
    if (!Array.isArray(results.turns)) return false;
    if (!Array.isArray(results.battle_log)) return false;
    if (typeof results.winner !== 'string' && results.winner !== null) return false;
    
    return true;
  };

  const handleSimulate = useCallback(async (e: React.MouseEvent) => {
    e.preventDefault();
    setError(null);
    setBattleResults(null);
    setCurrentTurn(0);

    console.log('Starting battle simulation in BattleSimulator...');
    console.log('Player team:', playerTeam);
    console.log('Opponent team:', opponentTeam);

    try {
      const results = await onSimulate();
      console.log('Battle simulation results:', results);
      
      if (!results) {
        throw new Error('No battle results received from server');
      }

      if (!validateBattleResults(results)) {
        throw new Error('Invalid battle results format received from server');
      }

      setBattleResults(results);
      setCurrentTurn(0);

      toast({
        title: 'Battle simulation complete',
        description: `Winner: ${results.winner || 'Draw'}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error in handleSimulate:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to simulate battle';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  }, [playerTeam, opponentTeam, onSimulate, toast]);

  const renderPokemonCard = useCallback((pokemon: Pokemon) => {
    return <PokemonCard pokemon={pokemon} />;
  }, []);

  if (error) {
    return (
      <Box p={4} borderWidth={1} borderRadius="lg" bg="red.50">
        <Text color="red.500">{error}</Text>
        <Button mt={4} onClick={() => setError(null)} colorScheme="red">
          Try Again
        </Button>
      </Box>
    );
  }

  return (
    <Box w="100%">
      <VStack spacing={6} align="stretch">
        <Grid templateColumns="repeat(2, 1fr)" gap={6}>
          <GridItem>
            <Heading size="md" mb={4}>Your Team</Heading>
            <VStack spacing={4}>
              {playerTeam.map((pokemon) => (
                <Box key={pokemon.name} w="100%">
                  {renderPokemonCard(pokemon)}
                </Box>
              ))}
            </VStack>
          </GridItem>
          <GridItem>
            <Heading size="md" mb={4}>Opponent's Team</Heading>
            <VStack spacing={4}>
              {opponentTeam.map((pokemon) => (
                <Box key={pokemon.name} w="100%">
                  {renderPokemonCard(pokemon)}
                </Box>
              ))}
            </VStack>
          </GridItem>
        </Grid>

        <Button
          colorScheme="blue"
          onClick={handleSimulate}
          isLoading={isSimulating}
          loadingText="Simulating..."
          size="lg"
          w="full"
        >
          Simulate Battle
        </Button>

        {battleResults && (
          <Box borderWidth={1} borderRadius="lg" p={4} bg="white" shadow="md">
            <VStack spacing={4} align="stretch">
              <Heading size="md">Battle Results</Heading>
              <Text fontSize="lg" fontWeight="bold" color={battleResults.winner ? "green.500" : "gray.500"}>
                {battleResults.winner ? `Winner: ${battleResults.winner}` : 'Battle ended in a draw'}
              </Text>

              <Box>
                <Text fontWeight="bold" mb={2}>Battle Log:</Text>
                <VStack align="stretch" spacing={2} maxH="300px" overflowY="auto">
                  {battleResults.battle_log.map((log, index) => (
                    <Text key={index}>{log}</Text>
                  ))}
                </VStack>
              </Box>

              {battleResults.turns.length > 0 && currentTurn < battleResults.turns.length && (
                <Box>
                  <Text fontWeight="bold" mb={2}>Turn {currentTurn + 1} / {battleResults.turns.length}</Text>
                  <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                    <GridItem>
                      <VStack align="stretch">
                        <Text fontWeight="bold">Player Action:</Text>
                        {battleResults.turns[currentTurn]?.player_action ? (
                          <Text>
                            {battleResults.turns[currentTurn].player_action.action_type === 'move' ? (
                              <>Using move: {battleResults.turns[currentTurn].player_action.move_name}</>
                            ) : battleResults.turns[currentTurn].player_action.action_type === 'switch' ? (
                              <>Switched from {battleResults.turns[currentTurn].player_action.from_pokemon} to {battleResults.turns[currentTurn].player_action.to_pokemon}</>
                            ) : (
                              'Unknown action'
                            )}
                          </Text>
                        ) : (
                          <Text>No action</Text>
                        )}
                      </VStack>
                    </GridItem>

                    <GridItem>
                      <VStack align="stretch">
                        <Text fontWeight="bold">Opponent Action:</Text>
                        {battleResults.turns[currentTurn]?.opponent_action ? (
                          <Text>
                            {battleResults.turns[currentTurn].opponent_action.action_type === 'move' ? (
                              <>Using move: {battleResults.turns[currentTurn].opponent_action.move_name}</>
                            ) : battleResults.turns[currentTurn].opponent_action.action_type === 'switch' ? (
                              <>Switched from {battleResults.turns[currentTurn].opponent_action.from_pokemon} to {battleResults.turns[currentTurn].opponent_action.to_pokemon}</>
                            ) : (
                              'Unknown action'
                            )}
                          </Text>
                        ) : (
                          <Text>No action</Text>
                        )}
                      </VStack>
                    </GridItem>
                  </Grid>

                  <Box mt={4}>
                    <Text fontWeight="bold">Turn Results:</Text>
                    {battleResults.turns[currentTurn]?.results.map((result, index) => (
                      <Box key={index} mt={2} p={2} borderWidth={1} borderRadius="md">
                        <Text>{result.action_desc}</Text>
                        {result.effects.length > 0 && result.effects.map((effect, effectIndex) => (
                          <Text key={effectIndex} color="gray.600" ml={4}>
                            {effect}
                          </Text>
                        ))}
                      </Box>
                    ))}
                  </Box>

                  <HStack spacing={4} justify="center" mt={4}>
                    <Button
                      onClick={() => setCurrentTurn(prev => Math.max(0, prev - 1))}
                      isDisabled={currentTurn === 0}
                    >
                      Previous Turn
                    </Button>
                    <Button
                      onClick={() => setCurrentTurn(prev => Math.min(battleResults.turns.length - 1, prev + 1))}
                      isDisabled={currentTurn === battleResults.turns.length - 1}
                    >
                      Next Turn
                    </Button>
                  </HStack>
                </Box>
              )}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
}; 