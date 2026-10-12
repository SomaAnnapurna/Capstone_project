# Country Data Pipeline and Analytics

A Python capstone project that scrapes the first 20 country records from Scrape This Site, stores them in SQLite, exposes CRUD operations through FastAPI, and exports API data to CSV with a population-versus-area scatter plot.

## Project files

- `Scraper.py` downloads and parses country records, then saves them to SQLite.
- `Database.py` defines the `Country` model and SQLite CRUD manager.
- `Api.py` provides health and country CRUD endpoints.
- `Client.py` downloads records from the API, writes a CSV file, and creates a scatter plot.
- `requirements.txt` lists the Python packages needed to run the project.
- `data/` is created automatically for the SQLite database and generated analysis files.

The project uses Python 3.9 or newer. It uses the Python standard-library SQLite driver, so no separate database server or credentials are required.

## Setup on macOS

Open this folder in VS Code. In its Terminal, create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the pipeline

Run these commands from this project folder.

1. Scrape and store up to 20 countries:

   ```bash
   python Scraper.py
   ```

   The database is created at `data/countries.db`. To use another record limit, run `python Scraper.py --limit 20`.

2. Start the API in a Terminal window and leave it running:

   ```bash
   uvicorn Api:app --reload
   ```

3. In a second Terminal window, activate the same virtual environment and run the analysis client:

   ```bash
   source .venv/bin/activate
   python Client.py
   ```

   The client writes `data/countries.csv` and `data/population_area.png`. Open the API documentation at `http://127.0.0.1:8000/docs`.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | API health and record count |
| `GET` | `/countries` | List all countries |
| `GET` | `/countries/{name}` | Get a country by name |
| `POST` | `/countries` | Create a country |
| `PUT` | `/countries/{name}` | Update capital, population, and area |
| `DELETE` | `/countries/{name}` | Delete a country |

Example request body for `POST /countries`:

```json
{
  "name": "Exampleland",
  "capital": "Example City",
  "population": 1000000,
  "area": 12345.6
}
```

## GitHub

The `.gitignore` file excludes `.venv`, local environment files, the SQLite database, and generated CSV/plot outputs. Commit the Python source, README, and `requirements.txt`; do not commit credentials or private data.
