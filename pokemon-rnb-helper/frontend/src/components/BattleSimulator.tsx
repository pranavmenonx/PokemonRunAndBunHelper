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
} from '@chakra-ui/react';

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
    // Reset state when teams change
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
    if (!pokemon || !pokemon.types || !pokemon.stats || !pokemon.moves) {
      console.error('Invalid Pokemon data:', pokemon);
      return null;
    }

    return (
      <Card>
        <CardHeader>
          <VStack align="start" spacing={2}>
            <Heading size="md">{pokemon.name}</Heading>
            <HStack>
              {pokemon.types.map((type) => (
                <Badge key={type} bg={TYPE_COLORS[type] || 'gray.500'}>
                  {type}
                </Badge>
              ))}
            </HStack>
          </VStack>
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
                    <Text>{stat}: {value}</Text>
                    <Progress value={(value / 255) * 100} size="sm" colorScheme="blue" />
                  </React.Fragment>
                ))}
              </Grid>
            </Box>
            <Box>
              <Text fontWeight="bold">Moves:</Text>
              <Grid templateColumns="repeat(2, 1fr)" gap={2}>
                {pokemon.moves.map((move) => (
                  <Badge
                    key={move.name}
                    variant="subtle"
                    colorScheme={TYPE_COLORS[move.type]?.split('.')[0] || 'gray'}
                  >
                    {move.name}
                  </Badge>
                ))}
              </Grid>
            </Box>
          </VStack>
        </CardBody>
      </Card>
    );
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