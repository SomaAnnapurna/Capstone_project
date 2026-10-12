from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from .database import Country, CountryDatabaseManager


database = CountryDatabaseManager()
app = FastAPI(title="Country Data API", version="1.0.0")


def _model_dict(model: BaseModel) -> dict[str, object]:
    """Support both Pydantic v1 and v2 installations."""
    dump = getattr(model, "model_dump", None)
    return dump() if dump else model.dict()


class CountryPayload(BaseModel):
    name: str = Field(min_length=1)
    capital: str | None = None
    population: int = Field(ge=0)
    area: float = Field(ge=0)


class CountryUpdate(BaseModel):
    capital: str | None = None
    population: int = Field(ge=0)
    area: float = Field(ge=0)


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "country_count": database.count()}


@app.get("/countries", response_model=list[CountryPayload])
def list_countries() -> list[dict[str, object]]:
    return [country.to_dict() for country in database.list_all()]


@app.get("/countries/{name}", response_model=CountryPayload)
def get_country(name: str) -> dict[str, object]:
    country = database.get(name)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return country.to_dict()


@app.post("/countries", response_model=CountryPayload, status_code=status.HTTP_201_CREATED)
def create_country(payload: CountryPayload) -> dict[str, object]:
    if database.get(payload.name) is not None:
        raise HTTPException(status_code=409, detail="Country already exists")
    country = database.create(Country(**_model_dict(payload)))
    return country.to_dict()


@app.put("/countries/{name}", response_model=CountryPayload)
def update_country(name: str, payload: CountryUpdate) -> dict[str, object]:
    country = database.update(name, **_model_dict(payload))
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return country.to_dict()


@app.delete("/countries/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(name: str) -> None:
    if not database.delete(name):
        raise HTTPException(status_code=404, detail="Country not found")
