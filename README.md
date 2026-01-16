# CS_2025_project - Chess Memory Game

## Description

A chess position memory training application. Users choose the number of pieces, memorize a position, and then recreate it. The app shows which pieces were placed correctly.

## Technologies

- **Flask 3.0.0** - Web framework
- **Flask-SQLAlchemy 3.1.1** - Database ORM
- **PostgreSQL 15** - Database (Docker Compose)
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD
- **Railway** - Deployment

## Project Structure

```
CS_2025_project/
├── app.py                    # Flask application
├── load_data.py              # Load CSV data
├── requirements.txt          # Dependencies
├── Dockerfile                # Docker config
├── docker-compose.yml        # Multi-container setup
├── .github/workflows/
│   └── ci-cd.yml            # CI/CD pipeline
├── templates/
│   └── index.html           # Web interface
└── data/
    └── puzzles.csv          # Chess positions
```

## Deployment with Docker Compose

### 1. Setup
```bash
# Clone repository
git clone git@github.com:CS-intro-with-Python/cs-project-2025-AssylkhanBalmukhanov.git
cd CS_2025_project
```

### 2. Start Application
```bash
docker-compose up -d
```

### 3. Load Data
```bash
docker exec chess_web python load_data.py data/puzzles.csv
```

### 4. Access
Open http://localhost:5000

## CSV Format

`data/puzzles.csv` format:
```csv
FEN,Evaluation,PieceCount
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1,0.0,32
```

## API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `GET /api/positions` - All positions
- `GET /api/positions/count/<n>` - Positions with n pieces
- `POST /api/game/start` - Start game
- `POST /api/game/submit` - Submit answer
- `GET /api/stats` - Statistics

## Logs

```bash
# View all logs
docker-compose logs -f

# Web service only
docker-compose logs -f web

# Database only
docker-compose logs -f db
```

## Stop Application

```bash
docker-compose down
```

## CI/CD

GitHub Actions automatically:
1. Builds Docker image
2. Runs container
3. Tests route accessibility

## Deployment to Railway

1. Push code to GitHub
2. Create Railway project from GitHub repo
3. Add PostgreSQL database
4. Set environment variables:
   - `SECRET_KEY=<random-key>`
   - `PORT=5000`
5. Deploy
6. Load data: `railway run python load_data.py data/puzzles.csv`

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection (auto-set by Railway)
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Environment (production/development)
- `PORT` - Application port (default: 5000)

## Troubleshooting

### Container won't start
```bash
docker-compose down -v
docker-compose up -d
```

### Data not loading
```bash
# Check file exists
ls -la data/puzzles.csv

# Reload data
docker exec chess_web python load_data.py data/puzzles.csv
```

### Port 5000 in use
```bash
# Kill process
lsof -ti:5000 | xargs kill -9
```

## License

Educational project for CS_2025 course. 
