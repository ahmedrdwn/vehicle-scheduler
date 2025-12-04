# Vehicle Scheduling Optimizer

A web application for solving vehicle scheduling problems using maximum bipartite matching. This tool helps determine the minimum number of vehicles required to cover all trips while respecting deadhead times between terminals.

## Features

- Interactive web interface for inputting trips and deadhead times
- Real-time schedule calculation
- Visual representation of vehicle blocks
- Example data loader for quick testing

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vue.js 3 with Tailwind CSS
- **Deployment**: Vercel

## Local Development

1. Install dependencies:
```bash
pip install -r web_app/requirements.txt
```

2. Run the application:
```bash
cd web_app
python main.py
```

3. Open your browser to `http://127.0.0.1:8000`

## Project Structure

```
.
├── web_app/
│   ├── main.py          # FastAPI application
│   ├── logic.py         # Scheduling algorithm
│   ├── requirements.txt # Python dependencies
│   └── static/
│       └── index.html   # Frontend UI
├── vercel.json          # Vercel configuration
└── README.md
```

## Algorithm

The application uses a maximum bipartite matching algorithm to solve the vehicle scheduling problem:

1. Builds a graph of feasible trip connections based on arrival times and deadhead times
2. Finds the maximum matching using bipartite matching
3. Calculates minimum vehicles: `total_trips - maximum_matching`
4. Extracts vehicle blocks (chains of connected trips)

## Deployment

### Vercel

This project is configured for Vercel deployment. Simply connect your GitHub repository to Vercel and it will automatically deploy.

### GitHub

1. Initialize git repository (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create a new repository on GitHub

3. Push to GitHub:
```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

## License

MIT

