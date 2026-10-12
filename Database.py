import os
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_DATABASE_PATH = Path(os.getenv("COUNTRY_DB_PATH", "data/countries.db"))


@dataclass(frozen=True)
class Country:
    name: str
    capital: str | None
    population: int
    area: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CountryDatabaseManager:
    """Owns the SQLite schema and provides explicit CRUD methods."""

    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
CREATE TABLE IF NOT EXISTS countries (
                    name TEXT PRIMARY KEY,
                    capital TEXT,
                    population INTEGER NOT NULL CHECK (population >= 0),
                    area REAL NOT NULL CHECK (area >= 0)
                )
                """
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Country:
        return Country(
            name=row["name"],
            capital=row["capital"],
            population=int(row["population"]),
            area=float(row["area"]),
        )

    def create(self, country: Country) -> Country:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO countries(name, capital, population, area) VALUES (?, ?, ?, ?)",
                (country.name, country.capital, country.population, country.area),
            )
        return country

    def upsert_many(self, countries: Iterable[Country]) -> int:
        rows = [(c.name, c.capital, c.population, c.area) for c in countries]
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO countries(name, capital, population, area)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    capital = excluded.capital,
                    population = excluded.population,
                    area = excluded.area
                """,
                rows,
                )
        return len(rows)

    def get(self, name: str) -> Country | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT name, capital, population, area FROM countries WHERE name = ?",
                (name,),
            ).fetchone()
        return self._from_row(row) if row else None

    def list_all(self) -> list[Country]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name, capital, population, area FROM countries ORDER BY name"
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, name: str, *, capital: str | None, population: int, area: float) -> Country | None:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE countries SET capital = ?, population = ?, area = ? WHERE name = ?",
                (capital, population, area, name),
            )
        return self.get(name) if cursor.rowcount else None

    def delete(self, name: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM countries WHERE name = ?", (name,))
        return cursor.rowcount > 0

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM countries").fetchone()[0])
