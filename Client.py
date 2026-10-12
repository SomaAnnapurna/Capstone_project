import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import requests

from .database import CountryDatabaseManager
from .scraper import fetch_countries


def scrape_command(args: argparse.Namespace) -> None:
    countries = fetch_countries(limit=args.limit)
    manager = CountryDatabaseManager(args.database)
    count = manager.upsert_many(countries)
    print(f"Loaded {count} country records into {args.database}")


def analyze_command(args: argparse.Namespace) -> None:
    response = requests.get(f"{args.base_url.rstrip('/')}/countries", timeout=20)
    response.raise_for_status()
    countries = response.json()
    csv_path = Path(args.csv)
    plot_path = Path(args.plot)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "capital", "population", "area"])
        writer.writeheader()
        writer.writerows(countries)
    figure, axis = plt.subplots(figsize=(10, 6))
    x = [country["area"] for country in countries]
    y = [country["population"] for country in countries]
    axis.scatter(x, y, alpha=0.8)
    for country in countries:
        axis.annotate(country["name"], (country["area"], country["population"]), fontsize=7, xytext=(4, 4), textcoords="offset points")
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlabel("Area (km², logarithmic scale)")
    axis.set_ylabel("Population (logarithmic scale)")
    axis.set_title("Population versus area for the first 20 countries")
    axis.grid(True, which="both", alpha=0.25)
    figure.tight_layout()
    figure.savefig(plot_path, dpi=160)
    plt.close(figure)
    print(f"Wrote {csv_path} and {plot_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Country data pipeline commands")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scrape = subparsers.add_parser("scrape", help="scrape and store country records")
    scrape.add_argument("--limit", type=int, default=20)
    scrape.add_argument("--database", default="data/countries.db")
    scrape.set_defaults(function=scrape_command)
    analyze = subparsers.add_parser("analyze", help="export API data and create a scatter plot")
    analyze.add_argument("--base-url", default="http://127.0.0.1:8000")
    analyze.add_argument("--csv", default="data/countries.csv")
    analyze.add_argument("--plot", default="data/population_area.png")
    analyze.set_defaults(function=analyze_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
