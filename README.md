# Pokemon Run and Bun Helper

A sophisticated battle simulation tool for Pokemon Run and Bun, featuring AI-powered battle strategy calculation and team analysis.

## Features

- **Battle Simulation**: Simulate battles between two Pokemon teams with detailed turn-by-turn analysis
- **AI Strategy Calculation**: Advanced AI that determines optimal moves and switch decisions
- **Team Analysis**: Analyze team compositions and matchups
- **Real-time Battle Log**: Detailed battle log showing moves, damage, effects, and switches
- **Modern UI**: Clean and responsive interface built with React and Chakra UI

## Tech Stack

### Frontend
- React with TypeScript
- Vite for build tooling
- Chakra UI for components
- Real-time state management
- Type-safe Pokemon data structures

### Backend
- Python with FastAPI
- AI-powered battle simulation
- Pokemon data parsing and validation
- Battle mechanics implementation
- RESTful API endpoints

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/pranavmenonx/PokemonRunAndBunHelper.git
cd PokemonRunAndBunHelper
```

2. Set up the backend:
```bash
cd pokemon-rnb-helper/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd ../frontend
npm install
```

### Running the Application

1. Start the backend server (from the backend directory):
```bash
python3 -m uvicorn main:app --reload --port 8001
```

2. Start the frontend development server (from the frontend directory):
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Usage

1. **Team Setup**
   - Import your Pokemon team using the Showdown format
   - Add Pokemon one by one with their moves, abilities, and stats

2. **Battle Simulation**
   - Select your team and the opponent's team
   - Click "Simulate Battle" to start the simulation
   - View detailed turn-by-turn results
   - Analyze AI decisions and battle outcomes

3. **Battle Analysis**
   - Review move effectiveness and damage calculations
   - See AI reasoning for switches and move choices
   - Analyze team matchups and potential improvements

## Project Structure

```
pokemon-rnb-helper/
├── backend/
│   ├── ai_logic.py         # AI decision making
│   ├── battle_logic.py     # Battle mechanics
│   ├── main.py            # FastAPI application
│   ├── showdown_parser.py # Pokemon data parser
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── types/        # TypeScript types
│   │   └── App.tsx       # Main application
│   ├── package.json      # Node dependencies
│   └── vite.config.ts    # Vite configuration
└── README.md
```

## API Endpoints

- `POST /parse-showdown`: Parse Pokemon data from Showdown format
- `POST /calculate-battle-strategy`: Calculate battle moves and strategy
- `POST /simulate-battle`: Run a complete battle simulation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Pokemon Showdown for battle mechanics reference
- Pokemon Run and Bun community
- Contributors and testers

## Contact

Pranav Menon - [@pranavmenonx](https://github.com/pranavmenonx)

Project Link: [https://github.com/pranavmenonx/PokemonRunAndBunHelper](https://github.com/pranavmenonx/PokemonRunAndBunHelper) 