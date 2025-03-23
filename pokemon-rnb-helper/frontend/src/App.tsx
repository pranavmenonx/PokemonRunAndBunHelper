import { Container, Stack, Heading, ChakraProvider } from "@chakra-ui/react";
import { BattleCalculator } from "./components/BattleCalculator";

function App() {
  return (
    <ChakraProvider>
      <Container maxW="container.xl" py={8}>
        <Stack spacing={8}>
          <Heading>Pokemon Run and Bun Helper</Heading>
          <BattleCalculator />
        </Stack>
      </Container>
    </ChakraProvider>
  );
}

export default App;
